/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Button from './ui/Button';
import Card from './ui/Card';

interface ConsentPreferences {
  essential: boolean;
  marketing: boolean;
  analytics: boolean;
  personalization: boolean;
}

interface ConsentBannerProps {
  onAccept: (preferences: ConsentPreferences) => void;
  onReject: () => void;
  privacyPolicyUrl?: string;
}

const ConsentBanner: React.FC<ConsentBannerProps> = ({
  onAccept,
  onReject,
  privacyPolicyUrl = '/privacy-policy',
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState<ConsentPreferences>({
    essential: true, // Always required
    marketing: false,
    analytics: false,
    personalization: false,
  });

  const handleAcceptAll = () => {
    const allAccepted: ConsentPreferences = {
      essential: true,
      marketing: true,
      analytics: true,
      personalization: true,
    };
    onAccept(allAccepted);
  };

  const handleAcceptSelected = () => {
    onAccept(preferences);
  };

  const handleRejectAll = () => {
    const onlyEssential: ConsentPreferences = {
      essential: true,
      marketing: false,
      analytics: false,
      personalization: false,
    };
    onAccept(onlyEssential);
    onReject();
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-tooltip p-4 animate-slide-in-up">
      <Card
        variant="glass"
        className="max-w-4xl mx-auto border-2 border-primary/30"
      >
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-display font-semibold text-text-primary">
                We value your privacy
              </h3>
              <p className="text-sm text-text-secondary mt-1">
                We use cookies and similar technologies to improve your experience, analyze site
                usage, and assist in our marketing efforts.
              </p>
            </div>
          </div>

          {/* Details Panel */}
          {showDetails && (
            <div className="space-y-3 animate-slide-in-down">
              {/* Essential Cookies */}
              <div className="flex items-start justify-between p-3 bg-bg-hover rounded-base">
                <div className="flex-1">
                  <label className="flex items-center gap-2 cursor-not-allowed">
                    <input
                      type="checkbox"
                      checked={true}
                      disabled
                      className="w-4 h-4 rounded border-border-default bg-bg-elev"
                    />
                    <div>
                      <span className="font-medium text-text-primary">Essential</span>
                      <p className="text-xs text-text-muted mt-0.5">
                        Required for the website to function properly. Cannot be disabled.
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Marketing Cookies */}
              <div className="flex items-start justify-between p-3 bg-bg-hover rounded-base">
                <div className="flex-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.marketing}
                      onChange={(e) =>
                        setPreferences({ ...preferences, marketing: e.target.checked })
                      }
                      className="w-4 h-4 rounded border-border-default bg-bg-elev accent-primary cursor-pointer"
                    />
                    <div>
                      <span className="font-medium text-text-primary">Marketing</span>
                      <p className="text-xs text-text-muted mt-0.5">
                        Used to deliver personalized ads and track campaign performance.
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Analytics Cookies */}
              <div className="flex items-start justify-between p-3 bg-bg-hover rounded-base">
                <div className="flex-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.analytics}
                      onChange={(e) =>
                        setPreferences({ ...preferences, analytics: e.target.checked })
                      }
                      className="w-4 h-4 rounded border-border-default bg-bg-elev accent-primary cursor-pointer"
                    />
                    <div>
                      <span className="font-medium text-text-primary">Analytics</span>
                      <p className="text-xs text-text-muted mt-0.5">
                        Help us understand how visitors interact with our website.
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Personalization Cookies */}
              <div className="flex items-start justify-between p-3 bg-bg-hover rounded-base">
                <div className="flex-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.personalization}
                      onChange={(e) =>
                        setPreferences({ ...preferences, personalization: e.target.checked })
                      }
                      className="w-4 h-4 rounded border-border-default bg-bg-elev accent-primary cursor-pointer"
                    />
                    <div>
                      <span className="font-medium text-text-primary">Personalization</span>
                      <p className="text-xs text-text-muted mt-0.5">
                        Remember your preferences and provide customized content.
                      </p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-sm text-accent hover:text-accent-hover underline transition-colors"
            >
              {showDetails ? 'Hide details' : 'Customize preferences'}
            </button>

            <a
              href={privacyPolicyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-accent hover:text-accent-hover underline transition-colors"
            >
              Privacy Policy
            </a>

            <div className="flex-1" />

            <div className="flex gap-3 w-full sm:w-auto">
              <Button variant="outline" onClick={handleRejectAll} className="flex-1 sm:flex-initial">
                Reject All
              </Button>
              {showDetails ? (
                <Button variant="primary" onClick={handleAcceptSelected} className="flex-1 sm:flex-initial">
                  Save Preferences
                </Button>
              ) : (
                <Button variant="primary" onClick={handleAcceptAll} className="flex-1 sm:flex-initial">
                  Accept All
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ConsentBanner;
