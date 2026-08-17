import { test, expect, chromium, type Browser } from "@playwright/test";
import { BrowserSession } from "../../src/abstraction/index.js";

// Requires the fixture static server (http://localhost:9999).
// Run via: E2E_FIXTURE_SERVER=true npx playwright test

test.describe("Quiet period", () => {
  let browser: Browser;

  test.beforeAll(async () => {
    browser = await chromium.launch();
    // Warm Chromium with a throwaway navigation so the first measured test does
    // not pay context/page cold-start, which would make wall-clock thresholds flaky.
    const warmup = new BrowserSession(browser, { baseUrl: "http://localhost:9999" });
    await warmup.loadPage("/page-without-requests-after-load.html");
    await warmup.close();
  });

  test.afterAll(async () => {
    await browser.close();
  });

  test("loadPage returns instead of hanging on a page that keeps firing requests", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "http://localhost:9999",
      quietPeriodMs: 100,
      maxWaitMs: 800,
      maxRequestsPerEndpoint: 1000,
    });

    const startTime = Date.now();
    const page = await session.loadPage("/page-with-excessive-requests.html");
    const elapsed = Date.now() - startTime;

    await session.close();

    // The behavioural guarantee is that it returns at all (does not hang). The
    // bound is deliberately loose — far above the 800ms hard cap — so machine
    // speed cannot make this flaky.
    expect(page).toBeDefined();
    expect(elapsed).toBeLessThan(5000);
  });

  test("loadPage on a quiet page returns via the quiet period, not the hard cap", async () => {
    // A very large hard cap means a fast return can only come from the
    // quiet-period path, not from waiting the cap out.
    const session = new BrowserSession(browser, {
      baseUrl: "http://localhost:9999",
      quietPeriodMs: 100,
      maxWaitMs: 30000,
    });

    const startTime = Date.now();
    await session.loadPage("/page-without-requests-after-load.html");
    const elapsed = Date.now() - startTime;

    await session.close();

    expect(elapsed).toBeLessThan(5000);
  });
});
