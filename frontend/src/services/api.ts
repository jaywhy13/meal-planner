import type { AxiosResponse } from 'axios';
import api from '../clients/api';
import type {
  DailyMeal,
  Food,
  Meal,
  MealPlan,
  MealPlanSummary,
  MealSettings,
  MealSuggestion,
  MealType,
} from '../types';

export interface CreateMealPlanInput {
  name: string;
  start_date?: string;
}

export type UpdateMealPlanInput = Partial<CreateMealPlanInput>;

export interface CreateFoodInput {
  name: string;
  category: string;
}

export type UpdateFoodInput = Partial<CreateFoodInput>;

export interface CreateMealInput {
  name: string;
  food_ids: number[];
  notes?: string;
}

export type UpdateMealInput = Partial<CreateMealInput>;

export interface CreateDailyMealInput {
  meal_plan: number | string;
  date: string;
  meal_type: MealType;
  meal_id: number | null;
}

export type UpdateDailyMealInput = Partial<CreateDailyMealInput>;

export interface CreateMealSettingsInput {
  meal_plan: number;
  breakfast_enabled?: boolean;
  lunch_enabled?: boolean;
  dinner_enabled?: boolean;
  snack_enabled?: boolean;
  monday_enabled?: boolean;
  tuesday_enabled?: boolean;
  wednesday_enabled?: boolean;
  thursday_enabled?: boolean;
  friday_enabled?: boolean;
  saturday_enabled?: boolean;
  sunday_enabled?: boolean;
}

export type UpdateMealSettingsInput = Partial<CreateMealSettingsInput>;

export const mealPlansAPI = {
  getAll: (): Promise<AxiosResponse<MealPlanSummary[]>> => api.get('/meal-plans'),
  getById: (id: number | string): Promise<AxiosResponse<MealPlan>> => api.get(`/meal-plans/${id}`),
  create: (data: CreateMealPlanInput): Promise<AxiosResponse<MealPlan>> =>
    api.post('/meal-plans', data),
  update: (id: number | string, data: UpdateMealPlanInput): Promise<AxiosResponse<MealPlan>> =>
    api.put(`/meal-plans/${id}`, data),
  delete: (id: number | string): Promise<AxiosResponse<void>> => api.delete(`/meal-plans/${id}`),
  generateMealPlan: (id: number | string): Promise<AxiosResponse<MealPlan>> =>
    api.post(`/meal-plans/${id}/generate_meal_plan`),
};

export const foodsAPI = {
  getAll: (): Promise<AxiosResponse<Food[]>> => api.get('/foods'),
  getById: (id: number | string): Promise<AxiosResponse<Food>> => api.get(`/foods/${id}`),
  create: (data: CreateFoodInput): Promise<AxiosResponse<Food>> => api.post('/foods', data),
  update: (id: number | string, data: UpdateFoodInput): Promise<AxiosResponse<Food>> =>
    api.put(`/foods/${id}`, data),
  delete: (id: number | string): Promise<AxiosResponse<void>> => api.delete(`/foods/${id}`),
  search: (query: string): Promise<AxiosResponse<Food[]>> =>
    api.get(`/foods/search?q=${encodeURIComponent(query)}`),
};

export const dailyMealsAPI = {
  getAll: (mealPlanId: number | string): Promise<AxiosResponse<DailyMeal[]>> =>
    api.get(`/daily-meals?meal_plan=${mealPlanId}`),
  getById: (id: number | string): Promise<AxiosResponse<DailyMeal>> =>
    api.get(`/daily-meals/${id}`),
  create: (data: CreateDailyMealInput): Promise<AxiosResponse<DailyMeal>> =>
    api.post('/daily-meals', data),
  update: (id: number | string, data: UpdateDailyMealInput): Promise<AxiosResponse<DailyMeal>> =>
    api.put(`/daily-meals/${id}`, data),
  delete: (id: number | string): Promise<AxiosResponse<void>> => api.delete(`/daily-meals/${id}`),
};

export const mealsAPI = {
  getAll: (nameSearch?: string): Promise<AxiosResponse<Meal[]>> =>
    api.get(nameSearch ? `/meals?q=${encodeURIComponent(nameSearch)}` : '/meals'),
  getById: (id: number | string): Promise<AxiosResponse<Meal>> => api.get(`/meals/${id}`),
  create: (data: CreateMealInput): Promise<AxiosResponse<Meal>> => api.post('/meals', data),
  update: (id: number | string, data: UpdateMealInput): Promise<AxiosResponse<Meal>> =>
    api.patch(`/meals/${id}`, data),
  delete: (id: number | string): Promise<AxiosResponse<void>> => api.delete(`/meals/${id}`),
};

export const mealSuggestionsAPI = {
  getAll: (): Promise<AxiosResponse<MealSuggestion[]>> => api.get('/meal-suggestions'),
  getById: (id: number | string): Promise<AxiosResponse<MealSuggestion>> =>
    api.get(`/meal-suggestions/${id}`),
  getByMealType: (mealType: MealType): Promise<AxiosResponse<MealSuggestion[]>> =>
    api.get(`/meal-suggestions/by_meal_type?meal_type=${mealType}`),
};

export const mealSettingsAPI = {
  getAll: (): Promise<AxiosResponse<MealSettings[]>> => api.get('/meal-settings'),
  getById: (id: number | string): Promise<AxiosResponse<MealSettings>> =>
    api.get(`/meal-settings/${id}`),
  getByMealPlan: (mealPlanId: number | string): Promise<AxiosResponse<MealSettings[]>> =>
    api.get(`/meal-settings?meal_plan=${mealPlanId}`),
  create: (data: CreateMealSettingsInput): Promise<AxiosResponse<MealSettings>> =>
    api.post('/meal-settings', data),
  update: (
    id: number | string,
    data: UpdateMealSettingsInput
  ): Promise<AxiosResponse<MealSettings>> => api.put(`/meal-settings/${id}`, data),
  delete: (id: number | string): Promise<AxiosResponse<void>> => api.delete(`/meal-settings/${id}`),
};

export default api;
