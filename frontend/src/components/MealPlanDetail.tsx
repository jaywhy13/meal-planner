import React, { useState, useEffect, KeyboardEvent } from 'react';
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
  SelectChangeEvent,
} from '@mui/material';
import { AutoAwesome, Settings, Save, Delete } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { mealPlansAPI, foodsAPI, dailyMealsAPI, mealsAPI, mealSettingsAPI } from '../services/api';
import MealSettings from './MealSettings';
import { FOOD_CATEGORIES } from '../constants/foodCategories';
import { colors, semantic, shadows } from '../theme/tokens';
import DateRangeBar from './mealPlanDetail/DateRangeBar';
import WeekGrid, { AddMealRequest, MealTypeOption } from './mealPlanDetail/WeekGrid';
import { WeekGridMeal } from './mealPlanDetail/MealCell';
import type {
  DailyMeal,
  Food,
  MealPlan,
  MealSettings as MealSettingsData,
  MealType,
} from '../types';

const MEAL_TYPES: MealTypeOption[] = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'snack', label: 'Snack' },
];

const MealPlanDetail = (): React.ReactElement => {
  const { id: idParam } = useParams<{ id: string }>();
  const id = idParam ?? '';
  const navigate = useNavigate();
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [dailyMeals, setDailyMeals] = useState<DailyMeal[]>([]);
  const [foods, setFoods] = useState<Food[]>([]);
  const [mealSettings, setMealSettings] = useState<MealSettingsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [editingMeal, setEditingMeal] = useState<WeekGridMeal | null>(null);
  const [currentWeek, setCurrentWeek] = useState<number>(1);
  const [selectedDay, setSelectedDay] = useState<number>(1);
  const [selectedMealType, setSelectedMealType] = useState<MealType>('breakfast');
  const [selectedFoods, setSelectedFoods] = useState<Food[]>([]);
  const [notes, setNotes] = useState<string>('');
  const [newFoodName, setNewFoodName] = useState<string>('');
  const [newFoodCategory, setNewFoodCategory] = useState<string>('');
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      fetchMealPlan();
      fetchFoods();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    if (mealPlan) {
      fetchDailyMeals();
      fetchMealSettings();
      const planMonday = dayjs(mealPlan.created_at).startOf('week').add(1, 'day');
      const daysSinceStart = dayjs().startOf('day').diff(planMonday, 'day');
      setCurrentWeek(Math.max(1, Math.floor(daysSinceStart / 7) + 1));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mealPlan]);

  const fetchMealPlan = async (): Promise<void> => {
    try {
      const response = await mealPlansAPI.getById(id);
      setMealPlan(response.data);
    } catch (caughtError) {
      setError('Failed to fetch meal plan');
    }
  };

  const fetchDailyMeals = async (): Promise<void> => {
    try {
      const response = await dailyMealsAPI.getAll(id);
      setDailyMeals(response.data);
    } catch (caughtError) {
      setError('Failed to fetch daily meals');
    } finally {
      setLoading(false);
    }
  };

  const fetchMealSettings = async (): Promise<void> => {
    try {
      const response = await mealSettingsAPI.getByMealPlan(id);
      if (response.data.length > 0) setMealSettings(response.data[0]);
    } catch (caughtError) {
      console.error('Error fetching meal settings:', caughtError);
    }
  };

  const fetchFoods = async (): Promise<void> => {
    try {
      const response = await foodsAPI.getAll();
      setFoods(response.data);
    } catch (caughtError) {
      console.error('Error fetching foods:', caughtError);
    }
  };

  const anchor = mealPlan ? dayjs(mealPlan.created_at) : dayjs();
  const week1Start = anchor.startOf('week').add(1, 'day');
  const weekStart = week1Start.add((currentWeek - 1) * 7, 'day');
  const weekEnd = weekStart.add(6, 'day');
  const rangeLabel = `${weekStart.format('MMM D')} – ${weekEnd.format('MMM D, YYYY')}`;

  const enabledMealTypes: MealTypeOption[] = mealSettings
    ? MEAL_TYPES.filter((option) => {
        const enabledKey = `${option.value}_enabled` as keyof MealSettingsData;
        return mealSettings[enabledKey] !== false;
      })
    : MEAL_TYPES;

  const mealsForCurrentWeek: WeekGridMeal[] = dailyMeals
    .filter((dailyMeal) => dailyMeal.week === currentWeek)
    .map((dailyMeal) => ({
      id: dailyMeal.id,
      day: dailyMeal.day ?? 0,
      meal_type: dailyMeal.meal_type,
      foods: dailyMeal.meal?.foods ?? [],
    }));

  const openAddDialog = ({ day, mealType }: AddMealRequest): void => {
    setEditingMeal(null);
    setSelectedDay(day);
    setSelectedMealType(mealType);
    setSelectedFoods([]);
    setNotes('');
    setNewFoodName('');
    setNewFoodCategory('');
    setOpenDialog(true);
  };

  const openEditDialog = (meal: WeekGridMeal): void => {
    setEditingMeal(meal);
    setSelectedDay(meal.day);
    setSelectedMealType(meal.meal_type);
    setSelectedFoods(meal.foods || []);
    const sourceDailyMeal = dailyMeals.find((existing) => existing.id === meal.id);
    setNotes(sourceDailyMeal?.meal?.notes || '');
    setNewFoodName('');
    setNewFoodCategory('');
    setOpenDialog(true);
  };

  const openAddDialogTopLevel = (): void => {
    setEditingMeal(null);
    setSelectedDay(1);
    setSelectedMealType('breakfast');
    setSelectedFoods([]);
    setNotes('');
    setNewFoodName('');
    setNewFoodCategory('');
    setOpenDialog(true);
  };

  const slotDateForSelectedDay = (): string =>
    weekStart.add(selectedDay - 1, 'day').format('YYYY-MM-DD');

  const generatedMealName = (): string => {
    if (selectedFoods.length === 0) return 'Untitled meal';
    return selectedFoods.map((food) => food.name).join(', ');
  };

  const persistMeal = async (): Promise<number> => {
    const mealPayload = {
      name: generatedMealName(),
      food_ids: selectedFoods.map((food) => food.id),
      notes,
    };
    const linkedMealId = editingMeal
      ? dailyMeals.find((existing) => existing.id === editingMeal.id)?.meal?.id
      : undefined;
    if (linkedMealId) {
      await mealsAPI.update(linkedMealId, mealPayload);
      return linkedMealId;
    }
    const response = await mealsAPI.create(mealPayload);
    return response.data.id;
  };

  const handleSaveMeal = async (): Promise<void> => {
    try {
      const mealId = await persistMeal();
      const slotData = {
        meal_plan: id,
        date: slotDateForSelectedDay(),
        meal_type: selectedMealType,
        meal_id: mealId,
      };
      if (editingMeal) {
        await dailyMealsAPI.update(editingMeal.id, slotData);
      } else {
        await dailyMealsAPI.create(slotData);
      }
      await fetchDailyMeals();
      setOpenDialog(false);
    } catch (caughtError) {
      setError('Failed to save meal');
    }
  };

  const handleDeleteMeal = async (): Promise<void> => {
    if (!editingMeal) return;
    if (!window.confirm('Delete this meal?')) return;
    try {
      await dailyMealsAPI.delete(editingMeal.id);
      await fetchDailyMeals();
      setOpenDialog(false);
    } catch (caughtError) {
      setError('Failed to delete meal');
    }
  };

  const handleGenerateMealPlan = async (): Promise<void> => {
    try {
      await mealPlansAPI.generateMealPlan(id);
      await fetchDailyMeals();
    } catch (caughtError) {
      setError('Failed to generate meal plan');
    }
  };

  const handleCreateNewFood = async (): Promise<void> => {
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
    } catch (caughtError) {
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
            onKeyDown={(event: KeyboardEvent<HTMLDivElement>) => {
              if (event.key === 'Enter') navigate('/');
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
        onPrev={() => setCurrentWeek((week) => Math.max(1, week - 1))}
        onNext={() => setCurrentWeek((week) => week + 1)}
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
                <Select<number>
                  value={selectedDay}
                  onChange={(event: SelectChangeEvent<number>) =>
                    setSelectedDay(Number(event.target.value))
                  }
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
                <Select<MealType>
                  value={selectedMealType}
                  onChange={(event: SelectChangeEvent<MealType>) =>
                    setSelectedMealType(event.target.value as MealType)
                  }
                  label="Meal Type"
                >
                  {MEAL_TYPES.map((mealType) => (
                    <MenuItem key={mealType.value} value={mealType.value}>
                      {mealType.label}
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
              onChange={(_event, newValue) => setSelectedFoods(newValue)}
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
                <TextField {...params} label="Foods" placeholder="Select foods..." />
              )}
            />

            <Box sx={{ border: `1px dashed ${semantic.borderDefault}`, p: 2, borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1.5 }}>
                Add a new food
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                <TextField
                  label="Name"
                  value={newFoodName}
                  onChange={(event) => setNewFoodName(event.target.value)}
                  size="small"
                  sx={{ flexGrow: 1 }}
                />
                <TextField
                  select
                  label="Category"
                  value={newFoodCategory}
                  onChange={(event) => setNewFoodCategory(event.target.value)}
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
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleCreateNewFood}
                  disabled={!newFoodName.trim()}
                >
                  Add
                </Button>
              </Box>
            </Box>

            <TextField
              label="Notes"
              multiline
              rows={3}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
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
            <Button
              onClick={handleSaveMeal}
              variant="contained"
              color="primary"
              startIcon={<Save />}
            >
              Save
            </Button>
          </Box>
        </DialogActions>
      </Dialog>

      <MealSettings
        mealPlanId={Number(id)}
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
