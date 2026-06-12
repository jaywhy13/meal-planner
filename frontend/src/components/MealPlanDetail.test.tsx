import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import MealPlanDetail from './MealPlanDetail';
import {
  mealPlansAPI,
  foodsAPI,
  dailyMealsAPI,
  mealsAPI,
  mealSettingsAPI,
} from '../services/api';
import type { Food, Meal, MealPlan } from '../types';

jest.mock('../services/api');

jest.mock(
  'react-router-dom',
  () => ({
    useParams: () => ({ id: '5' }),
    useNavigate: () => jest.fn(),
  }),
  { virtual: true }
);

const buildFood = (overrides: Partial<Food> = {}): Food => ({
  id: 1,
  name: 'Oats',
  category: 'Grain',
  created_at: '2026-05-01T00:00:00Z',
  ...overrides,
});

const buildMeal = (overrides: Partial<Meal> = {}): Meal => ({
  id: 10,
  name: 'Oats',
  foods: [buildFood()],
  notes: '',
  created_at: '2026-05-01T00:00:00Z',
  updated_at: '2026-05-01T00:00:00Z',
  ...overrides,
});

const buildMealPlan = (overrides: Partial<MealPlan> = {}): MealPlan => ({
  id: 5,
  name: 'May Plan',
  start_date: '2026-05-01',
  created_at: '2026-05-01T00:00:00Z',
  updated_at: '2026-05-01T00:00:00Z',
  daily_meals: [],
  meal_settings: null,
  ...overrides,
});

const renderMealPlanDetail = (): void => {
  render(<MealPlanDetail />);
};

const mockedMealPlansAPI = mealPlansAPI as jest.Mocked<typeof mealPlansAPI>;
const mockedFoodsAPI = foodsAPI as jest.Mocked<typeof foodsAPI>;
const mockedDailyMealsAPI = dailyMealsAPI as jest.Mocked<typeof dailyMealsAPI>;
const mockedMealsAPI = mealsAPI as jest.Mocked<typeof mealsAPI>;
const mockedMealSettingsAPI = mealSettingsAPI as jest.Mocked<typeof mealSettingsAPI>;

const okResponse = <T,>(data: T) =>
  ({ data, status: 200, statusText: 'OK', headers: {}, config: {} }) as never;

beforeEach(() => {
  jest.clearAllMocks();
  mockedMealPlansAPI.getById.mockResolvedValue(okResponse(buildMealPlan()));
  mockedFoodsAPI.getAll.mockResolvedValue(okResponse([buildFood()]));
  mockedDailyMealsAPI.getAll.mockResolvedValue(okResponse([]));
  mockedDailyMealsAPI.create.mockResolvedValue(okResponse({} as never));
  mockedMealsAPI.create.mockResolvedValue(okResponse(buildMeal()));
  mockedMealSettingsAPI.getByMealPlan.mockResolvedValue(okResponse([]));
});

const openAddDialogAndSelectFood = async (): Promise<void> => {
  fireEvent.click(await screen.findByRole('button', { name: /add meal/i }));
  const foodsInput = await screen.findByLabelText('Foods');
  fireEvent.mouseDown(foodsInput);
  fireEvent.click(await screen.findByText('Oats'));
};

describe('MealPlanDetail save flow', () => {
  it('creates a Meal with the selected foods, then links it to a new daily meal', async () => {
    renderMealPlanDetail();
    await openAddDialogAndSelectFood();

    fireEvent.click(screen.getByRole('button', { name: /^save$/i }));

    await waitFor(() => expect(mockedMealsAPI.create).toHaveBeenCalledTimes(1));
    expect(mockedMealsAPI.create).toHaveBeenCalledWith(
      expect.objectContaining({ food_ids: [1] })
    );

    await waitFor(() => expect(mockedDailyMealsAPI.create).toHaveBeenCalledTimes(1));
    expect(mockedDailyMealsAPI.create).toHaveBeenCalledWith(
      expect.objectContaining({ meal_id: 10, meal_type: 'breakfast', meal_plan: '5' })
    );
  });

  it('does not post the dropped food_ids/notes fields on the daily meal', async () => {
    renderMealPlanDetail();
    await openAddDialogAndSelectFood();

    fireEvent.click(screen.getByRole('button', { name: /^save$/i }));

    await waitFor(() => expect(mockedDailyMealsAPI.create).toHaveBeenCalledTimes(1));
    const dailyMealPayload = mockedDailyMealsAPI.create.mock.calls[0][0];
    expect(dailyMealPayload).not.toHaveProperty('food_ids');
    expect(dailyMealPayload).not.toHaveProperty('notes');
    expect(dailyMealPayload).toHaveProperty('date');
  });
});
