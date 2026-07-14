// Accessible-first descriptor; testId is an escape hatch for elements with no ARIA name.
export type ElementLocator =
  | { role: string; name: string }
  | { label: string }
  | { text: string }
  | { testId: string };

export interface RecordedRequest {
  url: string;
  method: string;
  status: number | null; // null when the request never received a response
}

export interface Redirect {
  from: string;
  to: string;
}

export interface SessionOptions {
  baseUrl: string;
  /** Treat the page as done after this long with no new request or navigation. Default 300 ms. */
  quietPeriodMs?: number;
  /** Never wait longer than this for one navigation. Default 2000 ms. */
  maxWaitMs?: number;
  /** Throw past this many full-page navigations. Default 20. */
  maxRedirects?: number;
  /** Throw past this many requests to one endpoint. Default 25. */
  maxRequestsPerEndpoint?: number;
}

export interface ResolvedSessionOptions {
  baseUrl: string;
  quietPeriodMs: number;
  maxWaitMs: number;
  maxRedirects: number;
  maxRequestsPerEndpoint: number;
}
