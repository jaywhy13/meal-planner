import { test, expect, chromium, type Browser } from "@playwright/test";
import * as path from "path";
import { BrowserSession } from "../../src/abstraction/index.js";

const fixturesDir = path.resolve(__dirname, "../../fixtures");

// Tests pass this full file:// URL as the path with baseUrl set to "", so
// loadPage does no base+path concatenation.
const absoluteFixtureUrl = (filename: string): string =>
  `file://${path.join(fixturesDir, filename)}`;

test.describe("ElementLocator resolution", () => {
  let browser: Browser;

  test.beforeAll(async () => {
    browser = await chromium.launch();
  });

  test.afterAll(async () => {
    await browser.close();
  });

  test("locates a button by role and name, reads visibility", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "",
      quietPeriodMs: 100,
      maxWaitMs: 1000,
    });

    const page = await session.loadPage(absoluteFixtureUrl("page-with-basic-elements.html"));
    const button = await page.button({ role: "button", name: "Click me" });

    expect(button.isVisible).toBe(true);
    expect(button.isEnabled).toBe(true);

    await session.close();
  });

  test("locates an input by label and reads its value after setValue", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "",
      quietPeriodMs: 100,
      maxWaitMs: 1000,
    });

    const page = await session.loadPage(absoluteFixtureUrl("page-with-basic-elements.html"));
    const input = await page.input({ label: "Username" });

    await page.setValue(input, "alice");
    const updatedInput = await page.input({ label: "Username" });

    expect(updatedInput.value).toBe("alice");

    await session.close();
  });

  test("locates a link by text and reads its href", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "",
      quietPeriodMs: 100,
      maxWaitMs: 1000,
    });

    const page = await session.loadPage(absoluteFixtureUrl("page-with-basic-elements.html"));
    const link = await page.link({ text: "About page" });

    expect(link.href).toBe("/about");

    await session.close();
  });

  test("locates a text element by testId and reads its content", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "",
      quietPeriodMs: 100,
      maxWaitMs: 1000,
    });

    const page = await session.loadPage(absoluteFixtureUrl("page-with-basic-elements.html"));
    const textElement = await page.text({ testId: "greeting" });

    expect(textElement.value).toBe("Hello, world!");

    await session.close();
  });

  test("locates a text element by text content and confirms visibility", async () => {
    const session = new BrowserSession(browser, {
      baseUrl: "",
      quietPeriodMs: 100,
      maxWaitMs: 1000,
    });

    const page = await session.loadPage(absoluteFixtureUrl("page-with-basic-elements.html"));
    const textElement = await page.text({ text: "Visible paragraph text" });

    expect(textElement.isVisible).toBe(true);

    await session.close();
  });
});
