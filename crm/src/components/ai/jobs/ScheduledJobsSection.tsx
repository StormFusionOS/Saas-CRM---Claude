/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Scheduled Jobs Section Component
 * Displays scheduled jobs with Run Now/Pause/Edit actions
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Button } from '@/components/ui/shadcn/button';
import { Badge } from '@/components/ui/shadcn/badge';
import {
  Play,
  Pause,
  Edit,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
} from 'lucide-react';
import type { ScheduledJob } from '@/lib/ai-types';
import { cn } from '@/lib/utils';
import { useToggleScheduledJob, useRunScheduledJob } from '@/lib/ai-queries';
import { useToast } from '@/components/ui/shadcn/use-toast';

interface ScheduledJobsSectionProps {
  jobs: ScheduledJob[];
  isLoading?: boolean;
}

interface JobCardProps {
  job: ScheduledJob;
  onRun: (jobId: number) => void;
  onToggle: (jobId: number) => void;
  isRunning: boolean;
  isToggling: boolean;
}

function formatCron(cron: string): string {
  // Simple cron formatter - could be enhanced with a library
  const patterns: Record<string, string> = {
    '0 0 * * *': 'Daily at midnight',
    '0 */6 * * *': 'Every 6 hours',
    '*/15 * * * *': 'Every 15 minutes',
    '0 9 * * 1': 'Weekly on Monday at 9 AM',
  };
  return patterns[cron] || cron;
}

function formatNextRun(nextRun?: string): string {
  if (!nextRun) return 'Not scheduled';

  const now = new Date();
  const next = new Date(nextRun);
  const diffMs = next.getTime() - now.getTime();

  if (diffMs <= 0) return 'Overdue';

  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) return `in ${diffDays}d`;
  if (diffHours > 0) return `in ${diffHours}h`;

  const diffMins = Math.floor(diffMs / 60000);
  return `in ${diffMins}m`;
}

function JobCard({ job, onRun, onToggle, isRunning, isToggling }: JobCardProps) {
  return (
    <Card className="relative overflow-hidden glow-hover">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-lg font-semibold text-text-primary">
                {job.name}
              </h3>
              <Badge
                variant={job.enabled ? 'default' : 'secondary'}
                className={cn(
                  'text-xs',
                  job.enabled
                    ? 'bg-success/10 text-success border-success/20'
                    : 'bg-muted'
                )}
              >
                {job.enabled ? 'Active' : 'Paused'}
              </Badge>
            </div>
            <p className="text-sm text-text-muted">{job.description}</p>
          </div>
        </div>

        {/* Schedule Info */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-text-secondary" />
            <div>
              <p className="text-xs text-text-muted">Schedule</p>
              <p className="text-sm font-medium text-text-primary">
                {formatCron(job.schedule)}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-text-secondary" />
            <div>
              <p className="text-xs text-text-muted">Next Run</p>
              <p className="text-sm font-medium text-text-primary">
                {formatNextRun(job.next_run)}
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        {job.last_run && (
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
            <div className="flex items-center gap-2">
              {job.last_status === 'completed' ? (
                <CheckCircle className="w-4 h-4 text-success" />
              ) : (
                <XCircle className="w-4 h-4 text-error" />
              )}
              <div>
                <p className="text-xs text-text-muted">Last Run</p>
                <p className="text-sm font-medium text-text-primary">
                  {new Date(job.last_run).toLocaleString()}
                </p>
              </div>
            </div>

            {job.avg_duration && (
              <div>
                <p className="text-xs text-text-muted">Avg Duration</p>
                <p className="text-sm font-medium text-text-primary">
                  {(job.avg_duration / 1000).toFixed(1)}s
                </p>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-4 border-t border-white/5">
          <Button
            variant="default"
            size="sm"
            onClick={() => onRun(job.id)}
            disabled={isRunning || !job.enabled}
            className="flex-1"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Now
              </>
            )}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onToggle(job.id)}
            disabled={isToggling}
          >
            {isToggling ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : job.enabled ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </Button>

          <Button variant="outline" size="sm">
            <Edit className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}

export function ScheduledJobsSection({ jobs, isLoading }: ScheduledJobsSectionProps) {
  const { mutate: runJob, isPending: isRunning } = useRunScheduledJob();
  const { mutate: toggleJob, isPending: isToggling } = useToggleScheduledJob();
  const { toast } = useToast();
  const [runningJobId, setRunningJobId] = React.useState<number | null>(null);
  const [togglingJobId, setTogglingJobId] = React.useState<number | null>(null);

  const handleRun = (jobId: number) => {
    setRunningJobId(jobId);
    runJob(jobId, {
      onSuccess: () => {
        toast({
          title: 'Job started',
          description: 'The job has been queued for execution.',
        });
        setRunningJobId(null);
      },
      onError: (error) => {
        toast({
          title: 'Failed to start job',
          description: error.message,
          variant: 'destructive',
        });
        setRunningJobId(null);
      },
    });
  };

  const handleToggle = (jobId: number) => {
    setTogglingJobId(jobId);
    toggleJob(jobId, {
      onSuccess: () => {
        toast({
          title: 'Job updated',
          description: 'The job schedule has been updated.',
        });
        setTogglingJobId(null);
      },
      onError: (error) => {
        toast({
          title: 'Failed to update job',
          description: error.message,
          variant: 'destructive',
        });
        setTogglingJobId(null);
      },
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-text-primary">Scheduled Jobs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <div className="space-y-4">
                <div className="h-6 bg-white/5 rounded w-3/4" />
                <div className="h-4 bg-white/5 rounded w-full" />
                <div className="h-4 bg-white/5 rounded w-5/6" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-text-primary">Scheduled Jobs</h2>
        <Badge variant="outline" className="text-sm">
          {jobs.filter(j => j.enabled).length} active
        </Badge>
      </div>

      {jobs.length === 0 ? (
        <Card className="py-12">
          <div className="text-center">
            <Calendar className="w-16 h-16 mx-auto text-text-muted mb-4" />
            <p className="text-lg text-text-secondary font-medium mb-2">
              No scheduled jobs
            </p>
            <p className="text-sm text-text-muted">
              Create scheduled jobs to automate AI tasks
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onRun={handleRun}
              onToggle={handleToggle}
              isRunning={isRunning && runningJobId === job.id}
              isToggling={isToggling && togglingJobId === job.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
