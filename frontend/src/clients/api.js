import axios from 'axios';

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
  withCredentials: true,
});

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

export default api;
