# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack meal planning application with a **Django REST API backend** and **React frontend**. Supports creating meal plans, managing foods, configuring meal settings, and viewing daily meal suggestions.

## Docker-First Policy

**Never run `python`, `yarn`, `pip`, or `manage.py` directly on the host.** All project operations go through Docker via `make`. This ensures a consistent environment and avoids local dependency issues.

There are three Makefiles:

| Location | Purpose |
|---|---|
| Root `Makefile` | Project lifecycle (`init`, `start`, `stop`) and AWS Lambda infrastructure |
| `backend/Makefile` | Django operations (migrations, tests, seeding) |
| `frontend/Makefile` | React operations (tests, builds) |

The `lambda-*` targets in the root `Makefile` are exclusively for AWS infrastructure — never use them for local development.

## Development Commands

### Project lifecycle (run from repo root)

```bash
make init    # First-time setup: creates empty .env files and builds containers
make start   # Start all services with hot-reload (frontend + backend)
make stop    # Stop all services
make ssh     # Open a bash shell in the backend container
```

### Worktree isolation (local agents only)

This applies only to agents running locally on this machine. Cloud-hosted agents (e.g. sandboxed cloud runners) already get isolation from their environment and don't need this script.

When working inside a Git worktree, **always prefix Docker/Make commands with `scripts/isolate-env-vars.sh`** so multiple worktrees can run side-by-side without colliding on host ports or container names:

```bash
scripts/isolate-env-vars.sh make start
scripts/isolate-env-vars.sh make ssh
scripts/isolate-env-vars.sh docker compose ps
```

The script derives a stable Compose project name and host-port offset from the worktree's root path and exports `COMPOSE_PROJECT_NAME`, `BACKEND_PORT`, `FRONTEND_PORT`, `DB_PORT`, and `REACT_APP_API_URL` before `exec`-ing the command. Without the prefix, everything runs on the default `8000/3000/5432` — same as before this script existed. The rest of the project (Makefiles, compose files, Django, React) only reads those env vars and knows nothing about worktrees.

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

## Code Conventions

### Naming

- **No abbreviations.** Write `meal_settings`, not `ms`; `daily_meal`, not `dm`; `serving_count`, not `sc`.
- **Name with intent.** When a generic name would let several different meanings pass the type check, encode the specific intent in the name. The reader shouldn't have to scan the body to know what's special about this value.

  ```python
  # Generic — what's notable about this plan? Have to read the body.
  meal_plan = MealPlan.objects.create(name="Test")
  assert DailyMeal.objects.filter(meal_plan=meal_plan).count() == 0

  # Intentional — the name says what role this fixture plays.
  meal_plan_without_meals = MealPlan.objects.create(name="Test")
  assert DailyMeal.objects.filter(meal_plan=meal_plan_without_meals).count() == 0
  ```

  Same rule applies to local variables, function parameters, and React state. If a reviewer would ask "what is this for?", the name is wrong — rename rather than add a comment.

### Comments

- Default to no comments. Add one only when the *why* is non-obvious — e.g. "dayjs treats Sunday as week start, so we walk back to Monday manually."
- Don't restate what the code does; rename the identifier instead.

### One level of abstraction per method

A method should read at a single level of abstraction. If the top of the method talks about high-level steps and the bottom is doing raw date math or hand-rolled ORM calls, split it: the outer method stays at the orchestration level and delegates each step to a helper that owns the details.

```python
# Mixes orchestration with calendar math and ORM internals
def create_daily_meals_for_month(meal_plan):
    year, month = meal_plan.start_date.year, meal_plan.start_date.month
    last = calendar.monthrange(year, month)[1]
    for day in range(1, last + 1):
        current_day = date(year, month, day)
        if current_day.weekday() in meal_plan.settings.enabled_weekday_indexes:
            for meal_type in meal_plan.settings.enabled_meal_types.all():
                DailyMeal.objects.create(
                    meal_plan=meal_plan, date=current_day, meal_type=meal_type,
                )

# Each method reads at one level; details hide one level down
def create_daily_meals_for_month(meal_plan):
    for day in days_in_month(meal_plan.start_date):
        if meal_plan.settings.includes(day):
            create_daily_meals_for(meal_plan, day)
```

The first version forces the reader to context-switch between "what are we doing" and "how do we do each piece." The second reads like a sentence and each helper can be understood (and tested) on its own.

### Tests

- **Test behaviour, not implementation details.** Assertions should fix on observable outcomes — what a caller sees, what ends up in the database, what the HTTP response contains — not on which internal helpers were invoked or what intermediate variables held. When someone refactors the internals, the test should still pass; when the behaviour breaks, the test should fail.

  Concretely: if a seed command creates a `DailyMeal` for every enabled day in the month, the test iterates the days and asserts each `DailyMeal` exists in the database. It does *not* mock the helper that builds a single meal and assert it was called N times — that pins the test to today's implementation and gives a green build even if the database ends up empty.

- Prefer named-variable loops over compact comprehensions in assertions:

  ```python
  for current_day in days_in_month:
      assert DailyMeal.objects.filter(date=current_day).exists()
  ```

  reads better than a nested `all(...)` one-liner.

## Architecture

### Backend (`backend/`)

- **`meal_planner/settings.py`** — Django settings; uses `python-decouple` for env vars, `dj-database-url` for DB config (SQLite in dev, PostgreSQL in prod via `DATABASE_URL`)
- **`meal_planner/urls.py`** — Top-level routing; mounts API under `/api/`
- **`meals/models.py`** — Core domain models: `MealPlan`, `Food`, `DailyMeal`, `MealSuggestion`, `MealSettings`, `MealType`
- **`meals/views.py`** — DRF ViewSets exposing CRUD + custom actions
- **`meals/serializers.py`** — DRF serializers for API I/O
- **`meals/urls.py`** — DRF router wiring ViewSets to `/api/` endpoints
- **`lambda_handler.py`** — AWS Lambda entry point

Static files are served by **WhiteNoise** in production; **Gunicorn** is the production WSGI server.

### Frontend (`frontend/src/`)

- **`App.js`** — React Router routes; top-level layout
- **`services/api.js`** — Axios client; reads `REACT_APP_API_URL` (defaults to `http://localhost:8000/api`); includes request/response interceptors
- **`components/`** — Page-level components: `MealPlansList`, `MealPlanDetail`, `FoodsManagement`, `MealSettings`, `Navbar`

UI is built with **Material-UI (MUI) v7** and **Emotion** for styling. Dates handled with **Day.js**.

### Deployment

Deployed to **AWS Lambda** via `lambda_handler.py` and the Lambda-related `Makefile` targets.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | SQLite (`db.sqlite3`) |
| `REACT_APP_API_URL` | Frontend API base URL | `http://localhost:8000/api` |
| `SECRET_KEY` | Django secret key | Required in production |
| `DEBUG` | Django debug mode | `True` in dev |

`make init` creates empty `.env` files — populate `backend/.env` and `frontend/.env` with the required values before starting.
