import { test, expect, chromium, type Browser } from "@playwright/test";
import {
  BrowserSession,
  TooManyRedirectsError,
  ExcessiveRequestsError,
} from "../../src/abstraction/index.js";

// Requires the fixture static server (http://localhost:9999).
test.describe("Loop protection", () => {
  let browser: Browser;

  test.beforeAll(async () => {
    browser = await chromium.launch();
  });

  test.afterAll(async () => {
    await browser.close();
  });

  test("throws ExcessiveRequestsError when a single endpoint exceeds maxRequestsPerEndpoint", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "http://localhost:9999",
      quietPeriodMs: 200,
      maxWaitMs: 5000,
      maxRequestsPerEndpoint: 5,
    });

    let thrownError: unknown = null;
    try {
      await session.loadPage("/page-with-excessive-requests.html");
    } catch (error) {
      thrownError = error;
    } finally {
      await session.close();
    }

    expect(thrownError).toBeInstanceOf(ExcessiveRequestsError);
    if (thrownError instanceof ExcessiveRequestsError) {
      expect(thrownError.endpoint).toContain("/api/auth/token/refresh");
      expect(thrownError.count).toBeGreaterThan(5);
      expect(thrownError.message).toContain("Excessive requests");
    }
  });

  test("ExcessiveRequestsError carries the offending endpoint and count", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "http://localhost:9999",
      quietPeriodMs: 200,
      maxWaitMs: 5000,
      maxRequestsPerEndpoint: 3,
    });

    let thrownError: unknown = null;
    try {
      await session.loadPage("/page-with-excessive-requests.html");
    } catch (error) {
      thrownError = error;
    } finally {
      await session.close();
    }

    expect(thrownError).toBeInstanceOf(ExcessiveRequestsError);
    if (thrownError instanceof ExcessiveRequestsError) {
      expect(typeof thrownError.endpoint).toBe("string");
      expect(typeof thrownError.count).toBe("number");
      expect(thrownError.count).toBeGreaterThan(3);
    }
  });

  test("throws TooManyRedirectsError when navigations exceed maxRedirects", async () => {
    // Set maxRequestsPerEndpoint very high so only the redirect protection can fire.
    // The redirect-loop fixture reloads the same page, which also generates
    // repeated requests; we want the navigation count to trip first.
    const session = new BrowserSession(browser, {
      baseUrl: "http://localhost:9999",
      quietPeriodMs: 200,
      maxWaitMs: 10000,
      maxRedirects: 2,
      maxRequestsPerEndpoint: 10000,
    });

    let thrownError: unknown = null;
    try {
      await session.loadPage("/page-with-redirect-loop.html");
    } catch (error) {
      thrownError = error;
    } finally {
      await session.close();
    }

    expect(thrownError).toBeInstanceOf(TooManyRedirectsError);
    if (thrownError instanceof TooManyRedirectsError) {
      expect(thrownError.redirects.length).toBeGreaterThan(2);
      expect(thrownError.message).toContain("loop");
    }
  });

  test("TooManyRedirectsError carries the full redirect trail", async () => {
    // Same as above: suppress the excessive-requests protection so the redirect
    // protection fires.
    const session = new BrowserSession(browser, {
      baseUrl: "http://localhost:9999",
      quietPeriodMs: 200,
      maxWaitMs: 10000,
      maxRedirects: 1,
      maxRequestsPerEndpoint: 10000,
    });

    let thrownError: unknown = null;
    try {
      await session.loadPage("/page-with-redirect-loop.html");
    } catch (error) {
      thrownError = error;
    } finally {
      await session.close();
    }

    expect(thrownError).toBeInstanceOf(TooManyRedirectsError);
    if (thrownError instanceof TooManyRedirectsError) {
      for (const redirect of thrownError.redirects) {
        expect(typeof redirect.from).toBe("string");
        expect(typeof redirect.to).toBe("string");
      }
    }
  });
});
