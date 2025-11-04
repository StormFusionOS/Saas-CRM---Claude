/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Change Log Table
 * Full review queue with filtering, sorting, and batch actions
 */

import React, { useState } from 'react';
import { useChangeLogs, useChangeLogActions } from '../../hooks/useGovernance';
import { ChangeLog } from '../../lib/governance-api';
import Button from '../ui/Button';
import Card from '../ui/Card';

interface ChangeLogRowProps {
  change: ChangeLog;
  onApprove: (changeId: string) => void;
  onReject: (changeId: string) => void;
  onViewDetails: (change: ChangeLog) => void;
}

const ChangeLogRow: React.FC<ChangeLogRowProps> = ({
  change,
  onApprove,
  onReject,
  onViewDetails,
}) => {
  const formatAge = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 24) return `${diffHours}h`;
    return `${diffDays}d`;
  };

  const getConfidenceColor = (confidence: number | null) => {
    if (!confidence) return 'text-text-muted';
    if (confidence >= 0.9) return 'text-success';
    if (confidence >= 0.7) return 'text-warning';
    return 'text-error';
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { bg: string; text: string }> = {
      pending: { bg: 'bg-warning/20', text: 'text-warning' },
      approved: { bg: 'bg-success/20', text: 'text-success' },
      rejected: { bg: 'bg-error/20', text: 'text-error' },
      executed: { bg: 'bg-primary/20', text: 'text-primary' },
      reverted: { bg: 'bg-text-muted/20', text: 'text-text-muted' },
    };

    const badge = badges[status] || { bg: 'bg-white/20', text: 'text-white' };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
        {status}
      </span>
    );
  };

  return (
    <tr
      className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
      onClick={() => onViewDetails(change)}
    >
      <td className="px-4 py-3">
        <span className="text-sm font-mono text-primary">{change.module}</span>
      </td>
      <td className="px-4 py-3">
        <span className="text-sm text-text-secondary">{change.action}</span>
      </td>
      <td className="px-4 py-3">
        <span className="text-sm text-text-muted">
          {change.target_type} #{change.target_id}
        </span>
      </td>
      <td className="px-4 py-3 text-right">
        {change.ai_confidence && (
          <span className={`text-sm font-medium ${getConfidenceColor(change.ai_confidence)}`}>
            {Math.round(change.ai_confidence * 100)}%
          </span>
        )}
      </td>
      <td className="px-4 py-3">
        <span className="text-sm text-text-muted">{formatAge(change.created_at)}</span>
      </td>
      <td className="px-4 py-3">{getStatusBadge(change.status)}</td>
      <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
        {change.status === 'pending' && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onReject(change.change_id)}
              className="text-error border-error/50 hover:bg-error/10"
            >
              Reject
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onApprove(change.change_id)}
              className="text-success border-success/50 hover:bg-success/10"
            >
              Approve
            </Button>
          </div>
        )}
      </td>
    </tr>
  );
};

const ChangeLogTable: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [moduleFilter, setModuleFilter] = useState<string>('');
  const [selectedChange, setSelectedChange] = useState<ChangeLog | null>(null);

  const { data: changes, loading, error, refetch } = useChangeLogs({
    status: statusFilter || undefined,
    module: moduleFilter || undefined,
  });

  const { approve, reject, loading: actionLoading } = useChangeLogActions();

  const handleApprove = async (changeId: string) => {
    const reason = prompt('Reason for approval (optional):');
    const success = await approve(changeId, reason || undefined);
    if (success) {
      refetch();
    }
  };

  const handleReject = async (changeId: string) => {
    const reason = prompt('Reason for rejection (required):');
    if (!reason) {
      alert('Rejection reason is required');
      return;
    }
    const success = await reject(changeId, reason);
    if (success) {
      refetch();
    }
  };

  const handleViewDetails = (change: ChangeLog) => {
    setSelectedChange(change);
  };

  const closeDetails = () => {
    setSelectedChange(null);
  };

  if (loading) {
    return (
      <Card padding="lg">
        <div className="animate-pulse">
          <div className="h-8 bg-white/10 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-white/10 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card padding="lg" className="border-error/50">
        <h2 className="text-2xl font-display font-bold mb-4 text-error">Change Log</h2>
        <p className="text-sm text-error mb-4">{error}</p>
        <Button variant="outline" onClick={refetch}>
          Retry
        </Button>
      </Card>
    );
  }

  return (
    <>
      <Card padding="lg">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-display font-bold">Change Log</h2>
          <div className="flex gap-4">
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-white/5 border border-white/10 rounded text-sm focus:outline-none focus:border-primary"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="executed">Executed</option>
              <option value="reverted">Reverted</option>
            </select>

            {/* Refresh Button */}
            <Button variant="outline" onClick={refetch}>
              Refresh
            </Button>
          </div>
        </div>

        {!changes || changes.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">✨</div>
            <p className="text-xl text-text-secondary font-medium mb-2">All caught up!</p>
            <p className="text-text-muted">
              No {statusFilter ? statusFilter : ''} changes to display.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                    Module
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                    Action
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">
                    Target
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-text-secondary">
                    Confidence
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
                {changes.map((change) => (
                  <ChangeLogRow
                    key={change.change_id}
                    change={change}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    onViewDetails={handleViewDetails}
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

      {/* Details Modal */}
      {selectedChange && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={closeDetails}
        >
          <Card
            padding="lg"
            className="max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e: React.MouseEvent) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-xl font-display font-bold mb-1">Change Details</h3>
                <p className="text-sm text-text-muted">{selectedChange.change_id}</p>
              </div>
              <button
                onClick={closeDetails}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-text-secondary">Module</label>
                <p className="text-text-primary font-mono">{selectedChange.module}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-text-secondary">Action</label>
                <p className="text-text-primary">{selectedChange.action}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-text-secondary">Target</label>
                <p className="text-text-primary">
                  {selectedChange.target_type} #{selectedChange.target_id}
                </p>
              </div>

              {selectedChange.old_value && (
                <div>
                  <label className="text-sm font-medium text-text-secondary">Current Value</label>
                  <pre className="mt-1 p-3 bg-white/5 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedChange.old_value, null, 2)}
                  </pre>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-text-secondary">Proposed Value</label>
                <pre className="mt-1 p-3 bg-white/5 rounded text-sm overflow-x-auto">
                  {JSON.stringify(selectedChange.new_value, null, 2)}
                </pre>
              </div>

              {selectedChange.reasoning && (
                <div>
                  <label className="text-sm font-medium text-text-secondary">AI Reasoning</label>
                  <p className="mt-1 text-text-primary">{selectedChange.reasoning}</p>
                </div>
              )}

              {selectedChange.ai_confidence && (
                <div>
                  <label className="text-sm font-medium text-text-secondary">Confidence</label>
                  <p className="text-text-primary">
                    {Math.round(selectedChange.ai_confidence * 100)}%
                  </p>
                </div>
              )}

              {selectedChange.evidence && (
                <div>
                  <label className="text-sm font-medium text-text-secondary">Evidence</label>
                  <pre className="mt-1 p-3 bg-white/5 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedChange.evidence, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6 pt-6 border-t border-white/10">
              <Button variant="outline" onClick={closeDetails} className="flex-1">
                Close
              </Button>
              {selectedChange.status === 'pending' && (
                <>
                  <Button
                    variant="outline"
                    onClick={() => {
                      handleReject(selectedChange.change_id);
                      closeDetails();
                    }}
                    className="flex-1 text-error border-error/50 hover:bg-error/10"
                  >
                    Reject
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      handleApprove(selectedChange.change_id);
                      closeDetails();
                    }}
                    className="flex-1 text-success border-success/50 hover:bg-success/10"
                  >
                    Approve
                  </Button>
                </>
              )}
            </div>
          </Card>
        </div>
      )}
    </>
  );
};

export default ChangeLogTable;
