/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Node Summary Card Component
 * Displays server information: hostname, uptime, OS, model versions
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Badge } from '@/components/ui/shadcn/badge';
import { Server, Clock, Cpu, HardDrive } from 'lucide-react';
import type { NodeInfo } from '@/lib/ai-types';

interface NodeSummaryCardProps {
  node: NodeInfo;
  isLoading?: boolean;
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h`;
  }
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

export function NodeSummaryCard({ node, isLoading }: NodeSummaryCardProps) {
  if (isLoading) {
    return (
      <Card className="relative overflow-hidden">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-white/5 rounded w-2/3" />
          <div className="space-y-2">
            <div className="h-4 bg-white/5 rounded w-full" />
            <div className="h-4 bg-white/5 rounded w-5/6" />
            <div className="h-4 bg-white/5 rounded w-4/6" />
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="relative overflow-hidden glow-hover">
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl" />

      <div className="relative space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Server className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                {node.hostname}
              </h3>
              <p className="text-sm text-text-muted">{node.os}</p>
            </div>
          </div>
          <Badge variant="outline" className="bg-success/10 text-success border-success/20">
            Online
          </Badge>
        </div>

        {/* System Info */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-text-secondary" />
            <div>
              <p className="text-xs text-text-muted">Uptime</p>
              <p className="text-sm font-medium text-text-primary">
                {formatUptime(node.uptime)}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-text-secondary" />
            <div>
              <p className="text-xs text-text-muted">CPU Cores</p>
              <p className="text-sm font-medium text-text-primary">
                {node.cpu_count}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-text-secondary" />
            <div>
              <p className="text-xs text-text-muted">Total RAM</p>
              <p className="text-sm font-medium text-text-primary">
                {node.total_ram_gb} GB
              </p>
            </div>
          </div>
        </div>

        {/* Model Versions */}
        <div className="pt-4 border-t border-white/5">
          <p className="text-xs font-medium text-text-secondary mb-3">AI Models</p>
          <div className="space-y-2">
            {Object.entries(node.model_versions).map(([model, version]) => (
              <div
                key={model}
                className="flex items-center justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
              >
                <span className="text-sm text-text-primary font-mono">{model}</span>
                <Badge variant="secondary" className="text-xs">
                  {version}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
