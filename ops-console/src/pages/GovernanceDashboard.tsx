/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Governance Dashboard Page
 * Main dashboard for AI governance review queue and system health
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import KPITile from '../components/governance/KPITile';
import ReviewQueueWidget from '../components/governance/ReviewQueueWidget';
import AuditIssuesTable from '../components/governance/AuditIssuesTable';
import { useGovernanceSummary } from '../hooks/useGovernance';
import Card from '../components/ui/Card';

const GovernanceDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: summary, loading, error } = useGovernanceSummary();

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-base p-8">
        <div className="animate-pulse">
          <div className="h-12 bg-white/10 rounded w-1/4 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white/10 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-bg-base p-8">
        <Card padding="lg" className="border-error/50">
          <h1 className="text-3xl font-display font-bold text-error mb-4">
            Governance Dashboard
          </h1>
          <p className="text-error">{error}</p>
        </Card>
      </div>
    );
  }

  const getHealthStatus = () => {
    if (!summary) return { label: 'Unknown', color: 'text-text-muted' };

    if (summary.health_status === 'healthy') {
      return { label: 'Healthy', color: 'text-success' };
    } else if (summary.health_status === 'degraded') {
      return { label: 'Degraded', color: 'text-warning' };
    } else {
      return { label: 'Critical', color: 'text-error' };
    }
  };

  const healthStatus = getHealthStatus();

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold text-gradient">
              AI Governance Dashboard
            </h1>
            <p className="text-sm text-text-muted mt-1">
              Review queue, system health, and automation metrics
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                summary?.health_status === 'healthy'
                  ? 'bg-success'
                  : summary?.health_status === 'degraded'
                  ? 'bg-warning'
                  : 'bg-error'
              } animate-pulse`}
            />
            <span className={`text-sm font-medium ${healthStatus.color}`}>
              {healthStatus.label}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-8">
        {/* KPI Row: AI Governance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <KPITile
            title="Review Queue"
            value={summary?.change_log.pending || 0}
            trend={
              (summary?.change_log.pending || 0) > 0
                ? 'up'
                : 'stable'
            }
            changeType={(summary?.change_log.pending || 0) > 0 ? 'neutral' : 'neutral'}
            onClick={() => navigate('/governance/review-queue')}
            className="cursor-pointer"
          />
          <KPITile
            title="Approved Changes"
            value={summary?.change_log.approved || 0}
            trend="up"
            changeType="increase"
            onClick={() => navigate('/governance/review-queue')}
            className="cursor-pointer"
          />
          <KPITile
            title="Executed Changes"
            value={summary?.change_log.executed || 0}
            trend="up"
            changeType="increase"
            onClick={() => navigate('/governance/review-queue')}
            className="cursor-pointer"
          />
        </div>

        {/* Secondary KPI Row: Task Logs & Issues */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <KPITile
            title="Running Jobs"
            value={summary?.task_logs.running || 0}
            trend={(summary?.task_logs.running || 0) > 0 ? 'up' : 'stable'}
            changeType="neutral"
          />
          <KPITile
            title="Completed Jobs"
            value={summary?.task_logs.completed || 0}
            trend="up"
            changeType="increase"
          />
          <KPITile
            title="Failed Jobs"
            value={summary?.task_logs.failed || 0}
            trend={(summary?.task_logs.failed || 0) > 0 ? 'down' : 'stable'}
            changeType={(summary?.task_logs.failed || 0) > 0 ? 'decrease' : 'neutral'}
          />
          <KPITile
            title="Open Issues"
            value={summary?.audit_issues.open || 0}
            trend={(summary?.audit_issues.open || 0) > 0 ? 'down' : 'stable'}
            changeType={(summary?.audit_issues.open || 0) > 0 ? 'decrease' : 'neutral'}
          />
        </div>

        {/* Review Queue Widget */}
        <div className="mb-8">
          <ReviewQueueWidget />
        </div>

        {/* Audit Issues Table */}
        <div className="mb-8">
          <AuditIssuesTable />
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Change Log Summary */}
          <Card padding="lg">
            <h3 className="text-lg font-display font-semibold mb-4">Change Log Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Pending Review</span>
                <span className="text-lg font-bold text-warning">
                  {summary?.change_log.pending || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Approved</span>
                <span className="text-lg font-bold text-success">
                  {summary?.change_log.approved || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Rejected</span>
                <span className="text-lg font-bold text-error">
                  {summary?.change_log.rejected || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Executed</span>
                <span className="text-lg font-bold text-primary">
                  {summary?.change_log.executed || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Reverted</span>
                <span className="text-lg font-bold text-text-muted">
                  {summary?.change_log.reverted || 0}
                </span>
              </div>
            </div>
          </Card>

          {/* Audit Issues Summary */}
          <Card padding="lg">
            <h3 className="text-lg font-display font-semibold mb-4">Audit Issues Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Open</span>
                <span className="text-lg font-bold text-warning">
                  {summary?.audit_issues.open || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Critical</span>
                <span className="text-lg font-bold text-error">
                  {summary?.audit_issues.critical || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Error</span>
                <span className="text-lg font-bold text-error">
                  {summary?.audit_issues.error || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-text-secondary">Warning</span>
                <span className="text-lg font-bold text-warning">
                  {summary?.audit_issues.warning || 0}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default GovernanceDashboard;
