/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Confirmation Modals for Review Actions
 * Accessible dialogs for approve/reject confirmations
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import Button from '../ui/Button';
import { AlertTriangle, CheckCircle } from 'lucide-react';

interface ApproveModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (reason?: string) => void;
  loading?: boolean;
  changeId: string;
}

export function ApproveModal({ open, onClose, onConfirm, loading, changeId }: ApproveModalProps) {
  const [reason, setReason] = useState('');

  const handleConfirm = () => {
    onConfirm(reason || undefined);
    setReason('');
  };

  const handleClose = () => {
    setReason('');
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-success" />
            </div>
            <div>
              <DialogTitle>Approve Change</DialogTitle>
              <DialogDescription>
                This change will be approved and executed immediately.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="bg-bg-base rounded-lg p-3 border border-white/10">
            <div className="text-sm font-mono text-text-muted">Change ID</div>
            <div className="text-sm font-mono text-primary mt-1">{changeId}</div>
          </div>

          <div className="space-y-2">
            <label htmlFor="approve-reason" className="text-sm font-medium text-text-secondary">
              Reason for approval (optional)
            </label>
            <textarea
              id="approve-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g., SEO improvement looks good, implementing..."
              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-success/50 resize-none"
              rows={3}
              disabled={loading}
            />
          </div>

          <div className="bg-warning/10 border border-warning/20 rounded-lg p-3">
            <div className="flex gap-2">
              <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0 mt-0.5" />
              <div className="text-xs text-warning">
                This action will execute the change immediately and cannot be undone without reverting.
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={loading}
            className="bg-success hover:bg-success/90 text-white"
          >
            {loading ? 'Approving...' : 'Approve & Execute'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface RejectModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => void;
  loading?: boolean;
  changeId: string;
}

export function RejectModal({ open, onClose, onConfirm, loading, changeId }: RejectModalProps) {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  const handleConfirm = () => {
    if (!reason.trim()) {
      setError('Rejection reason is required');
      return;
    }

    onConfirm(reason);
    setReason('');
    setError('');
  };

  const handleClose = () => {
    setReason('');
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-error" />
            </div>
            <div>
              <DialogTitle>Reject Change</DialogTitle>
              <DialogDescription>
                This change will be rejected and will not be executed.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="bg-bg-base rounded-lg p-3 border border-white/10">
            <div className="text-sm font-mono text-text-muted">Change ID</div>
            <div className="text-sm font-mono text-primary mt-1">{changeId}</div>
          </div>

          <div className="space-y-2">
            <label htmlFor="reject-reason" className="text-sm font-medium text-text-secondary">
              Reason for rejection <span className="text-error">*</span>
            </label>
            <textarea
              id="reject-reason"
              value={reason}
              onChange={(e) => {
                setReason(e.target.value);
                setError('');
              }}
              placeholder="e.g., Title change conflicts with brand guidelines..."
              className={`w-full px-3 py-2 bg-white/5 border rounded-lg text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 resize-none ${
                error
                  ? 'border-error focus:ring-error/50'
                  : 'border-white/10 focus:ring-error/50'
              }`}
              rows={3}
              disabled={loading}
              aria-required="true"
              aria-invalid={!!error}
              aria-describedby={error ? 'reject-error' : undefined}
            />
            {error && (
              <p id="reject-error" className="text-xs text-error" role="alert">
                {error}
              </p>
            )}
          </div>

          <div className="bg-error/10 border border-error/20 rounded-lg p-3">
            <div className="text-xs text-error">
              A detailed reason is required to maintain audit trail and help improve AI suggestions.
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={loading}
            className="bg-error hover:bg-error/90 text-white"
          >
            {loading ? 'Rejecting...' : 'Reject Change'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
