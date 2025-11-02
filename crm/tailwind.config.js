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
    },
  },
  plugins: [],
}
