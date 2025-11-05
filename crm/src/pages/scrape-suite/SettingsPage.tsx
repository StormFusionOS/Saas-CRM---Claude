/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Scrape Suite Settings & Configuration Page
 */

import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  Settings,
  Clock,
  RefreshCw,
  Globe,
  Shield,
  CheckCircle,
  AlertCircle,
  Save
} from 'lucide-react';
import scrapeApi from '@/lib/scrape-api';
import type { ScrapeSettings } from '@/lib/scrape-api';

const SettingsPage: React.FC = () => {
  // State
  const [settings, setSettings] = useState<ScrapeSettings | null>(null);
  const [formData, setFormData] = useState<ScrapeSettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  // Check for changes
  useEffect(() => {
    if (settings && formData) {
      const changed = JSON.stringify(settings) !== JSON.stringify(formData);
      setHasChanges(changed);
    }
  }, [settings, formData]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await scrapeApi.getSettings();
      setSettings(data);
      setFormData(data);
    } catch (err: any) {
      console.error('Failed to load settings:', err);
      setError(err.response?.data?.detail || 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData) return;

    try {
      setSaving(true);
      setError(null);
      setSuccess(false);
      const updated = await scrapeApi.updateSettings(formData);
      setSettings(updated);
      setFormData(updated);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      console.error('Failed to save settings:', err);
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (settings) {
      setFormData({ ...settings });
      setError(null);
      setSuccess(false);
    }
  };

  const updateField = <K extends keyof ScrapeSettings>(
    field: K,
    value: ScrapeSettings[K]
  ) => {
    if (formData) {
      setFormData({ ...formData, [field]: value });
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Scrape Suite Settings
          </h1>
          <p className="text-neutral-400">
            Configure scraping schedules, refresh intervals, and system options
          </p>
        </div>
        <Card variant="glass" padding="lg">
          <div className="text-center py-8 text-neutral-400">
            Loading settings...
          </div>
        </Card>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Scrape Suite Settings
          </h1>
          <p className="text-neutral-400">
            Configure scraping schedules, refresh intervals, and system options
          </p>
        </div>
        <Card variant="glass" padding="lg">
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 text-danger mx-auto mb-3" />
            <p className="text-white font-medium mb-2">Failed to Load Settings</p>
            <p className="text-neutral-400 mb-4">{error}</p>
            <Button variant="primary" onClick={loadSettings}>
              Retry
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Scrape Suite Settings
          </h1>
          <p className="text-neutral-400">
            Configure scraping schedules, refresh intervals, and system options
          </p>
        </div>
        <div className="flex items-center gap-2">
          {hasChanges && (
            <Button
              variant="secondary"
              onClick={handleReset}
              disabled={saving}
            >
              Reset
            </Button>
          )}
          <Button
            variant="primary"
            icon={<Save className="w-4 h-4" />}
            onClick={handleSave}
            disabled={!hasChanges || saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="flex items-center gap-2 p-4 bg-success/10 border border-success/20 rounded-lg">
          <CheckCircle className="w-5 h-5 text-success" />
          <p className="text-success font-medium">Settings saved successfully</p>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-4 bg-danger/10 border border-danger/20 rounded-lg">
          <AlertCircle className="w-5 h-5 text-danger" />
          <p className="text-danger font-medium">{error}</p>
        </div>
      )}

      {/* General Settings */}
      <Card variant="glass" padding="lg">
        <div className="flex items-start gap-4 mb-6">
          <div className="p-3 rounded-lg bg-primary/20 flex-shrink-0">
            <Settings className="w-6 h-6 text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-white mb-2">
              General Configuration
            </h2>
            <p className="text-sm text-neutral-400">
              Basic settings for the Scrape Suite module
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Review Mode */}
          <div className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-4 h-4 text-warning" />
                <label className="font-medium text-white">Review Mode</label>
              </div>
              <p className="text-sm text-neutral-400">
                Require manual approval before publishing scraped data changes
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={formData.review_mode}
                onChange={(e) => updateField('review_mode', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          {/* Proxy Pool */}
          <div className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Globe className="w-4 h-4 text-info" />
                <label className="font-medium text-white">Proxy Pool</label>
              </div>
              <p className="text-sm text-neutral-400">
                Use proxy rotation for scraping to avoid rate limits and blocks
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={formData.proxy_pool_enabled}
                onChange={(e) => updateField('proxy_pool_enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          {/* Max Pages Per Crawl */}
          <div className="p-4 bg-dark-800 rounded-lg">
            <label className="block font-medium text-white mb-2">
              Maximum Pages Per Crawl
            </label>
            <p className="text-sm text-neutral-400 mb-3">
              Limit the number of pages to crawl per site to prevent overload
            </p>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min="1"
                max="1000"
                value={formData.max_pages_per_crawl}
                onChange={(e) => updateField('max_pages_per_crawl', parseInt(e.target.value) || 100)}
                className="w-32 px-4 py-2 bg-dark-600 border border-white/10 rounded-lg text-white focus:outline-none focus:border-primary"
              />
              <span className="text-sm text-neutral-400">pages</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Automated Schedules */}
      <Card variant="glass" padding="lg">
        <div className="flex items-start gap-4 mb-6">
          <div className="p-3 rounded-lg bg-success/20 flex-shrink-0">
            <Clock className="w-6 h-6 text-success" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-white mb-2">
              Automated Scraping Schedules
            </h2>
            <p className="text-sm text-neutral-400">
              Configure automated scraping frequencies for different tasks
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {/* Daily SERP */}
          <div className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
            <div className="flex-1">
              <label className="font-medium text-white block mb-1">
                Daily SERP Snapshots
              </label>
              <p className="text-sm text-neutral-400">
                Capture keyword rankings daily at 03:00 UTC
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={formData.daily_serp_enabled}
                onChange={(e) => updateField('daily_serp_enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          {/* Weekly Crawl */}
          <div className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
            <div className="flex-1">
              <label className="font-medium text-white block mb-1">
                Weekly Competitor Crawls
              </label>
              <p className="text-sm text-neutral-400">
                Monitor competitor site changes every Sunday at 02:00 UTC
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={formData.weekly_crawl_enabled}
                onChange={(e) => updateField('weekly_crawl_enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          {/* Monthly Crawl */}
          <div className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
            <div className="flex-1">
              <label className="font-medium text-white block mb-1">
                Monthly Full-Site Audits
              </label>
              <p className="text-sm text-neutral-400">
                Comprehensive technical audits on the 1st of each month at 01:00 UTC
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={formData.monthly_crawl_enabled}
                onChange={(e) => updateField('monthly_crawl_enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-dark-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* Refresh Intervals */}
      <Card variant="glass" padding="lg">
        <div className="flex items-start gap-4 mb-6">
          <div className="p-3 rounded-lg bg-warning/20 flex-shrink-0">
            <RefreshCw className="w-6 h-6 text-warning" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-white mb-2">
              Refresh Intervals
            </h2>
            <p className="text-sm text-neutral-400">
              Configure how often to refresh different types of data
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Backlinks Refresh */}
          <div className="p-4 bg-dark-800 rounded-lg">
            <label className="block font-medium text-white mb-2">
              Backlinks Refresh
            </label>
            <p className="text-sm text-neutral-400 mb-3">
              How often to check and refresh backlink data
            </p>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min="1"
                max="90"
                value={formData.backlinks_refresh_days}
                onChange={(e) => updateField('backlinks_refresh_days', parseInt(e.target.value) || 7)}
                className="w-24 px-4 py-2 bg-dark-600 border border-white/10 rounded-lg text-white focus:outline-none focus:border-primary"
              />
              <span className="text-sm text-neutral-400">days</span>
            </div>
          </div>

          {/* Citations Refresh */}
          <div className="p-4 bg-dark-800 rounded-lg">
            <label className="block font-medium text-white mb-2">
              Citations Refresh
            </label>
            <p className="text-sm text-neutral-400 mb-3">
              How often to check and refresh business citations
            </p>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min="1"
                max="365"
                value={formData.citations_refresh_days}
                onChange={(e) => updateField('citations_refresh_days', parseInt(e.target.value) || 30)}
                className="w-24 px-4 py-2 bg-dark-600 border border-white/10 rounded-lg text-white focus:outline-none focus:border-primary"
              />
              <span className="text-sm text-neutral-400">days</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Save Button (sticky at bottom) */}
      {hasChanges && (
        <div className="sticky bottom-4 flex justify-end">
          <div className="flex items-center gap-2 p-4 bg-dark-900 border border-white/10 rounded-lg shadow-lg">
            <span className="text-sm text-neutral-400 mr-2">You have unsaved changes</span>
            <Button
              variant="secondary"
              onClick={handleReset}
              disabled={saving}
            >
              Reset
            </Button>
            <Button
              variant="primary"
              icon={<Save className="w-4 h-4" />}
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
