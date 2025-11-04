/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import { usePWAUpdate } from '../../hooks/usePWA';
import Button from '../ui/Button';
import Card from '../ui/Card';

export const PWAUpdatePrompt: React.FC = () => {
  const { needRefresh, offlineReady, updateServiceWorker } = usePWAUpdate();
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdate = async () => {
    setIsUpdating(true);
    try {
      await updateServiceWorker(true);
    } catch (error) {
      console.error('Failed to update service worker:', error);
      setIsUpdating(false);
    }
  };

  if (!needRefresh && !offlineReady) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm animate-slide-down">
      <Card variant="glass" padding="md" className="border border-success/20">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-10 h-10 bg-success/20 rounded-lg flex items-center justify-center">
            {needRefresh ? (
              <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>

          <div className="flex-1 min-w-0">
            {needRefresh ? (
              <>
                <h3 className="text-sm font-semibold text-text-primary mb-1">
                  Update Available
                </h3>
                <p className="text-xs text-text-secondary mb-3">
                  A new version of StormFusion CRM is available. Reload to get the latest features and improvements.
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleUpdate}
                    disabled={isUpdating}
                    className="flex-1"
                  >
                    {isUpdating ? 'Updating...' : 'Reload'}
                  </Button>
                </div>
              </>
            ) : (
              <>
                <h3 className="text-sm font-semibold text-text-primary mb-1">
                  Ready for Offline Use
                </h3>
                <p className="text-xs text-text-secondary">
                  StormFusion CRM is now available offline. You can continue working even without an internet connection.
                </p>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PWAUpdatePrompt;
