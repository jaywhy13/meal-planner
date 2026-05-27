import api from './api';

export class AuthClient {
  /** @param {{email: string, password: string}} data
   *  @returns {Promise<import('axios').AxiosResponse>} */
  login(data) {
    return api.post('/auth/login', data);
  }

  /** @returns {Promise<import('axios').AxiosResponse>} */
  logout() {
    return api.post('/auth/logout');
  }

  /** @param {{email: string, password: string, first_name: string, last_name: string}} data
   *  @returns {Promise<import('axios').AxiosResponse>} */
  register(data) {
    return api.post('/auth/register', data);
  }

  /** @returns {Promise<import('axios').AxiosResponse>} */
  profile() {
    return api.get('/auth/profile');
  }

  /** @param {string} email
   *  @returns {Promise<import('axios').AxiosResponse>} */
  forgotPassword(email) {
    return api.post('/auth/forgot-password', { email });
  }

  /** @param {{uid: string, token: string, password: string}} data
   *  @returns {Promise<import('axios').AxiosResponse>} */
  resetPassword(data) {
    return api.post('/auth/reset-password', data);
  }
}
