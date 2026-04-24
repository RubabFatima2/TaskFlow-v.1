'use client';

import { useAuth } from '@/context/AuthContext';

export default function useAuthHook() {
  const { user, isAuthenticated, login, register, logout } = useAuth();

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
  };
}
