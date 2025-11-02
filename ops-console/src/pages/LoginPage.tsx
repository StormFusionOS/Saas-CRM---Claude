/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';
import { authAPI } from '../lib/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('Nathan@RiverCityClean.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await authAPI.login(email, password);
      login(response.data.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base relative overflow-hidden">
      {/* Radial gradient accent */}
      <div className="absolute inset-0 pointer-events-none"
           style={{ background: 'radial-gradient(circle at center, rgba(0, 183, 253, 0.15) 0%, rgba(10, 15, 28, 1) 70%)' }} />

      <Card variant="glass" padding="lg" className="max-w-md w-full relative z-10">
        <h2 className="text-3xl font-display font-bold mb-2 text-center text-gradient">
          Ops Console
        </h2>
        <p className="text-text-secondary text-center mb-8">Operations & Monitoring</p>

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

          <Button type="submit" variant="primary" size="lg" fullWidth>
            Sign In
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default LoginPage;
