import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister, googleAuth as apiGoogleAuth, getCurrentUser } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to load user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await apiLogin(email, password);
    if (response.success) {
      setToken(response.token);
      setUser(response.user);
      localStorage.setItem('token', response.token);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const register = async (email, password, name) => {
    const response = await apiRegister(email, password, name);
    if (response.success) {
      setToken(response.token);
      setUser(response.user);
      localStorage.setItem('token', response.token);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const googleAuth = async (googleToken) => {
    const response = await apiGoogleAuth(googleToken);
    if (response.success) {
      setToken(response.token);
      setUser(response.user);
      localStorage.setItem('token', response.token);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const isAdmin = () => user?.role === 'admin';
  const isWriter = () => user?.role === 'writer' || user?.role === 'admin';
  const isReader = () => user?.role === 'reader';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        googleAuth,
        logout,
        isAdmin,
        isWriter,
        isReader,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
