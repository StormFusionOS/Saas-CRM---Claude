/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Suite Dashboard Page
 * Real-time monitoring and controls for AI infrastructure
 */

import React from 'react';
import { useAIOverview, useJobs } from '@/lib/ai-queries';
import { NodeSummaryCard } from '@/components/ai/dashboard/NodeSummaryCard';
import { LiveMetricRings } from '@/components/ai/dashboard/LiveMetricRings';
import { ActiveJobsPanel } from '@/components/ai/dashboard/ActiveJobsPanel';
import { QuickActionsBar } from '@/components/ai/dashboard/QuickActionsBar';

const AIDashboardPage: React.FC = () => {
  // Fetch overview data with 5-second polling
  const { data: overview, isLoading: overviewLoading } = useAIOverview();

  // Fetch active jobs (running + queued) with 3-second polling
  const { data: jobsData, isLoading: jobsLoading } = useJobs();

  // Filter to only show running and queued jobs
  const activeJobs = React.useMemo(() => {
    if (!jobsData?.jobs) return [];
    return jobsData.jobs.filter(job =>
      job.state === 'running' || job.state === 'queued'
    );
  }, [jobsData]);

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">
          AI Suite Dashboard
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Real-time monitoring and controls for AI infrastructure
        </p>
      </div>

      <main className="p-8 space-y-6">
        {/* Top row: Node Summary + System Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <NodeSummaryCard
            node={overview?.node}
            isLoading={overviewLoading}
          />
          <div className="lg:col-span-2">
            <LiveMetricRings
              metrics={overview?.metrics}
              thresholds={overview?.thresholds}
              isLoading={overviewLoading}
            />
          </div>
        </div>

        {/* Quick Actions */}
        <QuickActionsBar />

        {/* Active Jobs Panel */}
        <ActiveJobsPanel
          jobs={activeJobs}
          isLoading={jobsLoading}
        />
      </main>
    </div>
  );
};

export default AIDashboardPage;
