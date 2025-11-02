import React from 'react';

export interface DonutSegment {
  label: string;
  value: number;
  color?: string;
}

export interface DonutProps {
  segments: DonutSegment[];
  size?: 'sm' | 'md' | 'lg';
  centerLabel?: string;
  centerValue?: string;
}

const Donut: React.FC<DonutProps> = ({
  segments,
  size = 'md',
  centerLabel,
  centerValue,
}) => {
  const sizeConfig = {
    sm: { width: 120, strokeWidth: 16 },
    md: { width: 180, strokeWidth: 24 },
    lg: { width: 240, strokeWidth: 32 },
  };

  const { width, strokeWidth } = sizeConfig[size];
  const radius = (width - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  // Default colors
  const defaultColors = [
    'var(--color-primary)',
    'var(--color-accent)',
    'rgb(16, 185, 129)',
    'rgb(245, 158, 11)',
    'rgb(239, 68, 68)',
    'rgb(139, 92, 246)',
  ];

  // Calculate total value
  const total = segments.reduce((sum, seg) => sum + seg.value, 0);

  // Build segments
  let cumulativePercent = 0;

  return (
    <div className="inline-flex flex-col items-center gap-3">
      <svg
        width={width}
        height={width}
        viewBox={`0 0 ${width} ${width}`}
        style={{ transform: 'rotate(-90deg)' }}
        role="img"
        aria-label={`Donut chart with ${segments.length} segments`}
      >
        {/* Background circle */}
        <circle
          cx={width / 2}
          cy={width / 2}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.05)"
          strokeWidth={strokeWidth}
        />

        {/* Segments */}
        {segments.map((segment, index) => {
          const percent = segment.value / total;
          const strokeDasharray = `${percent * circumference} ${circumference}`;
          const strokeDashoffset = -cumulativePercent * circumference;
          const color = segment.color || defaultColors[index % defaultColors.length];

          cumulativePercent += percent;

          return (
            <circle
              key={index}
              cx={width / 2}
              cy={width / 2}
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              style={{
                transition: 'stroke-dashoffset 0.5s ease, stroke-dasharray 0.5s ease',
                filter: `drop-shadow(0 0 4px ${color})`,
              }}
            />
          );
        })}

        {/* Center text */}
        {(centerLabel || centerValue) && (
          <g transform={`translate(${width / 2}, ${width / 2}) rotate(90)`}>
            {centerValue && (
              <text
                textAnchor="middle"
                className="text-2xl font-bold fill-text-primary"
                y={centerLabel ? -5 : 5}
              >
                {centerValue}
              </text>
            )}
            {centerLabel && (
              <text
                textAnchor="middle"
                className="text-sm fill-text-secondary"
                y={centerValue ? 15 : 5}
              >
                {centerLabel}
              </text>
            )}
          </g>
        )}
      </svg>

      {/* Legend */}
      <div className="flex flex-col gap-1">
        {segments.map((segment, index) => {
          const color = segment.color || defaultColors[index % defaultColors.length];
          const percent = ((segment.value / total) * 100).toFixed(1);

          return (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: color }}
              />
              <span className="text-text-secondary">
                {segment.label}: <span className="text-text-primary font-medium">{percent}%</span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Donut;
