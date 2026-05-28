import React, { KeyboardEvent } from 'react';
import { Box, Typography } from '@mui/material';
import { colors, semantic, radius, shadows } from '../../theme/tokens';
import { getEmojiForFoods } from '../../constants/foodEmojis';
import type { Food, MealType } from '../../types';

const CELL_HEIGHT = 132;

export interface WeekGridMeal {
  id: number;
  day: number;
  meal_type: MealType;
  foods: Food[];
}

const summarize = (foods: Food[] | undefined | null): string => {
  if (!foods || foods.length === 0) return '';
  if (foods.length === 1) return foods[0].name;
  if (foods.length === 2) return `${foods[0].name} & ${foods[1].name}`;
  return `${foods[0].name} & ${foods.length - 1} more`;
};

interface EmptyCellProps {
  onAdd: () => void;
  isToday?: boolean;
}

const EmptyCell = ({ onAdd, isToday }: EmptyCellProps): React.ReactElement => (
  <Box
    role="button"
    tabIndex={0}
    onClick={onAdd}
    onKeyDown={(event: KeyboardEvent<HTMLDivElement>) => {
      if (event.key === 'Enter' || event.key === ' ') onAdd();
    }}
    sx={{
      height: CELL_HEIGHT,
      borderRadius: `${radius.r12}px`,
      border: `1.5px dashed ${semantic.borderDefault}`,
      bgcolor: isToday ? colors.green50 : 'transparent',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: semantic.textMuted,
      cursor: 'pointer',
      transition: 'background-color 120ms ease, border-color 120ms ease',
      '&:hover': {
        bgcolor: colors.green50,
        borderColor: colors.green500,
        color: colors.green600,
      },
    }}
  >
    <Box sx={{ fontSize: 24, lineHeight: 1 }}>+</Box>
  </Box>
);

interface FilledCellProps {
  meal: WeekGridMeal;
  onEdit: (meal: WeekGridMeal) => void;
  isToday?: boolean;
}

const FilledCell = ({ meal, onEdit, isToday }: FilledCellProps): React.ReactElement => {
  const emoji = getEmojiForFoods(meal.foods);
  const label = summarize(meal.foods) || '(empty)';

  return (
    <Box
      role="button"
      tabIndex={0}
      onClick={() => onEdit(meal)}
      onKeyDown={(event: KeyboardEvent<HTMLDivElement>) => {
        if (event.key === 'Enter' || event.key === ' ') onEdit(meal);
      }}
      sx={{
        height: CELL_HEIGHT,
        borderRadius: `${radius.r12}px`,
        bgcolor: semantic.bgCard,
        boxShadow: shadows.cardLift,
        border: isToday ? `1.5px solid ${colors.green500}` : `1px solid ${semantic.borderDefault}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        px: 1.5,
        py: 1.5,
        cursor: 'pointer',
        transition: 'transform 120ms ease, box-shadow 120ms ease',
        '&:hover': {
          transform: 'translateY(-1px)',
          boxShadow: '0 6px 20px rgba(17, 24, 39, 0.08)',
        },
      }}
    >
      <Box sx={{ fontSize: 28, mb: 0.5 }}>{emoji}</Box>
      <Typography
        sx={{
          fontSize: 13,
          fontWeight: 600,
          color: semantic.textPrimary,
          textAlign: 'center',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {label}
      </Typography>
    </Box>
  );
};

export interface MealCellProps {
  meal?: WeekGridMeal | null;
  onAdd: () => void;
  onEdit: (meal: WeekGridMeal) => void;
  isToday?: boolean;
}

const MealCell = ({ meal, onAdd, onEdit, isToday }: MealCellProps): React.ReactElement =>
  meal ? (
    <FilledCell meal={meal} onEdit={onEdit} isToday={isToday} />
  ) : (
    <EmptyCell onAdd={onAdd} isToday={isToday} />
  );

export default MealCell;
