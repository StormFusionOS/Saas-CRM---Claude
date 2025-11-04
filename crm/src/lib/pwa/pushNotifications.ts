/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Push Notifications API utilities
 *
 * NOTE: This is a skeleton implementation. To enable push notifications:
 * 1. Configure VAPID keys on your backend
 * 2. Implement push subscription endpoint on your API
 * 3. Set up push notification backend service
 */

export interface PushSubscriptionData {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
}

/**
 * Check if push notifications are supported
 */
export function isPushSupported(): boolean {
  return 'PushManager' in window && 'serviceWorker' in navigator;
}

/**
 * Check current push notification permission status
 */
export function getPushPermission(): NotificationPermission {
  if (!isPushSupported()) {
    return 'denied';
  }

  return Notification.permission;
}

/**
 * Request push notification permission
 */
export async function requestPushPermission(): Promise<NotificationPermission> {
  if (!isPushSupported()) {
    throw new Error('Push notifications not supported');
  }

  try {
    const permission = await Notification.requestPermission();
    console.log('Push notification permission:', permission);
    return permission;
  } catch (error) {
    console.error('Failed to request push permission:', error);
    throw error;
  }
}

/**
 * Subscribe to push notifications
 *
 * TODO: Replace with your actual VAPID public key
 */
export async function subscribeToPush(): Promise<PushSubscriptionData | null> {
  if (!isPushSupported()) {
    throw new Error('Push notifications not supported');
  }

  const permission = await requestPushPermission();

  if (permission !== 'granted') {
    console.log('Push permission not granted');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.ready;

    // TODO: Replace with your VAPID public key
    const vapidPublicKey = 'YOUR_VAPID_PUBLIC_KEY_HERE';

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
    });

    const subscriptionData: PushSubscriptionData = {
      endpoint: subscription.endpoint,
      keys: {
        p256dh: arrayBufferToBase64(subscription.getKey('p256dh')!),
        auth: arrayBufferToBase64(subscription.getKey('auth')!)
      }
    };

    console.log('Push subscription created:', subscriptionData);

    // TODO: Send subscription to your backend
    // await sendSubscriptionToBackend(subscriptionData);

    return subscriptionData;
  } catch (error) {
    console.error('Failed to subscribe to push:', error);
    throw error;
  }
}

/**
 * Unsubscribe from push notifications
 */
export async function unsubscribeFromPush(): Promise<boolean> {
  if (!isPushSupported()) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      const result = await subscription.unsubscribe();
      console.log('Unsubscribed from push:', result);

      // TODO: Remove subscription from your backend
      // await removeSubscriptionFromBackend(subscription.endpoint);

      return result;
    }

    return false;
  } catch (error) {
    console.error('Failed to unsubscribe from push:', error);
    return false;
  }
}

/**
 * Get current push subscription
 */
export async function getPushSubscription(): Promise<PushSubscription | null> {
  if (!isPushSupported()) {
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    return await registration.pushManager.getSubscription();
  } catch (error) {
    console.error('Failed to get push subscription:', error);
    return null;
  }
}

/**
 * Show a local notification (doesn't require push)
 */
export async function showNotification(
  title: string,
  options?: NotificationOptions
): Promise<void> {
  if (!isPushSupported()) {
    console.warn('Notifications not supported');
    return;
  }

  const permission = await requestPushPermission();

  if (permission !== 'granted') {
    console.log('Notification permission not granted');
    return;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    await registration.showNotification(title, {
      icon: '/icon-192.png',
      badge: '/icon-192.png',
      vibrate: [200, 100, 200],
      ...options
    });
  } catch (error) {
    console.error('Failed to show notification:', error);
  }
}

// Utility functions

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';

  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }

  return window.btoa(binary);
}

/**
 * TODO: Implement backend integration
 */
/*
async function sendSubscriptionToBackend(subscription: PushSubscriptionData): Promise<void> {
  await fetch('/api/v1/push/subscribe', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(subscription)
  });
}

async function removeSubscriptionFromBackend(endpoint: string): Promise<void> {
  await fetch('/api/v1/push/unsubscribe', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ endpoint })
  });
}
*/
