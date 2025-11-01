/**
 * Consent Banner Component
 *
 * GDPR/CCPA cookie consent banner displayed on first visit.
 *
 * Features:
 * - Accept all / Reject all
 * - Customize preferences link
 * - Persistent across sessions
 * - Accessible (ARIA labels)
 *
 * Usage:
 *   import { ConsentBanner } from './consent/ui/ConsentBanner';
 *
 *   function App() {
 *     return (
 *       <>
 *         <ConsentBanner userId="user_123" />
 *         <YourApp />
 *       </>
 *     );
 *   }
 */

import { useState, useEffect } from 'react';

interface ConsentBannerProps {
  userId?: string;
  onAccept?: (purposes: string[]) => void;
  onReject?: () => void;
  onCustomize?: () => void;
}

export function ConsentBanner({
  userId,
  onAccept,
  onReject,
  onCustomize
}: ConsentBannerProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has already responded
    const hasConsented = localStorage.getItem('consent_responded');
    if (!hasConsented) {
      setIsVisible(true);
    }
  }, []);

  const handleAcceptAll = () => {
    const allPurposes = ['analytics', 'marketing', 'personalization'];

    // Save consent to backend
    if (userId) {
      fetch('/api/consent/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          purposes: allPurposes,
          source: 'web'
        })
      }).catch(err => console.error('Failed to save consent:', err));
    }

    // Mark as responded
    localStorage.setItem('consent_responded', 'true');
    localStorage.setItem('consent_all', 'true');

    setIsVisible(false);
    onAccept?.(allPurposes);
  };

  const handleRejectAll = () => {
    // Only essential cookies (no consent saved)
    localStorage.setItem('consent_responded', 'true');
    localStorage.setItem('consent_all', 'false');

    setIsVisible(false);
    onReject?.();
  };

  const handleCustomize = () => {
    setIsVisible(false);
    // Redirect to preferences page
    window.location.href = '/settings/privacy';
    onCustomize?.();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-labelledby="consent-banner-title"
      aria-describedby="consent-banner-description"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: '#1a1a1a',
        color: '#fff',
        padding: '1.5rem',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.3)',
        zIndex: 9999
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2
          id="consent-banner-title"
          style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}
        >
          We value your privacy
        </h2>

        <p
          id="consent-banner-description"
          style={{ marginBottom: '1rem', color: '#ccc' }}
        >
          We use cookies and similar technologies to improve your experience,
          analyze site usage, and assist in our marketing efforts. You can
          customize your preferences or accept all.
        </p>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button
            onClick={handleAcceptAll}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#4CAF50',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Accept All
          </button>

          <button
            onClick={handleRejectAll}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#666',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Reject All
          </button>

          <button
            onClick={handleCustomize}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: 'transparent',
              color: '#fff',
              border: '1px solid #fff',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Customize Preferences
          </button>
        </div>

        <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#999' }}>
          By clicking "Accept All", you consent to our use of cookies.{' '}
          <a href="/privacy-policy" style={{ color: '#4CAF50' }}>
            Learn more
          </a>
        </p>
      </div>
    </div>
  );
}
