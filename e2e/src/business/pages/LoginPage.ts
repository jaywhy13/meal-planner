import type { BrowserSession, Page } from "../../abstraction/index.js";
import { Routes } from "../routes.js";

export class LoginPage {
  private static readonly LABEL_EMAIL = "Email";
  private static readonly LABEL_PASSWORD = "Password";
  private static readonly CAPTION_SIGN_IN = "Sign in";

  constructor(private readonly session: BrowserSession) {}

  open(): Promise<Page> {
    return this.session.loadPage(Routes.LOGIN);
  }

  async login(email: string, password: string): Promise<Page> {
    const page = await this.session.loadPage(Routes.LOGIN);
    await page.setValue(await page.input({ label: LoginPage.LABEL_EMAIL }), email);
    await page.setValue(await page.input({ label: LoginPage.LABEL_PASSWORD }), password);
    const signInButton = await page.button({ role: "button", name: LoginPage.CAPTION_SIGN_IN });
    return page.click(signInButton);
  }
}
