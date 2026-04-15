# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack meal planning application with a **Django REST API backend** and **React frontend**. Supports creating meal plans, managing foods, configuring meal settings, and viewing daily meal suggestions.

## Development Commands

### Recommended: Docker (Primary Workflow)

```bash
make init    # First-time setup: creates .env files and builds containers
make start   # Start all services with hot-reload (frontend + backend + db)
make stop    # Stop all services
make ssh     # SSH into the backend container
```

### Backend (Django)

From `backend/`:
```bash
python manage.py runserver          # Dev server on :8000
python manage.py migrate            # Apply migrations
python manage.py makemigrations     # Create new migrations
python manage.py populate_data      # Load initial food/meal data
python manage.py test               # Run backend tests
python manage.py test meals.tests.SpecificTest  # Run a single test
```

### Frontend (React)

From `frontend/`:
```bash
yarn start   # Dev server on :3000 (used in Docker)
yarn test    # Run tests (React Testing Library + Jest)
yarn build   # Production build
```

> Note: Docker uses `yarn`; you can also use `npm` locally.

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

`make init` generates the necessary `.env` files from templates.
