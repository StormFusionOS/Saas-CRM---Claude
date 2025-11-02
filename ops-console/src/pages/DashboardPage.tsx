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
      {/* Page header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Ops Dashboard</h1>
        <p className="text-sm text-text-muted mt-1">System status and monitoring overview</p>
      </div>

      {/* Main content */}
      <main className="p-8">
        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Services</h3>
            <p className="text-4xl font-display font-bold text-success">12 / 12</p>
            <div className="mt-2 text-xs text-success">All systems operational</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Alerts</h3>
            <p className="text-4xl font-display font-bold text-warning">3</p>
            <div className="mt-2 text-xs text-text-muted">Requires attention</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">CPU Usage</h3>
            <p className="text-4xl font-display font-bold text-primary">45%</p>
            <div className="mt-2 text-xs text-text-muted">Normal range</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Memory</h3>
            <p className="text-4xl font-display font-bold text-electric-cyan">62%</p>
            <div className="mt-2 text-xs text-text-muted">6.2GB / 10GB</div>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card padding="lg">
          <h2 className="text-xl font-display font-semibold mb-4">Recent System Events</h2>
          <div className="space-y-3">
            <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
              <span className="text-2xl">✅</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-text-primary">CRM API deployed successfully</p>
                <p className="text-xs text-text-muted">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
              <span className="text-2xl">⚠️</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-text-primary">High memory usage detected on ops-db</p>
                <p className="text-xs text-text-muted">3 hours ago</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
              <span className="text-2xl">🔄</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-text-primary">Redis cache cleared automatically</p>
                <p className="text-xs text-text-muted">5 hours ago</p>
              </div>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default DashboardPage;
