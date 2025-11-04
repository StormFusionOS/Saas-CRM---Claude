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

interface ShellProps {
  children: React.ReactNode;
}

const Shell: React.FC<ShellProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showQuickAdd, setShowQuickAdd] = useState(false);
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
        setShowUserMenu(false);
        setShowNotifications(false);
        setShowQuickAdd(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
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
            <input
              type="text"
              placeholder="Search or press Cmd+K..."
              className="w-full px-4 py-2 pl-10 bg-white/5 border border-white/10 rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
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
          <div className="relative">
            <button
              onClick={() => setShowQuickAdd(!showQuickAdd)}
              className="p-2 rounded-lg bg-primary hover:bg-primary-hover transition-colors text-white font-medium px-4"
              aria-label="Quick Add"
            >
              <span className="hidden md:inline">+ Quick Add</span>
              <span className="md:hidden">+</span>
            </button>

            {showQuickAdd && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowQuickAdd(false)}
                />
                <div className="absolute right-0 top-full mt-2 w-56 bg-bg-elevated border border-white/10 rounded-lg shadow-xl z-50 py-2">
                  <button
                    onClick={() => {
                      setShowQuickAdd(false);
                      navigate('/leads?action=new');
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-text-primary hover:bg-white/5 transition-colors flex items-center gap-3"
                  >
                    <span>🎯</span>
                    New Lead
                  </button>
                  <button
                    onClick={() => {
                      setShowQuickAdd(false);
                      navigate('/quotes?action=new');
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-text-primary hover:bg-white/5 transition-colors flex items-center gap-3"
                  >
                    <span>📄</span>
                    New Quote
                  </button>
                  <button
                    onClick={() => {
                      setShowQuickAdd(false);
                      navigate('/calendar?action=new');
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-text-primary hover:bg-white/5 transition-colors flex items-center gap-3"
                  >
                    <span>📅</span>
                    New Event
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg hover:bg-white/5 transition-colors relative"
              aria-label="Notifications"
            >
              <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
              <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>
            </button>

            {showNotifications && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowNotifications(false)}
                />
                <div className="absolute right-0 top-full mt-2 w-80 bg-bg-elevated border border-white/10 rounded-lg shadow-xl z-50 py-2">
                  <div className="px-4 py-2 border-b border-white/10">
                    <h3 className="text-sm font-semibold text-text-primary">Notifications</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    <div className="px-4 py-3 hover:bg-white/5 transition-colors border-b border-white/5">
                      <p className="text-sm text-text-primary">New lead assigned to you</p>
                      <p className="text-xs text-text-muted mt-1">5 minutes ago</p>
                    </div>
                    <div className="px-4 py-3 hover:bg-white/5 transition-colors border-b border-white/5">
                      <p className="text-sm text-text-primary">Quote #1234 approved</p>
                      <p className="text-xs text-text-muted mt-1">1 hour ago</p>
                    </div>
                    <div className="px-4 py-3 hover:bg-white/5 transition-colors">
                      <p className="text-sm text-text-primary">System health check completed</p>
                      <p className="text-xs text-text-muted mt-1">2 hours ago</p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Health Indicator */}
          {showHealthInHeader && (
            <div className="relative group">
              <button
                onClick={() => navigate('/health')}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors"
                aria-label="System Health"
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
              </button>
              <div className="absolute right-0 top-full mt-2 w-48 bg-bg-elevated border border-white/10 rounded-lg shadow-xl p-3 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity z-50">
                <p className="text-xs text-text-secondary">
                  System Status: <span className="text-text-primary font-medium">{healthStatus}</span>
                </p>
                <p className="text-xs text-text-muted mt-1">Click to view details</p>
              </div>
            </div>
          )}

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors"
              aria-label="User menu"
            >
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-primary font-bold text-sm">
                  {user?.email?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
            </button>

            {showUserMenu && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowUserMenu(false)}
                />
                <div className="absolute right-0 top-full mt-2 w-56 bg-bg-elevated border border-white/10 rounded-lg shadow-xl z-50 py-2">
                  <div className="px-4 py-2 border-b border-white/10">
                    <p className="text-sm font-medium text-text-primary">{user?.email || 'User'}</p>
                    {user?.roles && user.roles.length > 0 && (
                      <p className="text-xs text-text-muted">{user.roles[0]}</p>
                    )}
                  </div>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigate('/settings');
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-text-primary hover:bg-white/5 transition-colors flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Settings
                  </button>
                  <div className="my-1 border-t border-white/10" />
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-left text-sm text-error hover:bg-error/10 transition-colors flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </button>
                </div>
              </>
            )}
          </div>
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
