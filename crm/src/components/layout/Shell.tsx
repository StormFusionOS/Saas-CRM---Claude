/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../lib/auth-context';
import CommandPalette from '../CommandPalette';
import { LeftSuitesNav } from '../navigation';
import '../navigation/LeftSuitesNav.css';
import { Button } from '../ui/shadcn/button';
import { Input } from '../ui/shadcn/input';
import { Avatar, AvatarFallback } from '../ui/shadcn/avatar';
import { Badge } from '../ui/shadcn/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/shadcn/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/shadcn/tooltip';

interface ShellProps {
  children: React.ReactNode;
}

const Shell: React.FC<ShellProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showHealthInHeader, setShowHealthInHeader] = useState(() => {
    return localStorage.getItem('showHealthInHeader') === 'true';
  });
  const [healthStatus, setHealthStatus] = useState<'good' | 'degraded' | 'down'>('good');

  // Badge counts for navigation
  const badges = {
    reviewQueue: 12,
    anomalyCount: 3,
    pendingChanges: 5,
    auditIssues: 8,
    unread: 24,
    healthAlerts: 2,
  };

  // Listen for settings changes
  useEffect(() => {
    const handleSettingsChange = () => {
      const showHealth = localStorage.getItem('showHealthInHeader') === 'true';
      setShowHealthInHeader(showHealth);
    };

    window.addEventListener('settingsChanged', handleSettingsChange);
    return () => window.removeEventListener('settingsChanged', handleSettingsChange);
  }, []);

  // Simulate health status check
  useEffect(() => {
    const checkHealth = () => {
      const random = Math.random();
      if (random > 0.9) {
        setHealthStatus('degraded');
      } else if (random > 0.98) {
        setHealthStatus('down');
      } else {
        setHealthStatus('good');
      }
    };

    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Command-K keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(true);
      }
      if (e.key === 'Escape') {
        setShowCommandPalette(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-bg-base flex flex-col">
      {/* Header */}
      <header className="glass-surface border-b border-white/5 sticky top-0 z-30 h-16 flex items-center px-4 gap-4">
        {/* Logo */}
        <div className="flex items-center gap-0 min-w-[200px]">
          <img src="/brand/logo-icon.svg" alt="StormFusion OS" className="w-[74px] h-[74px]" />
          <span className="text-2xl font-display font-bold text-gradient hidden md:block">
            StormFusion OS
          </span>
        </div>

        {/* Global Search */}
        <div className="flex-1 flex justify-center">
          <div className="relative w-full max-w-xs sm:max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl">
            <Input
              type="text"
              placeholder="Search or press Cmd+K..."
              className="pl-10 bg-white/5 border-white/10"
              onFocus={() => setShowCommandPalette(true)}
            />
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          {/* Quick Add Button */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="bg-primary hover:bg-primary-hover text-white">
                <span className="hidden md:inline">+ Quick Add</span>
                <span className="md:hidden">+</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuItem onClick={() => navigate('/leads?action=new')}>
                <span className="mr-2">🎯</span>
                New Lead
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/quotes?action=new')}>
                <span className="mr-2">📄</span>
                New Quote
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/calendar?action=new')}>
                <span className="mr-2">📅</span>
                New Event
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs">3</Badge>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="max-h-96 overflow-y-auto">
                <DropdownMenuItem className="flex flex-col items-start p-3 cursor-default">
                  <p className="text-sm text-text-primary">New lead assigned to you</p>
                  <p className="text-xs text-text-muted mt-1">5 minutes ago</p>
                </DropdownMenuItem>
                <DropdownMenuItem className="flex flex-col items-start p-3 cursor-default">
                  <p className="text-sm text-text-primary">Quote #1234 approved</p>
                  <p className="text-xs text-text-muted mt-1">1 hour ago</p>
                </DropdownMenuItem>
                <DropdownMenuItem className="flex flex-col items-start p-3 cursor-default">
                  <p className="text-sm text-text-primary">System health check completed</p>
                  <p className="text-xs text-text-muted mt-1">2 hours ago</p>
                </DropdownMenuItem>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Health Indicator */}
          {showHealthInHeader && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate('/health')}
                    className="flex items-center gap-2"
                  >
                    <div
                      className={`w-2 h-2 rounded-full animate-pulse ${
                        healthStatus === 'good'
                          ? 'bg-success'
                          : healthStatus === 'degraded'
                          ? 'bg-warning'
                          : 'bg-error'
                      }`}
                      style={{
                        boxShadow: healthStatus === 'good'
                          ? '0 0 8px rgba(16, 185, 129, 0.8)'
                          : healthStatus === 'degraded'
                          ? '0 0 8px rgba(245, 158, 11, 0.8)'
                          : '0 0 8px rgba(239, 68, 68, 0.8)',
                      }}
                    />
                    <span className="text-xs text-text-secondary hidden md:inline">
                      {healthStatus === 'good'
                        ? 'Healthy'
                        : healthStatus === 'degraded'
                        ? 'Degraded'
                        : 'Down'}
                    </span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="text-xs">
                    System Status: <span className="font-medium">{healthStatus}</span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Click to view details</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary/20 text-primary font-bold">
                    {user?.email?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <p className="text-sm font-medium">{user?.email || 'User'}</p>
                {user?.roles && user.roles.length > 0 && (
                  <p className="text-xs text-muted-foreground font-normal">{user.roles[0]}</p>
                )}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate('/settings')}>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-error focus:text-error">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Navigation */}
        <aside className="glass-surface border-r border-white/5 w-64 flex flex-col">
          <LeftSuitesNav
            activeRoute={location.pathname}
            userRoles={user?.roles || ['SALES']}
            onNavigate={(route) => navigate(route)}
            badges={badges}
            userId={user?.id?.toString() || 'default'}
          />
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>

      {/* Command Palette */}
      <CommandPalette
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
      />
    </div>
  );
};

export default Shell;
