import React from 'react';
import dayjs from 'dayjs';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import MealPlansList from './MealPlansList';
import { mealPlansAPI } from '../services/api';
import type { MealPlanSummary } from '../types';

jest.mock('../services/api');

jest.mock(
  'react-router-dom',
  () => ({
    useNavigate: () => jest.fn(),
  }),
  { virtual: true }
);

const buildMealPlanSummary = (overrides: Partial<MealPlanSummary> = {}): MealPlanSummary => ({
  id: 1,
  name: 'May Plan',
  start_date: '2026-05-01',
  created_at: '2026-05-01T00:00:00Z',
  updated_at: '2026-05-01T00:00:00Z',
  ...overrides,
});

const mockedMealPlansAPI = mealPlansAPI as jest.Mocked<typeof mealPlansAPI>;

const okResponse = <T,>(data: T) =>
  ({ data, status: 200, statusText: 'OK', headers: {}, config: {} }) as never;

beforeEach(() => {
  jest.clearAllMocks();
  mockedMealPlansAPI.getAll.mockResolvedValue(okResponse([buildMealPlanSummary()]));
});

const openCreateDialog = async (): Promise<void> => {
  fireEvent.click(await screen.findByRole('button', { name: /\+ new plan/i }));
};

describe('MealPlansList create meal plan dialog', () => {
  it('renders a start date input defaulting to today', async () => {
    render(<MealPlansList />);
    await openCreateDialog();

    const startDateInput = screen.getByLabelText('Start Date') as HTMLInputElement;
    expect(startDateInput.value).toBe(dayjs().format('YYYY-MM-DD'));
  });

  it('sends start_date in the create payload', async () => {
    mockedMealPlansAPI.create.mockResolvedValue(okResponse(buildMealPlanSummary({ id: 2 })));
    render(<MealPlansList />);
    await openCreateDialog();

    fireEvent.change(screen.getByLabelText('Meal Plan Name'), {
      target: { value: 'June Plan' },
    });
    fireEvent.change(screen.getByLabelText('Start Date'), {
      target: { value: '2026-06-01' },
    });

    fireEvent.click(screen.getByRole('button', { name: /^create$/i }));

    await waitFor(() => expect(mockedMealPlansAPI.create).toHaveBeenCalledTimes(1));
    expect(mockedMealPlansAPI.create).toHaveBeenCalledWith({
      name: 'June Plan',
      start_date: '2026-06-01',
    });
  });

  it('does not submit when the start date is cleared', async () => {
    render(<MealPlansList />);
    await openCreateDialog();

    fireEvent.change(screen.getByLabelText('Meal Plan Name'), {
      target: { value: 'June Plan' },
    });
    fireEvent.change(screen.getByLabelText('Start Date'), {
      target: { value: '' },
    });

    fireEvent.click(screen.getByRole('button', { name: /^create$/i }));

    expect(mockedMealPlansAPI.create).not.toHaveBeenCalled();
  });
});
