/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * React hooks for governance data fetching
 */

import { useState, useEffect, useCallback } from 'react';
import governanceAPI, {
  ChangeLog,
  TaskLog,
  AuditIssue,
  ModuleConfig,
  GovernanceSummary,
} from '../lib/governance-api';

interface UseDataResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching governance summary/dashboard metrics
 */
export function useGovernanceSummary(): UseDataResult<GovernanceSummary> {
  const [data, setData] = useState<GovernanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const summary = await governanceAPI.getSummary();
      setData(summary);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch summary');
      console.error('Error fetching governance summary:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for fetching change logs (review queue)
 */
export function useChangeLogs(params?: {
  status?: string;
  module?: string;
  limit?: number;
}): UseDataResult<ChangeLog[]> {
  const [data, setData] = useState<ChangeLog[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await governanceAPI.getChangeLogs(params);
      setData(result.changes);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch change logs');
      console.error('Error fetching change logs:', err);
    } finally {
      setLoading(false);
    }
  }, [params?.status, params?.module, params?.limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for fetching task logs
 */
export function useTaskLogs(params?: {
  status?: string;
  job_name?: string;
  limit?: number;
}): UseDataResult<TaskLog[]> {
  const [data, setData] = useState<TaskLog[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await governanceAPI.getTaskLogs(params);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch task logs');
      console.error('Error fetching task logs:', err);
    } finally {
      setLoading(false);
    }
  }, [params?.status, params?.job_name, params?.limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for fetching audit issues
 */
export function useAuditIssues(params?: {
  status?: string;
  severity?: string;
  limit?: number;
}): UseDataResult<AuditIssue[]> {
  const [data, setData] = useState<AuditIssue[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await governanceAPI.getAuditIssues(params);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch audit issues');
      console.error('Error fetching audit issues:', err);
    } finally {
      setLoading(false);
    }
  }, [params?.status, params?.severity, params?.limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for fetching module configurations
 */
export function useModuleConfigs(): UseDataResult<ModuleConfig[]> {
  const [data, setData] = useState<ModuleConfig[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const configs = await governanceAPI.getModuleConfigs();
      setData(configs);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch module configs');
      console.error('Error fetching module configs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for change log actions (approve, reject, execute)
 */
export function useChangeLogActions() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const approve = async (changeId: string, reason?: string) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.approveChange(changeId, reason);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to approve change');
      console.error('Error approving change:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const reject = async (changeId: string, reason: string) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.rejectChange(changeId, reason);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to reject change');
      console.error('Error rejecting change:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const execute = async (changeId: string) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.executeChange(changeId);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to execute change');
      console.error('Error executing change:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const revert = async (changeId: string, reason: string) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.revertChange(changeId, reason);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to revert change');
      console.error('Error reverting change:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    approve,
    reject,
    execute,
    revert,
    loading,
    error,
  };
}

/**
 * Hook for audit issue actions
 */
export function useAuditIssueActions() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const acknowledge = async (issueId: number) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.acknowledgeIssue(issueId);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to acknowledge issue');
      console.error('Error acknowledging issue:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const resolve = async (issueId: number, notes?: string) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.resolveIssue(issueId, notes);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to resolve issue');
      console.error('Error resolving issue:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const ignore = async (issueId: number, notes?: string) => {
    try {
      setLoading(true);
      setError(null);
      await governanceAPI.ignoreIssue(issueId, notes);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to ignore issue');
      console.error('Error ignoring issue:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    acknowledge,
    resolve,
    ignore,
    loading,
    error,
  };
}
