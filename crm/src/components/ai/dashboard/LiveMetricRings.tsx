/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Live Metric Rings Component
 * Displays real-time system metrics (CPU, GPU, RAM, Disk, Network) with circular progress indicators
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Progress } from '@/components/ui/shadcn/progress';
import { Cpu, Zap, MemoryStick, HardDrive, Network } from 'lucide-react';
import type { SystemMetrics, MetricThresholds } from '@/lib/ai-types';
import { cn } from '@/lib/utils';

interface LiveMetricRingsProps {
  metrics: SystemMetrics;
  thresholds: MetricThresholds;
  isLoading?: boolean;
}

interface MetricRingProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  unit?: string;
  thresholds: MetricThresholds;
}

function getMetricColor(value: number, thresholds: MetricThresholds): string {
  if (value >= thresholds.critical) {
    return 'text-error';
  }
  if (value >= thresholds.warning) {
    return 'text-warning';
  }
  return 'text-success';
}

function getProgressColor(value: number, thresholds: MetricThresholds): string {
  if (value >= thresholds.critical) {
    return 'bg-error';
  }
  if (value >= thresholds.warning) {
    return 'bg-warning';
  }
  return 'bg-success';
}

function MetricRing({ label, value, icon, unit = '%', thresholds }: MetricRingProps) {
  const colorClass = getMetricColor(value, thresholds);
  const progressColor = getProgressColor(value, thresholds);

  return (
    <div className="flex flex-col items-center space-y-3">
      {/* Circular Progress */}
      <div className="relative w-24 h-24">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="48"
            cy="48"
            r="44"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-white/10"
          />
          {/* Progress circle */}
          <circle
            cx="48"
            cy="48"
            r="44"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 44}`}
            strokeDashoffset={`${2 * Math.PI * 44 * (1 - value / 100)}`}
            className={cn(
              'transition-all duration-500',
              progressColor
            )}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="p-2 rounded-lg bg-bg-elevated">
            {icon}
          </div>
        </div>
      </div>

      {/* Label and value */}
      <div className="text-center">
        <p className={cn('text-2xl font-bold font-display', colorClass)}>
          {value.toFixed(0)}{unit}
        </p>
        <p className="text-xs text-text-muted mt-1">{label}</p>
      </div>
    </div>
  );
}

export function LiveMetricRings({ metrics, thresholds, isLoading }: LiveMetricRingsProps) {
  if (isLoading) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-white/5 rounded w-1/3" />
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex flex-col items-center space-y-3">
                <div className="w-24 h-24 bg-white/5 rounded-full" />
                <div className="h-4 bg-white/5 rounded w-16" />
              </div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-text-primary">
            System Metrics
          </h3>
          <div className="flex items-center gap-4 text-xs text-text-muted">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-success" />
              <span>Healthy</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-warning" />
              <span>Warning ({thresholds.warning}%+)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-error" />
              <span>Critical ({thresholds.critical}%+)</span>
            </div>
          </div>
        </div>

        {/* Metric Rings */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
          <MetricRing
            label="CPU"
            value={metrics.cpu}
            icon={<Cpu className="w-5 h-5 text-primary" />}
            thresholds={thresholds}
          />
          <MetricRing
            label="GPU"
            value={metrics.gpu}
            icon={<Zap className="w-5 h-5 text-accent" />}
            thresholds={thresholds}
          />
          <MetricRing
            label="RAM"
            value={metrics.ram}
            icon={<MemoryStick className="w-5 h-5 text-secondary" />}
            thresholds={thresholds}
          />
          <MetricRing
            label="Disk"
            value={metrics.disk}
            icon={<HardDrive className="w-5 h-5 text-warning" />}
            thresholds={thresholds}
          />
          <MetricRing
            label="Network"
            value={Math.min((metrics.network / 1000) * 100, 100)} // Scale to percentage
            icon={<Network className="w-5 h-5 text-info" />}
            unit=" Mbps"
            thresholds={thresholds}
          />
        </div>

        {/* Last updated */}
        <div className="pt-4 border-t border-white/5">
          <p className="text-xs text-text-muted text-center">
            Last updated: {new Date(metrics.timestamp).toLocaleTimeString()}
          </p>
        </div>
      </div>
    </Card>
  );
}
