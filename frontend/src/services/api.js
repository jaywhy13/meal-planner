import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    console.log(`${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retried) {
      originalRequest._retried = true;
      try {
        await api.post('/auth/token/refresh');
        return api(originalRequest);
      } catch {
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    if (error.code === 'ECONNREFUSED') {
      console.error('Cannot connect to backend.');
    } else {
      console.error('API Error:', error.response?.status, error.response?.data || error.message);
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  register: (data) => api.post('/auth/register', data),
  profile: () => api.get('/auth/profile'),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};

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
