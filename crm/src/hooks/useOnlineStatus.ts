/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import { useState, useEffect } from 'react';

export interface OnlineStatus {
  isOnline: boolean;
  wasOffline: boolean;
  downtime: number | null;
}

export function useOnlineStatus(): OnlineStatus {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);
  const [offlineTimestamp, setOfflineTimestamp] = useState<number | null>(null);
  const [downtime, setDowntime] = useState<number | null>(null);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);

      if (offlineTimestamp) {
        const downtimeMs = Date.now() - offlineTimestamp;
        setDowntime(downtimeMs);
        setWasOffline(true);
        setOfflineTimestamp(null);

        // Clear wasOffline flag after 5 seconds
        setTimeout(() => {
          setWasOffline(false);
          setDowntime(null);
        }, 5000);

        console.log(`Back online after ${Math.round(downtimeMs / 1000)}s`);
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      setOfflineTimestamp(Date.now());
      console.log('Connection lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Periodic connectivity check
    const checkConnectivity = async () => {
      if (!navigator.onLine) {
        return;
      }

      try {
        // Try to fetch a small resource to verify real connectivity
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);

        await fetch('/favicon.ico', {
          method: 'HEAD',
          cache: 'no-cache',
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!isOnline) {
          handleOnline();
        }
      } catch (error) {
        if (isOnline) {
          handleOffline();
        }
      }
    };

    const connectivityInterval = setInterval(checkConnectivity, 30000); // Check every 30s

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(connectivityInterval);
    };
  }, [isOnline, offlineTimestamp]);

  return {
    isOnline,
    wasOffline,
    downtime
  };
}
