import type { AxiosResponse } from 'axios';
import api from './api';
import type {
  AuthenticatedUser,
  LoginRequest,
  RegisterRequest,
  ResetPasswordRequest,
} from '../types';

export interface AuthResponse {
  user: AuthenticatedUser;
}

export class AuthClient {
  login(data: LoginRequest): Promise<AxiosResponse<AuthResponse>> {
    return api.post('/auth/login', data);
  }

  logout(): Promise<AxiosResponse<void>> {
    return api.post('/auth/logout');
  }

  register(data: RegisterRequest): Promise<AxiosResponse<AuthResponse>> {
    return api.post('/auth/register', data);
  }

  profile(): Promise<AxiosResponse<AuthenticatedUser>> {
    return api.get('/auth/profile');
  }

  forgotPassword(email: string): Promise<AxiosResponse<void>> {
    return api.post('/auth/forgot-password', { email });
  }

  resetPassword(data: ResetPasswordRequest): Promise<AxiosResponse<void>> {
    return api.post('/auth/reset-password', data);
  }
}
