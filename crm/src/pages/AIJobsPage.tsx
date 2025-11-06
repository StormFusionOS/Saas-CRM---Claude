/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Jobs Page
 * Job scheduling, execution monitoring, and task logs
 */

import React from 'react';
import { useScheduledJobs, useJobs } from '@/lib/ai-queries';
import { ScheduledJobsSection } from '@/components/ai/jobs/ScheduledJobsSection';
import { TaskLogsTable } from '@/components/ai/jobs/TaskLogsTable';
import { ActiveJobsPanel } from '@/components/ai/dashboard/ActiveJobsPanel';

const AIJobsPage: React.FC = () => {
  // Fetch scheduled jobs
  const { data: scheduledJobs, isLoading: scheduledLoading } = useScheduledJobs();

  // Fetch active jobs (running + queued)
  const { data: jobsData, isLoading: jobsLoading } = useJobs();

  // Filter to active jobs only
  const activeJobs = React.useMemo(() => {
    if (!jobsData?.jobs) return [];
    return jobsData.jobs.filter(
      (job) => job.state === 'running' || job.state === 'queued'
    );
  }, [jobsData]);

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">
          AI Jobs & Scheduler
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Job scheduling, execution monitoring, and task logs
        </p>
      </div>

      {/* Main Content */}
      <main className="p-8 space-y-8">
        {/* Active Jobs Panel */}
        {activeJobs.length > 0 && (
          <ActiveJobsPanel jobs={activeJobs} isLoading={jobsLoading} />
        )}

        {/* Scheduled Jobs */}
        <ScheduledJobsSection
          jobs={scheduledJobs || []}
          isLoading={scheduledLoading}
        />

        {/* Task Logs */}
        <TaskLogsTable />
      </main>
    </div>
  );
};

export default AIJobsPage;
