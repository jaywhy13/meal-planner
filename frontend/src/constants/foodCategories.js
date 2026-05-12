export const FOOD_CATEGORIES = [
  'Protein',
  'Vegetable',
  'Fruit',
  'Grain',
  'Starch',
  'Dairy',
  'Other',
];

export const CATEGORY_COLORS = {
  Protein: 'primary',
  Vegetable: 'success',
  Fruit: 'warning',
  Grain: 'info',
  Starch: 'error',
  Dairy: 'secondary',
  Other: 'default',
};

export const getCategoryColor = (category) =>
  CATEGORY_COLORS[category] || 'default';
