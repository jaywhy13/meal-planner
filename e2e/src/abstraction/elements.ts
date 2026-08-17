import type { Locator } from "@playwright/test";
import type { Page as PlaywrightPage } from "@playwright/test";
import type { ElementLocator, RecordedRequest, Redirect, ResolvedSessionOptions } from "./types.js";
import { TooManyRedirectsError, ExcessiveRequestsError } from "./errors.js";

// Explicit branch per locator shape, no fallback ordering; an unhandled shape throws.
export function resolveLocator(
  playwrightPage: PlaywrightPage,
  locator: ElementLocator
): Locator {
  if ("role" in locator) {
    return playwrightPage.getByRole(locator.role as Parameters<typeof playwrightPage.getByRole>[0], { name: locator.name });
  }
  if ("label" in locator) {
    return playwrightPage.getByLabel(locator.label);
  }
  if ("text" in locator) {
    return playwrightPage.getByText(locator.text);
  }
  if ("testId" in locator) {
    return playwrightPage.getByTestId(locator.testId);
  }
  const exhaustiveCheck: never = locator;
  throw new Error(`Unhandled ElementLocator shape: ${JSON.stringify(exhaustiveCheck)}`);
}

// Static snapshots — captured at query time, no live references to the page or browser.

export class Button {
  readonly descriptor: ElementLocator;
  readonly isVisible: boolean;
  readonly isEnabled: boolean;

  constructor(descriptor: ElementLocator, isVisible: boolean, isEnabled: boolean) {
    this.descriptor = descriptor;
    this.isVisible = isVisible;
    this.isEnabled = isEnabled;
  }
}

export class Input {
  readonly descriptor: ElementLocator;
  readonly value: string;
  readonly isVisible: boolean;

  constructor(descriptor: ElementLocator, value: string, isVisible: boolean) {
    this.descriptor = descriptor;
    this.value = value;
    this.isVisible = isVisible;
  }
}

export class Link {
  readonly descriptor: ElementLocator;
  readonly href: string;
  readonly isVisible: boolean;

  constructor(descriptor: ElementLocator, href: string, isVisible: boolean) {
    this.descriptor = descriptor;
    this.href = href;
    this.isVisible = isVisible;
  }
}

export class TextElement {
  readonly descriptor: ElementLocator;
  readonly value: string;
  readonly isVisible: boolean;

  constructor(descriptor: ElementLocator, value: string, isVisible: boolean) {
    this.descriptor = descriptor;
    this.value = value;
    this.isVisible = isVisible;
  }
}

export class Form {
  readonly descriptor: ElementLocator;

  constructor(descriptor: ElementLocator) {
    this.descriptor = descriptor;
  }
}

// Resolves once no request/navigation has fired for quietPeriodMs, or once
// maxWaitMs elapses — whichever is first. Rejects if loop limits are exceeded.
export async function waitForQuiet(
  playwrightPage: PlaywrightPage,
  options: ResolvedSessionOptions,
  requests: RecordedRequest[],
  redirects: Redirect[]
): Promise<void> {
  const { quietPeriodMs, maxWaitMs, maxRedirects, maxRequestsPerEndpoint } = options;

  await new Promise<void>((resolve, reject) => {
    let quietTimer: ReturnType<typeof setTimeout> | null = null;

    const scheduleQuietTimer = (): void => {
      if (quietTimer !== null) {
        clearTimeout(quietTimer);
      }
      quietTimer = setTimeout(() => {
        cleanup();
        resolve();
      }, quietPeriodMs);
    };

    const hardTimer = setTimeout(() => {
      cleanup();
      resolve();
    }, maxWaitMs);

    const enforceLoopLimits = (): void => {
      if (redirects.length > maxRedirects) {
        cleanup();
        reject(new TooManyRedirectsError(redirects));
        return;
      }

      const endpointCounts = countRequestsByPathname(requests);
      for (const [endpoint, count] of Object.entries(endpointCounts)) {
        if (count > maxRequestsPerEndpoint) {
          cleanup();
          reject(new ExcessiveRequestsError(endpoint, count));
          return;
        }
      }
    };

    const onActivity = (): void => {
      enforceLoopLimits();
      scheduleQuietTimer();
    };

    playwrightPage.on("request", onActivity);
    playwrightPage.on("framenavigated", onActivity);

    const cleanup = (): void => {
      if (quietTimer !== null) {
        clearTimeout(quietTimer);
        quietTimer = null;
      }
      clearTimeout(hardTimer);
      playwrightPage.off("request", onActivity);
      playwrightPage.off("framenavigated", onActivity);
    };

    scheduleQuietTimer();
  });
}

function countRequestsByPathname(requests: RecordedRequest[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const request of requests) {
    let pathname: string;
    try {
      pathname = new URL(request.url).pathname;
    } catch {
      pathname = request.url;
    }
    counts[pathname] = (counts[pathname] ?? 0) + 1;
  }
  return counts;
}
