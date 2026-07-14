import type { Redirect } from "./types.js";

// Carries the redirect trail so a failure names the loop, not a generic timeout.
export class TooManyRedirectsError extends Error {
  readonly redirects: Redirect[];

  constructor(redirects: Redirect[]) {
    super(
      `Redirect loop detected: ${redirects.length} navigations. Trail: ${redirects
        .map((redirect) => `${redirect.from} → ${redirect.to}`)
        .join(", ")}`
    );
    this.name = "TooManyRedirectsError";
    this.redirects = redirects;
  }
}

// Carries the offending endpoint and count so a failure names the loop, not a generic timeout.
export class ExcessiveRequestsError extends Error {
  readonly endpoint: string;
  readonly count: number;

  constructor(endpoint: string, count: number) {
    super(`Excessive requests detected: ${count} requests to ${endpoint}`);
    this.name = "ExcessiveRequestsError";
    this.endpoint = endpoint;
    this.count = count;
  }
}
