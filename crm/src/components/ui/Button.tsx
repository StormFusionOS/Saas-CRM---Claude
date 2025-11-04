/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', fullWidth = false, className = '', children, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-base transition-all duration-base focus-ring disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] active:scale-[0.98]';

    const variantClasses = {
      primary: 'bg-primary hover:bg-primary-hover active:bg-primary-active text-text-inverse shadow-sm glow-hover',
      secondary: 'bg-bg-elev hover:bg-bg-hover active:bg-bg-active text-text-primary border border-border-default',
      outline: 'bg-transparent hover:bg-bg-hover active:bg-bg-active text-text-primary border border-border-strong',
      ghost: 'bg-transparent hover:bg-bg-hover active:bg-bg-active text-text-primary',
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    const widthClass = fullWidth ? 'w-full' : '';

    const combinedClasses = [
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      widthClass,
      className,
    ].filter(Boolean).join(' ');

    return (
      <button ref={ref} className={combinedClasses} {...props}>
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
