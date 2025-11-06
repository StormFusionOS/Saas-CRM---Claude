/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Suite TypeScript Interfaces
 */

// ============================================================================
// AI Server Overview Types
// ============================================================================

export interface NodeInfo {
  hostname: string;
  uptime: number; // seconds
  os: string;
  model_versions: Record<string, string>;
  cpu_count: number;
  total_ram_gb: number;
}

export interface SystemMetrics {
  cpu: number;      // 0-100
  gpu: number;      // 0-100
  ram: number;      // 0-100
  disk: number;     // 0-100
  network: number;  // Mbps
  timestamp: string;
}

export interface MetricThresholds {
  warning: number;  // 75
  critical: number; // 90
}

export interface AIOverview {
  node: NodeInfo;
  metrics: SystemMetrics;
  thresholds: MetricThresholds;
  active_jobs_count: number;
  queued_jobs_count: number;
}

// ============================================================================
// Job Types
// ============================================================================

export type JobState = 'running' | 'queued' | 'completed' | 'failed' | 'cancelled';

export interface Job {
  id: number;
  name: string;
  state: JobState;
  progress: number; // 0-100
  eta?: string;     // ISO date
  started_at?: string;
  completed_at?: string;
  template_id?: number;
  error?: string;
  created_by?: string;
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
}

// ============================================================================
// Prompt Template Types
// ============================================================================

export interface PromptMetrics {
  success_rate: number;
  total_runs: number;
  avg_duration: number;
  rejection_count: number;
}

export interface PromptTemplate {
  id: number;
  name: string;
  description: string;
  template: string;
  version: string;
  tags: string[];
  metrics: PromptMetrics;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface PromptRunRequest {
  template_id: number;
  context: Record<string, any>;
  validate?: boolean;
}

export interface PromptRunResponse {
  id: number;
  template_id: number;
  output: string;
  validation_issues?: string[];
  duration: number;
  tokens_used?: number;
  cost?: number;
}

export interface ValidationResult {
  is_valid: boolean;
  issues: string[];
  suggestions?: string[];
}

// ============================================================================
// Job Scheduler Types
// ============================================================================

export interface ScheduledJob {
  id: number;
  name: string;
  description: string;
  schedule: string;      // cron expression
  enabled: boolean;
  last_run?: string;
  next_run: string;
  task_type: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export type TaskLogStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface TaskLog {
  id: number;
  job_id: number;
  job_name: string;
  status: TaskLogStatus;
  started_at: string;
  completed_at?: string;
  duration?: number; // seconds
  output?: string;
  error?: string;
}

export interface TaskLogsFilters {
  job_id?: number;
  status?: TaskLogStatus;
  from?: string;
  to?: string;
  page?: number;
  page_size?: number;
}

export interface TaskLogsResponse {
  logs: TaskLog[];
  total: number;
  page: number;
  page_size: number;
}

// ============================================================================
// Health Status Types
// ============================================================================

export type HealthStatus = 'healthy' | 'degraded' | 'down';

export interface HealthSummary {
  overall: HealthStatus;
  services: {
    ai_server: HealthStatus;
    database: HealthStatus;
    storage: HealthStatus;
    api: HealthStatus;
  };
  issues: string[];
  last_check: string;
}

// ============================================================================
// Quick Actions Types
// ============================================================================

export interface QuickAction {
  id: string;
  label: string;
  icon: string;
  action: () => void | Promise<void>;
  disabled?: boolean;
}

// ============================================================================
// API Response Wrapper
// ============================================================================

export interface APIResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
