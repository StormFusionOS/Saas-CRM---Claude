/**
 * Copyright (c) 2025 River CityClean
 * SPDX-License-Identifier: MIT
 *
 * React hook for streaming Scrape Suite job progress via SSE.
 *
 * Features:
 * - Real-time job status and progress updates
 * - Automatic reconnection with exponential backoff
 * - Clean disconnection on unmount
 * - TypeScript types for events
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// ==============================================================================
// Types
// ==============================================================================

export type JobEventType =
  | 'connected'
  | 'status_change'
  | 'progress'
  | 'completed'
  | 'failed'
  | 'error'
  | 'disconnected';

export interface JobEvent {
  event: JobEventType;
  job_id: string;
  timestamp: string;
  status?: string;
  task_name?: string;
  items_processed?: number;
  items_succeeded?: number;
  items_failed?: number;
  duration_seconds?: number;
  error_message?: string;
  output_summary?: Record<string, any>;
  message?: string;
  started_at?: string;
  completed_at?: string;
}

export interface JobStreamState {
  status: string | null;
  isConnected: boolean;
  itemsProcessed: number;
  itemsSucceeded: number;
  itemsFailed: number;
  taskName: string | null;
  error: string | null;
  lastEvent: JobEvent | null;
  isCompleted: boolean;
}

// ==============================================================================
// Hook
// ==============================================================================

/**
 * Hook for streaming job progress via SSE.
 *
 * @param jobId Job ID to monitor (null to disable streaming)
 * @param options Configuration options
 * @returns Stream state and control functions
 *
 * @example
 * ```tsx
 * const { status, isConnected, itemsProcessed, disconnect } = useScrapeJobStream(jobId);
 *
 * return (
 *   <div>
 *     <div>Status: {status}</div>
 *     <div>Progress: {itemsProcessed}</div>
 *     {isCompleted && <div>Job completed!</div>}
 *   </div>
 * );
 * ```
 */
export function useScrapeJobStream(
  jobId: string | null,
  options: {
    onEvent?: (event: JobEvent) => void;
    onComplete?: (event: JobEvent) => void;
    onError?: (error: string) => void;
    maxRetries?: number;
    retryDelay?: number;
  } = {}
) {
  const {
    onEvent,
    onComplete,
    onError,
    maxRetries = 5,
    retryDelay = 1000,
  } = options;

  // State
  const [state, setState] = useState<JobStreamState>({
    status: null,
    isConnected: false,
    itemsProcessed: 0,
    itemsSucceeded: 0,
    itemsFailed: 0,
    taskName: null,
    error: null,
    lastEvent: null,
    isCompleted: false,
  });

  // Refs for cleanup and reconnection logic
  const eventSourceRef = useRef<EventSource | null>(null);
  const retryCountRef = useRef(0);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldConnectRef = useRef(true);

  /**
   * Connect to SSE stream
   */
  const connect = useCallback(() => {
    if (!jobId || !shouldConnectRef.current) return;

    // Get auth token from localStorage
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.error('[useScrapeJobStream] No auth token found');
      setState(prev => ({
        ...prev,
        error: 'Authentication required',
        isConnected: false,
      }));
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      // Build SSE URL with auth token as query param
      // (EventSource doesn't support custom headers, so we pass token in URL)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const url = `${apiUrl}/api/v1/scrape/stream/job/${jobId}?token=${token}`;

      console.log(`[useScrapeJobStream] Connecting to ${jobId}...`);

      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle messages
      eventSource.onmessage = (e) => {
        try {
          const event: JobEvent = JSON.parse(e.data);
          console.log('[useScrapeJobStream] Event:', event);

          // Update state based on event type
          setState(prev => {
            const newState: JobStreamState = {
              ...prev,
              lastEvent: event,
              isConnected: event.event !== 'disconnected',
            };

            // Handle specific event types
            switch (event.event) {
              case 'connected':
                newState.error = null;
                retryCountRef.current = 0;
                break;

              case 'status_change':
                newState.status = event.status || prev.status;
                newState.taskName = event.task_name || prev.taskName;
                break;

              case 'progress':
                newState.status = event.status || prev.status;
                newState.itemsProcessed = event.items_processed || prev.itemsProcessed;
                newState.itemsSucceeded = event.items_succeeded || prev.itemsSucceeded;
                newState.itemsFailed = event.items_failed || prev.itemsFailed;
                break;

              case 'completed':
              case 'failed':
                newState.status = event.status || prev.status;
                newState.itemsProcessed = event.items_processed || prev.itemsProcessed;
                newState.itemsSucceeded = event.items_succeeded || prev.itemsSucceeded;
                newState.itemsFailed = event.items_failed || prev.itemsFailed;
                newState.isCompleted = true;
                newState.isConnected = false;
                break;

              case 'error':
                newState.error = event.message || event.error_message || 'Unknown error';
                newState.isConnected = false;
                break;

              case 'disconnected':
                newState.isConnected = false;
                break;
            }

            return newState;
          });

          // Call callbacks
          if (onEvent) {
            onEvent(event);
          }

          if ((event.event === 'completed' || event.event === 'failed') && onComplete) {
            onComplete(event);
          }

          if (event.event === 'error' && onError) {
            onError(event.message || event.error_message || 'Unknown error');
          }

        } catch (err) {
          console.error('[useScrapeJobStream] Failed to parse event:', err);
        }
      };

      // Handle connection open
      eventSource.onopen = () => {
        console.log(`[useScrapeJobStream] Connected to ${jobId}`);
        setState(prev => ({
          ...prev,
          isConnected: true,
          error: null,
        }));
        retryCountRef.current = 0;
      };

      // Handle errors and reconnection
      eventSource.onerror = (err) => {
        console.error('[useScrapeJobStream] Connection error:', err);

        eventSource.close();
        eventSourceRef.current = null;

        setState(prev => ({
          ...prev,
          isConnected: false,
        }));

        // Attempt reconnection with exponential backoff
        if (shouldConnectRef.current && retryCountRef.current < maxRetries) {
          const delay = retryDelay * Math.pow(2, retryCountRef.current);
          console.log(`[useScrapeJobStream] Retrying in ${delay}ms (attempt ${retryCountRef.current + 1}/${maxRetries})`);

          retryTimeoutRef.current = setTimeout(() => {
            retryCountRef.current++;
            connect();
          }, delay);
        } else if (retryCountRef.current >= maxRetries) {
          console.error('[useScrapeJobStream] Max retries reached');
          setState(prev => ({
            ...prev,
            error: 'Connection failed after multiple retries',
          }));

          if (onError) {
            onError('Connection failed after multiple retries');
          }
        }
      };

    } catch (err) {
      console.error('[useScrapeJobStream] Failed to connect:', err);
      setState(prev => ({
        ...prev,
        error: 'Failed to establish connection',
        isConnected: false,
      }));
    }
  }, [jobId, maxRetries, retryDelay, onEvent, onComplete, onError]);

  /**
   * Disconnect from SSE stream
   */
  const disconnect = useCallback(() => {
    console.log('[useScrapeJobStream] Disconnecting...');
    shouldConnectRef.current = false;

    // Clear retry timeout
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    // Close EventSource
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
    }));
  }, []);

  // Effect: Connect when jobId changes
  useEffect(() => {
    shouldConnectRef.current = true;

    if (jobId) {
      connect();
    }

    // Cleanup on unmount or jobId change
    return () => {
      disconnect();
    };
  }, [jobId, connect, disconnect]);

  return {
    ...state,
    disconnect,
    reconnect: connect,
  };
}


// ==============================================================================
// Hook for All Jobs Stream
// ==============================================================================

export interface AllJobsEvent {
  event: 'connected' | 'job_update' | 'job_completed' | 'error' | 'disconnected';
  job_id?: string;
  task_name?: string;
  module?: string;
  status?: string;
  items_processed?: number;
  items_succeeded?: number;
  items_failed?: number;
  duration_seconds?: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  timestamp: string;
  message?: string;
}

/**
 * Hook for streaming all active jobs.
 *
 * Useful for dashboard views showing multiple jobs.
 *
 * @param module Filter by module (e.g., 'scrape_suite')
 * @param enabled Enable/disable streaming
 * @returns Jobs map and stream state
 *
 * @example
 * ```tsx
 * const { jobs, isConnected } = useAllJobsStream('scrape_suite', true);
 *
 * return (
 *   <div>
 *     {Object.entries(jobs).map(([jobId, job]) => (
 *       <div key={jobId}>
 *         {job.task_name}: {job.status} ({job.items_processed})
 *       </div>
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useAllJobsStream(
  module: string | null = null,
  enabled: boolean = true
) {
  const [jobs, setJobs] = useState<Record<string, AllJobsEvent>>({});
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const shouldConnectRef = useRef(true);

  const connect = useCallback(() => {
    if (!enabled || !shouldConnectRef.current) return;

    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.error('[useAllJobsStream] No auth token found');
      setError('Authentication required');
      return;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const moduleParam = module ? `module=${module}&` : '';
    const url = `${apiUrl}/api/v1/scrape/stream/all-jobs?${moduleParam}token=${token}`;

    console.log('[useAllJobsStream] Connecting...');

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (e) => {
      try {
        const event: AllJobsEvent = JSON.parse(e.data);

        if (event.event === 'job_update' && event.job_id) {
          setJobs(prev => ({
            ...prev,
            [event.job_id!]: event,
          }));
        } else if (event.event === 'job_completed' && event.job_id) {
          // Remove completed job after short delay
          setTimeout(() => {
            setJobs(prev => {
              const { [event.job_id!]: _, ...rest } = prev;
              return rest;
            });
          }, 5000);
        }
      } catch (err) {
        console.error('[useAllJobsStream] Failed to parse event:', err);
      }
    };

    eventSource.onopen = () => {
      console.log('[useAllJobsStream] Connected');
      setIsConnected(true);
      setError(null);
    };

    eventSource.onerror = (err) => {
      console.error('[useAllJobsStream] Connection error:', err);
      eventSource.close();
      setIsConnected(false);
    };
  }, [enabled, module]);

  const disconnect = useCallback(() => {
    shouldConnectRef.current = false;
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    shouldConnectRef.current = true;
    if (enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, module, connect, disconnect]);

  return {
    jobs,
    isConnected,
    error,
    disconnect,
    reconnect: connect,
  };
}
