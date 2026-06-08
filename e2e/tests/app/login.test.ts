import { test, expect, chromium, type Browser } from "@playwright/test";
import { BrowserSession } from "../../src/abstraction/index.js";
import { LoginPage, Routes, createTestUser } from "../../src/business/index.js";

const BASE_URL = process.env["E2E_BASE_URL"] ?? "http://localhost:3000";

test("loading the login page as an anonymous user does not loop or flood requests", async () => {
  const browser: Browser = await chromium.launch();
  const session = new BrowserSession(browser, { baseUrl: BASE_URL });

  try {
    const page = await new LoginPage(session).open();

    expect(page.isAt(Routes.LOGIN)).toBe(true);
    expect(page.redirects.length).toBeLessThanOrEqual(1);
    expect(page.requests.count("/api/auth/*")).toBeLessThan(5);
  } finally {
    await session.close();
    await browser.close();
  }
});

test("a registered user can log in and lands on the home page", async () => {
  const browser: Browser = await chromium.launch();
  const session = new BrowserSession(browser, { baseUrl: BASE_URL });

  try {
    const user = await createTestUser();
    const page = await new LoginPage(session).login(user.email, user.password);

    expect(page.isAt(Routes.HOME)).toBe(true);
  } finally {
    await session.close();
    await browser.close();
  }
});
