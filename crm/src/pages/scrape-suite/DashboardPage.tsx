/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import { Activity, TrendingUp, Search, Globe } from 'lucide-react';

const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold text-white mb-2">
          Scrape Suite Dashboard
        </h1>
        <p className="text-neutral-400">
          Overview of web scraping activities, SERP monitoring, and competitor intelligence
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Active Runs</p>
              <p className="text-2xl font-bold text-white">0</p>
            </div>
            <div className="p-2 rounded-lg bg-primary/20">
              <Activity className="w-5 h-5 text-primary" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Keywords Tracked</p>
              <p className="text-2xl font-bold text-white">0</p>
            </div>
            <div className="p-2 rounded-lg bg-success/20">
              <Search className="w-5 h-5 text-success" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Competitors</p>
              <p className="text-2xl font-bold text-white">0</p>
            </div>
            <div className="p-2 rounded-lg bg-warning/20">
              <Globe className="w-5 h-5 text-warning" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">SERP Changes</p>
              <p className="text-2xl font-bold text-white">0</p>
            </div>
            <div className="p-2 rounded-lg bg-info/20">
              <TrendingUp className="w-5 h-5 text-info" />
            </div>
          </div>
        </Card>
      </div>

      {/* Empty State */}
      <Card variant="glass" padding="lg">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4">
            <Activity className="w-8 h-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">
            No Scrape Jobs Configured
          </h3>
          <p className="text-neutral-400 mb-6 max-w-md mx-auto">
            Get started by configuring your first keyword tracking, competitor monitoring, or web scraping job.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Button
              variant="primary"
              onClick={() => window.location.href = '/scrape/keywords'}
              aria-label="Configure keyword tracking"
            >
              Add Keywords
            </Button>
            <Button
              variant="secondary"
              onClick={() => window.location.href = '/scrape/competitors'}
              aria-label="Add competitor sites"
            >
              Add Competitors
            </Button>
            <Button
              variant="ghost"
              onClick={() => window.location.href = '/scrape/settings'}
              aria-label="Configure scrape settings"
            >
              Settings
            </Button>
          </div>
        </div>
      </Card>

      {/* Recent Activity - Empty State */}
      <Card variant="glass" padding="lg">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
        <div className="text-center py-8 text-neutral-400">
          <p>No recent scraping activity to display</p>
        </div>
      </Card>
    </div>
  );
};

export default DashboardPage;
