import api from '../clients/api';

// Meal Plans API
export const mealPlansAPI = {
  getAll: () => api.get('/meal-plans'),
  getById: (id) => api.get(`/meal-plans/${id}`),
  create: (data) => api.post('/meal-plans', data),
  update: (id, data) => api.put(`/meal-plans/${id}`, data),
  delete: (id) => api.delete(`/meal-plans/${id}`),
  generateMealPlan: (id) => api.post(`/meal-plans/${id}/generate_meal_plan`),
};

// Foods API
export const foodsAPI = {
  getAll: () => api.get('/foods'),
  getById: (id) => api.get(`/foods/${id}`),
  create: (data) => api.post('/foods', data),
  update: (id, data) => api.put(`/foods/${id}`, data),
  delete: (id) => api.delete(`/foods/${id}`),
  search: (query) => api.get(`/foods/search?q=${encodeURIComponent(query)}`),
};

// Daily Meals API
export const dailyMealsAPI = {
  getAll: (mealPlanId) => api.get(`/daily-meals?meal_plan=${mealPlanId}`),
  getById: (id) => api.get(`/daily-meals/${id}`),
  create: (data) => api.post('/daily-meals', data),
  update: (id, data) => api.put(`/daily-meals/${id}`, data),
  delete: (id) => api.delete(`/daily-meals/${id}`),
};

// Meal Suggestions API
export const mealSuggestionsAPI = {
  getAll: () => api.get('/meal-suggestions'),
  getById: (id) => api.get(`/meal-suggestions/${id}`),
  getByMealType: (mealType) => api.get(`/meal-suggestions/by_meal_type?meal_type=${mealType}`),
};

// Meal Settings API
export const mealSettingsAPI = {
  getAll: () => api.get('/meal-settings'),
  getById: (id) => api.get(`/meal-settings/${id}`),
  getByMealPlan: (mealPlanId) => api.get(`/meal-settings?meal_plan=${mealPlanId}`),
  create: (data) => api.post('/meal-settings', data),
  update: (id, data) => api.put(`/meal-settings/${id}`, data),
  delete: (id) => api.delete(`/meal-settings/${id}`),
};

export default api;
