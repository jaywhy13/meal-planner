import React, { useState } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { RestaurantMenu, MoreVert, Delete } from '@mui/icons-material';
import { colors, semantic, radius, shadows } from '../../theme/tokens';

const GRADIENTS = [
  'linear-gradient(135deg, #4ADE80 0%, #22C55E 100%)',
  'linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%)',
  'linear-gradient(135deg, #FB923C 0%, #F97316 100%)',
  'linear-gradient(135deg, #F472B6 0%, #EC4899 100%)',
];

const pickGradient = (id) => GRADIENTS[Math.abs(id) % GRADIENTS.length];

const formatDate = (iso) =>
  new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });

const MealPlanCard = ({ plan, onView, onDelete }) => {
  const [menuAnchor, setMenuAnchor] = useState(null);
  const gradient = pickGradient(plan.id);

  const handleDelete = () => {
    setMenuAnchor(null);
    onDelete(plan);
  };

  return (
    <Card
      sx={{
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: shadows.cardLift,
        transition: 'transform 160ms ease, box-shadow 160ms ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 28px rgba(17, 24, 39, 0.10)',
        },
      }}
    >
      <Box
        sx={{
          position: 'relative',
          height: 120,
          background: gradient,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Box
          sx={{
            color: 'rgba(255,255,255,0.95)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            '& svg': { fontSize: 40 },
          }}
        >
          <RestaurantMenu />
        </Box>
        <IconButton
          size="small"
          onClick={(e) => setMenuAnchor(e.currentTarget)}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            color: colors.white,
            bgcolor: 'rgba(255,255,255,0.18)',
            '&:hover': { bgcolor: 'rgba(255,255,255,0.30)' },
          }}
          aria-label="Card options"
        >
          <MoreVert fontSize="small" />
        </IconButton>
        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={() => setMenuAnchor(null)}
        >
          <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
            <Delete fontSize="small" sx={{ mr: 1 }} />
            Delete
          </MenuItem>
        </Menu>
      </Box>

      <Box sx={{ p: 2.5, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        <Typography
          sx={{
            fontSize: 18,
            fontWeight: 700,
            color: semantic.textPrimary,
            lineHeight: 1.3,
          }}
        >
          {plan.name}
        </Typography>
        <Typography sx={{ fontSize: 13, color: semantic.textMuted }}>
          Created {formatDate(plan.created_at)}
        </Typography>

        <Button
          fullWidth
          onClick={() => onView(plan)}
          sx={{
            mt: 1,
            bgcolor: colors.green50,
            color: colors.green600,
            borderRadius: `${radius.r12}px`,
            py: 1.25,
            fontWeight: 600,
            '&:hover': { bgcolor: colors.green100 },
          }}
        >
          View →
        </Button>
      </Box>
    </Card>
  );
};

export default MealPlanCard;
