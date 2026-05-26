# Testing

## Backend (Django)

### Running Tests

```bash
# All backend tests
python manage.py test meals

# A specific test class
python manage.py test meals.tests.MealPlanStartDateTests

# Via Docker
make ssh
# then: python manage.py test meals
```

CI runs `python manage.py test meals` on every push/PR that touches `backend/`.

### Test Framework

Tests use Django's `APITestCase` from Django REST Framework. This gives you a test client that speaks JSON and handles content negotiation.

### What to Test

Test **behaviour through the API**, not internal model methods in isolation. The API is the contract — if the endpoint returns the right response and the database is in the right state, the internals are working.

Each test should fix on one observable outcome:

```python
def test_create_without_start_date_returns_400(self) -> None:
    url: str = reverse('mealplan-list')
    response: Response = self.client.post(url, {'name': 'Test Plan'}, format='json')
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn('start_date', response.data)
```

This tests the behaviour the caller cares about: "if I omit start_date, I get a 400 with a message about start_date." It doesn't test which serializer field raised the error or how validation is wired internally.

### Test Structure

**Organize by feature, not by model.** Group tests into classes named after the feature or behaviour being tested:

```python
class MealSettingsDayToggleTests(APITestCase):
    ...

class MealPlanStartDateTests(APITestCase):
    ...
```

### Data Setup — Use Factories

**Use factories, not shared `setUp` or helper methods.** Each test should create only the data it needs, close to where it's asserted on. Factories provide sensible defaults so each test only specifies the fields it cares about, and tests stay decoupled from each other.

Factories live in `meals/factories.py` and use `factory_boy`:

```python
# meals/factories.py
from __future__ import annotations
import factory
from .models import MealPlan, MealSettings, Food, DailyMeal

class MealPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealPlan

    name: str = factory.Sequence(lambda n: f'Plan {n}')
    start_date: str = '2026-05-01'

class MealSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealSettings

    meal_plan: MealPlan = factory.SubFactory(MealPlanFactory)

class FoodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Food

    name: str = factory.Sequence(lambda n: f'Food {n}')
    category: str = 'Other'
```

Tests use factories inline — the data is right next to the assertion:

```python
def test_patch_day_toggle_persists(self) -> None:
    settings: MealSettings = MealSettingsFactory()
    url: str = reverse('mealsettings-detail', args=[settings.pk])
    self.client.patch(url, {'saturday_enabled': False}, format='json')
    settings.refresh_from_db()
    self.assertFalse(settings.saturday_enabled)

def test_create_with_start_date_succeeds(self) -> None:
    url: str = reverse('mealplan-list')
    response: Response = self.client.post(
        url, {'name': 'June Plan', 'start_date': '2026-06-01'}, format='json',
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['start_date'], '2026-06-01')
```

Notice that `MealSettingsFactory()` automatically creates a parent `MealPlan` via `SubFactory` — no need to wire that up manually. Override only the fields your test cares about: `MealSettingsFactory(meal_plan__name='Custom Plan')`.

### What NOT to Test

- Don't test Django or DRF internals (serializer field types, router URL generation).
- Don't mock the database. Tests use SQLite in-process — it's fast enough and catches real query issues.
- Don't test that a model's `__str__` returns a specific format unless the format is part of the API contract.

### Assertions

- Use DRF's status constants (`status.HTTP_200_OK`) instead of bare integers.
- Assert on `response.data` (parsed JSON), not `response.content` (raw bytes).
- When checking that a field exists in a response, use `assertIn('field_name', response.data)`.
- When checking database state after an API call, use `refresh_from_db()` on the instance.

## Frontend (React)

### Running Tests

```bash
# All frontend tests
cd frontend && yarn test

# In CI
npm run build  # CI runs build, which catches lint + compile errors
```

### Test Framework

React Testing Library + Jest (via Create React App).

### What to Test

Test **component behaviour from the user's perspective**: what's rendered, what happens when the user clicks. Don't test implementation details like internal state values or which hooks fired.

```javascript
it('calls onPrev / onNext when the arrows are clicked', () => {
  const props = buildDateRangeBarProps();
  render(<DateRangeBar {...props} />);

  fireEvent.click(screen.getByLabelText('Previous week'));
  fireEvent.click(screen.getByLabelText('Next week'));

  expect(props.onPrev).toHaveBeenCalledTimes(1);
  expect(props.onNext).toHaveBeenCalledTimes(1);
});
```

### Test Structure

- Test files live next to the component they test: `MealCell.js` + `MealCell.test.js` in the same directory.
- Group related assertions under `describe` blocks named after the state being tested (`'MealCell empty state'`, `'MealCell filled state'`).
- Each `it` block tests one thing.

### Props and Data Setup — Use Factories

**Use factory functions, not shared `baseProps` objects.** A `baseProps` object at the top of the file creates the same problem as a shared `setUp` — tests become coupled to a single data shape, and changing the defaults breaks unrelated tests. Instead, write a factory function that returns sensible defaults and accepts overrides:

```javascript
/**
 * @param {Partial<import('./DateRangeBar').DateRangeBarProps>} overrides
 * @returns {import('./DateRangeBar').DateRangeBarProps}
 */
function buildDateRangeBarProps(overrides = {}) {
  return {
    label: 'May 11 – May 17, 2026',
    onPrev: jest.fn(),
    onNext: jest.fn(),
    canPrev: true,
    canNext: true,
    ...overrides,
  };
}

it('disables the prev arrow when canPrev is false', () => {
  const props = buildDateRangeBarProps({ canPrev: false });
  render(<DateRangeBar {...props} />);
  expect(screen.getByLabelText('Previous week')).toBeDisabled();
});

it('calls onNext when the next arrow is clicked', () => {
  const props = buildDateRangeBarProps();
  render(<DateRangeBar {...props} />);
  fireEvent.click(screen.getByLabelText('Next week'));
  expect(props.onNext).toHaveBeenCalledTimes(1);
});
```

Why a function instead of a const: the factory creates fresh `jest.fn()` mocks on every call, so tests can't accidentally share mock state. Each test gets an independent copy of everything.

For data objects (not just props), use the same pattern:

```javascript
/**
 * @param {Partial<{id: number, foods: Array<{name: string, category: string}>}>} overrides
 * @returns {{id: number, foods: Array<{name: string, category: string}>}}
 */
function buildMeal(overrides = {}) {
  return {
    id: 1,
    foods: [{ name: 'Oatmeal', category: 'Grain' }],
    ...overrides,
  };
}

it('shows a single food name', () => {
  const props = buildMealCellProps({ meal: buildMeal() });
  render(<MealCell {...props} />);
  expect(screen.getByText('Oatmeal')).toBeInTheDocument();
});
```

### Querying Elements

Prefer accessible queries in this order:
1. `getByRole` / `getByLabelText` — matches what assistive technology sees.
2. `getByText` — matches what the user reads.
3. `getByTestId` — last resort when no accessible handle exists.

### Mocking

- Use `jest.fn()` for callback props. Assert on call count and arguments.
- Don't mock the API layer in unit tests for presentational components — those components don't call APIs. If you're testing a page component that fetches data, consider an integration test or mock at the Axios level.
- Don't mock React hooks or internal state.

### What NOT to Test

- Don't snapshot test. Snapshots are brittle, produce noisy diffs, and get rubber-stamped on update.
- Don't test MUI's internal behaviour (e.g., that a `<Select>` opens a dropdown).
- Don't test styling values (colors, spacing) — those are design concerns, not logic.
