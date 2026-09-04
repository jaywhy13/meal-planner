import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FoodsManagement from './FoodsManagement';
import { foodsAPI } from '../services/api';
import type { Food } from '../types';

jest.mock('../services/api');

jest.mock(
  'react-router-dom',
  () => ({
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

const mockedFoodsAPI = foodsAPI as jest.Mocked<typeof foodsAPI>;

const okResponse = <T,>(data: T) =>
  ({ data, status: 200, statusText: 'OK', headers: {}, config: {} }) as never;

beforeEach(() => {
  jest.clearAllMocks();
  mockedFoodsAPI.getAll.mockResolvedValue(okResponse([buildFood()]));
});

describe('FoodsManagement category select', () => {
  it('shrinks the Category label so it does not sit on top of the placeholder option', async () => {
    render(<FoodsManagement />);

    fireEvent.click(await screen.findByRole('button', { name: /add food/i }));

    expect(await screen.findByText('Category', { selector: 'label' })).toHaveClass(
      'MuiInputLabel-shrink'
    );
  });
});
