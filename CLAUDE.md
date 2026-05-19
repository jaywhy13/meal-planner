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

### Worktree isolation (agents: read this)

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
