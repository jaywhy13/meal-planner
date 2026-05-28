import React from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { semantic, radius, shadows } from '../../theme/tokens';

export interface DateRangeBarProps {
  label: string;
  onPrev: () => void;
  onNext: () => void;
  canPrev: boolean;
  canNext: boolean;
}

const DateRangeBar = ({
  label,
  onPrev,
  onNext,
  canPrev,
  canNext,
}: DateRangeBarProps): React.ReactElement => (
  <Box
    sx={{
      bgcolor: semantic.bgCard,
      borderRadius: `${radius.r16}px`,
      boxShadow: shadows.cardLift,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      px: 2,
      py: 1.25,
      mb: 3,
    }}
  >
    <IconButton onClick={onPrev} disabled={!canPrev} aria-label="Previous week">
      <ChevronLeft />
    </IconButton>
    <Typography sx={{ fontSize: 15, fontWeight: 600, color: semantic.textPrimary }}>
      {label}
    </Typography>
    <IconButton onClick={onNext} disabled={!canNext} aria-label="Next week">
      <ChevronRight />
    </IconButton>
  </Box>
);

export default DateRangeBar;
