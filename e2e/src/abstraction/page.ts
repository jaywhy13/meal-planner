import type { Page as PlaywrightPage } from "@playwright/test";
import type { ElementLocator, RecordedRequest, Redirect } from "./types.js";
import { RequestLog } from "./request-log.js";
import {
  Button,
  Input,
  Link,
  TextElement,
  Form,
  resolveLocator,
} from "./elements.js";

// No statusCode field: this is a client-routed SPA where most transitions have no
// HTTP status. Per-request statuses live inside `requests`.
export class Page {
  readonly path: string;
  readonly url: string;
  readonly title: string;
  readonly redirects: Redirect[];
  readonly requests: RequestLog;

  constructor(
    private readonly playwrightPage: PlaywrightPage,
    private readonly waitAndBuildPage: () => Promise<Page>,
    path: string,
    url: string,
    title: string,
    redirects: Redirect[],
    requests: RecordedRequest[]
  ) {
    this.path = path;
    this.url = url;
    this.title = title;
    this.redirects = redirects;
    this.requests = new RequestLog(requests);
  }

  isAt(route: string): boolean {
    return this.path === route;
  }

  // Queries locate the element, read its live properties, and return a static snapshot.

  async button(locator: ElementLocator): Promise<Button> {
    const element = resolveLocator(this.playwrightPage, locator);
    const [isVisible, isEnabled] = await Promise.all([
      element.isVisible(),
      element.isEnabled(),
    ]);
    return new Button(locator, isVisible, isEnabled);
  }

  async input(locator: ElementLocator): Promise<Input> {
    const element = resolveLocator(this.playwrightPage, locator);
    const [value, isVisible] = await Promise.all([
      element.inputValue(),
      element.isVisible(),
    ]);
    return new Input(locator, value, isVisible);
  }

  async link(locator: ElementLocator): Promise<Link> {
    const element = resolveLocator(this.playwrightPage, locator);
    const [rawHref, isVisible] = await Promise.all([
      element.getAttribute("href"),
      element.isVisible(),
    ]);
    return new Link(locator, rawHref ?? "", isVisible);
  }

  async text(locator: ElementLocator): Promise<TextElement> {
    const element = resolveLocator(this.playwrightPage, locator);
    const [value, isVisible] = await Promise.all([
      element.innerText(),
      element.isVisible(),
    ]);
    return new TextElement(locator, value, isVisible);
  }

  async form(locator: ElementLocator): Promise<Form> {
    return new Form(locator);
  }

  // Interaction verbs re-resolve from the snapshot's descriptor so a stale snapshot
  // still acts on the current DOM element.

  async click(element: Button | Link): Promise<Page> {
    const liveElement = resolveLocator(this.playwrightPage, element.descriptor);
    await liveElement.click();
    return this.waitAndBuildPage();
  }

  async setValue(input: Input, value: string): Promise<void> {
    const liveElement = resolveLocator(this.playwrightPage, input.descriptor);
    await liveElement.fill(value);
  }

  async submit(form: Form): Promise<Page> {
    const liveElement = resolveLocator(this.playwrightPage, form.descriptor);
    await liveElement.dispatchEvent("submit");
    return this.waitAndBuildPage();
  }
}
