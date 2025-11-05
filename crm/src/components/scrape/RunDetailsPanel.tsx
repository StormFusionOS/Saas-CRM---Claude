/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Run Details Panel Component
 * Right-side panel showing detailed job information
 */

import React from 'react';
import { JobStatus } from '@/lib/scrape-api';
import ProgressBar from './ProgressBar';

interface RunDetailsPanelProps {
  job: JobStatus | null;
  onClose: () => void;
}

export default function RunDetailsPanel({ job, onClose }: RunDetailsPanelProps) {
  if (!job) return null;

  // Format dates
  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Format duration
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;

    if (hours > 0) {
      return `${hours}h ${remainingMins}m ${secs}s`;
    } else if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  const totalItems = job.items_processed || job.items_succeeded + job.items_failed;
  const isCompleted = job.status.toLowerCase() === 'completed';
  const isFailed = job.status.toLowerCase() === 'failed';

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-25 dark:bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed top-0 right-0 h-full w-full md:w-[500px] bg-white dark:bg-gray-900 shadow-xl z-50 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Job Details
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-6">
          {/* Job Name & ID */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {job.task_name || 'Scrape Job'}
            </h3>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium">Job ID:</span> {job.job_id}
            </div>
            {job.task_id && (
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <span className="font-medium">Task ID:</span> {job.task_id}
              </div>
            )}
          </div>

          {/* Status */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Status
            </h4>
            <div className="flex items-center gap-2">
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  isCompleted
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : isFailed
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                }`}
              >
                {job.status}
              </span>
            </div>
          </div>

          {/* Timing */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Timing
            </h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Queued:</span>
                <span className="text-gray-900 dark:text-white">
                  {formatDateTime(job.queued_at)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Started:</span>
                <span className="text-gray-900 dark:text-white">
                  {formatDateTime(job.started_at)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Completed:</span>
                <span className="text-gray-900 dark:text-white">
                  {formatDateTime(job.completed_at)}
                </span>
              </div>
              <div className="flex justify-between font-medium">
                <span className="text-gray-600 dark:text-gray-400">Duration:</span>
                <span className="text-gray-900 dark:text-white">
                  {formatDuration(job.duration_seconds)}
                </span>
              </div>
            </div>
          </div>

          {/* Progress */}
          {totalItems > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Progress
              </h4>
              <ProgressBar
                total={totalItems}
                succeeded={job.items_succeeded}
                failed={job.items_failed}
              />
              <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {totalItems}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Total</div>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {job.items_succeeded}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Succeeded
                  </div>
                </div>
                <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {job.items_failed}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Failed</div>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {job.error_message && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Error
              </h4>
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                <p className="text-sm text-red-800 dark:text-red-400 whitespace-pre-wrap">
                  {job.error_message}
                </p>
              </div>
            </div>
          )}

          {/* Output Summary */}
          {job.output_summary && Object.keys(job.output_summary).length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Output Summary
              </h4>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 space-y-2">
                {Object.entries(job.output_summary).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400 font-medium">
                      {key}:
                    </span>
                    <span className="text-gray-900 dark:text-white">
                      {typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Acceptance Checks (placeholder for future enhancement) */}
          {isCompleted && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Acceptance Checks
              </h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <svg
                    className="w-4 h-4 text-green-600 dark:text-green-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span className="text-gray-700 dark:text-gray-300">
                    Job completed successfully
                  </span>
                </div>
                {job.items_failed === 0 && totalItems > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <svg
                      className="w-4 h-4 text-green-600 dark:text-green-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">
                      No failed items
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Actions
            </h4>
            <div className="space-y-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(job.job_id);
                }}
                className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors text-sm font-medium"
              >
                Copy Job ID
              </button>
              <button
                onClick={() => {
                  // Navigate to results (placeholder)
                  console.log('View results for job:', job.job_id);
                }}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                View Results
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
