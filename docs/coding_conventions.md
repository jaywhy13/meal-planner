# Coding Conventions

## Naming

**No abbreviations.** Write `meal_plan`, not `mp`; `selected_foods`, not `sel_foods`; `is_healthy`, not `ih`.

**Name with intent.** When a generic name would let several different meanings pass, encode the specific intent in the name. The reader shouldn't have to scan the body to know what's special about this value.

```python
# Generic — what's notable about this plan?
plan = MealPlan.objects.create(name="Plan", start_date="2026-05-01")

# Intentional — the name says what role this fixture plays.
plan_without_settings = MealPlan.objects.create(name="Plan", start_date="2026-05-01")
```

```javascript
// Generic — which foods are these?
const items = response.data;

// Intentional
const available_foods = response.data;
```

### Python (Backend)

- **snake_case** for variables, functions, methods, module names.
- **PascalCase** for classes (`MealPlanViewSet`, `DailyMealSerializer`).
- **UPPER_SNAKE_CASE** for constants and Django settings.
- Model fields: `snake_case`, matching the database column name Django generates.
- URL patterns: `kebab-case` (`meal-plans`, `daily-meals`).

### JavaScript (Frontend)

- **camelCase** for variables, functions, props, state.
- **PascalCase** for React components and component file names.
- API response data keeps the backend's `snake_case` — don't transform keys at the boundary.
- Constants: `UPPER_SNAKE_CASE` (`MEAL_TYPES`, `FOOD_CATEGORIES`).

## Type Annotations

All code uses explicit type annotations. Don't leave types implied just because the code runs without them.

**Python**: Use type hints on all function signatures, return types, and non-trivial local variables. Use `from __future__ import annotations` for forward references.

```python
from __future__ import annotations
from django.db.models import QuerySet

class MealPlanRepository:
    def get_by_id(self, plan_id: int) -> MealPlan:
        return MealPlan.objects.get(pk=plan_id)

    def get_active(self) -> QuerySet[MealPlan]:
        return MealPlan.objects.filter(is_active=True)

def generate_meal_plan(meal_plan: MealPlan, settings: MealSettings) -> None:
    suggestions: QuerySet[MealSuggestion] = suggestion_repository.get_healthy()
    enabled_types: list[str] = get_enabled_meal_types(settings)
```

**JavaScript**: Use JSDoc annotations on class methods, exported functions, and factory functions. Annotate parameters and return types.

```javascript
/**
 * @param {number} planId
 * @returns {Promise<{plan: Object, settings: Object|null}>}
 */
async loadWithSettings(planId) { ... }
```

## Comments

Default to no comments. Add one only when the *why* is non-obvious.

Good:
```javascript
// dayjs treats Sunday as the start of the week, so we shift +1 day
const week1Start = anchor.startOf('week').add(1, 'day');
```

Bad (restates what the code does):
```python
# Get all foods
foods = Food.objects.all()
```

If you need a comment to explain what code does, rename the variable or extract a function instead.

## One Level of Abstraction per Method

A method should read at a single level of abstraction. If the top talks about high-level steps and the bottom is doing raw query construction, split it.

```python
# Mixed levels — orchestration and query details in one view method
def generate_meal_plan(self, request: Request, pk: int = None) -> Response:
    meal_plan = self.get_object()
    meal_settings, created = MealSettings.objects.get_or_create(meal_plan=meal_plan)
    suggestions = MealSuggestion.objects.filter(is_healthy=True)
    for week in range(1, 5):
        for day in range(1, 6):
            enabled_meal_types: list[str] = []
            if meal_settings.breakfast_enabled:
                enabled_meal_types.append('breakfast')
            # ... 20 more lines of detail

# Better — view delegates to the service layer
def generate_meal_plan(self, request: Request, pk: int = None) -> Response:
    meal_plan: MealPlan = self.get_object()
    self.meal_plan_service.generate(meal_plan)
    serializer = self.get_serializer(meal_plan)
    return Response(serializer.data)
```

## Error Handling

- **Backend**: Let DRF handle validation errors. Serializer field validation and model constraints produce proper 400 responses automatically. Only add custom error handling when DRF's defaults don't cover the case.
- **Frontend**: API errors are caught in the page-level component that made the call. Set an `error` state string and render it in an `<Alert>`. Don't swallow errors silently — at minimum, `console.error` them.
- Don't add try/catch around code that can't fail. Trust Django's ORM and DRF's framework guarantees.

## File Organization

### Backend

- One Django app (`meals`) owns the entire domain. Don't create new apps unless the domain genuinely splits (e.g., user accounts, billing).
- **View layer**: `urls.py` (routes), `views.py` (ViewSets), `serializers.py` (validation/representation). These three files work together as the HTTP surface.
- **Service layer**: `services.py` (or `services/` package). Business logic and orchestration. Called by views, calls repositories.
- **Repository layer**: `repositories.py` (or `repositories/` package). All ORM queries. The rest of the codebase never calls `Model.objects` directly.
- **Models**: `models.py`. Schema only — fields, constraints, choices, `Meta`, `__str__`. No business methods on models.
- **Factories**: `factories.py`. Test data factories using `factory_boy`.
- Management commands go in `meals/management/commands/`.

### Frontend

- Page-level components live directly in `components/`.
- Feature-scoped sub-components go in `components/<feature>/` (e.g., `components/mealPlanDetail/WeekGrid.js`).
- **Services**: `services/` — business logic, data transformation, orchestration across multiple API calls. Components call services, not clients.
- **Clients**: `clients/` — Axios wrappers grouped by API resource. `clients/api.js` configures the shared Axios instance. Each resource gets its own file (`clients/mealPlansClient.js`).
- Shared constants in `constants/`. Design tokens in `theme/`.
- One component per file. File name matches the component name (`MealCell.js` exports `MealCell`).

## Dependencies

- **Backend**: Pin exact versions in `requirements.txt`. No `>=` or `~=` specifiers — CI and production should use the same versions.
- **Frontend**: Use `yarn` (Docker uses it). `package-lock.json` is checked in for CI.

## Django-Specific

- **No fat models.** Models define fields, constraints, `Meta`, and `__str__`. Business logic goes in `services.py`, persistence queries go in `repositories.py`.
- Use `TextChoices` for enumerated fields (see `MealType`).
- Use `auto_now_add` / `auto_now` for timestamp fields.
- Configure `Meta.ordering` and `Meta.unique_together` on models rather than enforcing these in views.
- Serializers that handle M2M writes should override `create`/`update` (see `DailyMealSerializer` for the pattern).
- Use `DefaultRouter(trailing_slash=False)` — the project doesn't use trailing slashes on API URLs.

## React-Specific

- Use functional components with hooks. No class components.
- State management: `useState` + `useEffect` for data fetching. No Redux, no Context API for data — the app is small enough that prop drilling is fine.
- Styling: MUI `sx` prop with theme tokens from `theme/tokens.js`. No CSS modules, no styled-components outside of what Emotion provides via MUI.
- Date handling: Day.js everywhere. Don't import moment or use native Date for display logic.
