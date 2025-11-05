/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Run Row Component
 * Individual job row in the Runs & Logs list
 */

import React from 'react';
import { JobStatus } from '@/lib/scrape-api';
import ProgressBar from './ProgressBar';

interface RunRowProps {
  job: JobStatus;
  isLive: boolean;
  onClick: () => void;
}

export default function RunRow({ job, isLive, onClick }: RunRowProps) {
  // Format dates
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Format duration
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'queued':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
      case 'retrying':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const totalItems = job.items_processed || job.items_succeeded + job.items_failed;
  const isRunning = job.status.toLowerCase() === 'running';

  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        {/* Job name and status */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {job.task_name || job.job_id}
            </h3>
            {isLive && (
              <span className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                Live
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                job.status
              )}`}
            >
              {job.status}
            </span>
            <span className="text-xs">Job ID: {job.job_id.slice(0, 8)}</span>
          </div>
        </div>

        {/* Timing */}
        <div className="text-right text-sm text-gray-600 dark:text-gray-400">
          <div className="font-medium">
            {job.started_at ? formatDate(job.started_at) : 'Not started'}
          </div>
          {job.duration_seconds !== null && (
            <div className="text-xs">Duration: {formatDuration(job.duration_seconds)}</div>
          )}
        </div>
      </div>

      {/* Progress bar (show if items are being processed) */}
      {totalItems > 0 && (
        <ProgressBar
          total={totalItems}
          succeeded={job.items_succeeded}
          failed={job.items_failed}
          className="mb-3"
        />
      )}

      {/* Error message */}
      {job.error_message && (
        <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-sm text-red-800 dark:text-red-400">
          {job.error_message}
        </div>
      )}

      {/* Output summary (if available) */}
      {job.output_summary && Object.keys(job.output_summary).length > 0 && (
        <div className="mt-2 flex items-center gap-3 text-xs text-gray-600 dark:text-gray-400">
          {Object.entries(job.output_summary).map(([key, value]) => (
            <span key={key}>
              <span className="font-medium">{key}:</span> {String(value)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
