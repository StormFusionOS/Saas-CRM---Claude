/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Button Component Wrapper
 *
 * Wraps shadcn/ui Button with our existing API for backward compatibility.
 * Maps our custom variants to shadcn variants while preserving props.
 */

import React from 'react';
import { Button as ShadcnButton } from './button';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'none';
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', fullWidth = false, icon, className = '', children, ...props }, ref) => {
    // Map our variants to shadcn variants
    const shadcnVariant =
      variant === 'primary' ? 'default' :
      variant === 'secondary' ? 'secondary' :
      variant === 'outline' ? 'outline' :
      variant === 'danger' ? 'destructive' :
      'ghost';

    // Map our sizes to shadcn sizes
    const shadcnSize =
      size === 'none' ? 'sm' :
      size === 'md' ? 'default' :
      size as 'default' | 'sm' | 'lg' | 'icon';

    // Add custom classes for our design system
    const customClasses = cn(
      // Preserve our hover/active animations
      'hover:scale-[1.02] active:scale-[0.98] transition-transform',
      // Add glow effect for primary buttons
      variant === 'primary' && 'glow-hover shadow-sm',
      // Full width
      fullWidth && 'w-full',
      // Icon spacing
      icon && 'gap-2',
      className
    );

    return (
      <ShadcnButton
        ref={ref}
        variant={shadcnVariant}
        size={shadcnSize}
        className={customClasses}
        {...props}
      >
        {icon}
        {children}
      </ShadcnButton>
    );
  }
);

Button.displayName = 'Button';

export default Button;
