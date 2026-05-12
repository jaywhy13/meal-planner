import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DateRangeBar from './DateRangeBar';

const baseProps = {
  label: 'May 11 – May 17, 2026',
  onPrev: () => {},
  onNext: () => {},
  canPrev: true,
  canNext: true,
};

describe('DateRangeBar', () => {
  it('renders the label', () => {
    render(<DateRangeBar {...baseProps} />);
    expect(screen.getByText('May 11 – May 17, 2026')).toBeInTheDocument();
  });

  it('calls onPrev / onNext when the arrows are clicked', () => {
    const onPrev = jest.fn();
    const onNext = jest.fn();
    render(<DateRangeBar {...baseProps} onPrev={onPrev} onNext={onNext} />);

    fireEvent.click(screen.getByLabelText('Previous week'));
    fireEvent.click(screen.getByLabelText('Next week'));

    expect(onPrev).toHaveBeenCalledTimes(1);
    expect(onNext).toHaveBeenCalledTimes(1);
  });

  it('disables the prev arrow when canPrev is false', () => {
    render(<DateRangeBar {...baseProps} canPrev={false} />);
    expect(screen.getByLabelText('Previous week')).toBeDisabled();
    expect(screen.getByLabelText('Next week')).toBeEnabled();
  });

  it('disables the next arrow when canNext is false', () => {
    render(<DateRangeBar {...baseProps} canNext={false} />);
    expect(screen.getByLabelText('Next week')).toBeDisabled();
    expect(screen.getByLabelText('Previous week')).toBeEnabled();
  });
});
