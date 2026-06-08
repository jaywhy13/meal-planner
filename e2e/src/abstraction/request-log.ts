import type { RecordedRequest } from "./types.js";

// `to`/`count` accept a glob pattern matched against the request pathname,
// e.g. `/auth/*` matches any path under `/auth/`.
export class RequestLog {
  private readonly recordedRequests: RecordedRequest[];

  constructor(requests: RecordedRequest[]) {
    this.recordedRequests = requests;
  }

  all(): RecordedRequest[] {
    return [...this.recordedRequests];
  }

  to(pattern: string): RecordedRequest[] {
    return this.recordedRequests.filter((request) =>
      matchesPattern(request.url, pattern)
    );
  }

  count(pattern: string): number {
    return this.to(pattern).length;
  }
}

function matchesPattern(url: string, pattern: string): boolean {
  let pathname: string;
  try {
    pathname = new URL(url).pathname;
  } catch {
    pathname = url;
  }

  const regexSource = pattern
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*/g, ".+");

  const regex = new RegExp(`^${regexSource}($|\\?|#)`);
  return regex.test(pathname);
}
