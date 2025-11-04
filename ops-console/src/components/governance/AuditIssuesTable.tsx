/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Audit Issues Table
 * Displays system health issues with severity indicators
 */

import React, { useState } from 'react';
import { useAuditIssues, useAuditIssueActions } from '../../hooks/useGovernance';
import { AuditIssue } from '../../lib/governance-api';
import Button from '../ui/Button';
import Card from '../ui/Card';

interface AuditIssueRowProps {
  issue: AuditIssue;
  onAcknowledge: (id: number) => void;
  onResolve: (id: number) => void;
  onIgnore: (id: number) => void;
}

const AuditIssueRow: React.FC<AuditIssueRowProps> = ({
  issue,
  onAcknowledge,
  onResolve,
  onIgnore,
}) => {
  const getSeverityBadge = (severity: string) => {
    const badges: Record<string, { bg: string; text: string }> = {
      critical: { bg: 'bg-error', text: 'text-white' },
      error: { bg: 'bg-error/70', text: 'text-white' },
      warning: { bg: 'bg-warning', text: 'text-black' },
      info: { bg: 'bg-primary/50', text: 'text-white' },
    };

    const badge = badges[severity] || { bg: 'bg-white/20', text: 'text-white' };

    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${badge.bg} ${badge.text}`}>
        {severity}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { bg: string; text: string }> = {
      open: { bg: 'bg-warning/20', text: 'text-warning' },
      acknowledged: { bg: 'bg-primary/20', text: 'text-primary' },
      resolved: { bg: 'bg-success/20', text: 'text-success' },
      ignored: { bg: 'bg-text-muted/20', text: 'text-text-muted' },
    };

    const badge = badges[status] || { bg: 'bg-white/20', text: 'text-white' };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
        {status}
      </span>
    );
  };

  const formatAge = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 24) return `${diffHours}h`;
    return `${diffDays}d`;
  };

  const rowClass =
    issue.severity === 'critical'
      ? 'bg-error/10 border-l-4 border-error'
      : issue.severity === 'error'
      ? 'bg-error/5 border-l-4 border-error/70'
      : '';

  return (
    <tr className={`border-b border-white/5 hover:bg-white/5 transition-colors ${rowClass}`}>
      <td className="px-4 py-3">
        <span className="text-sm text-text-muted">{issue.issue_type}</span>
      </td>
      <td className="px-4 py-3">{getSeverityBadge(issue.severity)}</td>
      <td className="px-4 py-3">
        <div>
          <p className="text-sm font-medium text-text-primary">{issue.title}</p>
          <p className="text-xs text-text-muted mt-1 line-clamp-2">{issue.description}</p>
        </div>
      </td>
      <td className="px-4 py-3">
        <span className="text-sm text-text-muted">{issue.affected_resource || '—'}</span>
      </td>
      <td className="px-4 py-3">
        <span className="text-sm text-text-muted">{formatAge(issue.created_at)}</span>
      </td>
      <td className="px-4 py-3">{getStatusBadge(issue.status)}</td>
      <td className="px-4 py-3">
        {issue.status === 'open' && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onAcknowledge(issue.id)}
              className="text-xs"
            >
              Ack
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onResolve(issue.id)}
              className="text-xs text-success border-success/50"
            >
              Resolve
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onIgnore(issue.id)}
              className="text-xs text-text-muted"
            >
              Ignore
            </Button>
          </div>
        )}
      </td>
    </tr>
  );
};

const AuditIssuesTable: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('open');
  const [severityFilter, setSeverityFilter] = useState<string>('');

  const { data: issues, loading, error, refetch } = useAuditIssues({
    status: statusFilter || undefined,
    severity: severityFilter || undefined,
  });

  const { acknowledge, resolve, ignore, loading: actionLoading } = useAuditIssueActions();

  const handleAcknowledge = async (id: number) => {
    const success = await acknowledge(id);
    if (success) refetch();
  };

  const handleResolve = async (id: number) => {
    const notes = prompt('Resolution notes (optional):');
    const success = await resolve(id, notes || undefined);
    if (success) refetch();
  };

  const handleIgnore = async (id: number) => {
    const notes = prompt('Reason for ignoring (optional):');
    const success = await ignore(id, notes || undefined);
    if (success) refetch();
  };

  if (loading) {
    return (
      <Card padding="lg">
        <div className="animate-pulse">
          <div className="h-8 bg-white/10 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-white/10 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card padding="lg" className="border-error/50">
        <h2 className="text-2xl font-display font-bold mb-4 text-error">Audit Issues</h2>
        <p className="text-sm text-error mb-4">{error}</p>
        <Button variant="outline" onClick={refetch}>
          Retry
        </Button>
      </Card>
    );
  }

  const criticalCount = issues?.filter((i) => i.severity === 'critical').length || 0;

  return (
    <Card padding="lg">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-display font-bold">Audit Issues</h2>
          {criticalCount > 0 && (
            <p className="text-sm text-error mt-1">⚠️ {criticalCount} critical issues require attention</p>
          )}
        </div>
        <div className="flex gap-4">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-white/5 border border-white/10 rounded text-sm focus:outline-none focus:border-primary"
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
            <option value="ignored">Ignored</option>
          </select>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-4 py-2 bg-white/5 border border-white/10 rounded text-sm focus:outline-none focus:border-primary"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>

          {/* Refresh Button */}
          <Button variant="outline" onClick={refetch}>
            Refresh
          </Button>
        </div>
      </div>

      {!issues || issues.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✓</div>
          <p className="text-xl text-text-secondary font-medium mb-2">System Healthy</p>
          <p className="text-text-muted">No {statusFilter} issues detected.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Severity
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Issue
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Resource
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Age
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {issues.map((issue) => (
                <AuditIssueRow
                  key={issue.id}
                  issue={issue}
                  onAcknowledge={handleAcknowledge}
                  onResolve={handleResolve}
                  onIgnore={handleIgnore}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {actionLoading && (
        <div className="fixed inset-0 bg-bg-base/50 flex items-center justify-center z-50">
          <div className="bg-bg-elev p-6 rounded-lg shadow-lg">
            <div className="text-center">
              <div className="text-lg text-text-primary mb-2">Processing...</div>
              <div className="text-sm text-text-muted">Please wait</div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default AuditIssuesTable;
