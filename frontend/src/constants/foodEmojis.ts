import type { Food, FoodCategory } from '../types';

const CATEGORY_EMOJI: Record<FoodCategory, string> = {
  Protein: '🍗',
  Vegetable: '🥦',
  Fruit: '🍎',
  Grain: '🌾',
  Starch: '🥔',
  Dairy: '🧀',
  Other: '🍽️',
};

export const getEmojiForFoods = (foods?: Pick<Food, 'category'>[] | null): string => {
  const first = foods && foods[0];
  if (!first) return '🍽️';
  return CATEGORY_EMOJI[first.category as FoodCategory] || CATEGORY_EMOJI.Other;
};

export default CATEGORY_EMOJI;
