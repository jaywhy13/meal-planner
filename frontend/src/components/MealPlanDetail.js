import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Autocomplete,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { AutoAwesome, Settings, Save, Delete } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { mealPlansAPI, foodsAPI, dailyMealsAPI, mealSettingsAPI } from '../services/api';
import MealSettings from './MealSettings';
import { FOOD_CATEGORIES } from '../constants/foodCategories';
import { colors, semantic, shadows } from '../theme/tokens';
import DateRangeBar from './mealPlanDetail/DateRangeBar';
import WeekGrid from './mealPlanDetail/WeekGrid';

const MEAL_TYPES = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'snack', label: 'Snack' },
];

const MealPlanDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [mealPlan, setMealPlan] = useState(null);
  const [dailyMeals, setDailyMeals] = useState([]);
  const [foods, setFoods] = useState([]);
  const [mealSettings, setMealSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingMeal, setEditingMeal] = useState(null);
  const [currentWeek, setCurrentWeek] = useState(1);
  const [selectedDay, setSelectedDay] = useState(1);
  const [selectedMealType, setSelectedMealType] = useState('breakfast');
  const [selectedFoods, setSelectedFoods] = useState([]);
  const [notes, setNotes] = useState('');
  const [newFoodName, setNewFoodName] = useState('');
  const [newFoodCategory, setNewFoodCategory] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    if (id) {
      fetchMealPlan();
      fetchFoods();
    }
    // fetchMealPlan and fetchFoods are stable; adding them would cause infinite loops
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    if (mealPlan) {
      fetchDailyMeals();
      fetchMealSettings();
      // Open on the week containing today, so users land on what's current
      // instead of always starting at Week 1 of the plan's anchor date.
      const planMonday = dayjs(mealPlan.created_at).startOf('week').add(1, 'day');
      const daysSinceStart = dayjs().startOf('day').diff(planMonday, 'day');
      setCurrentWeek(Math.max(1, Math.floor(daysSinceStart / 7) + 1));
    }
    // fetchDailyMeals and fetchMealSettings are stable; adding them would cause infinite loops
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mealPlan]);

  const fetchMealPlan = async () => {
    try {
      const response = await mealPlansAPI.getById(id);
      setMealPlan(response.data);
    } catch (err) {
      setError('Failed to fetch meal plan');
    }
  };

  const fetchDailyMeals = async () => {
    try {
      const response = await dailyMealsAPI.getAll(id);
      setDailyMeals(response.data);
    } catch (err) {
      setError('Failed to fetch daily meals');
    } finally {
      setLoading(false);
    }
  };

  const fetchMealSettings = async () => {
    try {
      const response = await mealSettingsAPI.getByMealPlan(id);
      if (response.data.length > 0) setMealSettings(response.data[0]);
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

  // Anchor Week 1 to the Monday of the week the plan was created.
  // dayjs treats Sunday as the start of the week, so we shift +1 day.
  const anchor = mealPlan ? dayjs(mealPlan.created_at) : dayjs();
  const week1Start = anchor.startOf('week').add(1, 'day');
  const weekStart = week1Start.add((currentWeek - 1) * 7, 'day');
  const weekEnd = weekStart.add(6, 'day');
  const rangeLabel = `${weekStart.format('MMM D')} – ${weekEnd.format('MMM D, YYYY')}`;

  const enabledMealTypes = mealSettings
    ? MEAL_TYPES.filter((t) => mealSettings[`${t.value}_enabled`] !== false)
    : MEAL_TYPES;

  const mealsForCurrentWeek = dailyMeals.filter((m) => m.week === currentWeek);

  const openAddDialog = ({ day, mealType }) => {
    setEditingMeal(null);
    setSelectedDay(day);
    setSelectedMealType(mealType);
    setSelectedFoods([]);
    setNotes('');
    setNewFoodName('');
    setNewFoodCategory('');
    setOpenDialog(true);
  };

  const openEditDialog = (meal) => {
    setEditingMeal(meal);
    setSelectedDay(meal.day);
    setSelectedMealType(meal.meal_type);
    setSelectedFoods(meal.foods || []);
    setNotes(meal.notes || '');
    setNewFoodName('');
    setNewFoodCategory('');
    setOpenDialog(true);
  };

  const openAddDialogTopLevel = () => {
    setEditingMeal(null);
    setSelectedDay(1);
    setSelectedMealType('breakfast');
    setSelectedFoods([]);
    setNotes('');
    setNewFoodName('');
    setNewFoodCategory('');
    setOpenDialog(true);
  };

  const handleSaveMeal = async () => {
    try {
      const mealData = {
        meal_plan: id,
        week: currentWeek,
        day: selectedDay,
        meal_type: selectedMealType,
        food_ids: selectedFoods.map((food) => food.id),
        notes,
      };
      if (editingMeal) {
        await dailyMealsAPI.update(editingMeal.id, mealData);
      } else {
        await dailyMealsAPI.create(mealData);
      }
      await fetchDailyMeals();
      setOpenDialog(false);
    } catch (err) {
      setError('Failed to save meal');
    }
  };

  const handleDeleteMeal = async () => {
    if (!editingMeal) return;
    if (!window.confirm('Delete this meal?')) return;
    try {
      await dailyMealsAPI.delete(editingMeal.id);
      await fetchDailyMeals();
      setOpenDialog(false);
    } catch (err) {
      setError('Failed to delete meal');
    }
  };

  const handleGenerateMealPlan = async () => {
    try {
      await mealPlansAPI.generateMealPlan(id);
      await fetchDailyMeals();
    } catch (err) {
      setError('Failed to generate meal plan');
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
    } catch (err) {
      setError('Failed to create new food');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!mealPlan) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">Meal plan not found</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ px: { xs: 3, md: 5 }, py: { xs: 3, md: 4 }, minHeight: '100vh' }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-end',
          mb: 3,
          gap: 2,
          flexWrap: 'wrap',
        }}
      >
        <Box sx={{ minWidth: 0 }}>
          <Box
            role="button"
            tabIndex={0}
            onClick={() => navigate('/')}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/');
            }}
            sx={{
              display: 'inline-block',
              color: colors.green600,
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
              mb: 0.5,
              '&:hover': { textDecoration: 'underline' },
            }}
          >
            ← Meal Plans
          </Box>
          <Typography variant="h1" sx={{ color: semantic.textPrimary }}>
            {mealPlan.name}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
          <Button variant="outlined" startIcon={<Settings />} onClick={() => setSettingsOpen(true)}>
            Settings
          </Button>
          <Button variant="outlined" startIcon={<AutoAwesome />} onClick={handleGenerateMealPlan}>
            Generate
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={openAddDialogTopLevel}
            sx={{
              px: 3,
              py: 1.25,
              boxShadow: shadows.buttonGlow,
              '&:hover': { boxShadow: shadows.buttonGlow },
            }}
          >
            + Add Meal
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <DateRangeBar
        label={rangeLabel}
        onPrev={() => setCurrentWeek((w) => Math.max(1, w - 1))}
        onNext={() => setCurrentWeek((w) => w + 1)}
        canPrev={currentWeek > 1}
        canNext
      />

      <WeekGrid
        weekStart={weekStart}
        mealTypes={enabledMealTypes}
        meals={mealsForCurrentWeek}
        onAddMeal={openAddDialog}
        onEditMeal={openEditDialog}
      />

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingMeal ? 'Edit Meal' : 'Add Meal'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Day</InputLabel>
                <Select
                  value={selectedDay}
                  onChange={(e) => setSelectedDay(e.target.value)}
                  label="Day"
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                    <MenuItem key={day} value={day}>
                      {weekStart.add(day - 1, 'day').format('ddd, MMM D')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Meal Type</InputLabel>
                <Select
                  value={selectedMealType}
                  onChange={(e) => setSelectedMealType(e.target.value)}
                  label="Meal Type"
                >
                  {MEAL_TYPES.map((t) => (
                    <MenuItem key={t.value} value={t.value}>
                      {t.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Autocomplete
              multiple
              options={foods}
              getOptionLabel={(option) => option.name}
              value={selectedFoods}
              onChange={(e, newValue) => setSelectedFoods(newValue)}
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
              renderInput={(params) => <TextField {...params} label="Foods" placeholder="Select foods..." />}
            />

            <Box sx={{ border: `1px dashed ${semantic.borderDefault}`, p: 2, borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1.5 }}>
                Add a new food
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                <TextField
                  label="Name"
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
                  sx={{ minWidth: 130 }}
                  SelectProps={{ native: true }}
                >
                  <option value="">Select...</option>
                  {FOOD_CATEGORIES.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </TextField>
                <Button variant="outlined" size="small" onClick={handleCreateNewFood} disabled={!newFoodName.trim()}>
                  Add
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
        <DialogActions sx={{ justifyContent: 'space-between', px: 3, pb: 2 }}>
          <Box>
            {editingMeal && (
              <Button onClick={handleDeleteMeal} color="error" startIcon={<Delete />}>
                Delete
              </Button>
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveMeal} variant="contained" color="primary" startIcon={<Save />}>
              Save
            </Button>
          </Box>
        </DialogActions>
      </Dialog>

      <MealSettings
        mealPlanId={id}
        open={settingsOpen}
        onClose={() => {
          setSettingsOpen(false);
          fetchMealSettings();
        }}
      />
    </Box>
  );
};

export default MealPlanDetail;
