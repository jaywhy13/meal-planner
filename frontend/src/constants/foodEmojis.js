const CATEGORY_EMOJI = {
  Protein: '🍗',
  Vegetable: '🥦',
  Fruit: '🍎',
  Grain: '🌾',
  Starch: '🥔',
  Dairy: '🧀',
  Other: '🍽️',
};

export const getEmojiForFoods = (foods) => {
  const first = foods && foods[0];
  if (!first) return '🍽️';
  return CATEGORY_EMOJI[first.category] || CATEGORY_EMOJI.Other;
};

export default CATEGORY_EMOJI;
