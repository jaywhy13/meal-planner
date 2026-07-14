import type { Browser, BrowserContext, Page as PlaywrightPage } from "@playwright/test";
import type { RecordedRequest, Redirect, SessionOptions, ResolvedSessionOptions } from "./types.js";
import { Page } from "./page.js";
import { waitForQuiet } from "./elements.js";

const DEFAULT_QUIET_PERIOD_MS = 300;
const DEFAULT_MAX_WAIT_MS = 2000;
const DEFAULT_MAX_REDIRECTS = 20;
const DEFAULT_MAX_REQUESTS_PER_ENDPOINT = 25;

// One session is one isolated browser context, so tests share no cookies or state.
export class BrowserSession {
  private readonly options: ResolvedSessionOptions;
  private context: BrowserContext | null = null;
  private playwrightPage: PlaywrightPage | null = null;
  private requestListenersAttached = false;

  private readonly sessionRequests: RecordedRequest[] = [];
  private readonly sessionRedirects: Redirect[] = [];

  // Tracks the URL at the point where waiting begins so we can detect same-URL
  // reload loops. A reload to the same URL still fires framenavigated, and the
  // motivating bug is exactly a /login → /login cycle.
  private firstUrl: string = "";

  constructor(private readonly browser: Browser, options: SessionOptions) {
    this.options = applyDefaults(options);
  }

  // Returns whatever page we land on — never asserts arrival. Throws if loop
  // limits are exceeded during the quiet-period wait.
  async loadPage(path: string): Promise<Page> {
    const playwrightPage = await this.ensurePage();
    this.attachRequestListeners(playwrightPage);

    const targetUrl = `${this.options.baseUrl}${path}`;
    const response = await playwrightPage.goto(targetUrl);
    // Seed from the post-goto URL so only later JavaScript-initiated navigations
    // (the looping kind) are counted as redirects.
    this.firstUrl = response?.url() ?? playwrightPage.url();

    await waitForQuiet(
      playwrightPage,
      this.options,
      this.sessionRequests,
      this.sessionRedirects
    );

    return this.buildCurrentPage();
  }

  /** Tear down the browser context and release all resources. */
  async close(): Promise<void> {
    if (this.context !== null) {
      await this.context.close();
      this.context = null;
      this.playwrightPage = null;
    }
  }

  private async ensurePage(): Promise<PlaywrightPage> {
    if (this.playwrightPage !== null) {
      return this.playwrightPage;
    }

    this.context = await this.browser.newContext();
    this.playwrightPage = await this.context.newPage();
    return this.playwrightPage;
  }

  private attachRequestListeners(playwrightPage: PlaywrightPage): void {
    // Guard against double-registration when loadPage is called more than once.
    if (this.requestListenersAttached) {
      return;
    }
    this.requestListenersAttached = true;

    playwrightPage.on("response", (response) => {
      this.sessionRequests.push({
        url: response.url(),
        method: response.request().method(),
        status: response.status(),
      });
    });

    playwrightPage.on("requestfailed", (request) => {
      this.sessionRequests.push({
        url: request.url(),
        method: request.method(),
        status: null,
      });
    });

    // Same-URL reloads still fire framenavigated and must count as redirects —
    // the motivating bug is a /login → /login reload loop.
    let previousUrl = "";

    playwrightPage.on("framenavigated", (frame) => {
      const isTopLevelFrame = frame.parentFrame() == null;
      if (!isTopLevelFrame) {
        // Ignore subframes (third-party ads, video embeds, chat widgets, etc.)
        return;
      }

      const currentUrl = frame.url();

      const navigationHasntHappenedYet = this.firstUrl === "";
      if (navigationHasntHappenedYet) {
        previousUrl = currentUrl;
        return;
      }

      const noNavigationRecordedYet = previousUrl === "";
      if (noNavigationRecordedYet) {
        previousUrl = currentUrl;
        return;
      }

      this.sessionRedirects.push({
        from: previousUrl,
        to: currentUrl,
      });
      previousUrl = currentUrl;
    });
  }

  private async buildCurrentPage(): Promise<Page> {
    const playwrightPage = this.playwrightPage!;
    const currentUrl = playwrightPage.url();
    let pathname: string;
    try {
      pathname = new URL(currentUrl).pathname;
    } catch {
      pathname = currentUrl;
    }

    const title = await playwrightPage.title();
    const snapshotRequests = [...this.sessionRequests];
    const snapshotRedirects = [...this.sessionRedirects];

    return new Page(
      playwrightPage,
      () => this.waitAndBuildPage(),
      pathname,
      currentUrl,
      title,
      snapshotRedirects,
      snapshotRequests
    );
  }

  // The callback handed to Page so interaction verbs can re-wait and return a
  // fresh Page without importing BrowserSession.
  private async waitAndBuildPage(): Promise<Page> {
    const playwrightPage = this.playwrightPage!;

    await waitForQuiet(
      playwrightPage,
      this.options,
      this.sessionRequests,
      this.sessionRedirects
    );

    return this.buildCurrentPage();
  }
}

function applyDefaults(options: SessionOptions): ResolvedSessionOptions {
  return {
    baseUrl: options.baseUrl,
    quietPeriodMs: options.quietPeriodMs ?? DEFAULT_QUIET_PERIOD_MS,
    maxWaitMs: options.maxWaitMs ?? DEFAULT_MAX_WAIT_MS,
    maxRedirects: options.maxRedirects ?? DEFAULT_MAX_REDIRECTS,
    maxRequestsPerEndpoint: options.maxRequestsPerEndpoint ?? DEFAULT_MAX_REQUESTS_PER_ENDPOINT,
  };
}
