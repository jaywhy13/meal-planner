import React from 'react';
import { Box, Typography } from '@mui/material';
import dayjs from 'dayjs';
import { colors, semantic } from '../../theme/tokens';
import MealCell from './MealCell';

const ROW_LABEL_WIDTH = 90;
const DAYS = [1, 2, 3, 4, 5, 6, 7];

const WeekGrid = ({
  weekStart,
  mealTypes,
  meals,
  onAddMeal,
  onEditMeal,
  onDeleteMeal,
}) => {
  const today = dayjs().startOf('day');
  const days = DAYS.map((dayNum) => {
    const date = weekStart.add(dayNum - 1, 'day');
    return {
      dayNum,
      date,
      isToday: date.isSame(today, 'day'),
    };
  });

  const findMeal = (dayNum, mealType) =>
    meals.find((m) => m.day === dayNum && m.meal_type === mealType);

  const columnTemplate = `${ROW_LABEL_WIDTH}px repeat(7, minmax(0, 1fr))`;

  return (
    <Box>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: columnTemplate,
          gap: 1.5,
          mb: 1.5,
        }}
      >
        <Box />
        {days.map(({ dayNum, date, isToday }) => (
          <Box
            key={dayNum}
            sx={{
              textAlign: 'center',
              py: 1,
              borderRadius: 1,
              bgcolor: isToday ? colors.green50 : 'transparent',
            }}
          >
            <Typography
              sx={{
                fontSize: 13,
                fontWeight: 700,
                color: isToday ? colors.green600 : semantic.textPrimary,
                lineHeight: 1.1,
              }}
            >
              {date.format('ddd')}
            </Typography>
            <Typography
              sx={{
                fontSize: 12,
                color: isToday ? colors.green600 : semantic.textMuted,
                lineHeight: 1.3,
              }}
            >
              {date.format('MMM D')}
            </Typography>
          </Box>
        ))}
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {mealTypes.map((type) => (
          <Box
            key={type.value}
            sx={{
              display: 'grid',
              gridTemplateColumns: columnTemplate,
              gap: 1.5,
              alignItems: 'stretch',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                pr: 1.5,
              }}
            >
              <Typography
                sx={{
                  fontSize: 13,
                  fontWeight: 500,
                  color: semantic.textMuted,
                  letterSpacing: '0.02em',
                }}
              >
                {type.label}
              </Typography>
            </Box>
            {days.map(({ dayNum, isToday }) => {
              const meal = findMeal(dayNum, type.value);
              return (
                <MealCell
                  key={dayNum}
                  meal={meal}
                  isToday={isToday}
                  onAdd={() => onAddMeal({ day: dayNum, mealType: type.value })}
                  onEdit={onEditMeal}
                  onDelete={onDeleteMeal}
                />
              );
            })}
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default WeekGrid;
