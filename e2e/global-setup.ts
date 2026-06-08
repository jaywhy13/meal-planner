import { FullConfig } from "@playwright/test";

const POLL_INTERVAL_MS = 1000;
const MAX_WAIT_MS = 60000;

async function waitUntilReachable(url: string, label: string): Promise<void> {
  const deadline = Date.now() + MAX_WAIT_MS;

  while (Date.now() < deadline) {
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(3000) });
      if (response.ok || response.status < 500) {
        console.log(`${label} is ready (${response.status})`);
        return;
      }
    } catch {
      // Not yet reachable — keep polling.
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }

  throw new Error(`${label} did not become ready within ${MAX_WAIT_MS}ms (${url})`);
}

export default async function globalSetup(_config: FullConfig): Promise<void> {
  const appUrl = process.env["E2E_BASE_URL"] ?? "http://localhost:3000";
  // The backend health endpoint is at /health (not under /api/).
  const backendHealthUrl = `${appUrl}/health`;

  await Promise.all([
    waitUntilReachable(appUrl, "web app"),
    waitUntilReachable(backendHealthUrl, "backend (via web proxy)"),
  ]);
}
