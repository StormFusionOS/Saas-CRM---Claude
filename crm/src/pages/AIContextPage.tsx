/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Context Page
 * RAG (Retrieval Augmented Generation) system for AI context management
 */

import React from 'react';
import Card from '../components/ui/Card';

const AIContextPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">AI Context & RAG</h1>
        <p className="text-sm text-text-muted mt-1">
          Retrieval Augmented Generation - Context retrieval and embeddings for AI models
        </p>
      </div>

      {/* Main Content */}
      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Indexed Documents</h3>
            <p className="text-4xl font-display font-bold text-electric-cyan">1.2K</p>
            <div className="mt-2 text-xs text-text-muted">WordPress pages</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Embeddings</h3>
            <p className="text-4xl font-display font-bold text-primary">45K</p>
            <div className="mt-2 text-xs text-text-muted">Vector dimensions</div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <h3 className="text-sm font-medium text-text-secondary mb-2">Queries (24h)</h3>
            <p className="text-4xl font-display font-bold text-success">892</p>
            <div className="mt-2 text-xs text-text-muted">Avg 45ms response</div>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Collections</h2>
            <div className="space-y-3">
              <div className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-primary">pages</span>
                  <span className="text-xs text-text-muted">1,234 docs</span>
                </div>
                <p className="text-xs text-text-secondary">WordPress pages and content</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-electric-cyan">keywords</span>
                  <span className="text-xs text-text-muted">3,456 docs</span>
                </div>
                <p className="text-xs text-text-secondary">SEO keyword research data</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Recent Queries</h2>
            <div className="text-center py-8">
              <div className="text-5xl mb-3">🔍</div>
              <p className="text-sm text-text-muted">Query history will appear here</p>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default AIContextPage;
