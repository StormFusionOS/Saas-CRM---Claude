/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Review Queue Table
 * Virtualized table with row drawer for reviewing AI-generated changes
 */

import React, { useState, useRef, useMemo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Drawer } from 'vaul';
import { ChangeLog } from '../../lib/governance-api';
import { useReviewQueue, useReviewActions } from '../../hooks/useReviewQueue';
import { ApproveModal, RejectModal } from './ConfirmationModals';
import DiffViewer from './DiffViewer';
import Button from '../ui/Button';
import Card from '../ui/Card';
import {
  ChevronRight,
  ChevronLeft,
  Filter,
  X,
  Clock,
  Sparkles,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';

interface ReviewQueueTableProps {
  moduleFilter?: string;
  onModuleFilterChange?: (module: string) => void;
}

const ReviewQueueTable: React.FC<ReviewQueueTableProps> = ({
  moduleFilter = '',
  onModuleFilterChange,
}) => {
  // State
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [selectedChange, setSelectedChange] = useState<ChangeLog | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [approveModalOpen, setApproveModalOpen] = useState(false);
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [actionChangeId, setActionChangeId] = useState('');

  // Refs
  const parentRef = useRef<HTMLDivElement>(null);

  // Fetch data
  const { changes, total, has_more, loading, error, refetch } = useReviewQueue({
    module: moduleFilter,
    page,
    limit,
  });

  // Actions
  const { approve, reject, loading: actionLoading, error: actionError } = useReviewActions(refetch);

  // Virtualizer
  const rowVirtualizer = useVirtualizer({
    count: changes.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 5,
  });

  // Formatters
  const formatAge = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 1) return 'just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return '1 day ago';
    return `${diffDays} days ago`;
  };

  const getConfidenceBadge = (confidence: number | null) => {
    if (!confidence) return null;

    const percent = Math.round(confidence * 100);
    let color = 'text-text-muted bg-white/10';

    if (confidence >= 0.9) color = 'text-success bg-success/20';
    else if (confidence >= 0.7) color = 'text-warning bg-warning/20';
    else color = 'text-error bg-error/20';

    return (
      <span className={`px-2 py-0.5 rounded text-xs font-medium ${color}`}>
        {percent}%
      </span>
    );
  };

  // Handlers
  const handleRowClick = (change: ChangeLog) => {
    setSelectedChange(change);
    setDrawerOpen(true);
  };

  const handleApproveClick = (changeId: string, e?: React.MouseEvent) => {
    e?.stopPropagation();
    setActionChangeId(changeId);
    setApproveModalOpen(true);
  };

  const handleRejectClick = (changeId: string, e?: React.MouseEvent) => {
    e?.stopPropagation();
    setActionChangeId(changeId);
    setRejectModalOpen(true);
  };

  const handleApproveConfirm = async (reason?: string) => {
    const success = await approve(actionChangeId, reason);
    if (success) {
      setApproveModalOpen(false);
      setDrawerOpen(false);
      setSelectedChange(null);
    }
  };

  const handleRejectConfirm = async (reason: string) => {
    const success = await reject(actionChangeId, reason);
    if (success) {
      setRejectModalOpen(false);
      setDrawerOpen(false);
      setSelectedChange(null);
    }
  };

  // Loading state
  if (loading && changes.length === 0) {
    return (
      <Card padding="lg">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-white/10 rounded w-1/4"></div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-14 bg-white/10 rounded"></div>
          ))}
        </div>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card padding="lg" className="border-error/50">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="w-6 h-6 text-error" />
          <div>
            <h3 className="text-lg font-display font-semibold text-error">Error Loading Queue</h3>
            <p className="text-sm text-text-muted mt-1">{error}</p>
          </div>
        </div>
        <Button variant="outline" onClick={refetch}>
          Retry
        </Button>
      </Card>
    );
  }

  // Empty state
  if (changes.length === 0) {
    return (
      <Card padding="lg">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✨</div>
          <h3 className="text-xl font-display font-semibold text-text-primary mb-2">
            All Caught Up!
          </h3>
          <p className="text-text-muted">
            No pending changes to review{moduleFilter ? ` in ${moduleFilter}` : ''}.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card padding="none" className="overflow-hidden">
        {/* Table Header */}
        <div className="border-b border-white/10 bg-bg-elev px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-display font-semibold text-text-primary">
                Review Queue
              </h3>
              <p className="text-sm text-text-muted mt-1">
                {total} pending {total === 1 ? 'change' : 'changes'}
              </p>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center gap-3">
              <div className="text-sm text-text-muted">
                Page {page} {has_more && 'of many'}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1 || loading}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!has_more || loading}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Virtualized Table */}
        <div
          ref={parentRef}
          className="h-[600px] overflow-auto"
          style={{ contain: 'strict' }}
        >
          <div
            style={{
              height: `${rowVirtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {/* Table Header */}
            <div className="sticky top-0 z-10 bg-bg-elev border-b border-white/10">
              <div className="grid grid-cols-12 gap-4 px-6 py-3 text-sm font-medium text-text-secondary">
                <div className="col-span-2">Module</div>
                <div className="col-span-2">Action</div>
                <div className="col-span-2">Target</div>
                <div className="col-span-2">Reasoning</div>
                <div className="col-span-1 text-center">Confidence</div>
                <div className="col-span-1">Age</div>
                <div className="col-span-2 text-right">Actions</div>
              </div>
            </div>

            {/* Virtualized Rows */}
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const change = changes[virtualRow.index];

              return (
                <div
                  key={virtualRow.key}
                  data-index={virtualRow.index}
                  ref={rowVirtualizer.measureElement}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
                  onClick={() => handleRowClick(change)}
                >
                  <div className="grid grid-cols-12 gap-4 px-6 py-4 items-center">
                    {/* Module */}
                    <div className="col-span-2">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-primary" />
                        <span className="text-sm font-mono text-primary truncate">
                          {change.module}
                        </span>
                      </div>
                    </div>

                    {/* Action */}
                    <div className="col-span-2">
                      <span className="text-sm text-text-secondary truncate">
                        {change.action}
                      </span>
                    </div>

                    {/* Target */}
                    <div className="col-span-2">
                      <span className="text-sm text-text-muted truncate">
                        {change.target_type} #{change.target_id}
                      </span>
                    </div>

                    {/* Reasoning */}
                    <div className="col-span-2">
                      <span className="text-sm text-text-muted truncate line-clamp-1">
                        {change.reasoning || 'No reasoning provided'}
                      </span>
                    </div>

                    {/* Confidence */}
                    <div className="col-span-1 flex justify-center">
                      {getConfidenceBadge(change.ai_confidence)}
                    </div>

                    {/* Age */}
                    <div className="col-span-1">
                      <div className="flex items-center gap-1 text-sm text-text-muted">
                        <Clock className="w-3 h-3" />
                        {formatAge(change.created_at)}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="col-span-2 flex justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => handleRejectClick(change.change_id, e)}
                        className="text-error border-error/30 hover:bg-error/10"
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Reject
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => handleApproveClick(change.change_id, e)}
                        className="text-success border-success/30 hover:bg-success/10"
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Approve
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 bg-bg-base/50 flex items-center justify-center">
            <div className="bg-bg-elev px-6 py-4 rounded-lg shadow-lg">
              <div className="text-sm text-text-primary">Loading...</div>
            </div>
          </div>
        )}
      </Card>

      {/* Row Drawer */}
      <Drawer.Root open={drawerOpen} onOpenChange={setDrawerOpen}>
        <Drawer.Portal>
          <Drawer.Overlay className="fixed inset-0 bg-black/40 z-40" />
          <Drawer.Content className="fixed bottom-0 left-0 right-0 max-h-[85vh] z-50 bg-bg-elev rounded-t-2xl border-t border-white/10 flex flex-col">
            {/* Drawer Handle */}
            <div className="mx-auto w-12 h-1.5 flex-shrink-0 rounded-full bg-white/20 my-4" />

            {/* Drawer Header */}
            <div className="px-6 pb-4 border-b border-white/10">
              <div className="flex items-start justify-between">
                <div>
                  <Drawer.Title className="text-xl font-display font-bold text-text-primary">
                    Review Change
                  </Drawer.Title>
                  <Drawer.Description className="text-sm text-text-muted mt-1">
                    {selectedChange?.change_id}
                  </Drawer.Description>
                </div>
                <Drawer.Close className="text-text-muted hover:text-text-primary transition-colors">
                  <X className="w-5 h-5" />
                </Drawer.Close>
              </div>
            </div>

            {/* Drawer Content */}
            <div className="flex-1 overflow-y-auto px-6 py-6">
              {selectedChange && (
                <div className="space-y-6 max-w-5xl mx-auto">
                  {/* Metadata */}
                  <div className="grid grid-cols-2 gap-4">
                    <Card padding="md">
                      <div className="text-sm font-medium text-text-secondary mb-1">Module</div>
                      <div className="text-text-primary font-mono">{selectedChange.module}</div>
                    </Card>
                    <Card padding="md">
                      <div className="text-sm font-medium text-text-secondary mb-1">Action</div>
                      <div className="text-text-primary">{selectedChange.action}</div>
                    </Card>
                    <Card padding="md">
                      <div className="text-sm font-medium text-text-secondary mb-1">Target</div>
                      <div className="text-text-primary">
                        {selectedChange.target_type} #{selectedChange.target_id}
                      </div>
                    </Card>
                    <Card padding="md">
                      <div className="text-sm font-medium text-text-secondary mb-1">Confidence</div>
                      <div className="text-text-primary">
                        {selectedChange.ai_confidence
                          ? `${Math.round(selectedChange.ai_confidence * 100)}%`
                          : 'N/A'}
                      </div>
                    </Card>
                  </div>

                  {/* AI Reasoning */}
                  {selectedChange.reasoning && (
                    <Card padding="md">
                      <div className="text-sm font-medium text-text-secondary mb-2">AI Reasoning</div>
                      <p className="text-text-primary text-sm leading-relaxed">
                        {selectedChange.reasoning}
                      </p>
                    </Card>
                  )}

                  {/* Diff Viewer */}
                  <DiffViewer
                    oldValue={selectedChange.old_value}
                    newValue={selectedChange.new_value}
                    label="Proposed Changes"
                  />

                  {/* Evidence */}
                  {selectedChange.evidence && (
                    <Card padding="md">
                      <div className="text-sm font-medium text-text-secondary mb-2">Evidence</div>
                      <pre className="text-xs text-text-muted overflow-x-auto">
                        {JSON.stringify(selectedChange.evidence, null, 2)}
                      </pre>
                    </Card>
                  )}
                </div>
              )}
            </div>

            {/* Drawer Footer */}
            <div className="px-6 py-4 border-t border-white/10 bg-bg-base">
              <div className="flex gap-3 max-w-5xl mx-auto">
                <Button
                  variant="outline"
                  onClick={() => setDrawerOpen(false)}
                  className="flex-1"
                >
                  Close
                </Button>
                {selectedChange && (
                  <>
                    <Button
                      variant="outline"
                      onClick={() => handleRejectClick(selectedChange.change_id)}
                      className="flex-1 text-error border-error/30 hover:bg-error/10"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reject
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleApproveClick(selectedChange.change_id)}
                      className="flex-1 text-success border-success/30 hover:bg-success/10"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Approve & Execute
                    </Button>
                  </>
                )}
              </div>
            </div>
          </Drawer.Content>
        </Drawer.Portal>
      </Drawer.Root>

      {/* Confirmation Modals */}
      <ApproveModal
        open={approveModalOpen}
        onClose={() => setApproveModalOpen(false)}
        onConfirm={handleApproveConfirm}
        loading={actionLoading}
        changeId={actionChangeId}
      />

      <RejectModal
        open={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        onConfirm={handleRejectConfirm}
        loading={actionLoading}
        changeId={actionChangeId}
      />

      {/* Action Error */}
      {actionError && (
        <div className="fixed bottom-4 right-4 bg-error/90 text-white px-4 py-3 rounded-lg shadow-lg max-w-md">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <div className="text-sm">{actionError}</div>
          </div>
        </div>
      )}
    </>
  );
};

export default ReviewQueueTable;
