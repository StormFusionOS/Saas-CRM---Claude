/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Suite API Client
 */

import type {
  AIOverview,
  JobsResponse,
  Job,
  PromptTemplate,
  PromptRunRequest,
  PromptRunResponse,
  ValidationResult,
  ScheduledJob,
  TaskLogsFilters,
  TaskLogsResponse,
  HealthSummary,
} from './ai-types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true' || true; // Default to mock for now

// ============================================================================
// Mock Data Generators
// ============================================================================

const generateMockOverview = (): AIOverview => ({
  node: {
    hostname: 'ai-server-prod-01',
    uptime: 2592000, // 30 days in seconds
    os: 'Ubuntu 22.04 LTS',
    model_versions: {
      'gpt-4': '2024-11-01',
      'claude-3.5-sonnet': '2024-10-22',
      'llama-3.1': '70B',
    },
    cpu_count: 32,
    total_ram_gb: 128,
  },
  metrics: {
    cpu: 45 + Math.random() * 20, // 45-65%
    gpu: 30 + Math.random() * 30, // 30-60%
    ram: 60 + Math.random() * 15, // 60-75%
    disk: 55 + Math.random() * 10, // 55-65%
    network: 150 + Math.random() * 50, // 150-200 Mbps
    timestamp: new Date().toISOString(),
  },
  thresholds: {
    warning: 75,
    critical: 90,
  },
  active_jobs_count: 3,
  queued_jobs_count: 2,
});

const generateMockJobs = (state?: string): Job[] => {
  const jobs: Job[] = [
    {
      id: 1,
      name: 'Content Generation - Blog Posts',
      state: 'running',
      progress: 67,
      eta: new Date(Date.now() + 300000).toISOString(),
      started_at: new Date(Date.now() - 600000).toISOString(),
      template_id: 5,
      created_by: 'admin@rivercityclean.com',
    },
    {
      id: 2,
      name: 'SEO Keyword Analysis',
      state: 'running',
      progress: 42,
      eta: new Date(Date.now() + 800000).toISOString(),
      started_at: new Date(Date.now() - 400000).toISOString(),
      template_id: 12,
    },
    {
      id: 3,
      name: 'Competitor Research',
      state: 'running',
      progress: 89,
      eta: new Date(Date.now() + 60000).toISOString(),
      started_at: new Date(Date.now() - 900000).toISOString(),
    },
    {
      id: 4,
      name: 'Email Campaign Draft',
      state: 'queued',
      progress: 0,
      created_by: 'marketing@rivercityclean.com',
    },
    {
      id: 5,
      name: 'Social Media Content',
      state: 'queued',
      progress: 0,
    },
  ];

  return state ? jobs.filter(j => j.state === state) : jobs;
};

const generateMockPromptTemplates = (): PromptTemplate[] => [
  {
    id: 1,
    name: 'Blog Post Generator',
    description: 'Generate SEO-optimized blog posts from keywords',
    template: 'Write a comprehensive blog post about {{topic}}...',
    version: '2.3.0',
    tags: ['content', 'seo', 'blog'],
    metrics: {
      success_rate: 94.5,
      total_runs: 1247,
      avg_duration: 12.3,
      rejection_count: 68,
    },
    created_at: '2024-09-15T10:00:00Z',
    updated_at: '2025-01-10T14:30:00Z',
    is_active: true,
  },
  {
    id: 2,
    name: 'Email Campaign Writer',
    description: 'Create engaging email campaigns',
    template: 'Create an email campaign for {{product}}...',
    version: '1.8.2',
    tags: ['email', 'marketing'],
    metrics: {
      success_rate: 91.2,
      total_runs: 834,
      avg_duration: 8.7,
      rejection_count: 73,
    },
    created_at: '2024-08-20T09:00:00Z',
    updated_at: '2024-12-05T16:20:00Z',
    is_active: true,
  },
  {
    id: 3,
    name: 'Social Media Post',
    description: 'Generate social media content',
    template: 'Create engaging social media posts for {{platform}}...',
    version: '3.1.0',
    tags: ['social', 'content'],
    metrics: {
      success_rate: 96.8,
      total_runs: 2156,
      avg_duration: 5.2,
      rejection_count: 69,
    },
    created_at: '2024-07-10T11:00:00Z',
    updated_at: '2025-01-15T10:45:00Z',
    is_active: true,
  },
];

const generateMockHealthSummary = (): HealthSummary => ({
  overall: 'healthy',
  services: {
    ai_server: 'healthy',
    database: 'healthy',
    storage: 'healthy',
    api: 'healthy',
  },
  issues: [],
  last_check: new Date().toISOString(),
});

// ============================================================================
// API Client
// ============================================================================

class AIAPIClient {
  private baseURL: string;
  private useMock: boolean;

  constructor(baseURL: string = API_BASE_URL, useMock: boolean = USE_MOCK_DATA) {
    this.baseURL = baseURL;
    this.useMock = useMock;
  }

  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    if (this.useMock) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));
      return this.getMockResponse<T>(endpoint);
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  private getMockResponse<T>(endpoint: string): T {
    // Route mock responses based on endpoint
    if (endpoint === '/api/ai/overview') {
      return generateMockOverview() as T;
    }
    if (endpoint.startsWith('/api/ai/jobs')) {
      const params = new URLSearchParams(endpoint.split('?')[1]);
      const state = params.get('state');
      const jobs = generateMockJobs(state || undefined);
      return { jobs, total: jobs.length } as T;
    }
    if (endpoint === '/api/prompts/templates') {
      return generateMockPromptTemplates() as T;
    }
    if (endpoint === '/api/health/summary') {
      return generateMockHealthSummary() as T;
    }
    throw new Error(`Mock not implemented for: ${endpoint}`);
  }

  // ============================================================================
  // Overview Endpoints
  // ============================================================================

  async getOverview(): Promise<AIOverview> {
    return this.fetch<AIOverview>('/api/ai/overview');
  }

  // ============================================================================
  // Jobs Endpoints
  // ============================================================================

  async getJobs(state?: string): Promise<JobsResponse> {
    const params = state ? `?state=${state}` : '';
    return this.fetch<JobsResponse>(`/api/ai/jobs${params}`);
  }

  async cancelJob(jobId: number): Promise<void> {
    return this.fetch<void>(`/api/ai/jobs/${jobId}/cancel`, {
      method: 'POST',
    });
  }

  // ============================================================================
  // Prompts Endpoints
  // ============================================================================

  async getPromptTemplates(): Promise<PromptTemplate[]> {
    return this.fetch<PromptTemplate[]>('/api/prompts/templates');
  }

  async getPromptTemplate(id: number): Promise<PromptTemplate> {
    return this.fetch<PromptTemplate>(`/api/prompts/templates/${id}`);
  }

  async createPromptTemplate(template: Omit<PromptTemplate, 'id' | 'created_at' | 'updated_at' | 'metrics'>): Promise<PromptTemplate> {
    return this.fetch<PromptTemplate>('/api/prompts/templates', {
      method: 'POST',
      body: JSON.stringify(template),
    });
  }

  async updatePromptTemplate(id: number, template: Partial<PromptTemplate>): Promise<PromptTemplate> {
    return this.fetch<PromptTemplate>(`/api/prompts/templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(template),
    });
  }

  async deletePromptTemplate(id: number): Promise<void> {
    return this.fetch<void>(`/api/prompts/templates/${id}`, {
      method: 'DELETE',
    });
  }

  async runPrompt(request: PromptRunRequest): Promise<PromptRunResponse> {
    return this.fetch<PromptRunResponse>('/api/prompts/run', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async validatePrompt(request: PromptRunRequest): Promise<ValidationResult> {
    return this.fetch<ValidationResult>('/api/prompts/validate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // ============================================================================
  // Scheduler Endpoints
  // ============================================================================

  async getScheduledJobs(): Promise<ScheduledJob[]> {
    return this.fetch<ScheduledJob[]>('/api/scheduler/jobs');
  }

  async runScheduledJob(jobId: number): Promise<void> {
    return this.fetch<void>(`/api/scheduler/jobs/${jobId}/run`, {
      method: 'POST',
    });
  }

  async toggleScheduledJob(jobId: number): Promise<ScheduledJob> {
    return this.fetch<ScheduledJob>(`/api/scheduler/jobs/${jobId}/toggle`, {
      method: 'POST',
    });
  }

  async getTaskLogs(filters: TaskLogsFilters): Promise<TaskLogsResponse> {
    const params = new URLSearchParams();
    if (filters.job_id) params.append('job_id', filters.job_id.toString());
    if (filters.status) params.append('status', filters.status);
    if (filters.from) params.append('from', filters.from);
    if (filters.to) params.append('to', filters.to);
    params.append('page', (filters.page || 1).toString());
    params.append('page_size', (filters.page_size || 20).toString());

    return this.fetch<TaskLogsResponse>(`/api/task-logs?${params.toString()}`);
  }

  // ============================================================================
  // Health Endpoints
  // ============================================================================

  async getHealthSummary(): Promise<HealthSummary> {
    return this.fetch<HealthSummary>('/api/health/summary');
  }
}

// Export singleton instance
export const aiAPI = new AIAPIClient();

// Export class for testing
export { AIAPIClient };
