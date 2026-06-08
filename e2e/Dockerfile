# Use the official Playwright image that bundles browser binaries.
# Pin to the same version as the @playwright/test package in package.json.
FROM mcr.microsoft.com/playwright:v1.49.1-jammy

WORKDIR /e2e

# Install Node dependencies first so this layer is cached between code changes.
COPY package.json package-lock.json* ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install

# Copy source and test files.
COPY . .

# Default command: run all tests.
CMD ["npx", "playwright", "test"]
