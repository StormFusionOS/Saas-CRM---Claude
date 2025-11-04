/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Brand colors
        'storm-blue': 'var(--color-storm-blue)',
        'electric-cyan': 'var(--color-electric-cyan)',
        'midnight': 'var(--color-midnight)',
        'deep-ocean': 'var(--color-deep-ocean)',
        'steel-gray': 'var(--color-steel-gray)',

        // Semantic colors
        'bg-base': 'var(--color-bg-base)',
        'bg-elev': 'var(--color-bg-elev)',
        'bg-hover': 'var(--color-bg-hover)',
        'bg-active': 'var(--color-bg-active)',

        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-muted': 'var(--color-text-muted)',
        'text-inverse': 'var(--color-text-inverse)',

        // Interactive
        'primary': 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        'primary-active': 'var(--color-primary-active)',
        'accent': 'var(--color-accent)',
        'accent-hover': 'var(--color-accent-hover)',
        'accent-active': 'var(--color-accent-active)',

        // Status
        'success': 'var(--color-success)',
        'warning': 'var(--color-warning)',
        'error': 'var(--color-error)',
        'info': 'var(--color-info)',
      },
      borderRadius: {
        'sm': 'var(--radius-sm)',
        'base': 'var(--radius-base)',
        'lg': 'var(--radius-lg)',
      },
      boxShadow: {
        'sm': 'var(--shadow-sm)',
        'base': 'var(--shadow-base)',
        'md': 'var(--shadow-md)',
        'lg': 'var(--shadow-lg)',
        'glow-cyan': 'var(--shadow-glow-cyan)',
        'glow-blue': 'var(--shadow-glow-blue)',
      },
      fontFamily: {
        'sans': 'var(--font-sans)',
        'display': 'var(--font-display)',
        'mono': 'var(--font-mono)',
      },
      spacing: {
        'nav': 'var(--space-nav-collapsed)',
        'nav-expanded': 'var(--space-nav-expanded)',
        'topbar': 'var(--space-topbar-height)',
      },
      transitionDuration: {
        'fast': 'var(--transition-fast)',
        'base': 'var(--transition-base)',
        'slow': 'var(--transition-slow)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'slide-in-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-down': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-left': {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'bounce-in': {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: 'var(--shadow-glow-cyan)' },
          '50%': { boxShadow: '0 0 30px rgba(0, 183, 253, 0.5)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fade-in var(--transition-base) ease-out',
        'fade-out': 'fade-out var(--transition-base) ease-in',
        'slide-in-up': 'slide-in-up var(--transition-base) ease-out',
        'slide-in-down': 'slide-in-down var(--transition-base) ease-out',
        'slide-in-left': 'slide-in-left var(--transition-base) ease-out',
        'slide-in-right': 'slide-in-right var(--transition-base) ease-out',
        'scale-in': 'scale-in var(--transition-base) ease-out',
        'bounce-in': 'bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [],
}
