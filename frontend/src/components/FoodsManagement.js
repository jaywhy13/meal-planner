import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
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
import {
  Add,
  Edit,
  Delete,
  ArrowBack,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { foodsAPI } from '../services/api';

const FoodsManagement = () => {
  const navigate = useNavigate();
  const [foods, setFoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingFood, setEditingFood] = useState(null);
  const [foodName, setFoodName] = useState('');
  const [foodCategory, setFoodCategory] = useState('');

  const foodCategories = [
    'Protein',
    'Vegetable',
    'Fruit',
    'Grain',
    'Dairy',
    'Other',
  ];

  useEffect(() => {
    fetchFoods();
  }, []);

  const fetchFoods = async () => {
    try {
      setLoading(true);
      const response = await foodsAPI.getAll();
      setFoods(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch foods');
      console.error('Error fetching foods:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFood = async () => {
    if (!foodName.trim()) return;

    try {
      const response = await foodsAPI.create({
        name: foodName.trim(),
        category: foodCategory || 'Other',
      });
      setFoods([...foods, response.data]);
      resetForm();
      setOpenDialog(false);
    } catch (err) {
      setError('Failed to create food');
      console.error('Error creating food:', err);
    }
  };

  const handleUpdateFood = async () => {
    if (!foodName.trim() || !editingFood) return;

    try {
      const response = await foodsAPI.update(editingFood.id, {
        name: foodName.trim(),
        category: foodCategory || 'Other',
      });
      setFoods(foods.map(food => 
        food.id === editingFood.id ? response.data : food
      ));
      resetForm();
      setOpenDialog(false);
    } catch (err) {
      setError('Failed to update food');
      console.error('Error updating food:', err);
    }
  };

  const handleDeleteFood = async (foodId) => {
    if (!window.confirm('Are you sure you want to delete this food?')) return;

    try {
      await foodsAPI.delete(foodId);
      setFoods(foods.filter(food => food.id !== foodId));
    } catch (err) {
      setError('Failed to delete food');
      console.error('Error deleting food:', err);
    }
  };

  const handleEditFood = (food) => {
    setEditingFood(food);
    setFoodName(food.name);
    setFoodCategory(food.category);
    setOpenDialog(true);
  };

  const resetForm = () => {
    setEditingFood(null);
    setFoodName('');
    setFoodCategory('');
  };

  const handleSave = () => {
    if (editingFood) {
      handleUpdateFood();
    } else {
      handleCreateFood();
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Protein': 'primary',
      'Vegetable': 'success',
      'Fruit': 'warning',
      'Grain': 'info',
      'Dairy': 'secondary',
      'Other': 'default',
    };
    return colors[category] || 'default';
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

      {/* Foods Table */}
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
                <TableCell>
                  {new Date(food.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleEditFood(food)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDeleteFood(food.id)}
                  >
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

      {/* Add/Edit Food Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingFood ? 'Edit Food' : 'Add New Food'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Food Name"
              value={foodName}
              onChange={(e) => setFoodName(e.target.value)}
              fullWidth
              required
            />
            
            <TextField
              select
              label="Category"
              value={foodCategory}
              onChange={(e) => setFoodCategory(e.target.value)}
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="">Select a category...</option>
              {foodCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleSave} 
            variant="contained"
            disabled={!foodName.trim()}
          >
            {editingFood ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FoodsManagement;
