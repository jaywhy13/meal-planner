import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MealCell, { WeekGridMeal } from './MealCell';
import type { Food } from '../../types';

const noop = (): void => {};

const buildMeal = (foods: Pick<Food, 'name' | 'category'>[]): WeekGridMeal => ({
  id: 1,
  day: 1,
  meal_type: 'breakfast',
  foods: foods.map((food, index) => ({
    id: index + 1,
    name: food.name,
    category: food.category,
    created_at: '2026-01-01T00:00:00Z',
  })),
});

describe('MealCell empty state', () => {
  it('renders a "+" affordance when no meal is given', () => {
    render(<MealCell onAdd={noop} onEdit={noop} />);
    expect(screen.getByText('+')).toBeInTheDocument();
  });

  it('calls onAdd when the empty cell is clicked', () => {
    const onAdd = jest.fn();
    render(<MealCell onAdd={onAdd} onEdit={noop} />);

    fireEvent.click(screen.getByRole('button'));
    expect(onAdd).toHaveBeenCalledTimes(1);
  });

  it('does not call onEdit when the empty cell is clicked', () => {
    const onEdit = jest.fn();
    render(<MealCell onAdd={noop} onEdit={onEdit} />);

    fireEvent.click(screen.getByRole('button'));
    expect(onEdit).not.toHaveBeenCalled();
  });
});

describe('MealCell filled state', () => {
  it('shows a single food name unchanged', () => {
    render(
      <MealCell
        meal={buildMeal([{ name: 'Oatmeal', category: 'Grain' }])}
        onAdd={noop}
        onEdit={noop}
      />
    );
    expect(screen.getByText('Oatmeal')).toBeInTheDocument();
  });

  it('joins two foods with an ampersand', () => {
    render(
      <MealCell
        meal={buildMeal([
          { name: 'Eggs', category: 'Protein' },
          { name: 'Toast', category: 'Grain' },
        ])}
        onAdd={noop}
        onEdit={noop}
      />
    );
    expect(screen.getByText('Eggs & Toast')).toBeInTheDocument();
  });

  it('summarizes three or more foods as "first & N more"', () => {
    render(
      <MealCell
        meal={buildMeal([
          { name: 'Chicken', category: 'Protein' },
          { name: 'Rice', category: 'Grain' },
          { name: 'Broccoli', category: 'Vegetable' },
          { name: 'Sauce', category: 'Other' },
        ])}
        onAdd={noop}
        onEdit={noop}
      />
    );
    expect(screen.getByText('Chicken & 3 more')).toBeInTheDocument();
  });

  it("uses the first food's category to pick the emoji", () => {
    render(
      <MealCell
        meal={buildMeal([
          { name: 'Apple', category: 'Fruit' },
          { name: 'Spinach', category: 'Vegetable' },
        ])}
        onAdd={noop}
        onEdit={noop}
      />
    );
    expect(screen.getByText('🍎')).toBeInTheDocument();
  });

  it('calls onEdit with the meal when clicked', () => {
    const onEdit = jest.fn();
    const meal = buildMeal([{ name: 'X', category: 'Other' }]);
    render(<MealCell meal={meal} onAdd={noop} onEdit={onEdit} />);

    fireEvent.click(screen.getByRole('button'));
    expect(onEdit).toHaveBeenCalledWith(meal);
  });
});
