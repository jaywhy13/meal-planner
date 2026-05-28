import type { FoodCategory } from '../types';

export const FOOD_CATEGORIES: FoodCategory[] = [
  'Protein',
  'Vegetable',
  'Fruit',
  'Grain',
  'Starch',
  'Dairy',
  'Other',
];

export type CategoryColor =
  | 'primary'
  | 'success'
  | 'warning'
  | 'info'
  | 'error'
  | 'secondary'
  | 'default';

export const CATEGORY_COLORS: Record<FoodCategory, CategoryColor> = {
  Protein: 'primary',
  Vegetable: 'success',
  Fruit: 'warning',
  Grain: 'info',
  Starch: 'error',
  Dairy: 'secondary',
  Other: 'default',
};

export const getCategoryColor = (category: FoodCategory | string): CategoryColor =>
  CATEGORY_COLORS[category as FoodCategory] || 'default';
