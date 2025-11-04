/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Background Sync API utilities for queueing requests when offline
 */

export interface SyncQueueItem {
  id: string;
  url: string;
  method: string;
  headers: Record<string, string>;
  body?: any;
  timestamp: number;
  retryCount: number;
}

const SYNC_QUEUE_KEY = 'pwa-sync-queue';
const MAX_RETRIES = 3;

/**
 * Add a request to the background sync queue
 */
export async function queueRequest(
  url: string,
  options: RequestInit = {}
): Promise<void> {
  const queue = getSyncQueue();

  const item: SyncQueueItem = {
    id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    url,
    method: options.method || 'GET',
    headers: (options.headers as Record<string, string>) || {},
    body: options.body ? JSON.parse(options.body as string) : undefined,
    timestamp: Date.now(),
    retryCount: 0
  };

  queue.push(item);
  saveSyncQueue(queue);

  console.log('Request queued for background sync:', item);

  // Register background sync if available
  if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register('sync-queue');
      console.log('Background sync registered');
    } catch (error) {
      console.error('Failed to register background sync:', error);
      // Fallback: try to sync immediately if sync API not available
      processSyncQueue();
    }
  } else {
    // Fallback: try to sync immediately if sync API not available
    processSyncQueue();
  }
}

/**
 * Process all queued requests
 */
export async function processSyncQueue(): Promise<void> {
  if (!navigator.onLine) {
    console.log('Cannot process sync queue: offline');
    return;
  }

  const queue = getSyncQueue();
  const failedItems: SyncQueueItem[] = [];

  for (const item of queue) {
    try {
      console.log(`Processing queued request: ${item.method} ${item.url}`);

      const response = await fetch(item.url, {
        method: item.method,
        headers: item.headers,
        body: item.body ? JSON.stringify(item.body) : undefined
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      console.log(`Successfully synced request: ${item.id}`);

      // Dispatch event for successful sync
      window.dispatchEvent(new CustomEvent('sync-success', {
        detail: { item, response: await response.json() }
      }));

    } catch (error) {
      console.error(`Failed to sync request ${item.id}:`, error);

      item.retryCount++;

      if (item.retryCount < MAX_RETRIES) {
        failedItems.push(item);
        console.log(`Will retry (${item.retryCount}/${MAX_RETRIES})`);
      } else {
        console.error(`Max retries reached for request ${item.id}, discarding`);

        // Dispatch event for failed sync
        window.dispatchEvent(new CustomEvent('sync-failed', {
          detail: { item, error }
        }));
      }
    }
  }

  // Save failed items back to queue
  saveSyncQueue(failedItems);
}

/**
 * Get the sync queue from localStorage
 */
function getSyncQueue(): SyncQueueItem[] {
  try {
    const queueData = localStorage.getItem(SYNC_QUEUE_KEY);
    return queueData ? JSON.parse(queueData) : [];
  } catch (error) {
    console.error('Failed to read sync queue:', error);
    return [];
  }
}

/**
 * Save the sync queue to localStorage
 */
function saveSyncQueue(queue: SyncQueueItem[]): void {
  try {
    localStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(queue));
  } catch (error) {
    console.error('Failed to save sync queue:', error);
  }
}

/**
 * Get count of pending sync requests
 */
export function getPendingSyncCount(): number {
  return getSyncQueue().length;
}

/**
 * Clear all pending sync requests
 */
export function clearSyncQueue(): void {
  localStorage.removeItem(SYNC_QUEUE_KEY);
}

/**
 * Initialize background sync listeners
 */
export function initBackgroundSync(): void {
  // Process queue when coming back online
  window.addEventListener('online', () => {
    console.log('Connection restored, processing sync queue');
    processSyncQueue();
  });

  // Listen for sync events from service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'SYNC_COMPLETE') {
        console.log('Background sync completed');
        processSyncQueue();
      }
    });
  }
}
