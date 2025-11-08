/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Governance API Client
 * Provides methods for interacting with AI governance endpoints
 */

import apiClient from './api';

export interface ChangeLog {
  change_id: string;
  module: string;
  action: string;
  target_type: string;
  target_id: number;
  old_value: any;
  new_value: any;
  reasoning: string | null;
  ai_confidence: number | null;
  evidence: any;
  status: string;
  created_at: string;
  approved_at: string | null;
  rejected_at: string | null;
  executed_at: string | null;
  reverted_at: string | null;
  approved_by: number | null;
  rejected_by: number | null;
  execution_error: string | null;
  rollback_ref: string | null;
}

export interface TaskLog {
  job_name: string;
  job_id: string;
  status: string;
  triggered_by: string;
  inputs: any;
  outputs: any;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  records_processed: number | null;
  changes_generated: number | null;
  errors_count: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuditIssue {
  id: number;
  issue_type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  description: string;
  affected_resource: string | null;
  detected_by: string;
  metadata: any;
  status: 'open' | 'acknowledged' | 'resolved' | 'ignored';
  created_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  resolved_by: number | null;
  resolution_notes: string | null;
  updated_at: string;
}

export interface ModuleConfig {
  module: string;
  operating_mode: 'review' | 'auto';
  enabled: boolean;
  confidence_threshold_auto: number;
  confidence_threshold_review: number;
  daily_limit_pilot: number;
  daily_limit_expand: number;
  daily_limit_full: number;
  current_phase: string;
  graduated_at: string | null;
  graduated_by: number | null;
  last_downgraded_at: string | null;
  downgrade_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface GovernanceSummary {
  change_log: {
    pending: number;
    approved: number;
    rejected: number;
    executed: number;
    reverted: number;
  };
  task_logs: {
    running: number;
    completed: number;
    failed: number;
    timeout: number;
  };
  audit_issues: {
    open: number;
    critical: number;
    error: number;
    warning: number;
  };
  health_status: 'healthy' | 'degraded' | 'critical';
}

/**
 * Governance API Client
 */
export const governanceAPI = {
  // ============================================================================
  // Change Logs (Review Queue)
  // ============================================================================

  /**
   * Get list of pending changes for review (paginated)
   */
  getPendingChanges: async (params?: {
    module?: string;
    page?: number;
    limit?: number;
  }): Promise<{
    changes: ChangeLog[];
    total: number;
    page: number;
    limit: number;
    has_more: boolean;
  }> => {
    const response = await apiClient.get('/ai/review/pending', { params });
    return response.data;
  },

  /**
   * Get list of change log entries (legacy endpoint)
   */
  getChangeLogs: async (params?: {
    status?: string;
    module?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ changes: ChangeLog[]; total: number }> => {
    const response = await apiClient.get('/change-log', { params });
    return response.data;
  },

  /**
   * Get single change log entry by ID (review endpoint)
   */
  getChangeLog: async (changeId: string): Promise<ChangeLog> => {
    const response = await apiClient.get(`/ai/review/${changeId}`);
    return response.data;
  },

  /**
   * Approve a change and execute it
   */
  approveChange: async (changeId: string, reason?: string): Promise<{
    change_id: string;
    status: string;
    message: string;
    task_log_id?: string;
  }> => {
    const response = await apiClient.post(`/ai/review/${changeId}/approve`, {
      decision_reason: reason,
    });
    return response.data;
  },

  /**
   * Reject a change
   */
  rejectChange: async (changeId: string, reason: string): Promise<{
    change_id: string;
    status: string;
    message: string;
    task_log_id?: string;
  }> => {
    const response = await apiClient.post(`/ai/review/${changeId}/reject`, {
      decision_reason: reason,
    });
    return response.data;
  },

  /**
   * Execute an approved change
   */
  executeChange: async (changeId: string): Promise<ChangeLog> => {
    const response = await apiClient.post(`/change-log/${changeId}/execute`);
    return response.data;
  },

  /**
   * Revert an executed change
   */
  revertChange: async (changeId: string, reason: string): Promise<ChangeLog> => {
    const response = await apiClient.post(`/change-log/${changeId}/revert`, {
      revert_reason: reason,
    });
    return response.data;
  },

  // ============================================================================
  // Task Logs
  // ============================================================================

  /**
   * Get list of task log entries
   */
  getTaskLogs: async (params?: {
    status?: string;
    job_name?: string;
    limit?: number;
    offset?: number;
  }): Promise<TaskLog[]> => {
    const response = await apiClient.get('/task-logs', { params });
    return response.data;
  },

  /**
   * Get single task log entry by job ID
   */
  getTaskLog: async (jobId: string): Promise<TaskLog> => {
    const response = await apiClient.get(`/task-logs/${jobId}`);
    return response.data;
  },

  // ============================================================================
  // Audit Issues
  // ============================================================================

  /**
   * Get list of audit issues
   */
  getAuditIssues: async (params?: {
    status?: string;
    severity?: string;
    limit?: number;
    offset?: number;
  }): Promise<AuditIssue[]> => {
    const response = await apiClient.get('/audit-issues', { params });
    return response.data;
  },

  /**
   * Get single audit issue by ID
   */
  getAuditIssue: async (issueId: number): Promise<AuditIssue> => {
    const response = await apiClient.get(`/audit-issues/${issueId}`);
    return response.data;
  },

  /**
   * Acknowledge an audit issue
   */
  acknowledgeIssue: async (issueId: number): Promise<AuditIssue> => {
    const response = await apiClient.put(`/audit-issues/${issueId}`, {
      status: 'acknowledged',
    });
    return response.data;
  },

  /**
   * Resolve an audit issue
   */
  resolveIssue: async (issueId: number, notes?: string): Promise<AuditIssue> => {
    const response = await apiClient.put(`/audit-issues/${issueId}`, {
      status: 'resolved',
      resolution_notes: notes,
    });
    return response.data;
  },

  /**
   * Ignore an audit issue
   */
  ignoreIssue: async (issueId: number, notes?: string): Promise<AuditIssue> => {
    const response = await apiClient.put(`/audit-issues/${issueId}`, {
      status: 'ignored',
      resolution_notes: notes,
    });
    return response.data;
  },

  // ============================================================================
  // Module Configuration
  // ============================================================================

  /**
   * Get all module configurations
   */
  getModuleConfigs: async (): Promise<ModuleConfig[]> => {
    const response = await apiClient.get('/module-config');
    return response.data;
  },

  /**
   * Get single module configuration
   */
  getModuleConfig: async (module: string): Promise<ModuleConfig> => {
    const response = await apiClient.get(`/module-config/${module}`);
    return response.data;
  },

  /**
   * Update module configuration
   */
  updateModuleConfig: async (
    module: string,
    updates: Partial<ModuleConfig>
  ): Promise<ModuleConfig> => {
    const response = await apiClient.put(`/module-config/${module}`, updates);
    return response.data;
  },

  /**
   * Graduate module to auto mode
   */
  graduateModule: async (module: string, notes?: string): Promise<ModuleConfig> => {
    const response = await apiClient.post(`/module-config/${module}/graduate`, {
      graduation_notes: notes,
    });
    return response.data;
  },

  /**
   * Rollback module to review mode
   */
  rollbackModule: async (module: string, reason: string): Promise<ModuleConfig> => {
    const response = await apiClient.post(`/module-config/${module}/rollback-to-review`, {
      rollback_reason: reason,
    });
    return response.data;
  },

  // ============================================================================
  // Dashboard Summary
  // ============================================================================

  /**
   * Get governance dashboard summary
   */
  getSummary: async (): Promise<GovernanceSummary> => {
    const response = await apiClient.get('/governance/summary');
    return response.data;
  },
};

export default governanceAPI;
