import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthService } from '../services/AuthService';

const AuthContext = createContext(null);

const authService = new AuthService();

/** @returns {JSX.Element} */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authService.getProfile()
      .then((profile) => setUser(profile))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  /** @param {string} email
   *  @param {string} password
   *  @returns {Promise<Object>} */
  const login = async (email, password) => {
    const loggedInUser = await authService.login(email, password);
    setUser(loggedInUser);
    return loggedInUser;
  };

  /** @param {{email: string, password: string, first_name: string, last_name: string}} data
   *  @returns {Promise<Object>} */
  const register = async (data) => {
    const registeredUser = await authService.register(data);
    setUser(registeredUser);
    return registeredUser;
  };

  /** @returns {Promise<void>} */
  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

/** @returns {{user: Object|null, loading: boolean, login: Function, register: Function, logout: Function}} */
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
