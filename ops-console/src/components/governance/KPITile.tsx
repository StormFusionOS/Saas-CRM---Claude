/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * KPI Tile Component
 * Displays a single KPI metric with optional trend and change indicators
 */

import React from 'react';
import Card from '../ui/Card';

export interface KPITileProps {
  title: string;
  value: number | string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  trend?: 'up' | 'down' | 'stable';
  suffix?: string;
  loading?: boolean;
  error?: string | null;
  onClick?: () => void;
  className?: string;
}

const KPITile: React.FC<KPITileProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  trend,
  suffix,
  loading,
  error,
  onClick,
  className = '',
}) => {
  if (loading) {
    return (
      <Card className={`relative overflow-hidden ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-white/10 rounded w-3/4 mb-4"></div>
          <div className="h-10 bg-white/10 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-white/10 rounded w-1/3"></div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`relative overflow-hidden border-error/50 ${className}`}>
        <h3 className="text-sm font-medium text-text-secondary mb-2">{title}</h3>
        <p className="text-sm text-error">{error}</p>
      </Card>
    );
  }

  const getTrendColor = () => {
    if (!trend) return 'text-text-muted';
    if (trend === 'up') return 'text-success';
    if (trend === 'down') return 'text-error';
    return 'text-text-muted';
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '→';
  };

  const getChangeColor = () => {
    if (!change) return 'text-text-muted';
    if (changeType === 'increase') return 'text-success';
    if (changeType === 'decrease') return 'text-error';
    return 'text-text-muted';
  };

  const glowColor = trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'primary';

  return (
    <Card
      className={`relative overflow-hidden glow-hover cursor-pointer transition-all ${className}`}
      onClick={onClick}
    >
      {/* Background glow */}
      <div className={`absolute top-0 right-0 w-24 h-24 bg-${glowColor}/10 rounded-full blur-2xl`} />

      {/* Content */}
      <div className="relative z-10">
        <h3 className="text-sm font-medium text-text-secondary mb-2">{title}</h3>

        <div className="flex items-baseline gap-2 mb-2">
          <p className={`text-4xl font-display font-bold ${getTrendColor()}`}>
            {typeof value === 'number' ? value.toLocaleString() : value}
            {suffix && <span className="text-2xl ml-1">{suffix}</span>}
          </p>
          {trend && (
            <span className={`text-2xl ${getTrendColor()}`}>{getTrendIcon()}</span>
          )}
        </div>

        {change !== undefined && (
          <div className={`text-xs ${getChangeColor()}`}>
            {change > 0 ? '+' : ''}{change} from last period
          </div>
        )}
      </div>
    </Card>
  );
};

export default KPITile;
