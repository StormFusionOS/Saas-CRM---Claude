/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Active Jobs Panel Component
 * Displays running/queued jobs with progress, ETA, and cancel actions
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Button } from '@/components/ui/shadcn/button';
import { Progress } from '@/components/ui/shadcn/progress';
import { Badge } from '@/components/ui/shadcn/badge';
import {
  Play,
  Clock,
  X,
  FileText,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import type { Job } from '@/lib/ai-types';
import { cn } from '@/lib/utils';
import { useCancelJob } from '@/lib/ai-queries';
import { useToast } from '@/components/ui/shadcn/use-toast';

interface ActiveJobsPanelProps {
  jobs: Job[];
  isLoading?: boolean;
}

interface JobItemProps {
  job: Job;
  onCancel: (jobId: number) => void;
  isCanceling: boolean;
}

function getJobStatusBadge(state: Job['state']) {
  const config = {
    running: { variant: 'default' as const, icon: Loader2, label: 'Running', className: 'bg-primary text-white' },
    queued: { variant: 'secondary' as const, icon: Clock, label: 'Queued', className: 'bg-muted' },
    completed: { variant: 'outline' as const, icon: CheckCircle, label: 'Completed', className: 'bg-success/10 text-success border-success/20' },
    failed: { variant: 'destructive' as const, icon: XCircle, label: 'Failed', className: 'bg-error/10 text-error' },
    cancelled: { variant: 'outline' as const, icon: AlertCircle, label: 'Cancelled', className: 'bg-muted' },
  };

  const { icon: Icon, label, className } = config[state];

  return (
    <Badge variant="outline" className={cn('gap-1', className)}>
      <Icon className={cn('w-3 h-3', state === 'running' && 'animate-spin')} />
      {label}
    </Badge>
  );
}

function formatETA(eta?: string): string {
  if (!eta) return 'Unknown';

  const now = new Date();
  const etaDate = new Date(eta);
  const diffMs = etaDate.getTime() - now.getTime();

  if (diffMs <= 0) return 'Completing...';

  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return '< 1 min';
  if (diffMins < 60) return `${diffMins} min`;

  const diffHours = Math.floor(diffMins / 60);
  const remainMins = diffMins % 60;
  return `${diffHours}h ${remainMins}m`;
}

function JobItem({ job, onCancel, isCanceling }: JobItemProps) {
  return (
    <div className="p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-4 h-4 text-text-secondary flex-shrink-0" />
            <h4 className="text-sm font-medium text-text-primary truncate">
              {job.name}
            </h4>
          </div>
          {job.created_by && (
            <p className="text-xs text-text-muted">
              Created by {job.created_by}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {getJobStatusBadge(job.state)}

          {job.state === 'running' && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-error hover:text-error hover:bg-error/10"
              onClick={() => onCancel(job.id)}
              disabled={isCanceling}
              title="Cancel job"
            >
              {isCanceling ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <X className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Progress */}
      {(job.state === 'running' || job.state === 'queued') && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-text-muted">
              Progress: {job.progress}%
            </span>
            {job.eta && (
              <span className="text-text-secondary flex items-center gap-1">
                <Clock className="w-3 h-3" />
                ETA: {formatETA(job.eta)}
              </span>
            )}
          </div>
          <Progress value={job.progress} className="h-2" />
        </div>
      )}

      {/* Error message */}
      {job.error && (
        <div className="p-2 rounded bg-error/10 border border-error/20">
          <p className="text-xs text-error">{job.error}</p>
        </div>
      )}

      {/* Timestamps */}
      <div className="flex items-center gap-4 text-xs text-text-muted pt-2 border-t border-white/5">
        {job.started_at && (
          <span>Started: {new Date(job.started_at).toLocaleTimeString()}</span>
        )}
        {job.completed_at && (
          <span>Completed: {new Date(job.completed_at).toLocaleTimeString()}</span>
        )}
      </div>
    </div>
  );
}

export function ActiveJobsPanel({ jobs, isLoading }: ActiveJobsPanelProps) {
  const { mutate: cancelJob, isPending: isCanceling } = useCancelJob();
  const { toast } = useToast();
  const [cancelingJobId, setCancelingJobId] = React.useState<number | null>(null);

  const handleCancel = (jobId: number) => {
    setCancelingJobId(jobId);
    cancelJob(jobId, {
      onSuccess: () => {
        toast({
          title: 'Job cancelled',
          description: 'The job has been successfully cancelled.',
        });
        setCancelingJobId(null);
      },
      onError: (error) => {
        toast({
          title: 'Failed to cancel job',
          description: error.message,
          variant: 'destructive',
        });
        setCancelingJobId(null);
      },
    });
  };

  if (isLoading) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-white/5 rounded w-1/4" />
          {[...Array(3)].map((_, i) => (
            <div key={i} className="p-4 rounded-lg bg-white/5 space-y-3">
              <div className="h-4 bg-white/10 rounded w-3/4" />
              <div className="h-2 bg-white/10 rounded w-full" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  const runningJobs = jobs.filter(j => j.state === 'running');
  const queuedJobs = jobs.filter(j => j.state === 'queued');
  const activeJobs = [...runningJobs, ...queuedJobs];

  return (
    <Card>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">
              Active Jobs
            </h3>
            <p className="text-sm text-text-muted mt-1">
              {runningJobs.length} running, {queuedJobs.length} queued
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
              <Play className="w-3 h-3 mr-1" />
              {runningJobs.length}
            </Badge>
            <Badge variant="outline" className="bg-muted">
              <Clock className="w-3 h-3 mr-1" />
              {queuedJobs.length}
            </Badge>
          </div>
        </div>

        {/* Jobs list */}
        {activeJobs.length === 0 ? (
          <div className="py-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/5 mb-4">
              <FileText className="w-8 h-8 text-text-muted" />
            </div>
            <p className="text-sm text-text-muted">No active jobs</p>
            <p className="text-xs text-text-muted mt-1">
              Jobs will appear here when they are running or queued
            </p>
          </div>
        ) : (
          <div className="space-y-3 max-h-[500px] overflow-y-auto">
            {activeJobs.map((job) => (
              <JobItem
                key={job.id}
                job={job}
                onCancel={handleCancel}
                isCanceling={isCanceling && cancelingJobId === job.id}
              />
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
