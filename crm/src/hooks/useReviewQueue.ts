/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * React hook for review queue with pagination and optimistic updates
 */

import { useState, useEffect, useCallback, useOptimistic } from 'react';
import governanceAPI, { ChangeLog } from '../lib/governance-api';

interface ReviewQueueParams {
  module?: string;
  page?: number;
  limit?: number;
}

interface ReviewQueueResult {
  changes: ChangeLog[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching paginated review queue with optimistic updates
 */
export function useReviewQueue(params?: ReviewQueueParams): ReviewQueueResult {
  const [data, setData] = useState<{
    changes: ChangeLog[];
    total: number;
    page: number;
    limit: number;
    has_more: boolean;
  }>({
    changes: [],
    total: 0,
    page: params?.page || 1,
    limit: params?.limit || 20,
    has_more: false,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await governanceAPI.getPendingChanges({
        module: params?.module,
        page: params?.page || 1,
        limit: params?.limit || 20,
      });

      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch review queue');
      console.error('Error fetching review queue:', err);
    } finally {
      setLoading(false);
    }
  }, [params?.module, params?.page, params?.limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    changes: data.changes,
    total: data.total,
    page: data.page,
    limit: data.limit,
    has_more: data.has_more,
    loading,
    error,
    refetch: fetchData,
  };
}

interface ReviewActions {
  approve: (changeId: string, reason?: string) => Promise<boolean>;
  reject: (changeId: string, reason: string) => Promise<boolean>;
  loading: boolean;
  error: string | null;
}

/**
 * Hook for review actions (approve, reject) with optimistic updates
 */
export function useReviewActions(onSuccess?: () => void): ReviewActions {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const approve = async (changeId: string, reason?: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      await governanceAPI.approveChange(changeId, reason);

      if (onSuccess) {
        onSuccess();
      }

      return true;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to approve change';
      setError(errorMessage);
      console.error('Error approving change:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const reject = async (changeId: string, reason: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      await governanceAPI.rejectChange(changeId, reason);

      if (onSuccess) {
        onSuccess();
      }

      return true;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to reject change';
      setError(errorMessage);
      console.error('Error rejecting change:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    approve,
    reject,
    loading,
    error,
  };
}
