/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const ClientPortalPreview: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">Client Portal Preview</h1>
          <p className="text-text-secondary mt-1">Customer-facing portal interface</p>
        </div>
        <Button variant="primary" size="lg">Open Portal</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portal Preview */}
        <div className="lg:col-span-2">
          <Card variant="glass" padding="none" className="overflow-hidden">
            {/* Portal Header */}
            <div className="bg-gradient-to-r from-primary/20 to-primary/10 border-b border-white/10 p-6">
              <div className="flex items-center gap-4">
                <img src="/brand/logo-icon.svg" alt="StormFusion" className="w-12 h-12" />
                <div>
                  <h2 className="text-xl font-bold text-text-primary">Welcome, Acme Corp</h2>
                  <p className="text-sm text-text-secondary">Customer Portal</p>
                </div>
              </div>
            </div>

            {/* Portal Content */}
            <div className="p-6 space-y-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: 'Active Services', value: '3' },
                  { label: 'Open Tickets', value: '1' },
                  { label: 'Invoices', value: '5' },
                ].map((stat, i) => (
                  <div key={i} className="p-4 bg-white/5 border border-white/10 rounded-lg text-center">
                    <p className="text-2xl font-bold text-text-primary">{stat.value}</p>
                    <p className="text-sm text-text-muted mt-1">{stat.label}</p>
                  </div>
                ))}
              </div>

              {/* Recent Activity */}
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">Recent Activity</h3>
                <div className="space-y-2">
                  {[
                    { icon: '✅', text: 'Service completed - Job #1234', time: '2 hours ago' },
                    { icon: '📄', text: 'New invoice #INV-5678', time: '1 day ago' },
                    { icon: '📅', text: 'Appointment scheduled', time: '3 days ago' },
                  ].map((activity, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 rounded-lg"
                    >
                      <span className="text-xl">{activity.icon}</span>
                      <div className="flex-1">
                        <p className="text-sm text-text-primary">{activity.text}</p>
                        <p className="text-xs text-text-muted mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">Quick Actions</h3>
                <div className="grid grid-cols-2 gap-3">
                  <button className="p-4 bg-primary/10 border border-primary/20 rounded-lg text-sm font-medium text-primary hover:bg-primary/20 transition-colors">
                    📅 Schedule Service
                  </button>
                  <button className="p-4 bg-white/5 border border-white/10 rounded-lg text-sm font-medium text-text-primary hover:bg-white/10 transition-colors">
                    💳 Pay Invoice
                  </button>
                  <button className="p-4 bg-white/5 border border-white/10 rounded-lg text-sm font-medium text-text-primary hover:bg-white/10 transition-colors">
                    📧 Contact Support
                  </button>
                  <button className="p-4 bg-white/5 border border-white/10 rounded-lg text-sm font-medium text-text-primary hover:bg-white/10 transition-colors">
                    📊 View Reports
                  </button>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Info Panel */}
        <div className="space-y-4">
          <Card variant="glass" padding="lg">
            <h3 className="text-lg font-semibold text-text-primary mb-3">Portal Features</h3>
            <ul className="space-y-2 text-sm">
              {[
                'Service history',
                'Invoice management',
                'Schedule appointments',
                'Support tickets',
                'Document library',
                'Payment processing',
                'Real-time updates',
              ].map((feature, i) => (
                <li key={i} className="flex items-center gap-2 text-text-secondary">
                  <span className="text-success">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
          </Card>

          <Card variant="glass" padding="lg">
            <h3 className="text-lg font-semibold text-text-primary mb-3">Access</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-text-secondary mb-2">Portal URL</p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded text-xs text-primary">
                    portal.stormfusion.app
                  </code>
                  <Button variant="ghost" size="sm">Copy</Button>
                </div>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-2">Active Clients</p>
                <p className="text-2xl font-bold text-text-primary">89</p>
              </div>
            </div>
          </Card>

          <Card variant="glass" padding="lg">
            <h3 className="text-lg font-semibold text-text-primary mb-3">Customization</h3>
            <div className="space-y-2">
              <Button variant="secondary" size="sm" fullWidth>
                Edit Branding
              </Button>
              <Button variant="secondary" size="sm" fullWidth>
                Configure Features
              </Button>
              <Button variant="secondary" size="sm" fullWidth>
                Manage Access
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ClientPortalPreview;
