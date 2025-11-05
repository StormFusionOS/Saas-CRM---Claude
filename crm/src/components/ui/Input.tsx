/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Input Component Wrapper
 *
 * Wraps shadcn/ui Input with our existing API for backward compatibility.
 * Preserves label, error, and helperText features.
 */

import React from 'react';
import { Input as ShadcnInput } from './shadcn/input';
import { Label } from './shadcn/label';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, fullWidth = true, className = '', ...props }, ref) => {
    const inputClasses = cn(
      // Add our custom focus-ring style
      'focus-ring hover:border-border-strong',
      error && 'border-error focus:ring-error',
      className
    );

    return (
      <div className={cn(fullWidth && 'w-full')}>
        {label && (
          <Label className="block text-sm font-medium text-text-primary mb-2">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </Label>
        )}
        <ShadcnInput
          ref={ref}
          className={inputClasses}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${props.id}-error` : helperText ? `${props.id}-helper` : undefined}
          aria-label={label}
          {...props}
        />
        {error && (
          <p id={`${props.id}-error`} className="mt-1 text-sm text-error">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={`${props.id}-helper`} className="mt-1 text-sm text-text-muted">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
