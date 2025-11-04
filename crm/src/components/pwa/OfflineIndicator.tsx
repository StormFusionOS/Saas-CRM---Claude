/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import { useOnlineStatus } from '../../hooks/useOnlineStatus';

export const OfflineIndicator: React.FC = () => {
  const { isOnline, wasOffline, downtime } = useOnlineStatus();

  // Show reconnected message temporarily
  if (wasOffline && isOnline && downtime) {
    return (
      <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 animate-slide-down">
        <div className="bg-success/10 border border-success text-success px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm font-medium">
            Back online {downtime > 1000 && `(offline for ${Math.round(downtime / 1000)}s)`}
          </span>
        </div>
      </div>
    );
  }

  // Show offline indicator
  if (!isOnline) {
    return (
      <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 animate-slide-down">
        <div className="bg-warning/10 border border-warning text-warning px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
            </svg>
            <span className="text-sm font-medium">
              Offline - Working in offline mode
            </span>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default OfflineIndicator;
