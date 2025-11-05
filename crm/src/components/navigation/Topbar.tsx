/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Topbar Component
 *
 * Top navigation bar with menu toggle, search, notifications, and user menu.
 * Features:
 * - Mobile menu toggle
 * - Command palette trigger (Cmd+K)
 * - Notifications dropdown with focus trap
 * - User menu dropdown
 * - ESC to close dropdowns
 * - Proper ARIA labels
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Menu,
  Search,
  Bell,
  User,
  LogOut,
  Settings,
  HelpCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Button from '@/components/ui/Button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/shadcn/dropdown-menu';
import { useAuth } from '@/lib/auth-context';

interface TopbarProps {
  onMenuToggle?: () => void;
  onCommandOpen?: () => void;
}

export function Topbar({ onMenuToggle, onCommandOpen }: TopbarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notifications] = React.useState([
    {
      id: 1,
      title: 'New lead assigned',
      description: 'John Doe has been assigned to you',
      time: '5m ago',
      unread: true,
    },
    {
      id: 2,
      title: 'Quote approved',
      description: 'Quote #1234 was approved by the client',
      time: '1h ago',
      unread: true,
    },
    {
      id: 3,
      title: 'Meeting reminder',
      description: 'Team standup in 15 minutes',
      time: '2h ago',
      unread: false,
    },
  ]);

  const unreadCount = notifications.filter((n) => n.unread).length;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleCommandOpen = (e: React.MouseEvent) => {
    e.preventDefault();
    onCommandOpen?.();
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        {/* Left: Mobile menu + Search */}
        <div className="flex items-center gap-4">
          {/* Mobile menu toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuToggle}
            className="lg:hidden h-9 w-9 p-0"
            aria-label="Toggle navigation menu"
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* Search / Command palette trigger */}
          <button
            onClick={handleCommandOpen}
            className={cn(
              'hidden md:flex items-center gap-2 px-3 py-2 rounded-lg',
              'bg-muted/50 hover:bg-muted transition-colors',
              'text-sm text-muted-foreground',
              'border border-border',
              'focus:outline-none focus:ring-2 focus:ring-primary'
            )}
            aria-label="Open command palette (Cmd+K)"
          >
            <Search className="h-4 w-4" />
            <span>Search...</span>
            <kbd className="hidden lg:inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-background px-1.5 font-mono text-xs font-medium text-muted-foreground">
              <span className="text-xs">⌘</span>K
            </kbd>
          </button>

          {/* Mobile search button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCommandOpen}
            className="md:hidden h-9 w-9 p-0"
            aria-label="Open search"
          >
            <Search className="h-5 w-5" />
          </Button>
        </div>

        {/* Right: Notifications + User menu */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="relative h-9 w-9 p-0"
                aria-label={`Notifications (${unreadCount} unread)`}
              >
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-white text-xs font-medium">
                    {unreadCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-80"
              aria-label="Notifications menu"
            >
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="max-h-[300px] overflow-y-auto">
                {notifications.map((notification) => (
                  <DropdownMenuItem
                    key={notification.id}
                    className="flex flex-col items-start gap-1 p-3"
                  >
                    <div className="flex items-start justify-between w-full gap-2">
                      <p className="font-medium text-sm">{notification.title}</p>
                      {notification.unread && (
                        <span className="flex h-2 w-2 rounded-full bg-primary" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {notification.description}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {notification.time}
                    </p>
                  </DropdownMenuItem>
                ))}
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="justify-center text-sm text-primary">
                View all notifications
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-9 w-9 rounded-full p-0"
                aria-label="User menu"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary">
                  <span className="text-white font-medium text-sm">
                    {user?.email?.[0]?.toUpperCase() || 'U'}
                  </span>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56" aria-label="User menu">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">
                    {user?.email || 'User'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {user?.roles?.join(', ') || 'User'}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate('/settings')}>
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/settings')}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem>
                <HelpCircle className="mr-2 h-4 w-4" />
                Help & Support
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-destructive focus:text-destructive"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
