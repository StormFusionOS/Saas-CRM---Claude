/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Snapshot Mini Chart
 * Simple sparkline showing keyword rank trend
 */

import React from 'react';

interface SnapshotMiniChartProps {
  data: number[]; // Array of rank positions over time
  width?: number;
  height?: number;
}

export default function SnapshotMiniChart({
  data,
  width = 100,
  height = 30,
}: SnapshotMiniChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        style={{ width, height }}
        className="flex items-center justify-center text-xs text-gray-400"
      >
        No data
      </div>
    );
  }

  // Calculate min/max for scaling (remember lower rank is better)
  const validData = data.filter((d) => d !== null && d !== undefined);
  if (validData.length === 0) {
    return (
      <div
        style={{ width, height }}
        className="flex items-center justify-center text-xs text-gray-400"
      >
        No data
      </div>
    );
  }

  const min = Math.min(...validData);
  const max = Math.max(...validData);
  const range = max - min || 1;

  // Generate SVG path
  const points = data.map((rank, index) => {
    if (rank === null || rank === undefined) return null;
    const x = (index / (data.length - 1 || 1)) * width;
    // Invert Y because lower rank is better (should be higher on chart)
    const y = height - ((rank - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  }).filter(Boolean);

  const pathData = points.length > 0 ? `M ${points.join(' L ')}` : '';

  // Determine trend color (green if improving/going down, red if worsening/going up)
  const firstRank = validData[0];
  const lastRank = validData[validData.length - 1];
  const trendColor =
    lastRank < firstRank
      ? '#10b981' // green - improving
      : lastRank > firstRank
      ? '#ef4444' // red - worsening
      : '#6b7280'; // gray - stable

  return (
    <svg
      width={width}
      height={height}
      className="inline-block"
      style={{ verticalAlign: 'middle' }}
    >
      <path
        d={pathData}
        fill="none"
        stroke={trendColor}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Show dots at each point */}
      {points.map((point, idx) => {
        if (!point) return null;
        const [x, y] = point.split(',').map(Number);
        return (
          <circle
            key={idx}
            cx={x}
            cy={y}
            r="2"
            fill={trendColor}
          />
        );
      })}
    </svg>
  );
}
