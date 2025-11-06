/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Featured Snippet Optimizer
 * Analyze and optimize content for featured snippet opportunities
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Target, List, CheckCircle, TrendingUp } from 'lucide-react';

const SnippetOptimizerPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Featured Snippet Optimizer</h1>
        <p className="text-sm text-text-muted mt-1">
          Analyze content and optimize for featured snippet positions
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Opportunities</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">Snippet targets found</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Won Snippets</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Currently ranking</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Potential</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">High-value targets</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <List className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Snippet Types</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">5</p>
              <div className="mt-2 text-xs text-text-muted">Formats supported</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Snippet Opportunities</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">Paragraph Snippets</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">Most Common</span>
                </div>
                <p className="text-xs text-text-muted">Direct answers to "what is" and "how to" questions</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">List Snippets</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">High CTR</span>
                </div>
                <p className="text-xs text-text-muted">Numbered or bulleted lists for step-by-step content</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Table Snippets</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Comparison</span>
                </div>
                <p className="text-xs text-text-muted">Structured data tables for pricing, specs, comparisons</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Optimization Tips</h2>
            <div className="space-y-4 text-sm text-text-secondary">
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Answer Questions Directly</p>
                  <p className="text-xs text-text-muted">Place clear answers within first 40-60 words</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Use Structured Formatting</p>
                  <p className="text-xs text-text-muted">Headers, lists, and tables help Google extract content</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Target Question Keywords</p>
                  <p className="text-xs text-text-muted">Focus on who, what, where, when, why, how queries</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default SnippetOptimizerPage;
