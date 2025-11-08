/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Review Queue Page
 * Human-in-the-loop review interface for AI-generated changes
 */

import React, { useState } from 'react';
import ReviewQueueTable from '../components/governance/ReviewQueueTable';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Filter, X, RefreshCw } from 'lucide-react';

const ReviewQueuePage: React.FC = () => {
  const [moduleFilter, setModuleFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const modules = [
    'ctr_optimizer',
    'meta_enhancer',
    'title_optimizer',
    'schema_generator',
    'content_analyzer',
    'snippet_optimizer',
    'faq_generator',
  ];

  const handleClearFilters = () => {
    setModuleFilter('');
  };

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  const hasActiveFilters = moduleFilter !== '';

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="border-b border-white/5 bg-bg-elev">
        <div className="max-w-[1600px] mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-display font-bold text-gradient">Review Queue</h1>
              <p className="text-sm text-text-muted mt-1">
                Review and approve AI-generated changes before execution
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                Filters
                {hasActiveFilters && (
                  <span className="ml-1 px-1.5 py-0.5 bg-primary/20 text-primary text-xs rounded">
                    1
                  </span>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="border-b border-white/5 bg-bg-elev/50">
          <div className="max-w-[1600px] mx-auto px-8 py-4">
            <Card padding="md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-text-primary">Filters</h3>
                {hasActiveFilters && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClearFilters}
                    className="text-text-muted hover:text-text-primary gap-2"
                  >
                    <X className="w-4 h-4" />
                    Clear All
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Module Filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-secondary">
                    AI Module
                  </label>
                  <select
                    value={moduleFilter}
                    onChange={(e) => setModuleFilter(e.target.value)}
                    className="w-full px-3 py-2 bg-bg-base border border-white/10 rounded-lg text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="">All Modules</option>
                    {modules.map((module) => (
                      <option key={module} value={module}>
                        {module.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Future: Date Filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-secondary">
                    Date Range
                  </label>
                  <select
                    disabled
                    className="w-full px-3 py-2 bg-bg-base border border-white/10 rounded-lg text-sm text-text-muted opacity-50 cursor-not-allowed"
                  >
                    <option>All Time</option>
                  </select>
                </div>

                {/* Future: Site Filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-secondary">
                    Site
                  </label>
                  <select
                    disabled
                    className="w-full px-3 py-2 bg-bg-base border border-white/10 rounded-lg text-sm text-text-muted opacity-50 cursor-not-allowed"
                  >
                    <option>All Sites</option>
                  </select>
                </div>
              </div>

              {hasActiveFilters && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2 text-sm text-text-muted">
                    <span>Active filters:</span>
                    {moduleFilter && (
                      <span className="px-2 py-1 bg-primary/20 text-primary rounded text-xs font-medium">
                        Module: {moduleFilter.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-8 py-8">
        <ReviewQueueTable
          key={refreshKey}
          moduleFilter={moduleFilter}
          onModuleFilterChange={setModuleFilter}
        />
      </main>
    </div>
  );
};

export default ReviewQueuePage;
