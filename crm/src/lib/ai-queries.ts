/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Suite React Query Hooks
 */

import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { aiAPI } from './ai-api';
import type {
  AIOverview,
  JobsResponse,
  PromptTemplate,
  PromptRunRequest,
  PromptRunResponse,
  ValidationResult,
  ScheduledJob,
  TaskLogsFilters,
  TaskLogsResponse,
  HealthSummary,
} from './ai-types';

// ============================================================================
// Query Keys
// ============================================================================

export const aiKeys = {
  all: ['ai'] as const,
  overview: () => [...aiKeys.all, 'overview'] as const,
  jobs: () => [...aiKeys.all, 'jobs'] as const,
  jobsByState: (state: string) => [...aiKeys.jobs(), state] as const,
  prompts: () => [...aiKeys.all, 'prompts'] as const,
  promptById: (id: number) => [...aiKeys.prompts(), id] as const,
  promptStats: () => [...aiKeys.prompts(), 'stats'] as const,
  scheduler: () => [...aiKeys.all, 'scheduler'] as const,
  scheduledJobs: () => [...aiKeys.scheduler(), 'jobs'] as const,
  taskLogs: (filters: TaskLogsFilters) => [...aiKeys.all, 'task-logs', filters] as const,
  health: () => [...aiKeys.all, 'health'] as const,
};

// ============================================================================
// Overview Hooks
// ============================================================================

export function useAIOverview(options?: Omit<UseQueryOptions<AIOverview>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: aiKeys.overview(),
    queryFn: () => aiAPI.getOverview(),
    refetchInterval: 5000, // Poll every 5 seconds
    ...options,
  });
}

// ============================================================================
// Jobs Hooks
// ============================================================================

export function useJobs(state?: string, options?: Omit<UseQueryOptions<JobsResponse>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: state ? aiKeys.jobsByState(state) : aiKeys.jobs(),
    queryFn: () => aiAPI.getJobs(state),
    refetchInterval: 3000, // Poll every 3 seconds for active jobs
    ...options,
  });
}

export function useCancelJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: number) => aiAPI.cancelJob(jobId),
    onSuccess: () => {
      // Invalidate jobs queries to refetch
      queryClient.invalidateQueries({ queryKey: aiKeys.jobs() });
      queryClient.invalidateQueries({ queryKey: aiKeys.overview() });
    },
  });
}

// ============================================================================
// Prompts Hooks
// ============================================================================

export function usePromptTemplates(options?: Omit<UseQueryOptions<PromptTemplate[]>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: aiKeys.prompts(),
    queryFn: () => aiAPI.getPromptTemplates(),
    staleTime: 30000, // Consider data fresh for 30 seconds
    ...options,
  });
}

export function usePromptTemplate(id: number, options?: Omit<UseQueryOptions<PromptTemplate>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: aiKeys.promptById(id),
    queryFn: () => aiAPI.getPromptTemplate(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreatePromptTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (template: Omit<PromptTemplate, 'id' | 'created_at' | 'updated_at' | 'metrics'>) =>
      aiAPI.createPromptTemplate(template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: aiKeys.prompts() });
    },
  });
}

export function useUpdatePromptTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, template }: { id: number; template: Partial<PromptTemplate> }) =>
      aiAPI.updatePromptTemplate(id, template),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: aiKeys.prompts() });
      queryClient.invalidateQueries({ queryKey: aiKeys.promptById(variables.id) });
    },
  });
}

export function useDeletePromptTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => aiAPI.deletePromptTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: aiKeys.prompts() });
    },
  });
}

export function useRunPrompt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PromptRunRequest) => aiAPI.runPrompt(request),
    onSuccess: () => {
      // Invalidate jobs since a new job may have been created
      queryClient.invalidateQueries({ queryKey: aiKeys.jobs() });
      queryClient.invalidateQueries({ queryKey: aiKeys.overview() });
    },
  });
}

export function useValidatePrompt() {
  return useMutation({
    mutationFn: (request: PromptRunRequest) => aiAPI.validatePrompt(request),
  });
}

// ============================================================================
// Scheduler Hooks
// ============================================================================

export function useScheduledJobs(options?: Omit<UseQueryOptions<ScheduledJob[]>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: aiKeys.scheduledJobs(),
    queryFn: () => aiAPI.getScheduledJobs(),
    staleTime: 60000, // Consider data fresh for 1 minute
    ...options,
  });
}

export function useRunScheduledJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: number) => aiAPI.runScheduledJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: aiKeys.jobs() });
      queryClient.invalidateQueries({ queryKey: aiKeys.overview() });
    },
  });
}

export function useToggleScheduledJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: number) => aiAPI.toggleScheduledJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: aiKeys.scheduledJobs() });
    },
  });
}

export function useTaskLogs(filters: TaskLogsFilters, options?: Omit<UseQueryOptions<TaskLogsResponse>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: aiKeys.taskLogs(filters),
    queryFn: () => aiAPI.getTaskLogs(filters),
    keepPreviousData: true, // Keep old data while fetching new page
    ...options,
  });
}

// ============================================================================
// Health Hooks
// ============================================================================

export function useHealthSummary(options?: Omit<UseQueryOptions<HealthSummary>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: aiKeys.health(),
    queryFn: () => aiAPI.getHealthSummary(),
    refetchInterval: 10000, // Poll every 10 seconds
    ...options,
  });
}
