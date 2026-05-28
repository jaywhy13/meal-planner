import { AuthClient } from '../clients/AuthClient';
import type {
  AuthenticatedUser,
  LoginRequest,
  RegisterRequest,
  ResetPasswordRequest,
} from '../types';

export class AuthService {
  private readonly authClient: AuthClient;

  constructor(authClient: AuthClient = new AuthClient()) {
    this.authClient = authClient;
  }

  async login(email: string, password: string): Promise<AuthenticatedUser> {
    const request: LoginRequest = { email, password };
    const response = await this.authClient.login(request);
    return response.data.user;
  }

  async register(data: RegisterRequest): Promise<AuthenticatedUser> {
    const response = await this.authClient.register(data);
    return response.data.user;
  }

  async logout(): Promise<void> {
    await this.authClient.logout().catch(() => undefined);
  }

  async getProfile(): Promise<AuthenticatedUser> {
    const response = await this.authClient.profile();
    return response.data;
  }

  async forgotPassword(email: string): Promise<void> {
    await this.authClient.forgotPassword(email);
  }

  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    await this.authClient.resetPassword(data);
  }
}
