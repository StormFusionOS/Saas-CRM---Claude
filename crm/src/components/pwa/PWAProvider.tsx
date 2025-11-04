/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useEffect } from 'react';
import PWAInstallPrompt from './PWAInstallPrompt';
import PWAUpdatePrompt from './PWAUpdatePrompt';
import OfflineIndicator from './OfflineIndicator';
import { initBackgroundSync } from '../../lib/pwa/backgroundSync';

export const PWAProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  useEffect(() => {
    // Initialize background sync on mount
    initBackgroundSync();

    // Log PWA capabilities
    console.log('PWA Capabilities:', {
      serviceWorker: 'serviceWorker' in navigator,
      pushManager: 'PushManager' in window,
      backgroundSync: 'serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype,
      notifications: 'Notification' in window,
      standalone: window.matchMedia('(display-mode: standalone)').matches
    });
  }, []);

  return (
    <>
      {children}
      <PWAInstallPrompt />
      <PWAUpdatePrompt />
      <OfflineIndicator />
    </>
  );
};

export default PWAProvider;
