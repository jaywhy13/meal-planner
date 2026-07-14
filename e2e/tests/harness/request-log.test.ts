import { test, expect } from "@playwright/test";
import { RequestLog } from "../../src/abstraction/index.js";

test.describe("RequestLog", () => {
  test("all() returns all recorded requests", () => {
    const log = new RequestLog([
      { url: "http://localhost:3000/api/meals", method: "GET", status: 200 },
      { url: "http://localhost:3000/api/auth/login", method: "POST", status: 401 },
    ]);

    expect(log.all()).toHaveLength(2);
  });

  test("to() returns requests matching a prefix pattern", () => {
    const log = new RequestLog([
      { url: "http://localhost:3000/api/auth/login", method: "POST", status: 200 },
      { url: "http://localhost:3000/api/auth/token/refresh", method: "POST", status: 401 },
      { url: "http://localhost:3000/api/meals", method: "GET", status: 200 },
    ]);

    const authRequests = log.to("/api/auth/*");

    expect(authRequests).toHaveLength(2);
    for (const request of authRequests) {
      expect(request.url).toContain("/api/auth/");
    }
  });

  test("to() with specific path returns only exact matches", () => {
    const log = new RequestLog([
      { url: "http://localhost:3000/api/auth/login", method: "POST", status: 200 },
      { url: "http://localhost:3000/api/auth/token/refresh", method: "POST", status: 401 },
    ]);

    const loginRequests = log.to("/api/auth/login");

    expect(loginRequests).toHaveLength(1);
    expect(loginRequests[0]?.url).toContain("/api/auth/login");
  });

  test("count() returns the number of matching requests", () => {
    const log = new RequestLog([
      { url: "http://localhost:3000/api/auth/token/refresh", method: "POST", status: 401 },
      { url: "http://localhost:3000/api/auth/token/refresh", method: "POST", status: 401 },
      { url: "http://localhost:3000/api/auth/token/refresh", method: "POST", status: 401 },
      { url: "http://localhost:3000/api/meals", method: "GET", status: 200 },
    ]);

    expect(log.count("/api/auth/*")).toBe(3);
    expect(log.count("/api/meals")).toBe(1);
    expect(log.count("/api/nonexistent")).toBe(0);
  });

  test("all() returns a copy — mutating it does not change the log", () => {
    const log = new RequestLog([
      { url: "http://localhost:3000/api/meals", method: "GET", status: 200 },
    ]);

    const allRequests = log.all();
    allRequests.push({ url: "http://localhost:3000/api/injected", method: "GET", status: 200 });

    expect(log.all()).toHaveLength(1);
  });
});
