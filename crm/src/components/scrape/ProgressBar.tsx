/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Progress Bar Component
 * Visual progress indicator for scrape jobs
 */

import React from 'react';

interface ProgressBarProps {
  total: number;
  succeeded: number;
  failed: number;
  className?: string;
}

export default function ProgressBar({
  total,
  succeeded,
  failed,
  className = '',
}: ProgressBarProps) {
  const processed = succeeded + failed;
  const percentComplete = total > 0 ? Math.round((processed / total) * 100) : 0;
  const percentSucceeded = total > 0 ? (succeeded / total) * 100 : 0;
  const percentFailed = total > 0 ? (failed / total) * 100 : 0;

  return (
    <div className={`space-y-1 ${className}`}>
      {/* Progress bar */}
      <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        {/* Succeeded portion (green) */}
        {percentSucceeded > 0 && (
          <div
            className="absolute top-0 left-0 h-full bg-green-500 transition-all duration-300"
            style={{ width: `${percentSucceeded}%` }}
          />
        )}
        {/* Failed portion (red) */}
        {percentFailed > 0 && (
          <div
            className="absolute top-0 h-full bg-red-500 transition-all duration-300"
            style={{
              left: `${percentSucceeded}%`,
              width: `${percentFailed}%`,
            }}
          />
        )}
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
        <span>
          {processed} / {total} ({percentComplete}%)
        </span>
        <div className="flex items-center gap-3">
          {succeeded > 0 && (
            <span className="text-green-600 dark:text-green-400">
              ✓ {succeeded}
            </span>
          )}
          {failed > 0 && (
            <span className="text-red-600 dark:text-red-400">✗ {failed}</span>
          )}
        </div>
      </div>
    </div>
  );
}
