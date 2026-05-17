import React from 'react';
import { Box, Typography } from '@mui/material';
import dayjs from 'dayjs';
import { colors, semantic, radius } from '../../theme/tokens';
import { getEmojiForFoods } from '../../constants/foodEmojis';

const PILL_COLORS = {
  breakfast: colors.yellow100,
  lunch: colors.green100,
  dinner: '#EDE9FE',
  snack: '#FCE7F3',
};

const DAY_COL = 80;
const WEEK_LABEL_COL = 32;

const FoodPill = ({ food, mealType, onClick }) => (
  <Box
    role="button"
    tabIndex={0}
    onClick={onClick}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') onClick();
    }}
    sx={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 0.5,
      px: 1.25,
      py: 0.4,
      borderRadius: `${radius.full}px`,
      bgcolor: PILL_COLORS[mealType] || colors.gray100,
      cursor: 'pointer',
      fontSize: 13,
      fontWeight: 500,
      color: semantic.textPrimary,
      whiteSpace: 'nowrap',
      transition: 'opacity 120ms',
      '&:hover': { opacity: 0.72 },
    }}
  >
    <Box component="span" sx={{ fontSize: 14, lineHeight: 1 }}>
      {getEmojiForFoods([food])}
    </Box>
    <Box component="span">{food.name}</Box>
  </Box>
);

const EmptySlot = ({ onClick, canAdd }) =>
  canAdd ? (
    <Box
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') onClick();
      }}
      sx={{
        color: semantic.textMuted,
        fontSize: 18,
        lineHeight: 1,
        cursor: 'pointer',
        userSelect: 'none',
        '&:hover': { color: colors.green500 },
      }}
    >
      —
    </Box>
  ) : (
    <Box sx={{ color: semantic.textMuted, fontSize: 18, lineHeight: 1, userSelect: 'none' }}>—</Box>
  );

const WeekList = ({ anchor, currentMonth, mealTypes, meals, onAddMeal, onEditMeal }) => {
  const today = dayjs().startOf('day');

  // Find Monday on or before the first of the month
  const monthStart = currentMonth.startOf('month');
  const monthEnd = currentMonth.endOf('month');

  const startDayOfWeek = monthStart.day(); // 0=Sun, 1=Mon, …, 6=Sat
  const daysBackToMonday = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1;
  const firstMonday = monthStart.subtract(daysBackToMonday, 'day');

  // Find Sunday on or after the last day of the month
  const endDayOfWeek = monthEnd.day();
  const daysForwardToSunday = endDayOfWeek === 0 ? 0 : 7 - endDayOfWeek;
  const lastSunday = monthEnd.add(daysForwardToSunday, 'day');

  // Build Mon–Sun week groups that overlap the month
  const weekGroups = [];
  let cursor = firstMonday;

  while (cursor.valueOf() <= lastSunday.valueOf()) {
    const weekMonday = cursor;
    const weekSunday = cursor.add(6, 'day');

    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = cursor.add(i, 'day');
      const daysFromAnchor = date.diff(anchor, 'day');
      let weekNum = null;
      let dayNum = null;

      if (daysFromAnchor >= 0) {
        weekNum = Math.floor(daysFromAnchor / 7) + 1;
        dayNum = (daysFromAnchor % 7) + 1;
      }

      days.push({
        date,
        weekNum,
        dayNum,
        isToday: date.isSame(today, 'day'),
        inMonth: date.isSame(currentMonth, 'month'),
      });
    }

    weekGroups.push({
      monday: weekMonday,
      sunday: weekSunday,
      label: `${weekMonday.format('MMM D')} – ${weekSunday.format('MMM D')}`,
      days,
    });

    cursor = cursor.add(7, 'day');
  }

  const findMeal = (weekNum, dayNum, mealType) => {
    if (weekNum == null || dayNum == null) return null;
    return meals.find((m) => m.week === weekNum && m.day === dayNum && m.meal_type === mealType) || null;
  };

  const colTemplate = `${DAY_COL}px repeat(${mealTypes.length}, 1fr)`;

  return (
    <Box>
      {/* Column headers */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: `${WEEK_LABEL_COL + DAY_COL}px repeat(${mealTypes.length}, 1fr)`,
          mb: 0.5,
        }}
      >
        <Box />
        {mealTypes.map((type) => (
          <Box key={type.value} sx={{ px: 2 }}>
            <Typography
              sx={{
                fontSize: 10,
                fontWeight: 600,
                color: semantic.textMuted,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              {type.label}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Week groups */}
      {weekGroups.map((group) => (
        <Box key={group.monday.valueOf()} sx={{ display: 'flex', mb: 2 }}>
          {/* Vertical week range label */}
          <Box
            sx={{
              width: WEEK_LABEL_COL,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography
              sx={{
                fontSize: 10,
                fontWeight: 500,
                color: semantic.textMuted,
                writingMode: 'vertical-rl',
                transform: 'rotate(180deg)',
                whiteSpace: 'nowrap',
              }}
            >
              {group.label}
            </Typography>
          </Box>

          {/* Day rows */}
          <Box
            sx={{
              flex: 1,
              border: `1px solid ${semantic.borderDefault}`,
              borderRadius: `${radius.r12}px`,
              overflow: 'hidden',
              bgcolor: semantic.bgCard,
            }}
          >
            {group.days.map((day, dayIndex) => (
              <Box
                key={day.date.valueOf()}
                sx={{
                  display: 'grid',
                  gridTemplateColumns: colTemplate,
                  borderLeft: day.isToday ? `3px solid ${colors.green500}` : 'none',
                  bgcolor: day.isToday ? colors.green50 : !day.inMonth ? colors.gray50 : 'transparent',
                  borderBottom:
                    dayIndex < group.days.length - 1
                      ? `1px solid ${semantic.borderDefault}`
                      : 'none',
                  minHeight: 56,
                  alignItems: 'center',
                }}
              >
                {/* Day number + abbreviated name */}
                <Box sx={{ px: 2, py: 1.5 }}>
                  <Typography
                    sx={{
                      fontSize: 26,
                      fontWeight: 700,
                      lineHeight: 1,
                      color: day.isToday
                        ? colors.green500
                        : !day.inMonth
                        ? semantic.textMuted
                        : semantic.textPrimary,
                    }}
                  >
                    {day.date.format('D')}
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: 10,
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                      color: day.isToday ? colors.green600 : semantic.textMuted,
                    }}
                  >
                    {day.date.format('ddd')}
                  </Typography>
                </Box>

                {/* Meal type cells */}
                {mealTypes.map((type) => {
                  const meal = findMeal(day.weekNum, day.dayNum, type.value);
                  const hasFoods = meal && meal.foods && meal.foods.length > 0;

                  return (
                    <Box
                      key={type.value}
                      sx={{
                        px: 1.5,
                        py: 1,
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 0.5,
                        alignItems: 'center',
                      }}
                    >
                      {hasFoods ? (
                        meal.foods.map((food) => (
                          <FoodPill
                            key={food.id}
                            food={food}
                            mealType={type.value}
                            onClick={() => onEditMeal(meal)}
                          />
                        ))
                      ) : meal ? (
                        <EmptySlot onClick={() => onEditMeal(meal)} canAdd />
                      ) : (
                        <EmptySlot
                          onClick={() =>
                            onAddMeal({ day: day.dayNum, mealType: type.value, week: day.weekNum })
                          }
                          canAdd={day.weekNum != null}
                        />
                      )}
                    </Box>
                  );
                })}
              </Box>
            ))}
          </Box>
        </Box>
      ))}
    </Box>
  );
};

export default WeekList;
