import axios, { AxiosError, AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL: string =
  process.env.REACT_APP_API_URL ||
  (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api');

interface RetriedRequestConfig extends InternalAxiosRequestConfig {
  _retried?: boolean;
}

const TOKEN_REFRESH_PATH = '/auth/token/refresh';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
  withCredentials: true,
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriedRequestConfig | undefined;

    // A 401 from the refresh endpoint itself must not trigger another refresh,
    // otherwise the interceptor recurses into an infinite request loop.
    const isTokenRefreshRequest = originalRequest?.url === TOKEN_REFRESH_PATH;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retried &&
      !isTokenRefreshRequest
    ) {
      originalRequest._retried = true;
      try {
        await api.post(TOKEN_REFRESH_PATH);
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
