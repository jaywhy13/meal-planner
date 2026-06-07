# End-to-end test suite — design

## Purpose

A general, extensible end-to-end harness that drives a real headless browser against a
production-like stack (real Django backend + built React frontend + Postgres). Its first job is
to catch **navigation / request storms** — unbounded redirect or retry loops — but it is built to
grow into broad behavioural coverage, not to chase one bug.

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
they raise exceptions only as *guards* against pathological conditions (e.g. a redirect storm),
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
- Enforce loop guards (bounded settle + fail-fast circuit breaker) that *throw*.

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
  settleQuietPeriodMs?: number;   // default 300 — "quiet" = no new request/navigation for this long
  settleTimeoutMs?: number;       // default 2000 — hard cap on a single settle
  maxRedirects?: number;          // default 20 — circuit breaker for full navigations
  maxRequestsPerEndpoint?: number; // default 25 — circuit breaker per endpoint pattern
}

class BrowserSession {
  constructor(browser: Browser, options: SessionOptions);

  /** Navigate to a path and return whatever page we actually land on. Never asserts arrival. */
  loadPage(path: string): Promise<Page>;

  /** Tear down the browser context. */
  close(): Promise<void>;
}
```

`loadPage` navigates, runs a **bounded settle**, and returns the resulting `Page`. It does not
verify it arrived where requested — a redirect away from `path` yields a `Page` whose `redirects`
log shows what happened. If the circuit breaker trips during settle, `loadPage` throws (see Loop
guards).

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

  // Element queries return typed handles (Layer-1 data types), not snapshots.
  button(locator: ElementLocator): Button;
  input(locator: ElementLocator): Input;
  link(locator: ElementLocator): Link;
  text(locator: ElementLocator): TextElement;
  form(locator: ElementLocator): Form;
}
```

### Network + navigation logs

Recording is **always on** from the moment a page loads. The log is the substrate for storm
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

Fluent methods (the verbs hang off the element, not free functions). Actions that change the page
return the resulting `Page`; reads return their value.

```ts
class Button {
  click(): Promise<Page>;
  isEnabled(): Promise<boolean>;
  isVisible(): Promise<boolean>;
}

class Input {
  setValue(value: string): Promise<void>;
  getValue(): Promise<string>;
}

class Link {
  click(): Promise<Page>;
  href(): Promise<string>;
}

class TextElement {
  read(): Promise<string>;
  isVisible(): Promise<boolean>;
}

class Form {
  submit(): Promise<Page>;
}
```

### Loop guards (throw, never assert)

Two mechanisms keep a storming app observable instead of hanging:

1. **Bounded settle.** After a navigation or action, wait until the page is quiet (no new request
   or navigation for `settleQuietPeriodMs`) *or* until `settleTimeoutMs` elapses — whichever comes
   first — then return the `Page`. Never an unbounded `networkidle` wait, which would hang forever
   on a storm and report a useless timeout.

2. **Fail-fast circuit breaker.** While settling, if full navigations exceed `maxRedirects` or
   requests to a single endpoint pattern exceed `maxRequestsPerEndpoint`, abort and throw a typed
   error rather than waiting out the timeout:

```ts
class TooManyRedirectsError extends Error {
  readonly redirects: Redirect[];
}
class RequestStormError extends Error {
  readonly endpoint: string;
  readonly count: number;
}
```

These errors carry the evidence (`redirects`, `endpoint`, `count`) so a failing test reads
"storm detected: 25 requests to `/auth/token/refresh`" rather than "timed out after 30s".

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
  // Co-located vocabulary — the page's own words.
  private static readonly EMAIL_LABEL = 'Email';
  private static readonly PASSWORD_LABEL = 'Password';
  private static readonly SIGN_IN = 'Sign in';

  constructor(private readonly session: BrowserSession) {}

  /** Loads /login and returns the resulting page (does not assert arrival). */
  open(): Promise<Page>;

  /** Fills credentials, submits, and returns the resulting page. */
  async login(email: string, password: string): Promise<Page> {
    const page = await this.session.loadPage(Routes.LOGIN);
    await page.input({ label: LoginPage.EMAIL_LABEL }).setValue(email);
    await page.input({ label: LoginPage.PASSWORD_LABEL }).setValue(password);
    return page.button({ role: 'button', name: LoginPage.SIGN_IN }).click();
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

### Flagship — redirect / request storm on the login page

This is the test that would have caught the live bug.

```ts
test('loading the login page as an anonymous user does not storm', async () => {
  const page = await new LoginPage(session).open();

  expect(page.isAt(Routes.LOGIN)).toBe(true);          // we stayed on /login
  expect(page.redirects.length).toBeLessThanOrEqual(1); // no redirect loop
  expect(page.requests.count('/auth/*')).toBeLessThan(5); // no request storm
});
```

If the bug is present, the circuit breaker throws `TooManyRedirectsError` / `RequestStormError`
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

- A root `Makefile` target **`make e2e`** brings up a production-like stack — built frontend, real
  Django backend, Postgres — and the Playwright runner, all via `docker compose`, wrapped in
  `scripts/isolate-env-vars.sh` so it is worktree-safe.
- A Playwright **global setup** waits on backend/frontend health before any test runs. It owns no
  test data — data is created per test by `createTestUser`.
- The suite lives in a top-level **`e2e/`** directory with its own `package.json` and Playwright
  config, since it spans both services and does not belong inside `frontend/`.

## CI

A GitHub Actions job runs `make e2e` against a fresh stack and **gates merges from day one**.
Reliability is a hard requirement: prefer event-based waits over fixed sleeps, deterministic
per-test data, retry-once with trace-on-failure for debuggability, and we treat any flake as a
bug to fix rather than tolerate.

## Delivery (stacked pull requests)

1. AGENTS.md → TypeScript correction (precedes everything).
2. This design document.
3. **Abstraction layer** + Docker / `make e2e` plumbing, with harness tests against a static
   fixture page.
4. **Business layer** — page objects, route/caption/label constants, `createTestUser`.
5. **Tests** + the blocking CI gate.
