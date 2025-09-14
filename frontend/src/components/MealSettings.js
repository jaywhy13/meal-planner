import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControlLabel,
  Switch,
  Box,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Settings } from '@mui/icons-material';
import { mealSettingsAPI } from '../services/api';

const MealSettings = ({ mealPlanId, open, onClose }) => {
  const [mealSettings, setMealSettings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open && mealPlanId) {
      fetchMealSettings();
    }
  }, [open, mealPlanId]);

  const fetchMealSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get existing settings
      const response = await mealSettingsAPI.getByMealPlan(mealPlanId);
      
      if (response.data.length > 0) {
        setMealSettings(response.data[0]);
      } else {
        // Create default settings if none exist
        const defaultSettings = {
          meal_plan: mealPlanId,
          breakfast_enabled: true,
          lunch_enabled: true,
          dinner_enabled: true,
          snack_enabled: true,
        };
        
        const createResponse = await mealSettingsAPI.create(defaultSettings);
        setMealSettings(createResponse.data);
      }
    } catch (err) {
      console.error('Error fetching meal settings:', err);
      setError('Failed to load meal settings');
      
      // Create default settings on error
      const defaultSettings = {
        meal_plan: mealPlanId,
        breakfast_enabled: true,
        lunch_enabled: true,
        dinner_enabled: true,
        snack_enabled: true,
      };
      setMealSettings(defaultSettings);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleMealType = (mealType) => {
    setMealSettings(prev => ({
      ...prev,
      [`${mealType}_enabled`]: !prev[`${mealType}_enabled`]
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      if (mealSettings.id) {
        await mealSettingsAPI.update(mealSettings.id, mealSettings);
      } else {
        await mealSettingsAPI.create(mealSettings);
      }
      
      onClose();
    } catch (err) {
      console.error('Error saving meal settings:', err);
      setError('Failed to save meal settings');
    } finally {
      setSaving(false);
    }
  };

  const mealTypes = [
    { key: 'breakfast', label: 'Breakfast' },
    { key: 'lunch', label: 'Lunch' },
    { key: 'dinner', label: 'Dinner' },
    { key: 'snack', label: 'Snack' },
  ];

  if (loading) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogContent sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Settings />
        Meal Settings
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Enable/Disable Meal Types
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Choose which meal types you want to include in your meal plan. 
            Disabled meal types will not appear in the meal plan.
          </Typography>
          
          {mealSettings && mealTypes.map((mealType) => (
            <FormControlLabel
              key={mealType.key}
              control={
                <Switch
                  checked={mealSettings[`${mealType.key}_enabled`]}
                  onChange={() => handleToggleMealType(mealType.key)}
                  color="primary"
                />
              }
              label={mealType.label}
              sx={{ display: 'block', mb: 1 }}
            />
          ))}
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MealSettings;
