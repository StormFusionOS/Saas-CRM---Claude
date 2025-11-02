/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface User {
  id: number;
  email: string;
  roles: string[];
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

// Decode JWT token to extract user information
function decodeToken(token: string): User | null {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    // Decode base64url payload
    const payload = parts[1];
    // Add padding if needed
    const paddedPayload = payload + '='.repeat((4 - (payload.length % 4)) % 4);
    const decoded = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
    const claims = JSON.parse(decoded);

    return {
      id: claims.user_id || 0,
      email: claims.sub || '',
      roles: claims.roles || [],
    };
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('auth_token')
  );
  const [user, setUser] = useState<User | null>(null);

  // Update user when token changes
  useEffect(() => {
    if (token) {
      const userData = decodeToken(token);
      setUser(userData);
    } else {
      setUser(null);
    }
  }, [token]);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('auth_token', newToken);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Hook to determine the landing page based on user role.
 * Returns the appropriate route path for the user's primary role.
 */
export function useRoleLanding(roles: string[] | undefined): string {
  if (!roles || roles.length === 0) {
    return '/dashboard';
  }

  // Priority order for role matching
  const roleMap: Record<string, string> = {
    OWNER: '/dashboard',        // Executive dashboard
    SALES_MANAGER: '/leads',    // Sales funnel (managers also go to leads)
    SALES: '/leads',            // Sales funnel
    DISPATCH: '/calendar',      // Ops board / scheduling
    TECH: '/pwa',              // Technician PWA view
    FINANCE: '/quotes',         // Finance / invoices
    SEO: '/seo',               // SEO dashboard
    MARKETING: '/seo',          // Marketing also goes to SEO
    ADMIN: '/health',           // Health & settings
  };

  // Return the first matching role's landing page
  for (const role of roles) {
    if (roleMap[role]) {
      return roleMap[role];
    }
  }

  // Default to dashboard if no role matches
  return '/dashboard';
}
