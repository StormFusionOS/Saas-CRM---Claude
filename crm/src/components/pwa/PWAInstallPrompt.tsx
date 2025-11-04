/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import { usePWAInstall } from '../../hooks/usePWA';
import Button from '../ui/Button';
import Card from '../ui/Card';

export const PWAInstallPrompt: React.FC = () => {
  const { isInstallable, promptInstall, dismissPrompt } = usePWAInstall();
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    // Don't show if dismissed in the last 7 days
    const dismissedTime = localStorage.getItem('pwa-install-dismissed');
    if (dismissedTime) {
      const daysSinceDismissed = (Date.now() - parseInt(dismissedTime)) / (1000 * 60 * 60 * 24);
      if (daysSinceDismissed < 7) {
        return;
      }
    }

    // Show prompt after 30 seconds of use
    const timer = setTimeout(() => {
      if (isInstallable) {
        setShowPrompt(true);
      }
    }, 30000);

    return () => clearTimeout(timer);
  }, [isInstallable]);

  const handleInstall = async () => {
    await promptInstall();
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    dismissPrompt();
    setShowPrompt(false);
  };

  if (!showPrompt || !isInstallable) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm animate-slide-up">
      <Card variant="glass" padding="md" className="border border-primary/20">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-text-primary mb-1">
              Install StormFusion CRM
            </h3>
            <p className="text-xs text-text-secondary mb-3">
              Install our app for quick access, offline support, and a better experience
            </p>

            <div className="flex gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleInstall}
                className="flex-1"
              >
                Install
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleDismiss}
              >
                Not now
              </Button>
            </div>
          </div>

          <button
            onClick={handleDismiss}
            className="flex-shrink-0 text-text-muted hover:text-text-primary transition-colors"
            aria-label="Close"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </Card>
    </div>
  );
};

export default PWAInstallPrompt;
