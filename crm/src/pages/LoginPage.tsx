/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, useRoleLanding } from '../lib/auth-context';
import { authAPI } from '../lib/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('Nathan@RiverCityClean.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await authAPI.login(email, password);
      login(response.access_token);

      // Decode the token to get user roles
      const parts = response.access_token.split('.');
      if (parts.length === 3) {
        const payload = parts[1];
        const paddedPayload = payload + '='.repeat((4 - (payload.length % 4)) % 4);
        const decoded = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
        const claims = JSON.parse(decoded);

        // Use role-based landing
        const landingPage = useRoleLanding(claims.roles);
        navigate(landingPage);
      } else {
        // Fallback to dashboard
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base relative overflow-hidden">
      {/* Radial gradient accent */}
      <div className="absolute inset-0 bg-gradient-radial from-primary/20 via-bg-base to-bg-base pointer-events-none"
           style={{ background: 'radial-gradient(circle at center, rgba(0, 90, 224, 0.15) 0%, rgba(10, 15, 28, 1) 70%)' }} />

      <Card variant="glass" padding="lg" className="max-w-md w-full relative z-10">
        <div className="flex flex-col items-center mb-8">
          <img src="/brand/logo-icon.svg" alt="StormFusion OS" className="w-20 h-20 mb-4" />
          <h2 className="text-3xl font-display font-bold mb-2 text-center text-gradient">
            StormFusion OS
          </h2>
          <p className="text-text-secondary text-center">Customer Portal Login</p>
        </div>

        {error && (
          <div className="bg-error/10 border border-error text-error p-3 rounded-base mb-6" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            type="email"
            id="email"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            aria-label="Email address"
          />

          <Input
            type="password"
            id="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            aria-label="Password"
          />

          <Button type="submit" variant="primary" size="lg" fullWidth disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default LoginPage;
