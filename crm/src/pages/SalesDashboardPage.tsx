/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import Card from '../components/ui/Card';

const SalesDashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Sales Dashboard</h1>
        <p className="text-sm text-text-muted mt-1">Your sales pipeline and performance overview</p>
      </div>

      {/* Main content */}
      <main className="p-8">
        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-storm-blue/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">New Leads</h3>
            <p className="text-4xl font-display font-bold text-primary">24</p>
            <div className="mt-2 text-xs text-text-muted">↑ 12% from last week</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">In Progress</h3>
            <p className="text-4xl font-display font-bold text-accent">12</p>
            <div className="mt-2 text-xs text-text-muted">Active deals</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Closed Won</h3>
            <p className="text-4xl font-display font-bold text-success">8</p>
            <div className="mt-2 text-xs text-text-muted">This month</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Revenue</h3>
            <p className="text-4xl font-display font-bold text-warning">$45K</p>
            <div className="mt-2 text-xs text-text-muted">This month</div>
          </Card>
        </div>

        {/* Additional content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Pipeline Overview</h2>
            <p className="text-text-secondary">Pipeline visualization coming soon...</p>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Recent Activity</h2>
            <p className="text-text-secondary">Activity feed coming soon...</p>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default SalesDashboardPage;
