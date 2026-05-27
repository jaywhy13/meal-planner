import { AuthClient } from '../clients/AuthClient';

export class AuthService {
  /** @param {AuthClient} [authClient] */
  constructor(authClient = new AuthClient()) {
    this.authClient = authClient;
  }

  /** @param {string} email
   *  @param {string} password
   *  @returns {Promise<Object>} */
  async login(email, password) {
    const response = await this.authClient.login({ email, password });
    return response.data.user;
  }

  /** @param {{email: string, password: string, first_name: string, last_name: string}} data
   *  @returns {Promise<Object>} */
  async register(data) {
    const response = await this.authClient.register(data);
    return response.data.user;
  }

  /** @returns {Promise<void>} */
  async logout() {
    await this.authClient.logout().catch(() => {});
  }

  /** @returns {Promise<Object|null>} */
  async getProfile() {
    const response = await this.authClient.profile();
    return response.data;
  }

  /** @param {string} email
   *  @returns {Promise<void>} */
  async forgotPassword(email) {
    await this.authClient.forgotPassword(email);
  }

  /** @param {{uid: string, token: string, password: string}} data
   *  @returns {Promise<void>} */
  async resetPassword(data) {
    await this.authClient.resetPassword(data);
  }
}
