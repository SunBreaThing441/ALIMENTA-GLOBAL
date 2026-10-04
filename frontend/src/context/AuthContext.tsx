/**
 * ALIMENTA GLOBAL — React Context State Management Layer
 * Provides reactive access to security state, permissions, and session lifecycles.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService, UserSession } from '../services/auth.service';

interface AuthContextValue {
  session: UserSession | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginDemo: (role?: UserSession['role']) => void;
  logout: (reason?: string) => void;
  hasPermission: (permission: string) => boolean;
  timeRemainingSeconds: number;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<UserSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRemainingSeconds, setTimeRemainingSeconds] = useState(0);

  // Synchronize on mount and monitor session lifecycle
  useEffect(() => {
    const current = authService.getSession();
    setSession(current);
    setIsLoading(false);

    const interval = setInterval(() => {
      const active = authService.getSession();
      setSession(active);
      if (active) {
        const remaining = Math.max(0, Math.floor((active.expiresAt - Date.now()) / 1000));
        setTimeRemainingSeconds(remaining);
        if (remaining <= 0) {
          authService.logout('Session token expired.');
        }
      } else {
        setTimeRemainingSeconds(0);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const loginDemo = useCallback((role: UserSession['role'] = 'citizen_contributor') => {
    const demoSession: UserSession = {
      userId: 'usr_unesco_obs_' + Math.floor(Math.random() * 8999 + 1000),
      username: 'Dr. Elena Rostova',
      email: 'e.rostova@unesco-commons.alimenta.org',
      role: role,
      organization: 'UNESCO World Food Health Commission',
      token: 'jwt_sec_v2_' + Array.from({ length: 48 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
      csrfToken: authService.generateSecureCsrf(),
      issuedAt: Date.now(),
      expiresAt: Date.now() + 3600 * 1000, // 1 hour
      permissions: [
        'read:commons',
        'audit:products',
        'write:barcodes',
        'moderate:submissions',
        'export:scientific_data'
      ],
    };
    authService.setSession(demoSession);
    setSession(demoSession);
  }, []);

  const logout = useCallback((reason?: string) => {
    authService.logout(reason);
    setSession(null);
  }, []);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!session) return false;
    return session.permissions.includes(permission) || session.role === 'system_admin';
  }, [session]);

  const value: AuthContextValue = {
    session,
    isAuthenticated: !!session && session.expiresAt > Date.now(),
    isLoading,
    loginDemo,
    logout,
    hasPermission,
    timeRemainingSeconds,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
