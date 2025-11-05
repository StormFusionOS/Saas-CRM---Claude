/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Job Start Drawer Component
 * Drawer with job type presets and scoping options
 */

import React, { useState } from 'react';
import scrapeApi, { JobTriggerRequest } from '@/lib/scrape-api';

interface JobStartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onJobStarted: () => void;
}

type JobType = 'serp' | 'crawl' | 'backlinks' | 'citations';

interface JobPreset {
  id: JobType;
  name: string;
  description: string;
  icon: string;
  defaultPayload: Record<string, any>;
}

const JOB_PRESETS: JobPreset[] = [
  {
    id: 'serp',
    name: 'SERP Snapshot',
    description: 'Track keyword rankings and SERP features',
    icon: '🔍',
    defaultPayload: {
      keywords: [],
      engines: ['google'],
      locations: ['US'],
    },
  },
  {
    id: 'crawl',
    name: 'Competitor Crawl',
    description: 'Monitor competitor content changes',
    icon: '🕷️',
    defaultPayload: {
      site_id: null,
      domain: '',
      max_pages: 100,
    },
  },
  {
    id: 'backlinks',
    name: 'Backlinks Refresh',
    description: 'Update backlink portfolio and domain authority',
    icon: '🔗',
    defaultPayload: {
      target_domain: '',
      check_lost: true,
    },
  },
  {
    id: 'citations',
    name: 'Citations Check',
    description: 'Validate NAP consistency across directories',
    icon: '📋',
    defaultPayload: {
      platforms: [],
      check_nap: true,
    },
  },
];

export default function JobStartDrawer({
  isOpen,
  onClose,
  onJobStarted,
}: JobStartDrawerProps) {
  const [selectedType, setSelectedType] = useState<JobType>('serp');
  const [payload, setPayload] = useState<Record<string, any>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get current preset
  const currentPreset = JOB_PRESETS.find((p) => p.id === selectedType);

  // Handle job submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const request: JobTriggerRequest = {
        type: selectedType,
        payload: {
          ...currentPreset?.defaultPayload,
          ...payload,
        },
      };

      await scrapeApi.triggerJob(request);

      // Success
      onJobStarted();
      onClose();
      resetForm();
    } catch (err: any) {
      console.error('Failed to start job:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to start job');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedType('serp');
    setPayload({});
    setError(null);
  };

  const handleClose = () => {
    if (!isSubmitting) {
      resetForm();
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-25 dark:bg-opacity-50 z-40"
        onClick={handleClose}
      />

      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-full md:w-[600px] bg-white dark:bg-gray-900 shadow-xl z-50 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Start Scrape Job
          </h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
          {/* Job Type Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Job Type
            </label>
            <div className="grid grid-cols-1 gap-3">
              {JOB_PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => setSelectedType(preset.id)}
                  className={`p-4 border-2 rounded-lg text-left transition-all ${
                    selectedType === preset.id
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-500'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{preset.icon}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {preset.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {preset.description}
                      </p>
                    </div>
                    {selectedType === preset.id && (
                      <svg
                        className="w-5 h-5 text-blue-600 dark:text-blue-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Job-specific options */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
              Job Configuration
            </h3>

            {/* SERP options */}
            {selectedType === 'serp' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Keywords (comma-separated)
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="cleaning services, house cleaning, maid service"
                    onChange={(e) =>
                      setPayload({
                        ...payload,
                        keywords: e.target.value
                          .split(',')
                          .map((k) => k.trim())
                          .filter(Boolean),
                      })
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Search Engine
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onChange={(e) =>
                      setPayload({ ...payload, engines: [e.target.value] })
                    }
                  >
                    <option value="google">Google</option>
                    <option value="bing">Bing</option>
                  </select>
                </div>
              </div>
            )}

            {/* Crawl options */}
            {selectedType === 'crawl' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Domain
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="example.com"
                    onChange={(e) =>
                      setPayload({ ...payload, domain: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Max Pages
                  </label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    defaultValue={100}
                    min={1}
                    max={1000}
                    onChange={(e) =>
                      setPayload({
                        ...payload,
                        max_pages: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
              </div>
            )}

            {/* Backlinks options */}
            {selectedType === 'backlinks' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Target Domain
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="yourdomain.com"
                    onChange={(e) =>
                      setPayload({ ...payload, target_domain: e.target.value })
                    }
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="check_lost"
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    defaultChecked
                    onChange={(e) =>
                      setPayload({ ...payload, check_lost: e.target.checked })
                    }
                  />
                  <label
                    htmlFor="check_lost"
                    className="text-sm text-gray-700 dark:text-gray-300"
                  >
                    Check for lost backlinks
                  </label>
                </div>
              </div>
            )}

            {/* Citations options */}
            {selectedType === 'citations' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Platforms (comma-separated)
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Yelp, Google My Business, Yellow Pages"
                    onChange={(e) =>
                      setPayload({
                        ...payload,
                        platforms: e.target.value
                          .split(',')
                          .map((p) => p.trim())
                          .filter(Boolean),
                      })
                    }
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="check_nap"
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    defaultChecked
                    onChange={(e) =>
                      setPayload({ ...payload, check_nap: e.target.checked })
                    }
                  />
                  <label
                    htmlFor="check_nap"
                    className="text-sm text-gray-700 dark:text-gray-300"
                  >
                    Validate NAP consistency
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3">
              <p className="text-sm text-red-800 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Starting...
                </>
              ) : (
                'Start Job'
              )}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
