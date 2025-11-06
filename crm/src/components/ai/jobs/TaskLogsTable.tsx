/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Task Logs Table Component
 * Filterable table showing job execution logs with pagination
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Button } from '@/components/ui/shadcn/button';
import { Badge } from '@/components/ui/shadcn/badge';
import { Input } from '@/components/ui/shadcn/input';
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Search,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import type { TaskLog, TaskLogsFilters } from '@/lib/ai-types';
import { cn } from '@/lib/utils';
import { useTaskLogs } from '@/lib/ai-queries';

interface TaskLogsTableProps {
  initialFilters?: Partial<TaskLogsFilters>;
}

function getStatusBadge(status: TaskLog['status']) {
  const config = {
    completed: {
      icon: CheckCircle,
      label: 'Completed',
      className: 'bg-success/10 text-success border-success/20',
    },
    failed: {
      icon: XCircle,
      label: 'Failed',
      className: 'bg-error/10 text-error border-error/20',
    },
    running: {
      icon: Clock,
      label: 'Running',
      className: 'bg-primary/10 text-primary border-primary/20',
    },
    pending: {
      icon: AlertCircle,
      label: 'Pending',
      className: 'bg-muted',
    },
  };

  const { icon: Icon, label, className } = config[status];

  return (
    <Badge variant="outline" className={cn('gap-1', className)}>
      <Icon className="w-3 h-3" />
      {label}
    </Badge>
  );
}

function formatDuration(ms?: number): string {
  if (!ms) return 'N/A';
  if (ms < 1000) return `${ms}ms`;
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}

export function TaskLogsTable({ initialFilters = {} }: TaskLogsTableProps) {
  const [filters, setFilters] = React.useState<TaskLogsFilters>({
    page: 1,
    page_size: 20,
    ...initialFilters,
  });

  const [searchQuery, setSearchQuery] = React.useState('');

  const { data: logsData, isLoading } = useTaskLogs(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, job_name: searchQuery || undefined, page: 1 });
  };

  const handleStatusFilter = (status?: TaskLog['status']) => {
    setFilters({ ...filters, status, page: 1 });
  };

  const handlePageChange = (newPage: number) => {
    setFilters({ ...filters, page: newPage });
  };

  if (isLoading && !logsData) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-white/5 rounded w-1/4" />
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-white/5 rounded" />
          ))}
        </div>
      </Card>
    );
  }

  const logs = logsData?.logs || [];
  const total = logsData?.total || 0;
  const totalPages = Math.ceil(total / filters.page_size);

  return (
    <Card>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-text-primary">Task Logs</h2>
            <p className="text-sm text-text-muted mt-1">
              {total} total executions
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <Input
                type="text"
                placeholder="Search by job name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </form>

          {/* Status Filter */}
          <div className="flex gap-2">
            <Button
              variant={!filters.status ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter(undefined)}
            >
              All
            </Button>
            <Button
              variant={filters.status === 'completed' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('completed')}
            >
              Completed
            </Button>
            <Button
              variant={filters.status === 'failed' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('failed')}
            >
              Failed
            </Button>
            <Button
              variant={filters.status === 'running' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('running')}
            >
              Running
            </Button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Job Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Started
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Message
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center">
                    <Clock className="w-12 h-12 mx-auto text-text-muted mb-3" />
                    <p className="text-text-secondary font-medium mb-1">
                      No logs found
                    </p>
                    <p className="text-sm text-text-muted">
                      {filters.status || filters.job_name
                        ? 'Try adjusting your filters'
                        : 'Logs will appear here when jobs run'}
                    </p>
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-white/5 transition-colors"
                  >
                    <td className="px-4 py-4">
                      <div>
                        <p className="text-sm font-medium text-text-primary">
                          {log.job_name}
                        </p>
                        {log.template_name && (
                          <p className="text-xs text-text-muted mt-1">
                            Template: {log.template_name}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      {getStatusBadge(log.status)}
                    </td>
                    <td className="px-4 py-4 text-sm text-text-secondary">
                      {new Date(log.started_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-4 text-sm font-mono text-text-secondary">
                      {formatDuration(log.duration)}
                    </td>
                    <td className="px-4 py-4">
                      {log.error ? (
                        <p className="text-sm text-error">{log.error}</p>
                      ) : log.result_summary ? (
                        <p className="text-sm text-text-muted truncate max-w-xs">
                          {log.result_summary}
                        </p>
                      ) : (
                        <span className="text-sm text-text-muted">—</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t border-white/5">
            <p className="text-sm text-text-muted">
              Page {filters.page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(filters.page - 1)}
                disabled={filters.page === 1}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(filters.page + 1)}
                disabled={filters.page === totalPages}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
