import React, { useState } from 'react';
import { Box, Typography, IconButton, Menu, MenuItem } from '@mui/material';
import { MoreVert, Edit, Delete } from '@mui/icons-material';
import { colors, semantic, radius, shadows } from '../../theme/tokens';
import { getEmojiForFoods } from '../../constants/foodEmojis';

const CELL_HEIGHT = 132;

const summarize = (foods) => {
  if (!foods || foods.length === 0) return '';
  if (foods.length === 1) return foods[0].name;
  if (foods.length === 2) return `${foods[0].name} & ${foods[1].name}`;
  return `${foods[0].name} & ${foods.length - 1} more`;
};

const EmptyCell = ({ onAdd, isToday }) => (
  <Box
    role="button"
    tabIndex={0}
    onClick={onAdd}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') onAdd();
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

const FilledCell = ({ meal, onEdit, onDelete, isToday }) => {
  const [menuAnchor, setMenuAnchor] = useState(null);
  const emoji = getEmojiForFoods(meal.foods);
  const label = summarize(meal.foods) || '(empty)';

  return (
    <Box
      sx={{
        position: 'relative',
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
          '& .meal-cell-menu': { opacity: 1 },
        },
      }}
      onClick={(e) => {
        if (menuAnchor) return;
        if (e.target.closest('.meal-cell-menu')) return;
        onEdit(meal);
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

      <IconButton
        className="meal-cell-menu"
        size="small"
        onClick={(e) => {
          e.stopPropagation();
          setMenuAnchor(e.currentTarget);
        }}
        sx={{
          position: 'absolute',
          top: 4,
          right: 4,
          opacity: menuAnchor ? 1 : 0,
          transition: 'opacity 120ms ease',
        }}
        aria-label="Meal options"
      >
        <MoreVert fontSize="small" />
      </IconButton>
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
        onClick={(e) => e.stopPropagation()}
      >
        <MenuItem
          onClick={() => {
            setMenuAnchor(null);
            onEdit(meal);
          }}
        >
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem
          onClick={() => {
            setMenuAnchor(null);
            onDelete(meal);
          }}
          sx={{ color: 'error.main' }}
        >
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

const MealCell = ({ meal, onAdd, onEdit, onDelete, isToday }) =>
  meal ? (
    <FilledCell meal={meal} onEdit={onEdit} onDelete={onDelete} isToday={isToday} />
  ) : (
    <EmptyCell onAdd={onAdd} isToday={isToday} />
  );

export default MealCell;
