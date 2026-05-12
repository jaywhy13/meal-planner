import React from 'react';
import { Box, Typography } from '@mui/material';
import { semantic } from '../theme/tokens';

const MealSettingsPlaceholder = () => (
  <Box sx={{ p: 6 }}>
    <Typography variant="h1" sx={{ mb: 2 }}>
      Meal Settings
    </Typography>
    <Typography sx={{ color: semantic.textSecondary }}>
      Global meal settings are coming soon. For now, settings live inside each
      meal plan.
    </Typography>
  </Box>
);

export default MealSettingsPlaceholder;
