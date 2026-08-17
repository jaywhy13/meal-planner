// E2E_API_URL defaults to http://localhost:8000/api — the backend's local dev address.
const API_BASE_URL = process.env["E2E_API_URL"] ?? "http://localhost:8000/api";

export interface TestUser {
  email: string;
  password: string;
}

export async function createTestUser(overrides?: Partial<TestUser>): Promise<TestUser> {
  const uniqueEmail = `e2e-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;
  const email = overrides?.email ?? uniqueEmail;
  const password = overrides?.password ?? "TestPassword123!";

  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, first_name: "", last_name: "" }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Registration failed (${response.status}): ${body}`);
  }

  return { email, password };
}
