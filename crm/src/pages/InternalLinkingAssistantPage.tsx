/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Internal Linking Assistant
 * Discover and implement strategic internal linking opportunities
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Link2, Lightbulb, CheckCircle, TrendingUp } from 'lucide-react';

const InternalLinkingAssistantPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Internal Linking Assistant</h1>
        <p className="text-sm text-text-muted mt-1">
          Discover and implement strategic internal linking opportunities
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Opportunities</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">Link suggestions</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Implemented</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Links added</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Link2 className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Anchor Texts</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">Suggestions ready</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Orphaned Pages</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Need links</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Link Opportunity Types</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">Contextual Links</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">High Value</span>
                </div>
                <p className="text-xs text-text-muted">Natural links within content body using relevant keywords</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Navigational Links</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Structure</span>
                </div>
                <p className="text-xs text-text-muted">Menu, sidebar, and footer links for site architecture</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Related Content</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Discovery</span>
                </div>
                <p className="text-xs text-text-muted">"Related articles" or "you might also like" sections</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Breadcrumbs</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Hierarchy</span>
                </div>
                <p className="text-xs text-text-muted">Path navigation showing page hierarchy</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Best Practices</h2>
            <div className="space-y-4 text-sm text-text-secondary">
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Descriptive Anchor Text</p>
                  <p className="text-xs text-text-muted">Use relevant keywords that describe the target page</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Link to Relevant Pages</p>
                  <p className="text-xs text-text-muted">Only link when it adds value to the reader</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Prioritize Important Pages</p>
                  <p className="text-xs text-text-muted">Pass more link equity to high-value pages</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Fix Orphaned Pages</p>
                  <p className="text-xs text-text-muted">Ensure all pages have at least one internal link</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Avoid Over-Optimization</p>
                  <p className="text-xs text-text-muted">Vary anchor text and link naturally</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default InternalLinkingAssistantPage;
