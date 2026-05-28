import React, { useState, useEffect, ChangeEvent } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  IconButton,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { Add, Edit, Delete, ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { foodsAPI } from '../services/api';
import { FOOD_CATEGORIES, getCategoryColor } from '../constants/foodCategories';
import type { Food } from '../types';

const FoodsManagement = (): React.ReactElement => {
  const navigate = useNavigate();
  const [foods, setFoods] = useState<Food[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [editingFood, setEditingFood] = useState<Food | null>(null);
  const [foodName, setFoodName] = useState<string>('');
  const [foodCategory, setFoodCategory] = useState<string>('');

  useEffect(() => {
    fetchFoods();
  }, []);

  const fetchFoods = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await foodsAPI.getAll();
      setFoods(response.data);
      setError(null);
    } catch (caughtError) {
      setError('Failed to fetch foods');
      console.error('Error fetching foods:', caughtError);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFood = async (): Promise<void> => {
    if (!foodName.trim()) return;

    try {
      const response = await foodsAPI.create({
        name: foodName.trim(),
        category: foodCategory || 'Other',
      });
      setFoods([...foods, response.data]);
      resetForm();
      setOpenDialog(false);
    } catch (caughtError) {
      setError('Failed to create food');
      console.error('Error creating food:', caughtError);
    }
  };

  const handleUpdateFood = async (): Promise<void> => {
    if (!foodName.trim() || !editingFood) return;

    try {
      const response = await foodsAPI.update(editingFood.id, {
        name: foodName.trim(),
        category: foodCategory || 'Other',
      });
      setFoods(foods.map((food) => (food.id === editingFood.id ? response.data : food)));
      resetForm();
      setOpenDialog(false);
    } catch (caughtError) {
      setError('Failed to update food');
      console.error('Error updating food:', caughtError);
    }
  };

  const handleDeleteFood = async (foodId: number): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this food?')) return;

    try {
      await foodsAPI.delete(foodId);
      setFoods(foods.filter((food) => food.id !== foodId));
    } catch (caughtError) {
      setError('Failed to delete food');
      console.error('Error deleting food:', caughtError);
    }
  };

  const handleEditFood = (food: Food): void => {
    setEditingFood(food);
    setFoodName(food.name);
    setFoodCategory(food.category);
    setOpenDialog(true);
  };

  const resetForm = (): void => {
    setEditingFood(null);
    setFoodName('');
    setFoodCategory('');
  };

  const handleSave = (): void => {
    if (editingFood) {
      handleUpdateFood();
    } else {
      handleCreateFood();
    }
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={() => navigate('/')}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h4" component="h1">
            Foods Management
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            resetForm();
            setOpenDialog(true);
          }}
        >
          Add Food
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {foods.map((food) => (
              <TableRow key={food.id}>
                <TableCell>
                  <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                    {food.name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={food.category}
                    color={getCategoryColor(food.category)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(food.created_at).toLocaleDateString()}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" onClick={() => handleEditFood(food)}>
                    <Edit />
                  </IconButton>
                  <IconButton size="small" color="error" onClick={() => handleDeleteFood(food.id)}>
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {foods.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No foods yet. Add your first food!
          </Typography>
        </Box>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingFood ? 'Edit Food' : 'Add New Food'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Food Name"
              value={foodName}
              onChange={(event: ChangeEvent<HTMLInputElement>) => setFoodName(event.target.value)}
              fullWidth
              required
            />

            <TextField
              select
              label="Category"
              value={foodCategory}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                setFoodCategory(event.target.value)
              }
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="">Select a category...</option>
              {FOOD_CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" disabled={!foodName.trim()}>
            {editingFood ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FoodsManagement;
