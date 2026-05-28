import { getEmojiForFoods } from './foodEmojis';

describe('getEmojiForFoods', () => {
  it('falls back to the plate emoji when no foods are given', () => {
    expect(getEmojiForFoods()).toBe('🍽️');
    expect(getEmojiForFoods([])).toBe('🍽️');
    expect(getEmojiForFoods(null)).toBe('🍽️');
  });

  it('uses the first food when multiple are provided', () => {
    expect(getEmojiForFoods([{ category: 'Protein' }, { category: 'Vegetable' }])).toBe('🍗');
  });

  it.each([
    ['Protein', '🍗'],
    ['Vegetable', '🥦'],
    ['Fruit', '🍎'],
    ['Grain', '🌾'],
    ['Starch', '🥔'],
    ['Dairy', '🧀'],
    ['Other', '🍽️'],
  ] as const)('maps category %s → %s', (category, expected) => {
    expect(getEmojiForFoods([{ category }])).toBe(expected);
  });

  it('falls back to the Other emoji for unknown categories', () => {
    expect(getEmojiForFoods([{ category: 'Mystery' as never }])).toBe('🍽️');
  });
});
