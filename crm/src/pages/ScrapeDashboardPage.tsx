/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import Card from '../components/ui/Card';

const ScrapeDashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Scrape Dashboard</h1>
        <p className="text-sm text-text-muted mt-1">Web scraping and data collection overview</p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-storm-blue/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Active Scrapers</h3>
            <p className="text-4xl font-display font-bold text-primary">12</p>
            <div className="mt-2 text-xs text-text-muted">Running now</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Audit Issues</h3>
            <p className="text-4xl font-display font-bold text-warning">8</p>
            <div className="mt-2 text-xs text-text-muted">Needs attention</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Backlinks Found</h3>
            <p className="text-4xl font-display font-bold text-success">1.2K</p>
            <div className="mt-2 text-xs text-text-muted">This month</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Rate Limit</h3>
            <p className="text-4xl font-display font-bold text-accent">45%</p>
            <div className="mt-2 text-xs text-text-muted">Capacity used</div>
          </Card>
        </div>

        <Card padding="lg">
          <h2 className="text-xl font-display font-semibold mb-4">Scraping Tools</h2>
          <p className="text-text-secondary">Access all data collection and analysis tools from the navigation menu.</p>
        </Card>
      </main>
    </div>
  );
};

export default ScrapeDashboardPage;
