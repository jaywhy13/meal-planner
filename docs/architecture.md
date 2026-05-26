# Architecture

## Stack Overview

| Layer | Technology | Location |
|---|---|---|
| Frontend | React 19, MUI 7, Axios, Day.js | `frontend/` |
| API | Django 4.2, Django REST Framework | `backend/meals/` |
| Database | PostgreSQL (prod), SQLite (dev) | via `DATABASE_URL` |
| Infrastructure | Docker Compose (dev), AWS Lambda (prod), Pulumi | `docker-compose.yml`, `infra/` |

## Layered Architecture

The backend uses explicit layers: a view layer for HTTP concerns, a service layer for business logic, a repository layer for persistence, and thin models for schema. The frontend mirrors this with components, services, and API clients.

### Backend Layers

```
requests
   │
   ▼
┌─ View Layer ─────────────────────────────────────────────┐
│  urls.py          ← Route registration (DRF router)      │
│  views.py         ← ViewSets: HTTP, permissions, dispatch │
│  serializers.py   ← Validation, field mapping, I/O shape  │
└──────────────────────────────────────────────────────────┘
   │
   ▼
services.py          ← Business logic, orchestration
   │
   ▼
repositories.py      ← Persistence: queries, creates, updates
   │
   ▼
models.py            ← Schema: fields, constraints, choices
   │
   ▼
PostgreSQL / SQLite
```

**Rules:**

1. **The view layer owns HTTP.** This is `urls.py` + `views.py` + `serializers.py` working together. ViewSets handle authentication, permissions, queryset scoping, and dispatching to the serializer. Serializers translate between the wire format (JSON) and the domain. Neither views nor serializers contain business logic — they call into the service layer for anything beyond simple CRUD.

2. **Services own business logic.** Any operation that involves decisions, coordination, or rules beyond "save this data" lives in `services.py` (or a `services/` package when it grows). Services are classes that take repositories as constructor dependencies, making them easy to test with fakes. They don't know about HTTP requests, serializers, or response formats.

   ```python
   # services.py
   from __future__ import annotations
   from .repositories import MealPlanRepository, MealSuggestionRepository, DailyMealRepository

   class MealPlanService:
       def __init__(
           self,
           meal_plan_repository: MealPlanRepository | None = None,
           suggestion_repository: MealSuggestionRepository | None = None,
           daily_meal_repository: DailyMealRepository | None = None,
       ) -> None:
           self.meal_plan_repository = meal_plan_repository or MealPlanRepository()
           self.suggestion_repository = suggestion_repository or MealSuggestionRepository()
           self.daily_meal_repository = daily_meal_repository or DailyMealRepository()

       def generate(self, meal_plan: MealPlan) -> None:
           settings = self.meal_plan_repository.get_or_create_settings(meal_plan)
           suggestions = self.suggestion_repository.get_healthy()
           for week, day in enabled_slots(settings):
               meal = self.daily_meal_repository.get_or_create(meal_plan, week, day)
               self.assign_suggestion(meal, suggestions)
   ```

3. **Repositories own persistence.** All ORM queries live in `repositories.py` — `filter`, `create`, `get_or_create`, `bulk_update`, etc. The rest of the codebase never calls `Model.objects` directly. This keeps query logic in one place, makes it testable in isolation, and means swapping a data source only requires changing the repository.

   ```python
   # repositories.py
   from __future__ import annotations
   from django.db.models import QuerySet
   from .models import MealPlan, MealSettings, MealSuggestion

   class MealPlanRepository:
       def get_or_create_settings(self, meal_plan: MealPlan) -> MealSettings:
           settings, _ = MealSettings.objects.get_or_create(meal_plan=meal_plan)
           return settings

   class MealSuggestionRepository:
       def get_healthy(self) -> QuerySet[MealSuggestion]:
           return MealSuggestion.objects.filter(is_healthy=True)
   ```

4. **Models own schema, not behaviour.** Models define fields, constraints (`unique_together`, choices), `Meta` options, and `__str__`. They do not contain business methods. No fat models — business logic goes in services, persistence logic goes in repositories.

### Frontend Layers

```
App.js                         ← Routes, theme provider
   │
   ▼
components/                    ← Page-level components (MealPlansList, MealPlanDetail, etc.)
   │
   ├── components/<feature>/   ← Feature-scoped sub-components (mealPlanDetail/WeekGrid, etc.)
   │
   ▼
services/                      ← Business logic, data transformation, orchestration
   │
   ▼
clients/                       ← API clients: Axios calls grouped by resource
   │
   ▼
theme/, constants/             ← Design tokens, shared constants
```

**Rules:**

1. **Components own rendering and user interaction.** Page-level components (`MealPlanDetail`, `FoodsManagement`) manage loading/error state and call into services. They don't contain business logic or make API calls directly.

2. **Sub-components are presentational.** Components under `components/<feature>/` (like `WeekGrid`, `MealCell`, `DateRangeBar`) receive data and callbacks via props. They don't call services or clients directly.

3. **Services own business logic.** Any data transformation, orchestration across multiple API calls, or decision-making lives in `services/`. Services are classes that take client dependencies in the constructor. Components import services, not clients.

   ```javascript
   // services/MealPlanService.js
   import { MealPlansClient } from '../clients/MealPlansClient';
   import { MealSettingsClient } from '../clients/MealSettingsClient';

   export class MealPlanService {
     /** @param {MealPlansClient} mealPlansClient
      *  @param {MealSettingsClient} mealSettingsClient */
     constructor(
       mealPlansClient = new MealPlansClient(),
       mealSettingsClient = new MealSettingsClient(),
     ) {
       this.mealPlansClient = mealPlansClient;
       this.mealSettingsClient = mealSettingsClient;
     }

     /** @param {number} planId
      *  @returns {Promise<{plan: Object, settings: Object|null}>} */
     async loadWithSettings(planId) {
       const [plan, settings] = await Promise.all([
         this.mealPlansClient.getById(planId),
         this.mealSettingsClient.getByMealPlan(planId),
       ]);
       return { plan: plan.data, settings: settings.data[0] ?? null };
     }
   }
   ```

4. **Clients own HTTP.** Each client file in `clients/` wraps Axios calls for one API resource. Clients are classes that know about URLs, HTTP methods, and request/response shapes. They don't contain business logic.

   ```javascript
   // clients/MealPlansClient.js
   import api from './api';

   export class MealPlansClient {
     /** @returns {Promise<import('axios').AxiosResponse>} */
     getAll() { return api.get('/meal-plans'); }

     /** @param {number} id
      *  @returns {Promise<import('axios').AxiosResponse>} */
     getById(id) { return api.get(`/meal-plans/${id}`); }

     /** @param {{name: string, start_date: string}} data
      *  @returns {Promise<import('axios').AxiosResponse>} */
     create(data) { return api.post('/meal-plans', data); }
   }
   ```

5. **Styling uses MUI's `sx` prop and theme tokens.** Shared design values live in `theme/tokens.js`. Don't use inline CSS objects outside of `sx`; don't create separate CSS/SCSS files.

### Cross-Cutting Concerns

- **CORS**: Handled by `django-cors-headers`. Allowed origins are configured in `settings.py`.
- **Static files**: Served by WhiteNoise in production. The React build output is served as Django static files in the Lambda deployment.
- **Environment config**: Backend uses `python-decouple`; frontend uses `REACT_APP_*` env vars via Create React App.

## Domain Model

```
MealPlan
  ├── has many DailyMeal (week, day, meal_type) ── has many Food (M2M)
  ├── has one MealSettings (meal type toggles, day-of-week toggles)
  └── start_date (anchors the plan to a calendar month)

Food (standalone, shared across plans)

MealSuggestion ── has many Food (M2M), filtered by meal_type
```

Key constraints:
- `DailyMeal` is unique on `(meal_plan, week, day, meal_type)`.
- `MealSettings` is a `OneToOneField` on `MealPlan`.
- `Food.name` is unique.

## API Shape

All endpoints are under `/api/`. The DRF router uses `trailing_slash=False`.

| Resource | Endpoint | ViewSet |
|---|---|---|
| Meal Plans | `/api/meal-plans` | `MealPlanViewSet` |
| Foods | `/api/foods` | `FoodViewSet` |
| Daily Meals | `/api/daily-meals` | `DailyMealViewSet` |
| Meal Suggestions | `/api/meal-suggestions` | `MealSuggestionViewSet` (read-only) |
| Meal Settings | `/api/meal-settings` | `MealSettingsViewSet` |

Custom actions:
- `POST /api/meal-plans/{id}/generate_meal_plan` — auto-populate a plan with suggestions.
- `GET /api/foods/search?q=...` — search foods by name.
- `GET /api/meal-suggestions/by_meal_type?meal_type=...` — filter suggestions.

## Deployment

- **Development**: `docker-compose up --watch` runs backend (Django runserver) + frontend (CRA dev server) + PostgreSQL.
- **Production**: Django is packaged into a Docker image and deployed to AWS Lambda via `lambda_handler.py`. The React build is included as static files. Infrastructure is managed with Pulumi (`infra/`).
