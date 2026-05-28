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
import { mealSettingsAPI, CreateMealSettingsInput } from '../services/api';
import type { MealSettings as MealSettingsData, MealType } from '../types';

type MealSettingsDraft = Partial<MealSettingsData>;

interface MealSettingsProps {
  mealPlanId: number;
  open: boolean;
  onClose: () => void;
}

interface MealTypeOption {
  key: MealType;
  label: string;
}

const MEAL_TYPE_OPTIONS: MealTypeOption[] = [
  { key: 'breakfast', label: 'Breakfast' },
  { key: 'lunch', label: 'Lunch' },
  { key: 'dinner', label: 'Dinner' },
  { key: 'snack', label: 'Snack' },
];

const buildDefaultCreateInput = (mealPlanId: number): CreateMealSettingsInput => ({
  meal_plan: mealPlanId,
  breakfast_enabled: true,
  lunch_enabled: true,
  dinner_enabled: true,
  snack_enabled: true,
});

const MealSettings = ({ mealPlanId, open, onClose }: MealSettingsProps): React.ReactElement => {
  const [mealSettings, setMealSettings] = useState<MealSettingsDraft | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && mealPlanId) {
      fetchMealSettings();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, mealPlanId]);

  const fetchMealSettings = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      const response = await mealSettingsAPI.getByMealPlan(mealPlanId);

      if (response.data.length > 0) {
        setMealSettings(response.data[0]);
      } else {
        const createResponse = await mealSettingsAPI.create(buildDefaultCreateInput(mealPlanId));
        setMealSettings(createResponse.data);
      }
    } catch (caughtError) {
      console.error('Error fetching meal settings:', caughtError);
      setError('Failed to load meal settings');
      setMealSettings(buildDefaultCreateInput(mealPlanId));
    } finally {
      setLoading(false);
    }
  };

  const handleToggleMealType = (mealType: MealType): void => {
    setMealSettings((previous) => {
      if (!previous) return previous;
      const enabledKey = `${mealType}_enabled` as keyof MealSettingsDraft;
      return {
        ...previous,
        [enabledKey]: !previous[enabledKey],
      };
    });
  };

  const handleSave = async (): Promise<void> => {
    if (!mealSettings) return;
    try {
      setSaving(true);
      setError(null);

      if (mealSettings.id) {
        await mealSettingsAPI.update(mealSettings.id, mealSettings);
      } else {
        await mealSettingsAPI.create({ ...mealSettings, meal_plan: mealPlanId });
      }

      onClose();
    } catch (caughtError) {
      console.error('Error saving meal settings:', caughtError);
      setError('Failed to save meal settings');
    } finally {
      setSaving(false);
    }
  };

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
            Choose which meal types you want to include in your meal plan. Disabled meal types will
            not appear in the meal plan.
          </Typography>

          {mealSettings &&
            MEAL_TYPE_OPTIONS.map((mealType) => {
              const enabledKey = `${mealType.key}_enabled` as keyof MealSettingsDraft;
              return (
                <FormControlLabel
                  key={mealType.key}
                  control={
                    <Switch
                      checked={Boolean(mealSettings[enabledKey])}
                      onChange={() => handleToggleMealType(mealType.key)}
                      color="primary"
                    />
                  }
                  label={mealType.label}
                  sx={{ display: 'block', mb: 1 }}
                />
              );
            })}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button onClick={handleSave} variant="contained" disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MealSettings;
