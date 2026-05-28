import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DateRangeBar, { DateRangeBarProps } from './DateRangeBar';

const buildDateRangeBarProps = (overrides: Partial<DateRangeBarProps> = {}): DateRangeBarProps => ({
  label: 'May 11 – May 17, 2026',
  onPrev: jest.fn(),
  onNext: jest.fn(),
  canPrev: true,
  canNext: true,
  ...overrides,
});

describe('DateRangeBar', () => {
  it('renders the label', () => {
    render(<DateRangeBar {...buildDateRangeBarProps()} />);
    expect(screen.getByText('May 11 – May 17, 2026')).toBeInTheDocument();
  });

  it('calls onPrev / onNext when the arrows are clicked', () => {
    const onPrev = jest.fn();
    const onNext = jest.fn();
    render(<DateRangeBar {...buildDateRangeBarProps({ onPrev, onNext })} />);

    fireEvent.click(screen.getByLabelText('Previous week'));
    fireEvent.click(screen.getByLabelText('Next week'));

    expect(onPrev).toHaveBeenCalledTimes(1);
    expect(onNext).toHaveBeenCalledTimes(1);
  });

  it('disables the prev arrow when canPrev is false', () => {
    render(<DateRangeBar {...buildDateRangeBarProps({ canPrev: false })} />);
    expect(screen.getByLabelText('Previous week')).toBeDisabled();
    expect(screen.getByLabelText('Next week')).toBeEnabled();
  });

  it('disables the next arrow when canNext is false', () => {
    render(<DateRangeBar {...buildDateRangeBarProps({ canNext: false })} />);
    expect(screen.getByLabelText('Next week')).toBeDisabled();
    expect(screen.getByLabelText('Previous week')).toBeEnabled();
  });
});
