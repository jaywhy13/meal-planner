# AGENTS.md

## Project Overview

Full-stack meal planning application with a **Django REST API backend** and **React frontend**. Supports creating meal plans, managing foods, configuring meal settings, and viewing daily meal suggestions.

## Defaults

- Be concise. Prefer short high-level overviews and ask for direction before going deeper.
- Avoid acronyms, even when they appear in source material. Say "Django REST Framework" instead of DRF, "Material UI" instead of MUI, "Create React App" instead of CRA — at least on first use.
- When explaining code or systems, use a Socratic approach: ask motivating questions before giving answers.
- When answering questions that require searching the codebase, include a brief "How I found this" section showing the key commands or search patterns used.

## Stack

- **Backend**: Python 3.10, Django 4.2, Django REST Framework, PostgreSQL (prod) / SQLite (dev)
- **Frontend**: React 19, Material UI 7, Axios, Day.js, JavaScript (not TypeScript)
- **Infrastructure**: Docker Compose (dev), AWS Lambda (prod), Pulumi
- **CI**: GitHub Actions — backend runs `python manage.py test meals`, frontend runs `npm run build`

## Docker-First Policy

**Never run `python`, `yarn`, `pip`, or `manage.py` directly on the host.** All project operations go through Docker via `make`. This ensures a consistent environment and avoids local dependency issues.

There are three Makefiles:

| Location | Purpose |
|---|---|
| Root `Makefile` | Project lifecycle (`init`, `start`, `stop`) and AWS Lambda infrastructure |
| `backend/Makefile` | Django operations (migrations, tests, seeding) |
| `frontend/Makefile` | React operations (tests, builds) |

The `lambda-*` targets in the root `Makefile` are exclusively for AWS infrastructure — never use them for local development.

## Architecture

**Backend** — four explicit layers. The **view layer** (`urls.py` + `views.py` + `serializers.py`) handles HTTP concerns. The **service layer** (`services.py`) owns all business logic — services are classes that take repository dependencies in the constructor. The **repository layer** (`repositories.py`) owns all ORM queries — also classes. **Models** (`models.py`) define schema only — fields, constraints, `__str__`. No fat models: business logic never lives on the model. All Python code uses type annotations.

**Frontend** — three layers. **Components** own rendering and user interaction. **Services** (`services/`) own business logic and orchestration — classes that take client dependencies in the constructor. **Clients** (`clients/`) wrap Axios calls grouped by API resource — also classes. Components call services, not clients directly. Use JSDoc annotations for type documentation.

All API endpoints live under `/api/` with no trailing slashes. One Django app (`meals`) owns the entire domain.

See [docs/architecture.md](docs/architecture.md) for the full version.

## Coding Conventions

**Naming**: No abbreviations. Name with intent — encode the specific role in the name so readers don't have to scan the body. Python uses `snake_case` for variables/functions, `PascalCase` for classes. JavaScript uses `camelCase` for variables/functions, `PascalCase` for components and classes.

**Type annotations**: All Python code uses type hints (`def method(self, name: str) -> MealPlan:`). All JavaScript uses JSDoc annotations for function signatures and class methods. Don't leave types implied.

**Comments**: Default to none. Add one only when the *why* is non-obvious (e.g., a Day.js week-start quirk). If you need a comment to explain what code does, rename the identifier instead.

**Abstraction**: One level of abstraction per method. If a method mixes orchestration with query details, split it.

**Error handling**: Let Django REST Framework handle validation errors. On the frontend, catch API errors in the page component, set an `error` state, render in `<Alert>`. Don't add try/catch around code that can't fail.

See [docs/coding_conventions.md](docs/coding_conventions.md) for the full version.

## Tests

**Backend**: `APITestCase` tests that exercise behaviour through the API. Test the HTTP response and database state, not internal helpers. Use `factory_boy` factories (`meals/factories.py`) to create test data inline — no shared `setUp`, no helper methods. Don't mock the database.

**Frontend**: React Testing Library + Jest. Test component behaviour from the user's perspective — what's rendered, what happens on click. Use factory functions (`buildDateRangeBarProps()`, `buildMeal()`) instead of shared `baseProps` objects — each call returns fresh data with independent `jest.fn()` mocks. Test files live next to the component (`MealCell.js` + `MealCell.test.js`). Prefer accessible queries (`getByRole`, `getByLabelText`, `getByText`). No snapshot tests.

```bash
# Run backend tests (from backend/)
make test

# Run frontend tests (from frontend/)
make test
```

See [docs/testing.md](docs/testing.md) for the full version.

## Development Workflow

### Project lifecycle (run from repo root)

```bash
make init    # First-time setup: creates .env files, builds containers
make start   # Start all services with hot-reload
make stop    # Stop all services
make ssh     # Shell into backend container
```

### Worktree isolation (local agents only)

This applies only to agents running locally on this machine. Cloud-hosted agents (e.g. sandboxed cloud runners) already get isolation from their environment and don't need this script.

When working inside a Git worktree, **always prefix Docker/Make commands with `scripts/isolate-env-vars.sh`** so multiple worktrees can run side-by-side without colliding on host ports or container names:

```bash
scripts/isolate-env-vars.sh make start
scripts/isolate-env-vars.sh make ssh
scripts/isolate-env-vars.sh docker compose ps
```

The script derives a stable Compose project name and host-port offset from the worktree's root path and exports `COMPOSE_PROJECT_NAME`, `BACKEND_PORT`, `FRONTEND_PORT`, `DB_PORT`, and `REACT_APP_API_URL` before `exec`-ing the command. Without the prefix, everything runs on the default `8000/3000/5432` — same as before this script existed.

### Backend (run from `backend/`)

```bash
make migrate                              # Apply database migrations
make makemigrations                       # Create migrations for all apps
make makemigrations ARGS="meals --name my_migration"  # Named migration
make seed                                 # Load initial food/meal data
make test                                 # Run all backend tests
make test TEST=meals.tests.SpecificTest   # Run a specific test
```

### Frontend (run from `frontend/`)

```bash
make test    # Run all frontend tests (non-interactive)
make build   # Production build
```

Backend runs on `:8000`, frontend on `:3000`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | SQLite (`db.sqlite3`) |
| `REACT_APP_API_URL` | Frontend API base URL | `http://localhost:8000/api` |
| `SECRET_KEY` | Django secret key | Required in production |
| `DEBUG` | Django debug mode | `True` in dev |

`make init` creates empty `.env` files — populate `backend/.env` and `frontend/.env` with the required values before starting.

## Challenge Premature Dismissals

Watch for ideas being rejected without a concrete objection — outright ("no", "that won't work") or subtle (pivoting to a different topic, going quiet, reframing the question so the idea no longer fits). When spotted, push back and name the specific idea that got dropped. Don't ask permission first — the friction is the point.

Exception: if the trade-offs have been explicitly worked through in the current conversation, or "I've decided, move on" is said, respect it.
