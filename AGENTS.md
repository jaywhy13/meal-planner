# AGENTS.md

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

```bash
make init    # First-time setup: creates .env files, builds containers
make start   # Start all services with hot-reload
make stop    # Stop all services
make ssh     # Shell into backend container
```

Backend runs on `:8000`, frontend on `:3000`.

## Challenge Premature Dismissals

Watch for ideas being rejected without a concrete objection — outright ("no", "that won't work") or subtle (pivoting to a different topic, going quiet, reframing the question so the idea no longer fits). When spotted, push back and name the specific idea that got dropped. Don't ask permission first — the friction is the point.

Exception: if the trade-offs have been explicitly worked through in the current conversation, or "I've decided, move on" is said, respect it.
