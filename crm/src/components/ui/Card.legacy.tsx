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
  animate?: 'none' | 'fade-in' | 'slide-in-up' | 'scale-in';
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', animate = 'none', className = '', children, ...props }, ref) => {
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

    const animationClasses = {
      none: '',
      'fade-in': 'animate-fade-in',
      'slide-in-up': 'animate-slide-in-up',
      'scale-in': 'animate-scale-in',
    };

    const combinedClasses = [
      baseClasses,
      variantClasses[variant],
      paddingClasses[padding],
      animationClasses[animate],
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
