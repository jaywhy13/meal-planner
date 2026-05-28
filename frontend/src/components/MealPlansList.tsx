import React, { useState, useEffect, ChangeEvent, KeyboardEvent } from 'react';
import { AxiosError } from 'axios';
import {
  Box,
  Typography,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { mealPlansAPI } from '../services/api';
import { semantic, shadows } from '../theme/tokens';
import DashboardEmptyState from './dashboard/DashboardEmptyState';
import MealPlanCard from './dashboard/MealPlanCard';
import type { MealPlanSummary } from '../types';

interface ApiErrorBody {
  detail?: string;
}

const MealPlansList = (): React.ReactElement => {
  const [mealPlans, setMealPlans] = useState<MealPlanSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [newMealPlanName, setNewMealPlanName] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMealPlans();
  }, []);

  const fetchMealPlans = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await mealPlansAPI.getAll();
      setMealPlans(response.data);
      setError(null);
    } catch (caughtError) {
      const axiosError = caughtError as AxiosError<ApiErrorBody>;
      if (axiosError.code === 'ECONNREFUSED' || axiosError.message.includes('Network Error')) {
        setError(
          'Cannot connect to backend. Please make sure the backend is running on port 8000.'
        );
      } else {
        setError(
          'Failed to fetch meal plans: ' + (axiosError.response?.data?.detail || axiosError.message)
        );
      }
      console.error('Error fetching meal plans:', caughtError);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMealPlan = async (): Promise<void> => {
    if (!newMealPlanName.trim()) return;

    try {
      const response = await mealPlansAPI.create({ name: newMealPlanName });
      setMealPlans([...mealPlans, response.data]);
      setNewMealPlanName('');
      setOpenDialog(false);
    } catch (caughtError) {
      setError('Failed to create meal plan');
      console.error('Error creating meal plan:', caughtError);
    }
  };

  const handleDeleteMealPlan = async (plan: MealPlanSummary): Promise<void> => {
    if (!window.confirm(`Delete "${plan.name}"? This cannot be undone.`)) return;
    try {
      await mealPlansAPI.delete(plan.id);
      setMealPlans(mealPlans.filter((existing) => existing.id !== plan.id));
    } catch (caughtError) {
      setError('Failed to delete meal plan');
      console.error('Error deleting meal plan:', caughtError);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ px: { xs: 3, md: 5 }, py: { xs: 3, md: 4 }, minHeight: '100vh' }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography variant="h1" sx={{ color: semantic.textPrimary }}>
          Meal Plans
        </Typography>
        {mealPlans.length > 0 && (
          <Button
            variant="contained"
            color="primary"
            onClick={() => setOpenDialog(true)}
            sx={{
              px: 3,
              py: 1.25,
              fontSize: 14,
              boxShadow: shadows.buttonGlow,
              '&:hover': { boxShadow: shadows.buttonGlow },
            }}
          >
            + New Plan
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {mealPlans.length === 0 ? (
        <DashboardEmptyState onCreate={() => setOpenDialog(true)} />
      ) : (
        <Grid container spacing={3}>
          {mealPlans.map((plan) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={plan.id}>
              <MealPlanCard
                plan={plan}
                onView={(selected) => navigate(`/meal-plan/${selected.id}`)}
                onDelete={handleDeleteMealPlan}
              />
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Create New Meal Plan</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Meal Plan Name"
            fullWidth
            variant="outlined"
            value={newMealPlanName}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              setNewMealPlanName(event.target.value)
            }
            onKeyPress={(event: KeyboardEvent<HTMLDivElement>) => {
              if (event.key === 'Enter') handleCreateMealPlan();
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateMealPlan} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MealPlansList;
