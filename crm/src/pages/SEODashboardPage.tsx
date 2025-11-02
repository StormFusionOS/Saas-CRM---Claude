/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import Card from '../components/ui/Card';

const SEODashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">SEO Dashboard</h1>
        <p className="text-sm text-text-muted mt-1">SEO performance and optimization overview</p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-storm-blue/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Pending Changes</h3>
            <p className="text-4xl font-display font-bold text-warning">5</p>
            <div className="mt-2 text-xs text-text-muted">Awaiting approval</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Schema Validated</h3>
            <p className="text-4xl font-display font-bold text-success">42</p>
            <div className="mt-2 text-xs text-text-muted">All pages</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Internal Links</h3>
            <p className="text-4xl font-display font-bold text-primary">3.2K</p>
            <div className="mt-2 text-xs text-text-muted">Across site</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">SLA Status</h3>
            <p className="text-4xl font-display font-bold text-success">98%</p>
            <div className="mt-2 text-xs text-text-muted">Meeting targets</div>
          </Card>
        </div>

        <Card padding="lg">
          <h2 className="text-xl font-display font-semibold mb-4">SEO Tools</h2>
          <p className="text-text-secondary">Access all SEO management tools from the navigation menu.</p>
        </Card>
      </main>
    </div>
  );
};

export default SEODashboardPage;
