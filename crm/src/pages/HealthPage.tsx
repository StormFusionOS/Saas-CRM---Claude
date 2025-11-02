/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import Card from '../components/ui/Card';

interface ServiceHealth {
  id: string;
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime: string;
  latency: string;
  lastChecked: Date;
  logUrl?: string;
}

const HealthPage: React.FC = () => {
  const [services, setServices] = useState<ServiceHealth[]>([
    {
      id: 'crm-api',
      name: 'CRM API',
      status: 'healthy',
      uptime: '99.98%',
      latency: '45ms',
      lastChecked: new Date(),
      logUrl: '/logs/crm-api',
    },
    {
      id: 'ops-api',
      name: 'Ops API',
      status: 'healthy',
      uptime: '99.95%',
      latency: '52ms',
      lastChecked: new Date(),
      logUrl: '/logs/ops-api',
    },
    {
      id: 'database',
      name: 'PostgreSQL Database',
      status: 'healthy',
      uptime: '99.99%',
      latency: '12ms',
      lastChecked: new Date(),
      logUrl: '/logs/database',
    },
    {
      id: 'redis',
      name: 'Redis Cache',
      status: 'healthy',
      uptime: '100%',
      latency: '3ms',
      lastChecked: new Date(),
      logUrl: '/logs/redis',
    },
    {
      id: 'email',
      name: 'Email Service (SMTP)',
      status: 'healthy',
      uptime: '99.92%',
      latency: '180ms',
      lastChecked: new Date(),
      logUrl: '/logs/email',
    },
    {
      id: 'twilio',
      name: 'Twilio SMS',
      status: 'degraded',
      uptime: '98.5%',
      latency: '320ms',
      lastChecked: new Date(),
      logUrl: '/logs/twilio',
    },
    {
      id: 'wordpress',
      name: 'WordPress Site',
      status: 'healthy',
      uptime: '99.87%',
      latency: '95ms',
      lastChecked: new Date(),
      logUrl: '/logs/wordpress',
    },
  ]);

  const [isRefreshing, setIsRefreshing] = useState<string | null>(null);

  const refreshService = async (serviceId: string) => {
    setIsRefreshing(serviceId);

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    setServices((prev) =>
      prev.map((service) =>
        service.id === serviceId
          ? {
              ...service,
              lastChecked: new Date(),
              // Simulate occasional status changes for realism
              status:
                Math.random() > 0.9
                  ? ('degraded' as const)
                  : ('healthy' as const),
              latency: `${Math.floor(Math.random() * 200 + 10)}ms`,
            }
          : service
      )
    );

    setIsRefreshing(null);
  };

  const refreshAll = async () => {
    setIsRefreshing('all');

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    setServices((prev) =>
      prev.map((service) => ({
        ...service,
        lastChecked: new Date(),
        status:
          Math.random() > 0.85 ? ('degraded' as const) : ('healthy' as const),
        latency: `${Math.floor(Math.random() * 200 + 10)}ms`,
      }))
    );

    setIsRefreshing(null);
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return date.toLocaleTimeString();
  };

  const healthyCount = services.filter((s) => s.status === 'healthy').length;
  const totalCount = services.length;
  const allHealthy = healthyCount === totalCount;

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Top bar */}
      <header className="glass-surface h-16 px-6 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-2xl font-display font-semibold text-gradient">
          System Health
        </h1>
        <div className="flex items-center gap-4">
          <button
            onClick={refreshAll}
            disabled={isRefreshing !== null}
            className="px-4 py-2 rounded-md bg-primary/10 hover:bg-primary/20 text-primary font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRefreshing === 'all' ? 'Refreshing...' : 'Refresh All'}
          </button>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                allHealthy ? 'bg-success' : 'bg-warning'
              } animate-pulse`}
            />
            <span className="text-sm text-text-secondary">
              {allHealthy
                ? 'All Systems Operational'
                : `${healthyCount}/${totalCount} Services Healthy`}
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => (
            <Card key={service.id} variant="neon" className="relative overflow-hidden">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-display font-semibold">
                  {service.name}
                </h3>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    service.status === 'healthy'
                      ? 'bg-success/20 text-success'
                      : service.status === 'degraded'
                      ? 'bg-warning/20 text-warning'
                      : 'bg-error/20 text-error'
                  }`}
                >
                  {service.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <div className="text-text-muted text-sm mb-1">Uptime</div>
                  <div className="text-text-primary font-mono text-lg">
                    {service.uptime}
                  </div>
                </div>
                <div>
                  <div className="text-text-muted text-sm mb-1">Latency</div>
                  <div className="text-text-primary font-mono text-lg">
                    {service.latency}
                  </div>
                </div>
              </div>

              {/* Last checked and actions */}
              <div className="flex items-center justify-between pt-4 border-t border-border-light">
                <div className="text-xs text-text-muted">
                  Last checked: {formatTimestamp(service.lastChecked)}
                </div>
                <div className="flex items-center gap-2">
                  {service.logUrl && (
                    <button
                      onClick={() => alert(`View logs: ${service.logUrl}`)}
                      className="text-xs text-primary hover:text-primary-light transition-colors"
                      title="View Logs"
                    >
                      Logs
                    </button>
                  )}
                  <button
                    onClick={() => refreshService(service.id)}
                    disabled={isRefreshing !== null}
                    className="text-xs text-primary hover:text-primary-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Refresh Status"
                  >
                    {isRefreshing === service.id ? '⟳' : '↻'}
                  </button>
                </div>
              </div>

              {/* Neon accent bar */}
              <div
                className="absolute bottom-0 left-0 right-0 h-1"
                style={{
                  background:
                    service.status === 'healthy'
                      ? 'linear-gradient(90deg, var(--color-success) 0%, var(--color-electric-cyan) 100%)'
                      : service.status === 'degraded'
                      ? 'linear-gradient(90deg, var(--color-warning) 0%, var(--color-error) 100%)'
                      : 'linear-gradient(90deg, var(--color-error) 0%, var(--color-error) 100%)',
                  boxShadow:
                    service.status === 'healthy'
                      ? 'var(--shadow-glow-cyan)'
                      : '0 0 10px rgba(245, 158, 11, 0.5)',
                }}
              />
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
};

export default HealthPage;
