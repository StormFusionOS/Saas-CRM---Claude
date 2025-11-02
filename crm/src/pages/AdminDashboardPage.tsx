/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import Card from '../components/ui/Card';

const AdminDashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Admin Dashboard</h1>
        <p className="text-sm text-text-muted mt-1">System administration and management overview</p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-storm-blue/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Review Queue</h3>
            <p className="text-4xl font-display font-bold text-warning">12</p>
            <div className="mt-2 text-xs text-text-muted">Pending review</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">System Health</h3>
            <p className="text-4xl font-display font-bold text-success">98%</p>
            <div className="mt-2 text-xs text-text-muted">All systems go</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Active Users</h3>
            <p className="text-4xl font-display font-bold text-primary">24</p>
            <div className="mt-2 text-xs text-text-muted">Online now</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Health Alerts</h3>
            <p className="text-4xl font-display font-bold text-warning">2</p>
            <div className="mt-2 text-xs text-text-muted">Needs attention</div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">System Overview</h2>
            <p className="text-text-secondary">System metrics and performance coming soon...</p>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Recent Activity</h2>
            <p className="text-text-secondary">Admin activity log coming soon...</p>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboardPage;
