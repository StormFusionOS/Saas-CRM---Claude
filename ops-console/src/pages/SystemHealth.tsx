/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import Card from '../components/ui/Card';

const SystemHealth: React.FC = () => {
  const services = [
    { name: 'API Gateway', status: 'healthy', uptime: '99.98%', latency: '45ms' },
    { name: 'Database Primary', status: 'healthy', uptime: '99.99%', latency: '12ms' },
    { name: 'Redis Cache', status: 'healthy', uptime: '100%', latency: '3ms' },
    { name: 'Worker Queue', status: 'degraded', uptime: '97.5%', latency: '120ms' },
  ];

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Top bar */}
      <header className="glass-surface h-16 px-6 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-2xl font-display font-semibold text-gradient">System Health</h1>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-sm text-text-secondary">All Systems Operational</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {services.map((service) => (
            <Card key={service.name} variant="neon" className="relative overflow-hidden">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-display font-semibold">{service.name}</h3>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    service.status === 'healthy'
                      ? 'bg-success/20 text-success'
                      : 'bg-warning/20 text-warning'
                  }`}
                >
                  {service.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-text-muted text-sm mb-1">Uptime</div>
                  <div className="text-text-primary font-mono text-lg">{service.uptime}</div>
                </div>
                <div>
                  <div className="text-text-muted text-sm mb-1">Latency</div>
                  <div className="text-text-primary font-mono text-lg">{service.latency}</div>
                </div>
              </div>

              {/* Neon accent bar */}
              <div
                className="absolute bottom-0 left-0 right-0 h-1"
                style={{
                  background: service.status === 'healthy'
                    ? 'linear-gradient(90deg, var(--color-success) 0%, var(--color-electric-cyan) 100%)'
                    : 'linear-gradient(90deg, var(--color-warning) 0%, var(--color-error) 100%)',
                  boxShadow: service.status === 'healthy' ? 'var(--shadow-glow-cyan)' : '0 0 10px rgba(245, 158, 11, 0.5)',
                }}
              />
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
};

export default SystemHealth;
