/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';

export interface GaugeProps {
  value: number; // 0-100
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'accent' | 'success' | 'warning' | 'error';
}

const Gauge: React.FC<GaugeProps> = ({
  value,
  label,
  size = 'md',
  color = 'primary'
}) => {
  const clampedValue = Math.max(0, Math.min(100, value));
  const percentage = clampedValue / 100;

  const sizeConfig = {
    sm: { radius: 40, strokeWidth: 8, width: 100, height: 60 },
    md: { radius: 60, strokeWidth: 10, width: 150, height: 90 },
    lg: { radius: 80, strokeWidth: 12, width: 200, height: 120 },
  };

  const colorConfig = {
    primary: 'var(--color-primary)',
    accent: 'var(--color-accent)',
    success: 'rgb(16, 185, 129)',
    warning: 'rgb(245, 158, 11)',
    error: 'rgb(239, 68, 68)',
  };

  const { radius, strokeWidth, width, height } = sizeConfig[size];
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference * (1 - percentage);

  const centerX = width / 2;
  const centerY = height - 10;

  return (
    <div className="inline-flex flex-col items-center gap-2">
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        style={{ overflow: 'visible' }}
        role="img"
        aria-label={`Gauge showing ${clampedValue}%`}
      >
        {/* Background arc */}
        <path
          d={`M ${centerX - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${centerX + radius} ${centerY}`}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Value arc */}
        <path
          d={`M ${centerX - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${centerX + radius} ${centerY}`}
          fill="none"
          stroke={colorConfig[color]}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{
            transition: 'stroke-dashoffset 0.5s ease',
            filter: `drop-shadow(0 0 6px ${colorConfig[color]})`,
          }}
        />

        {/* Center value text */}
        <text
          x={centerX}
          y={centerY - radius / 2}
          textAnchor="middle"
          className="text-2xl font-bold fill-text-primary"
        >
          {clampedValue}%
        </text>
      </svg>
      {label && (
        <span className="text-sm text-text-secondary">{label}</span>
      )}
    </div>
  );
};

export default Gauge;
