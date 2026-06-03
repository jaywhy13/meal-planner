export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export type FoodCategory =
  | 'Protein'
  | 'Vegetable'
  | 'Fruit'
  | 'Grain'
  | 'Starch'
  | 'Dairy'
  | 'Other';

export interface Food {
  id: number;
  name: string;
  category: FoodCategory | '';
  created_at: string;
}

export interface Meal {
  id: number;
  foods: Food[];
  notes: string;
}

export interface DailyMeal {
  id: number;
  meal_plan: number;
  date: string;
  day_of_week: number;
  meal_type: MealType;
  foods: Food[];
  notes: string;
}

export interface MealSettings {
  id: number;
  meal_plan?: number;
  breakfast_enabled: boolean;
  lunch_enabled: boolean;
  dinner_enabled: boolean;
  snack_enabled: boolean;
  monday_enabled: boolean;
  tuesday_enabled: boolean;
  wednesday_enabled: boolean;
  thursday_enabled: boolean;
  friday_enabled: boolean;
  saturday_enabled: boolean;
  sunday_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface MealPlanSummary {
  id: number;
  name: string;
  start_date: string;
  created_at: string;
  updated_at: string;
}

export interface MealPlan extends MealPlanSummary {
  daily_meals: DailyMeal[];
  meal_settings: MealSettings | null;
}

export interface MealSuggestion {
  id: number;
  name: string;
  description: string;
  foods: Food[];
  meal_type: MealType;
  is_healthy: boolean;
  created_at: string;
}

export interface AuthenticatedUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ResetPasswordRequest {
  uid: string;
  token: string;
  password: string;
}
