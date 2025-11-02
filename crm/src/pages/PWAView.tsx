/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const PWAView: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">Tech PWA Preview</h1>
          <p className="text-text-secondary mt-1">Technician mobile application interface</p>
        </div>
        <Button variant="primary" size="lg">Open PWA</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Mobile Preview */}
        <div className="lg:col-span-2">
          <Card variant="glass" padding="lg">
            <div className="flex justify-center">
              <div className="w-full max-w-md">
                {/* Phone Frame */}
                <div className="relative mx-auto border-8 border-gray-800 rounded-[3rem] h-[600px] w-[300px] shadow-xl">
                  <div className="w-full h-full bg-bg-elevated rounded-[2rem] overflow-hidden">
                    {/* Status Bar */}
                    <div className="bg-bg-base h-10 flex items-center justify-between px-6 text-xs text-text-secondary">
                      <span>9:41</span>
                      <div className="flex items-center gap-1">
                        <span>📶</span>
                        <span>📡</span>
                        <span>🔋</span>
                      </div>
                    </div>

                    {/* App Content */}
                    <div className="p-4 space-y-4">
                      <div className="text-center">
                        <img src="/brand/logo-icon.svg" alt="StormFusion" className="w-16 h-16 mx-auto mb-2" />
                        <h2 className="text-lg font-bold text-text-primary">StormFusion Tech</h2>
                        <p className="text-sm text-text-secondary">Field Technician App</p>
                      </div>

                      {/* Today's Jobs */}
                      <div>
                        <h3 className="text-sm font-semibold text-text-primary mb-2">Today's Jobs</h3>
                        <div className="space-y-2">
                          {['Job #1234 - Acme Corp', 'Job #1235 - Tech Solutions', 'Job #1236 - Green Co'].map(
                            (job, i) => (
                              <div
                                key={i}
                                className="p-3 bg-white/5 border border-white/10 rounded-lg text-sm"
                              >
                                <p className="font-medium text-text-primary">{job}</p>
                                <p className="text-xs text-text-muted mt-1">
                                  {i === 0 ? 'In Progress' : 'Scheduled'}
                                </p>
                              </div>
                            )
                          )}
                        </div>
                      </div>

                      {/* Quick Actions */}
                      <div className="grid grid-cols-2 gap-2">
                        <button className="p-3 bg-primary/10 border border-primary/20 rounded-lg text-xs font-medium text-primary">
                          📍 Check In
                        </button>
                        <button className="p-3 bg-white/5 border border-white/10 rounded-lg text-xs font-medium text-text-primary">
                          📸 Add Photo
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Info Panel */}
        <div className="space-y-4">
          <Card variant="glass" padding="lg">
            <h3 className="text-lg font-semibold text-text-primary mb-3">Features</h3>
            <ul className="space-y-2 text-sm">
              {[
                'Real-time job assignments',
                'GPS tracking & check-in',
                'Photo documentation',
                'Digital signatures',
                'Offline mode support',
                'Inventory management',
              ].map((feature, i) => (
                <li key={i} className="flex items-center gap-2 text-text-secondary">
                  <span className="text-success">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
          </Card>

          <Card variant="glass" padding="lg">
            <h3 className="text-lg font-semibold text-text-primary mb-3">Status</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-text-secondary">Active Techs</span>
                <span className="font-semibold text-text-primary">12</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Jobs Today</span>
                <span className="font-semibold text-text-primary">34</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Completed</span>
                <span className="font-semibold text-success">28</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PWAView;
