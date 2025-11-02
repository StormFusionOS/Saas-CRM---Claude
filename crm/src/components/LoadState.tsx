/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import Button from './ui/Button';

interface LoadStateProps {
  state: 'loading' | 'error' | 'empty' | 'success';
  error?: string;
  emptyMessage?: string;
  onRetry?: () => void;
  children?: React.ReactNode;
}

const LoadState: React.FC<LoadStateProps> = ({
  state,
  error,
  emptyMessage = 'No data available',
  onRetry,
  children,
}) => {
  if (state === 'loading') {
    return (
      <div className="p-8">
        {/* Skeleton Loading */}
        <div className="space-y-4 animate-pulse">
          <div className="h-8 bg-white/10 rounded w-1/3"></div>
          <div className="h-4 bg-white/5 rounded w-2/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white/5 rounded-lg"></div>
            ))}
          </div>
          <div className="space-y-3 mt-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-white/5 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (state === 'error') {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-64">
        <div className="text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-text-primary mb-2">
          Something went wrong
        </h3>
        <p className="text-text-secondary text-center max-w-md mb-6">
          {error || 'An unexpected error occurred. Please try again.'}
        </p>
        {onRetry && (
          <Button variant="primary" onClick={onRetry}>
            🔄 Try Again
          </Button>
        )}
      </div>
    );
  }

  if (state === 'empty') {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-64">
        <div className="text-6xl mb-4">📭</div>
        <h3 className="text-xl font-semibold text-text-primary mb-2">
          No data yet
        </h3>
        <p className="text-text-secondary text-center max-w-md">
          {emptyMessage}
        </p>
      </div>
    );
  }

  // Success state - render children
  return <>{children}</>;
};

export default LoadState;
