import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Add, Edit, Delete, CalendarToday } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { mealPlansAPI } from '../services/api';

const MealPlansList = () => {
  const [mealPlans, setMealPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newMealPlanName, setNewMealPlanName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMealPlans();
  }, []);

  const fetchMealPlans = async () => {
    try {
      setLoading(true);
      const response = await mealPlansAPI.getAll();
      setMealPlans(response.data);
      setError(null);
    } catch (err) {
      if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to backend. Please make sure the backend is running on port 8000. Try running: docker-compose up --build');
      } else {
        setError('Failed to fetch meal plans: ' + (err.response?.data?.detail || err.message));
      }
      console.error('Error fetching meal plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMealPlan = async () => {
    if (!newMealPlanName.trim()) return;

    try {
      const response = await mealPlansAPI.create({ name: newMealPlanName });
      setMealPlans([...mealPlans, response.data]);
      setNewMealPlanName('');
      setOpenDialog(false);
    } catch (err) {
      setError('Failed to create meal plan');
      console.error('Error creating meal plan:', err);
    }
  };

  const handleDeleteMealPlan = async (id) => {
    if (!window.confirm('Are you sure you want to delete this meal plan?')) return;

    try {
      await mealPlansAPI.delete(id);
      setMealPlans(mealPlans.filter(plan => plan.id !== id));
    } catch (err) {
      setError('Failed to delete meal plan');
      console.error('Error deleting meal plan:', err);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Meal Plans
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
        >
          New Meal Plan
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {mealPlans.map((mealPlan) => (
          <Grid item xs={12} sm={6} md={4} key={mealPlan.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {mealPlan.name}
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  Created: {formatDate(mealPlan.created_at)}
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  Updated: {formatDate(mealPlan.updated_at)}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  startIcon={<CalendarToday />}
                  onClick={() => navigate(`/meal-plan/${mealPlan.id}`)}
                >
                  View
                </Button>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => navigate(`/meal-plan/${mealPlan.id}`)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDeleteMealPlan(mealPlan.id)}
                >
                  Delete
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {mealPlans.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No meal plans yet. Create your first one!
          </Typography>
        </Box>
      )}

      {/* Create Meal Plan Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Create New Meal Plan</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Meal Plan Name"
            fullWidth
            variant="outlined"
            value={newMealPlanName}
            onChange={(e) => setNewMealPlanName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleCreateMealPlan();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateMealPlan} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MealPlansList;
