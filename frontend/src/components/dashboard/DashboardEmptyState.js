import React from 'react';
import { Box, Typography, Button, Chip, Card } from '@mui/material';
import { RestaurantMenu } from '@mui/icons-material';
import { colors, semantic, shadows } from '../../theme/tokens';

const CATEGORY_CHIPS = [
  { label: '🥗 Salads', bg: colors.green100, fg: colors.green600 },
  { label: '🍳 Breakfast', bg: colors.yellow100, fg: '#92400E' },
  { label: '🍝 Dinners', bg: '#FFEDD5', fg: '#9A3412' },
  { label: '🥤 Smoothies', bg: '#DBEAFE', fg: '#1E40AF' },
];

const DashboardEmptyState = ({ onCreate }) => (
  <Box
    sx={{
      flex: 1,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      px: 4,
      py: 6,
    }}
  >
    <Card
      sx={{
        maxWidth: 640,
        width: '100%',
        px: { xs: 4, sm: 8 },
        py: { xs: 5, sm: 7 },
        textAlign: 'center',
        boxShadow: shadows.cardLift,
      }}
    >
      <Box
        sx={{
          width: 100,
          height: 100,
          borderRadius: '50%',
          bgcolor: colors.green500,
          color: colors.white,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mx: 'auto',
          mb: 3,
          boxShadow: shadows.ctaGlow,
          '& svg': { fontSize: 44 },
        }}
      >
        <RestaurantMenu />
      </Box>

      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 1,
          mb: 3,
        }}
      >
        {CATEGORY_CHIPS.map((c) => (
          <Chip
            key={c.label}
            label={c.label}
            sx={{
              bgcolor: c.bg,
              color: c.fg,
              fontWeight: 600,
              fontSize: 13,
              height: 28,
            }}
          />
        ))}
      </Box>

      <Typography variant="h2" sx={{ mb: 1.5, color: semantic.textPrimary }}>
        Your meal planning adventure starts here!
      </Typography>
      <Typography
        variant="body1"
        sx={{ color: semantic.textSecondary, mb: 4, maxWidth: 440, mx: 'auto' }}
      >
        Plan your family's meals for the week, discover new recipes, and make grocery shopping a
        breeze. Let's get started!
      </Typography>

      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={onCreate}
        sx={{
          px: 4,
          py: 1.5,
          fontSize: 15,
          boxShadow: shadows.ctaGlow,
          '&:hover': { boxShadow: shadows.ctaGlow },
        }}
      >
        + Create My First Meal Plan
      </Button>

      <Typography sx={{ mt: 3, fontSize: 12, color: semantic.textMuted }}>
        ✨ Tip: You can plan up to 7 days at once and reuse plans from previous weeks.
      </Typography>
    </Card>
  </Box>
);

export default DashboardEmptyState;
