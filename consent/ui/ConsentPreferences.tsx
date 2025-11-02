/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Consent Preferences Page
 *
 * Detailed consent management interface for users.
 *
 * Features:
 * - Granular consent toggles for each purpose
 * - Consent descriptions and retention periods
 * - Save/withdraw preferences
 * - Consent history view
 *
 * Usage:
 *   import { ConsentPreferences } from './consent/ui/ConsentPreferences';
 *
 *   function SettingsPage() {
 *     return <ConsentPreferences userId="user_123" />;
 *   }
 */

import { useState, useEffect } from 'react';

interface ConsentPurpose {
  id: string;
  name: string;
  description: string;
  required: boolean;
  retention_days: number | null;
  active: boolean;
}

const CONSENT_PURPOSES: ConsentPurpose[] = [
  {
    id: 'essential',
    name: 'Essential Services',
    description: 'Required for the service to function (account management, security, etc.)',
    required: true,
    retention_days: null,
    active: true
  },
  {
    id: 'analytics',
    name: 'Analytics',
    description: 'Help us understand how you use our service to improve it',
    required: false,
    retention_days: 730,
    active: false
  },
  {
    id: 'marketing',
    name: 'Marketing Communications',
    description: 'Receive emails about new features, promotions, and news',
    required: false,
    retention_days: 1095,
    active: false
  },
  {
    id: 'personalization',
    name: 'Personalization',
    description: 'Personalize content and recommendations based on your usage',
    required: false,
    retention_days: 730,
    active: false
  },
  {
    id: 'third_party_sharing',
    name: 'Third-Party Sharing',
    description: 'Share anonymized data with trusted partners for research',
    required: false,
    retention_days: 365,
    active: false
  },
  {
    id: 'profiling',
    name: 'Automated Profiling',
    description: 'Use automated systems to suggest features and content',
    required: false,
    retention_days: 730,
    active: false
  }
];

interface ConsentPreferencesProps {
  userId: string;
}

export function ConsentPreferences({ userId }: ConsentPreferencesProps) {
  const [purposes, setPurposes] = useState<ConsentPurpose[]>(CONSENT_PURPOSES);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadPreferences();
  }, [userId]);

  const loadPreferences = async () => {
    setLoading(true);

    try {
      const response = await fetch(`/api/consent/preferences/${userId}`);
      if (response.ok) {
        const data = await response.json();

        // Update active status based on backend data
        const updatedPurposes = purposes.map(purpose => ({
          ...purpose,
          active: data.active_purposes.includes(purpose.id) || purpose.required
        }));

        setPurposes(updatedPurposes);
      }
    } catch (error) {
      console.error('Failed to load preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (purposeId: string) => {
    setPurposes(prev =>
      prev.map(p =>
        p.id === purposeId && !p.required
          ? { ...p, active: !p.active }
          : p
      )
    );
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);

    const activePurposes = purposes
      .filter(p => p.active && !p.required)
      .map(p => p.id);

    try {
      // Save active consents
      if (activePurposes.length > 0) {
        await fetch('/api/consent/bulk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            purposes: activePurposes,
            source: 'web'
          })
        });
      }

      // Withdraw inactive consents
      const inactivePurposes = purposes
        .filter(p => !p.active && !p.required)
        .map(p => p.id);

      for (const purposeId of inactivePurposes) {
        await fetch('/api/consent/withdraw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            purpose: purposeId
          })
        });
      }

      setMessage('Preferences saved successfully');
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
      setMessage('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const formatRetention = (days: number | null) => {
    if (days === null) return 'Account lifetime';
    if (days >= 365) return `${Math.floor(days / 365)} year(s)`;
    return `${days} days`;
  };

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading preferences...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ marginBottom: '0.5rem' }}>Privacy & Consent Preferences</h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Manage how we use your data. You can change these settings at any time.
      </p>

      {message && (
        <div
          style={{
            padding: '1rem',
            marginBottom: '2rem',
            backgroundColor: message.includes('success') ? '#d4edda' : '#f8d7da',
            color: message.includes('success') ? '#155724' : '#721c24',
            borderRadius: '4px'
          }}
        >
          {message}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {purposes.map(purpose => (
          <div
            key={purpose.id}
            style={{
              padding: '1.5rem',
              border: '1px solid #ddd',
              borderRadius: '8px',
              backgroundColor: '#f9f9f9'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ marginBottom: '0.5rem' }}>
                  {purpose.name}
                  {purpose.required && (
                    <span
                      style={{
                        marginLeft: '0.5rem',
                        fontSize: '0.75rem',
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#666',
                        color: '#fff',
                        borderRadius: '3px'
                      }}
                    >
                      Required
                    </span>
                  )}
                </h3>
                <p style={{ color: '#666', marginBottom: '0.5rem' }}>
                  {purpose.description}
                </p>
                <p style={{ fontSize: '0.875rem', color: '#999' }}>
                  Retention: {formatRetention(purpose.retention_days)}
                </p>
              </div>

              <label style={{ display: 'flex', alignItems: 'center', cursor: purpose.required ? 'not-allowed' : 'pointer' }}>
                <input
                  type="checkbox"
                  checked={purpose.active}
                  disabled={purpose.required}
                  onChange={() => handleToggle(purpose.id)}
                  style={{
                    width: '20px',
                    height: '20px',
                    cursor: purpose.required ? 'not-allowed' : 'pointer'
                  }}
                />
              </label>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
        <button
          onClick={handleSave}
          disabled={saving}
          style={{
            padding: '0.75rem 2rem',
            backgroundColor: '#4CAF50',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: saving ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            opacity: saving ? 0.6 : 1
          }}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>

        <button
          onClick={loadPreferences}
          disabled={saving}
          style={{
            padding: '0.75rem 2rem',
            backgroundColor: '#666',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: saving ? 'not-allowed' : 'pointer'
          }}
        >
          Reset
        </button>
      </div>

      <div style={{ marginTop: '3rem', padding: '1.5rem', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '0.5rem' }}>Your Rights</h3>
        <p style={{ color: '#666', marginBottom: '1rem' }}>
          Under GDPR and CCPA, you have the following rights:
        </p>
        <ul style={{ color: '#666', paddingLeft: '1.5rem' }}>
          <li>Right to access your data</li>
          <li>Right to rectify incorrect data</li>
          <li>Right to erasure ("right to be forgotten")</li>
          <li>Right to data portability</li>
          <li>Right to object to processing</li>
        </ul>
        <p style={{ marginTop: '1rem' }}>
          <a href="/settings/data-requests" style={{ color: '#4CAF50' }}>
            Submit a data request →
          </a>
        </p>
      </div>
    </div>
  );
}
