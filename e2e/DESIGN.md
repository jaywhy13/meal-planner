# End-to-end test suite — design

## Purpose

A general, extensible end-to-end harness that drives a real headless browser against a
production-like stack (the real Django backend + the built React frontend served by nginx). Its first job is
to catch **runaway redirect and request loops** — pages that redirect endlessly or hammer an
endpoint forever — but it is built to grow into broad behavioural coverage, not to chase one bug.

### Motivating bug

The production login page redirects endlessly. Pull request #58 fixed an infinite **401 retry**
loop in the Axios response interceptor, but a separate **redirect** loop remains: on load,
`AuthProvider` calls the anonymous `getProfile` probe, which `401`s; the interceptor refreshes,
that also `401`s, and the `catch` runs `window.location.href = '/login'` — a full page load — even
when the user is already on `/login`. The page reloads, the probe runs again, and the cycle never
terminates.

Unit tests could not catch this: it only manifests in a real browser that actually performs
navigations and accumulates network traffic. That is the gap this suite closes.

## Layering

Three layers, with dependency arrows pointing inward, mirroring the project's existing
view/service/repository discipline:

```
tests (assertions)  ->  business-native layer (page objects)  ->  tooling abstraction (browser)
```

1. **Tooling abstraction layer** — wraps the browser tool (Playwright). Knows *nothing* about the
   meal-planner app: no routes, no button captions, no labels. Exposes generic primitives and
   typed UI element data types. Contains **no assertions**.
2. **Business-native layer** — page-object classes organised by app page. Owns app vocabulary
   (routes, captions, labels) and actions like `login(email, password)`. Returns the generic
   `Page` from the abstraction layer. Contains **no assertions**.
3. **Tests** — the only layer that asserts. Uses the business layer to act and the `Page`
   introspection surface to verify outcomes.

**No layer below the tests asserts anything.** The lower layers expose state for tests to inspect;
they raise exceptions only as *guards* against pathological conditions (e.g. a runaway redirect loop),
which is distinct from making a test assertion.

Underlying tool choice — **Playwright** — is hidden entirely behind the abstraction layer. If we
ever replace it, only the abstraction layer changes.

---

## Layer 1 — Tooling abstraction

### Responsibilities

- Own the browser lifecycle (`BrowserSession`).
- Provide generic navigation and interaction primitives.
- Locate elements with accessible-first descriptors.
- Continuously record a network + navigation log.
- Protect against runaway loops: wait for the page to go quiet, and *throw* the moment there are
  too many redirects or too many requests to one endpoint.

### Element location

Accessible-first, matching the frontend's React Testing Library convention. A locator is a small
descriptor; the abstraction layer branches explicitly on which field is present (one branch per
case, no fallback ordering), with `testId` only as an escape hatch:

```ts
type ElementLocator =
  | { role: string; name: string }   // getByRole({ name })
  | { label: string }                // getByLabel
  | { text: string }                 // getByText
  | { testId: string };              // escape hatch only
```

### `BrowserSession`

Owns the Playwright browser/page. Takes its browser dependency in the constructor so it is
swappable in tests of the harness itself.

```ts
interface SessionOptions {
  baseUrl: string;
  // The waiting knobs below have sane defaults; tests rarely set them. They exist so a
  // test against a deliberately slow page can widen the window without editing the harness.
  quietPeriodMs?: number;         // default 300 — treat the page as "done" after this long with no new request/navigation
  maxWaitMs?: number;             // default 2000 — never wait longer than this for one navigation
  maxRedirects?: number;          // default 20 — throw past this many full-page navigations
  maxRequestsPerEndpoint?: number; // default 25 — throw past this many requests to one endpoint
}

class BrowserSession {
  constructor(browser: Browser, options: SessionOptions);

  /** Navigate to a path and return whatever page we actually land on. Never asserts arrival. */
  loadPage(path: string): Promise<Page>;

  /** Tear down the browser context. */
  close(): Promise<void>;
}
```

`loadPage` navigates, **waits for the page to go quiet** (capped by `maxWaitMs` so a looping
page can never hang it), and returns the resulting `Page`. It does not verify it arrived where
requested — a redirect away from `path` yields a `Page` whose `redirects` log shows what happened.
If there are too many redirects or too many requests to one endpoint while waiting, `loadPage`
throws (see [Infinite-loop protection](#infinite-loop-protection-throw-never-assert)).

### `Page`

The value returned by every navigation and action. Carries location, the logs, element queries,
and `isXxx` sugar. Carries **no `statusCode`** — this is a client-routed single-page application,
so most transitions have no HTTP status; status lives per-request inside `requests`.

```ts
class Page {
  readonly path: string;            // current pathname
  readonly url: string;             // full current URL
  readonly title: string;           // document.title
  readonly redirects: Redirect[];   // ordered full-document navigations that occurred
  readonly requests: RequestLog;    // queryable network log

  isAt(route: string): boolean;     // sugar over `path`

  // Queries locate an element and return a static snapshot of it (see "Elements are
  // snapshots" below). They are async because reading the live element is async.
  button(locator: ElementLocator): Promise<Button>;
  input(locator: ElementLocator): Promise<Input>;
  link(locator: ElementLocator): Promise<Link>;
  text(locator: ElementLocator): Promise<TextElement>;
  form(locator: ElementLocator): Promise<Form>;

  // Interaction lives on the page, not on the element: the element is just a descriptor,
  // the page knows how to act on it. Each interaction re-locates from the snapshot's
  // descriptor, so a stale snapshot still acts on the right element.
  click(element: Button | Link): Promise<Page>;
  setValue(input: Input, value: string): Promise<void>;
  submit(form: Form): Promise<Page>;
}
```

### Network + navigation logs

Recording is **always on** from the moment a page loads. The log is the substrate for loop
detection; tests query it directly.

```ts
interface RecordedRequest {
  url: string;
  method: string;
  status: number | null;   // null if the request never completed
}

class RequestLog {
  all(): RecordedRequest[];
  to(pattern: string): RecordedRequest[];   // glob/prefix match, e.g. '/auth/*'
  count(pattern: string): number;
}

interface Redirect {
  from: string;
  to: string;
}
```

### Typed UI element data types

An element is a **static snapshot**, not a live handle. A query (`page.button(...)`) locates the
element once, captures its descriptor plus the properties readable at that instant, and returns a
plain data object. The verbs live on the `Page` (`page.click(button)`), so the element carries no
reference back to the page or the browser.

**Snapshots can go stale — by design.** The captured properties (`isVisible`, an input's `value`)
reflect the DOM *at query time* and do **not** update when the page changes. This is a deliberate
trade-off: a simple, decoupled value object at the cost of freshness. After an interaction that
changes the page, **re-query** to get a fresh snapshot rather than re-reading the old one. (The
`descriptor` it carries is enough for the page to re-locate the live element when acting on it, so
interactions are always against the current DOM even if the read-only properties are stale.)

```ts
class Button {
  readonly descriptor: ElementLocator;
  readonly isVisible: boolean;
  readonly isEnabled: boolean;
}

class Input {
  readonly descriptor: ElementLocator;
  readonly value: string;      // consistent with TextElement.value — both are read snapshots
  readonly isVisible: boolean;
}

class Link {
  readonly descriptor: ElementLocator;
  readonly href: string;
  readonly isVisible: boolean;
}

class TextElement {
  readonly descriptor: ElementLocator;
  readonly value: string;      // the element's text
  readonly isVisible: boolean;
}

class Form {
  readonly descriptor: ElementLocator;
}
```

### Infinite-loop protection (throw, never assert)

Two mechanisms keep a looping app observable instead of hanging:

1. **Wait for the page to go quiet — but never forever.** After a navigation or action, wait until
   no new request or navigation has fired for `quietPeriodMs`, *or* until `maxWaitMs` elapses —
   whichever comes first — then return the `Page`. The hard `maxWaitMs` cap is the whole point: an
   open-ended "wait for the network to be idle" would hang forever on a loop and report a useless
   timeout instead of the actual problem.

2. **Stop and report the moment a loop is obvious.** While waiting, if full-page navigations exceed
   `maxRedirects`, or requests to a single endpoint exceed `maxRequestsPerEndpoint`, abort
   immediately and throw a typed error that *names the loop* rather than waiting out the cap:

```ts
class TooManyRedirectsError extends Error {
  readonly redirects: Redirect[];
}
class ExcessiveRequestsError extends Error {
  readonly endpoint: string;
  readonly count: number;
}
```

These errors carry the evidence (`redirects`, `endpoint`, `count`) so a failing test reads
"25 requests to `/auth/token/refresh`" rather than "timed out after 30s".

---

## Layer 2 — Business-native layer

### Responsibilities

- One page-object **class per app page**, organised by page.
- Own the app's vocabulary: routes, button captions, field labels — **co-located with the page**
  that uses them, not in a global bag.
- Expose actions (e.g. `login`) that drive the abstraction layer and return the generic `Page`.
- Provide test-data factories that create fresh state per test.
- Contain **no assertions**.

### Routes

`loadPage` needs paths up front, so routes live in one small registry (the only cross-page
constant). Routes are app knowledge, so they belong to the business layer, not the abstraction
layer.

```ts
const Routes = {
  LOGIN: '/login',
  HOME: '/',
  SIGN_UP: '/signup',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
} as const;
```

### Page objects

Each page owns its captions/labels as private constants and uses them inside its actions. Actions
return the generic `Page` so a broken app cannot hand back a "valid" typed page object — the test
inspects what actually happened.

```ts
class LoginPage {
  // Co-located vocabulary — the page's own words. `LABEL_`/`CAPTION_` prefixes so every
  // label or caption is greppable as a group.
  private static readonly LABEL_EMAIL = 'Email';
  private static readonly LABEL_PASSWORD = 'Password';
  private static readonly CAPTION_SIGN_IN = 'Sign in';

  constructor(private readonly session: BrowserSession) {}

  /** Loads /login and returns the resulting page (does not assert arrival). */
  open(): Promise<Page>;

  /** Fills credentials, submits, and returns the resulting page. */
  async login(email: string, password: string): Promise<Page> {
    const page = await this.session.loadPage(Routes.LOGIN);
    await page.setValue(await page.input({ label: LoginPage.LABEL_EMAIL }), email);
    await page.setValue(await page.input({ label: LoginPage.LABEL_PASSWORD }), password);
    const signInButton = await page.button({ role: 'button', name: LoginPage.CAPTION_SIGN_IN });
    return page.click(signInButton);
  }
}
```

Further page objects (`SignUpPage`, `ForgotPasswordPage`, `ResetPasswordPage`, `HomePage`) follow
the same shape and are added as tests need them.

### Test-data factory

Each test creates its **own** user via the real registration endpoint (`POST /api/auth/register`)
with a unique email, so tests share no state and cannot clash. This follows the project's
"declare test data close to where it's used / factory per test" convention and is the foundation
of the zero-flakiness goal.

```ts
interface TestUser {
  email: string;
  password: string;
}

/** Registers a fresh, uniquely-named user against the real backend and returns its credentials. */
function createTestUser(overrides?: Partial<TestUser>): Promise<TestUser>;
```

---

## Layer 3 — Tests

The only layer with assertions. Acts through the business layer; verifies through the `Page`
introspection surface. One concern per test.

### Flagship — runaway redirect / request loop on the login page

This is the test that would have caught the live bug.

```ts
test('loading the login page as an anonymous user does not loop or flood requests', async () => {
  const page = await new LoginPage(session).open();

  expect(page.isAt(Routes.LOGIN)).toBe(true);          // we stayed on /login
  expect(page.redirects.length).toBeLessThanOrEqual(1); // no redirect loop
  expect(page.requests.count('/auth/*')).toBeLessThan(5); // no request flood
});
```

If the bug is present, the harness throws `TooManyRedirectsError` / `ExcessiveRequestsError`
before these assertions even run — and the error names the offending endpoint.

### Happy-path login

```ts
test('a registered user can log in and lands on the home page', async () => {
  const user = await createTestUser();

  const page = await new LoginPage(session).login(user.email, user.password);

  expect(page.isAt(Routes.HOME)).toBe(true);
});
```

---

## Running the suite

Per the Docker-first policy, nothing runs on the host:

- A root `Makefile` target **`make e2e`** brings up a production-like stack — the built frontend
  served by nginx, the real Django backend — and the Playwright runner, all via
  `docker compose`, wrapped in `scripts/isolate-env-vars.sh` so it is worktree-safe.
- A Playwright **global setup** waits on backend/frontend health before any test runs. It owns no
  test data — data is created per test by `createTestUser`.
- The suite lives in a top-level **`e2e/`** directory with its own `package.json` and Playwright
  config, since it spans both services and does not belong inside `frontend/`.

## CI

A GitHub Actions job runs `make e2e` against a fresh stack. It starts **non-blocking**: the
flagship test is red until the redirect-loop bug is fixed, so gating merges on it now would block
every pull request. Once the bug is fixed and the suite is green, we flip it to **required**.

Reliability is a hard requirement: prefer event-based waits over fixed sleeps, and use
deterministic per-test data with a trace captured on failure. **We never retry a failed test
automatically** — a flake must be felt and fixed, not silently re-run into a green build.

## Delivery (stacked pull requests)

1. AGENTS.md → TypeScript correction (precedes everything).
2. This design document.
3. **Abstraction layer** + Docker / `make e2e` plumbing, with harness tests against a static
   fixture page.
4. **Business layer** — page objects, route/caption/label constants, `createTestUser`.
5. **Tests** + the (initially non-blocking) CI job.
