import { defineConfig, devices } from "@playwright/test";

const isFixtureMode = process.env["E2E_FIXTURE_SERVER"] === "true";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env["CI"],
  retries: 0,
  reporter: "list",
  use: {
    baseURL: process.env["E2E_BASE_URL"] ?? "http://localhost:3000",
    trace: "retain-on-failure",
  },
  globalSetup: isFixtureMode ? undefined : "./global-setup.ts",
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: isFixtureMode
    ? {
        command: "npx http-server fixtures -p 9999 --silent",
        url: "http://localhost:9999",
        reuseExistingServer: !process.env["CI"],
      }
    : undefined,
});
