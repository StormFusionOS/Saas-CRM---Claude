/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Card Component Wrapper
 *
 * Wraps shadcn/ui Card with our existing API for backward compatibility.
 * Adds our custom variants (glass, neon) on top of shadcn's base card.
 */

import React from 'react';
import { Card as ShadcnCard } from './shadcn/card';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'neon';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  animate?: 'none' | 'fade-in' | 'slide-in-up' | 'scale-in';
  hover?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', animate = 'none', hover = false, className = '', children, ...props }, ref) => {
    // Variant-specific classes
    const variantClasses = {
      default: '', // Use shadcn default
      glass: 'glass-surface shadow-md backdrop-blur-md bg-opacity-80',
      neon: 'border-2 border-accent neon-border shadow-glow-cyan',
    };

    // Padding classes
    const paddingClasses = {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    // Animation classes
    const animationClasses = {
      none: '',
      'fade-in': 'animate-fade-in',
      'slide-in-up': 'animate-slide-in-up',
      'scale-in': 'animate-scale-in',
    };

    const customClasses = cn(
      variantClasses[variant],
      paddingClasses[padding],
      animationClasses[animate],
      hover && 'hover:scale-[1.02] hover:shadow-lg transition-all cursor-pointer',
      className
    );

    return (
      <ShadcnCard ref={ref} className={customClasses} {...props}>
        {children}
      </ShadcnCard>
    );
  }
);

Card.displayName = 'Card';

export default Card;
