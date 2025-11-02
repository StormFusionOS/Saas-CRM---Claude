/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import Card from '../components/ui/Card';

const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      {/* Top bar */}
      <header className="glass-surface h-16 px-6 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-2xl font-display font-semibold text-gradient">Dashboard</h1>
        <div className="text-sm text-text-secondary">RiverCityClean CRM</div>
      </header>

      {/* Main content */}
      <main className="p-8">
        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
            <div className="mt-2 text-xs text-text-muted">Active conversations</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Closed Won</h3>
            <p className="text-4xl font-display font-bold text-success">8</p>
            <div className="mt-2 text-xs text-text-muted">This month</div>
          </Card>
        </div>

        {/* Additional content placeholder */}
        <Card padding="lg">
          <h2 className="text-xl font-display font-semibold mb-4">Recent Activity</h2>
          <p className="text-text-secondary">Activity feed coming soon...</p>
        </Card>
      </main>
    </div>
  );
};

export default DashboardPage;
