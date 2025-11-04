/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Review Queue Widget
 * Shows top pending AI-generated changes awaiting approval
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../ui/Card';
import Button from '../ui/Button';
import { useChangeLogs, useChangeLogActions } from '../../hooks/useGovernance';
import { ChangeLog } from '../../lib/governance-api';

interface ReviewQueueItemProps {
  change: ChangeLog;
  onApprove: (changeId: string) => void;
  onReject: (changeId: string) => void;
}

const ReviewQueueItem: React.FC<ReviewQueueItemProps> = ({ change, onApprove, onReject }) => {
  const getConfidenceColor = (confidence: number | null) => {
    if (!confidence) return 'text-text-muted';
    if (confidence >= 0.9) return 'text-success';
    if (confidence >= 0.7) return 'text-warning';
    return 'text-error';
  };

  const formatAge = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-mono text-primary">{change.module}</span>
          <span className="text-xs text-text-muted">→</span>
          <span className="text-xs text-text-secondary">{change.action}</span>
        </div>
        <p className="text-sm text-text-primary">
          {change.target_type} #{change.target_id}
        </p>
        <div className="flex items-center gap-3 mt-1">
          {change.ai_confidence && (
            <span className={`text-xs font-medium ${getConfidenceColor(change.ai_confidence)}`}>
              {Math.round(change.ai_confidence * 100)}% confidence
            </span>
          )}
          <span className="text-xs text-text-muted">{formatAge(change.created_at)}</span>
        </div>
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onReject(change.change_id)}
          className="text-error border-error/50 hover:bg-error/10"
        >
          ✗
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onApprove(change.change_id)}
          className="text-success border-success/50 hover:bg-success/10"
        >
          ✓
        </Button>
      </div>
    </div>
  );
};

const ReviewQueueWidget: React.FC = () => {
  const navigate = useNavigate();
  const { data: changes, loading, error, refetch } = useChangeLogs({ status: 'pending', limit: 5 });
  const { approve, reject, loading: actionLoading } = useChangeLogActions();

  const handleApprove = async (changeId: string) => {
    const success = await approve(changeId, 'Approved from dashboard');
    if (success) {
      refetch();
    }
  };

  const handleReject = async (changeId: string) => {
    const reason = prompt('Reason for rejection (optional):');
    const success = await reject(changeId, reason || 'Rejected from dashboard');
    if (success) {
      refetch();
    }
  };

  if (loading) {
    return (
      <Card padding="lg">
        <div className="animate-pulse">
          <div className="h-6 bg-white/10 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-white/10 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card padding="lg" className="border-error/50">
        <h2 className="text-xl font-display font-semibold mb-4 text-error">Review Queue</h2>
        <p className="text-sm text-error">{error}</p>
        <Button variant="outline" size="sm" onClick={refetch} className="mt-4">
          Retry
        </Button>
      </Card>
    );
  }

  const pendingCount = changes?.length || 0;

  return (
    <Card padding="lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-display font-semibold">Review Queue</h2>
          <p className="text-sm text-text-muted mt-1">
            {pendingCount} pending {pendingCount === 1 ? 'change' : 'changes'}
          </p>
        </div>
        {pendingCount > 0 && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-warning animate-pulse" />
            <span className="text-xs text-warning">Needs review</span>
          </div>
        )}
      </div>

      {pendingCount === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">✨</div>
          <p className="text-text-secondary font-medium">All caught up!</p>
          <p className="text-sm text-text-muted mt-1">
            No pending AI suggestions right now.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {changes?.map((change) => (
            <ReviewQueueItem
              key={change.change_id}
              change={change}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-white/10">
        <Button
          variant="outline"
          onClick={() => navigate('/governance/review-queue')}
          className="w-full"
        >
          View All Changes →
        </Button>
      </div>

      {actionLoading && (
        <div className="absolute inset-0 bg-bg-base/50 flex items-center justify-center rounded-lg">
          <div className="text-sm text-text-muted">Processing...</div>
        </div>
      )}
    </Card>
  );
};

export default ReviewQueueWidget;
