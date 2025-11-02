/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'neon';
  padding?: 'sm' | 'md' | 'lg';
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', className = '', children, ...props }, ref) => {
    const baseClasses = 'rounded-lg transition-all duration-base';

    const variantClasses = {
      default: 'bg-bg-elev border border-border-default shadow-base',
      glass: 'glass-surface shadow-md',
      neon: 'bg-bg-elev border-2 border-accent neon-border shadow-glow-cyan',
    };

    const paddingClasses = {
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    const combinedClasses = [
      baseClasses,
      variantClasses[variant],
      paddingClasses[padding],
      className,
    ].filter(Boolean).join(' ');

    return (
      <div ref={ref} className={combinedClasses} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card;
