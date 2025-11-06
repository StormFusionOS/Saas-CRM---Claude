/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Quick Actions Bar Component
 * Provides quick access to common AI Suite actions
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/shadcn/button';
import Card from '@/components/ui/Card';
import {
  Sparkles,
  FileText,
  Activity,
  Database,
  Settings,
  Calendar,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuickAction {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  variant?: 'default' | 'outline' | 'secondary';
  className?: string;
}

export function QuickActionsBar() {
  const navigate = useNavigate();

  const actions: QuickAction[] = [
    {
      id: 'run-prompt',
      label: 'Run Prompt',
      description: 'Execute AI prompt from library',
      icon: <Sparkles className="w-5 h-5" />,
      action: () => navigate('/ai/prompt-runner'),
      variant: 'default',
      className: 'bg-primary hover:bg-primary-hover text-white',
    },
    {
      id: 'view-logs',
      label: 'View Logs',
      description: 'Check job execution logs',
      icon: <FileText className="w-5 h-5" />,
      action: () => navigate('/ai/jobs'),
      variant: 'outline',
    },
    {
      id: 'health-check',
      label: 'Health Check',
      description: 'System health status',
      icon: <Activity className="w-5 h-5" />,
      action: () => navigate('/health'),
      variant: 'outline',
    },
    {
      id: 'backup',
      label: 'Backup Now',
      description: 'Create system backup',
      icon: <Database className="w-5 h-5" />,
      action: () => {
        // TODO: Implement backup action
        alert('Backup feature coming soon!');
      },
      variant: 'outline',
    },
    {
      id: 'scheduler',
      label: 'Job Scheduler',
      description: 'Manage scheduled tasks',
      icon: <Calendar className="w-5 h-5" />,
      action: () => navigate('/ai/jobs'),
      variant: 'outline',
    },
    {
      id: 'settings',
      label: 'AI Settings',
      description: 'Configure AI Suite',
      icon: <Settings className="w-5 h-5" />,
      action: () => navigate('/ai/governance'),
      variant: 'outline',
    },
  ];

  return (
    <Card>
      <div className="space-y-4">
        {/* Header */}
        <div>
          <h3 className="text-lg font-semibold text-text-primary">
            Quick Actions
          </h3>
          <p className="text-sm text-text-muted mt-1">
            Common tasks and shortcuts
          </p>
        </div>

        {/* Actions Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {actions.map((action) => (
            <button
              key={action.id}
              onClick={action.action}
              className={cn(
                'flex flex-col items-center gap-3 p-4 rounded-lg',
                'border border-border bg-white/5 hover:bg-white/10',
                'transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary',
                'group'
              )}
            >
              <div className={cn(
                'p-3 rounded-lg transition-colors',
                action.className?.includes('bg-primary')
                  ? 'bg-primary/20'
                  : 'bg-white/10 group-hover:bg-primary/20'
              )}>
                {action.icon}
              </div>

              <div className="text-center">
                <p className="text-sm font-medium text-text-primary">
                  {action.label}
                </p>
                <p className="text-xs text-text-muted mt-1 hidden lg:block">
                  {action.description}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </Card>
  );
}
