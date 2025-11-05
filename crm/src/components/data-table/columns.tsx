/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Column Definition Helpers
 *
 * Provides type-safe helpers for creating TanStack Table column definitions
 * with common patterns like sorting, filtering, and visibility toggles.
 */

import React from 'react';
import { ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import Button from '@/components/ui/Button';

/**
 * Creates a sortable column header with sort indicators
 */
export function createSortableHeader<TData>(
  column: any,
  title: string
): React.ReactNode {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      className="h-8 px-2 -ml-2 hover:bg-muted/50"
    >
      <span>{title}</span>
      {column.getIsSorted() === 'asc' ? (
        <ArrowUp className="ml-2 h-4 w-4" />
      ) : column.getIsSorted() === 'desc' ? (
        <ArrowDown className="ml-2 h-4 w-4" />
      ) : (
        <ArrowUpDown className="ml-2 h-4 w-4 opacity-50" />
      )}
    </Button>
  );
}

/**
 * Creates a text column with optional sorting
 */
export function createTextColumn<TData>(
  accessorKey: string,
  header: string,
  options?: {
    sortable?: boolean;
    enableHiding?: boolean;
    cell?: (value: any) => React.ReactNode;
  }
): ColumnDef<TData> {
  return {
    accessorKey,
    header: options?.sortable
      ? ({ column }) => createSortableHeader(column, header)
      : header,
    enableHiding: options?.enableHiding ?? true,
    cell: options?.cell
      ? ({ getValue }) => options.cell!(getValue())
      : ({ getValue }) => getValue(),
  };
}

/**
 * Creates a date column with formatting and optional sorting
 */
export function createDateColumn<TData>(
  accessorKey: string,
  header: string,
  options?: {
    sortable?: boolean;
    enableHiding?: boolean;
    format?: (date: Date | string) => string;
  }
): ColumnDef<TData> {
  const defaultFormat = (date: Date | string) => {
    if (!date) return '-';
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return {
    accessorKey,
    header: options?.sortable
      ? ({ column }) => createSortableHeader(column, header)
      : header,
    enableHiding: options?.enableHiding ?? true,
    cell: ({ getValue }) => {
      const value = getValue();
      return (options?.format || defaultFormat)(value as Date | string);
    },
  };
}

/**
 * Creates a status badge column
 */
export function createStatusColumn<TData>(
  accessorKey: string,
  header: string,
  statusMap: Record<
    string,
    { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
  >
): ColumnDef<TData> {
  return {
    accessorKey,
    header,
    enableHiding: true,
    cell: ({ getValue }) => {
      const value = getValue() as string;
      const status = statusMap[value] || {
        label: value,
        variant: 'default' as const,
      };
      return (
        <span
          className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
            status.variant === 'default'
              ? 'bg-primary/10 text-primary'
              : status.variant === 'secondary'
              ? 'bg-secondary/10 text-secondary'
              : status.variant === 'destructive'
              ? 'bg-destructive/10 text-destructive'
              : 'bg-muted text-muted-foreground'
          }`}
        >
          {status.label}
        </span>
      );
    },
  };
}

/**
 * Creates a currency column with formatting
 */
export function createCurrencyColumn<TData>(
  accessorKey: string,
  header: string,
  options?: {
    sortable?: boolean;
    enableHiding?: boolean;
    currency?: string;
  }
): ColumnDef<TData> {
  return {
    accessorKey,
    header: options?.sortable
      ? ({ column }) => createSortableHeader(column, header)
      : header,
    enableHiding: options?.enableHiding ?? true,
    cell: ({ getValue }) => {
      const value = getValue() as number;
      if (value === null || value === undefined) return '-';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: options?.currency || 'USD',
      }).format(value);
    },
  };
}
