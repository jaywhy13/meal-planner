import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  Autocomplete,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  ArrowBack,
  Add,
  Edit,
  Delete,
  AutoAwesome,
  Save,
  Settings,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { mealPlansAPI, foodsAPI, dailyMealsAPI, mealSettingsAPI } from '../services/api';
import MealSettings from './MealSettings';

const MealPlanDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [mealPlan, setMealPlan] = useState(null);
  const [dailyMeals, setDailyMeals] = useState([]);
  const [foods, setFoods] = useState([]);
  const [mealSettings, setMealSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingMeal, setEditingMeal] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedWeek, setSelectedWeek] = useState(1);
  const [selectedDay, setSelectedDay] = useState(1);
  const [selectedMealType, setSelectedMealType] = useState('breakfast');
  const [selectedFoods, setSelectedFoods] = useState([]);
  const [notes, setNotes] = useState('');
  const [newFoodName, setNewFoodName] = useState('');
  const [newFoodCategory, setNewFoodCategory] = useState('');
  const [showNewFoodForm, setShowNewFoodForm] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const mealTypes = [
    { value: 'breakfast', label: 'Breakfast' },
    { value: 'lunch', label: 'Lunch' },
    { value: 'dinner', label: 'Dinner' },
    { value: 'snack', label: 'Snack' },
  ];

  const foodCategories = [
    'Protein',
    'Vegetable',
    'Fruit',
    'Grain',
    'Dairy',
    'Other',
  ];

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  useEffect(() => {
    if (id) {
      fetchMealPlan();
      fetchFoods();
    }
  }, [id]);

  useEffect(() => {
    if (mealPlan) {
      fetchDailyMeals();
      fetchMealSettings();
    }
  }, [mealPlan]);

  const fetchMealPlan = async () => {
    try {
      const response = await mealPlansAPI.getById(id);
      setMealPlan(response.data);
    } catch (err) {
      setError('Failed to fetch meal plan');
      console.error('Error fetching meal plan:', err);
    }
  };

  const fetchDailyMeals = async () => {
    try {
      const response = await dailyMealsAPI.getAll(id);
      setDailyMeals(response.data);
    } catch (err) {
      setError('Failed to fetch daily meals');
      console.error('Error fetching daily meals:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMealSettings = async () => {
    try {
      const response = await mealSettingsAPI.getByMealPlan(id);
      if (response.data.length > 0) {
        setMealSettings(response.data[0]);
      }
    } catch (err) {
      console.error('Error fetching meal settings:', err);
    }
  };

  const fetchFoods = async () => {
    try {
      const response = await foodsAPI.getAll();
      setFoods(response.data);
    } catch (err) {
      console.error('Error fetching foods:', err);
    }
  };

  const handleEditMeal = (meal) => {
    setEditingMeal(meal);
    setSelectedWeek(meal.week);
    setSelectedDay(meal.day);
    setSelectedMealType(meal.meal_type);
    setSelectedFoods(meal.foods || []);
    setNotes(meal.notes || '');
    setOpenDialog(true);
  };

  const handleSaveMeal = async () => {
    try {
      const mealData = {
        meal_plan: id,
        week: selectedWeek,
        day: selectedDay,
        meal_type: selectedMealType,
        food_ids: selectedFoods.map(food => food.id),
        notes: notes,
      };

      console.log('Sending meal data:', mealData);

      if (editingMeal) {
        await dailyMealsAPI.update(editingMeal.id, mealData);
      } else {
        await dailyMealsAPI.create(mealData);
      }

      await fetchDailyMeals();
      setOpenDialog(false);
      resetForm();
    } catch (err) {
      setError('Failed to save meal');
      console.error('Error saving meal:', err);
    }
  };

  const handleDeleteMeal = async (mealId) => {
    if (!window.confirm('Are you sure you want to delete this meal?')) return;

    try {
      await dailyMealsAPI.delete(mealId);
      await fetchDailyMeals();
    } catch (err) {
      setError('Failed to delete meal');
      console.error('Error deleting meal:', err);
    }
  };

  const handleGenerateMealPlan = async () => {
    try {
      await mealPlansAPI.generateMealPlan(id);
      await fetchDailyMeals();
    } catch (err) {
      setError('Failed to generate meal plan');
      console.error('Error generating meal plan:', err);
    }
  };

  const handleCreateNewFood = async () => {
    if (!newFoodName.trim()) return;

    try {
      const response = await foodsAPI.create({
        name: newFoodName.trim(),
        category: newFoodCategory || 'Other',
      });
      
      setFoods([...foods, response.data]);
      setSelectedFoods([...selectedFoods, response.data]);
      
      setNewFoodName('');
      setNewFoodCategory('');
      setShowNewFoodForm(false);
    } catch (err) {
      setError('Failed to create new food');
      console.error('Error creating food:', err);
    }
  };

  const resetForm = () => {
    setEditingMeal(null);
    setSelectedWeek(1);
    setSelectedDay(1);
    setSelectedMealType('breakfast');
    setSelectedFoods([]);
    setNotes('');
    setNewFoodName('');
    setNewFoodCategory('');
    setShowNewFoodForm(false);
  };

  const getMealForWeekDay = (week, day, mealType) => {
    return dailyMeals.find(
      meal => meal.week === week && meal.day === day && meal.meal_type === mealType
    );
  };

  const getEnabledMealTypes = () => {
    if (!mealSettings) return mealTypes;
    
    return mealTypes.filter(mealType => {
      const settingKey = `${mealType.value}_enabled`;
      return mealSettings[settingKey] !== false;
    });
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!mealPlan) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">Meal plan not found</Alert>
      </Container>
    );
  }

  const enabledMealTypes = getEnabledMealTypes();

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={() => navigate('/')}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h4" component="h1">
            {mealPlan.name}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => setSettingsOpen(true)}
          >
            Meal Settings
          </Button>
          <Button
            variant="outlined"
            startIcon={<AutoAwesome />}
            onClick={handleGenerateMealPlan}
          >
            Generate Plan
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {
              resetForm();
              setOpenDialog(true);
            }}
          >
            Add Meal
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 4-Week Meal Plan Grid */}
      {[1, 2, 3, 4].map(week => (
        <Card key={week} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Week {week}
            </Typography>
            
            <Grid container spacing={2}>
              {[1, 2, 3, 4, 5].map(day => (
                <Grid item xs={12} sm={6} md={2.4} key={day}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent sx={{ p: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {dayNames[day - 1]}
                      </Typography>
                      
                      {enabledMealTypes.map((mealType) => {
                        const meal = getMealForWeekDay(week, day, mealType.value);
                        return (
                          <Box key={mealType.value} sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              {mealType.label}:
                            </Typography>
                            {meal ? (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Typography variant="caption" sx={{ flexGrow: 1 }}>
                                  {meal.foods?.map(food => food.name).join(', ') || 'No foods'}
                                </Typography>
                                <Tooltip title="Edit">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleEditMeal(meal)}
                                  >
                                    <Edit fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Delete">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleDeleteMeal(meal.id)}
                                  >
                                    <Delete fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            ) : (
                              <Button
                                size="small"
                                variant="text"
                                onClick={() => {
                                  resetForm();
                                  setSelectedWeek(week);
                                  setSelectedDay(day);
                                  setSelectedMealType(mealType.value);
                                  setOpenDialog(true);
                                }}
                              >
                                Add
                              </Button>
                            )}
                          </Box>
                        );
                      })}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      ))}

      {/* Add/Edit Meal Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingMeal ? 'Edit Meal' : 'Add New Meal'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Week</InputLabel>
              <Select
                value={selectedWeek}
                onChange={(e) => setSelectedWeek(e.target.value)}
                label="Week"
              >
                {[1, 2, 3, 4].map(week => (
                  <MenuItem key={week} value={week}>Week {week}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth>
              <InputLabel>Day</InputLabel>
              <Select
                value={selectedDay}
                onChange={(e) => setSelectedDay(e.target.value)}
                label="Day"
              >
                {[1, 2, 3, 4, 5].map(day => (
                  <MenuItem key={day} value={day}>{dayNames[day - 1]}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              select
              label="Meal Type"
              value={selectedMealType}
              onChange={(e) => setSelectedMealType(e.target.value)}
              SelectProps={{ native: true }}
            >
              {mealTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </TextField>

            <Autocomplete
              multiple
              options={foods}
              getOptionLabel={(option) => option.name}
              value={selectedFoods}
              onChange={(event, newValue) => setSelectedFoods(newValue)}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    variant="outlined"
                    label={option.name}
                    {...getTagProps({ index })}
                    key={option.id}
                  />
                ))
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Foods"
                  placeholder="Select foods..."
                />
              )}
            />

            {/* New Food Creation Form */}
            <Box sx={{ border: '1px dashed #ccc', p: 2, borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Add New Food
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <TextField
                  label="Food Name"
                  value={newFoodName}
                  onChange={(e) => setNewFoodName(e.target.value)}
                  size="small"
                  sx={{ flexGrow: 1 }}
                />
                <TextField
                  select
                  label="Category"
                  value={newFoodCategory}
                  onChange={(e) => setNewFoodCategory(e.target.value)}
                  size="small"
                  sx={{ minWidth: 120 }}
                  SelectProps={{ native: true }}
                >
                  <option value="">Select...</option>
                  {foodCategories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </TextField>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleCreateNewFood}
                  disabled={!newFoodName.trim()}
                >
                  Add Food
                </Button>
              </Box>
            </Box>

            <TextField
              label="Notes"
              multiline
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveMeal} variant="contained" startIcon={<Save />}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Meal Settings Dialog */}
      <MealSettings
        mealPlanId={id}
        open={settingsOpen}
        onClose={() => {
          setSettingsOpen(false);
          fetchMealSettings();
        }}
      />
    </Container>
  );
};

export default MealPlanDetail;