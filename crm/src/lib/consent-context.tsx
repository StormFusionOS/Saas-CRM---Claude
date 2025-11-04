/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ConsentPreferences {
  essential: boolean;
  marketing: boolean;
  analytics: boolean;
  personalization: boolean;
}

interface ConsentContextType {
  preferences: ConsentPreferences | null;
  hasConsented: boolean;
  acceptConsent: (prefs: ConsentPreferences) => void;
  rejectConsent: () => void;
  updatePreferences: (prefs: Partial<ConsentPreferences>) => void;
  showBanner: boolean;
  resetConsent: () => void;
}

const ConsentContext = createContext<ConsentContextType | undefined>(undefined);

const CONSENT_STORAGE_KEY = 'user_consent_preferences';
const CONSENT_VERSION = '1.0';
const CONSENT_EXPIRY_DAYS = 365;

interface StoredConsent {
  preferences: ConsentPreferences;
  version: string;
  timestamp: number;
}

export const ConsentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [preferences, setPreferences] = useState<ConsentPreferences | null>(null);
  const [hasConsented, setHasConsented] = useState(false);
  const [showBanner, setShowBanner] = useState(false);

  // Load consent preferences from localStorage on mount
  useEffect(() => {
    const loadConsent = () => {
      const stored = localStorage.getItem(CONSENT_STORAGE_KEY);
      if (stored) {
        try {
          const data: StoredConsent = JSON.parse(stored);

          // Check if consent is expired (365 days)
          const expiryTime = data.timestamp + CONSENT_EXPIRY_DAYS * 24 * 60 * 60 * 1000;
          const isExpired = Date.now() > expiryTime;

          // Check if version matches
          const isOldVersion = data.version !== CONSENT_VERSION;

          if (isExpired || isOldVersion) {
            // Consent expired or outdated, clear and show banner
            localStorage.removeItem(CONSENT_STORAGE_KEY);
            setShowBanner(true);
            return;
          }

          // Valid consent found
          setPreferences(data.preferences);
          setHasConsented(true);
          setShowBanner(false);
        } catch (error) {
          console.error('Error loading consent preferences:', error);
          setShowBanner(true);
        }
      } else {
        // No consent found, show banner
        setShowBanner(true);
      }
    };

    loadConsent();
  }, []);

  // Save consent to localStorage
  const saveConsent = (prefs: ConsentPreferences) => {
    const data: StoredConsent = {
      preferences: prefs,
      version: CONSENT_VERSION,
      timestamp: Date.now(),
    };

    localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(data));
    setPreferences(prefs);
    setHasConsented(true);
    setShowBanner(false);

    // Initialize analytics/marketing scripts based on consent
    initializeTracking(prefs);
  };

  const acceptConsent = (prefs: ConsentPreferences) => {
    saveConsent(prefs);
  };

  const rejectConsent = () => {
    const minimalPrefs: ConsentPreferences = {
      essential: true,
      marketing: false,
      analytics: false,
      personalization: false,
    };
    saveConsent(minimalPrefs);
  };

  const updatePreferences = (partialPrefs: Partial<ConsentPreferences>) => {
    if (preferences) {
      const updatedPrefs = { ...preferences, ...partialPrefs };
      saveConsent(updatedPrefs);
    }
  };

  const resetConsent = () => {
    localStorage.removeItem(CONSENT_STORAGE_KEY);
    setPreferences(null);
    setHasConsented(false);
    setShowBanner(true);
  };

  // Initialize tracking scripts based on consent
  const initializeTracking = (prefs: ConsentPreferences) => {
    if (prefs.analytics) {
      // Initialize analytics (e.g., Google Analytics)
      console.log('Analytics tracking enabled');
      // window.gtag('consent', 'update', { analytics_storage: 'granted' });
    } else {
      console.log('Analytics tracking disabled');
      // window.gtag('consent', 'update', { analytics_storage: 'denied' });
    }

    if (prefs.marketing) {
      // Initialize marketing pixels (e.g., Facebook Pixel, Google Ads)
      console.log('Marketing tracking enabled');
      // window.gtag('consent', 'update', { ad_storage: 'granted' });
    } else {
      console.log('Marketing tracking disabled');
      // window.gtag('consent', 'update', { ad_storage: 'denied' });
    }

    if (prefs.personalization) {
      // Initialize personalization features
      console.log('Personalization enabled');
    } else {
      console.log('Personalization disabled');
    }
  };

  return (
    <ConsentContext.Provider
      value={{
        preferences,
        hasConsented,
        acceptConsent,
        rejectConsent,
        updatePreferences,
        showBanner,
        resetConsent,
      }}
    >
      {children}
    </ConsentContext.Provider>
  );
};

export const useConsent = (): ConsentContextType => {
  const context = useContext(ConsentContext);
  if (!context) {
    throw new Error('useConsent must be used within a ConsentProvider');
  }
  return context;
};
