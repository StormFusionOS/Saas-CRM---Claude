/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Backlink Gap Finder
 * Discover competitor backlinks you're missing
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Search, Link, Target, TrendingUp } from 'lucide-react';

const BacklinkGapFinderPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Backlink Gap Finder</h1>
        <p className="text-sm text-text-muted mt-1">
          Discover competitor backlinks you're missing and prioritize outreach
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Search className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Gaps Found</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">Backlink opportunities</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Link className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Acquired Links</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Successfully obtained</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Priority Targets</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">High-value domains</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Avg Domain Authority</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Of gap links</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Gap Analysis Process</h2>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Identify Competitors</p>
                  <p className="text-xs text-text-muted">Select 3-5 direct competitors ranking for your target keywords</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Extract Backlinks</p>
                  <p className="text-xs text-text-muted">Use SEO tools to pull all competitor backlink profiles</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Find Gaps</p>
                  <p className="text-xs text-text-muted">Identify domains linking to competitors but not to you</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  4
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Score Opportunities</p>
                  <p className="text-xs text-text-muted">Rank by domain authority, relevance, and attainability</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  5
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Plan Outreach</p>
                  <p className="text-xs text-text-muted">Create personalized outreach campaigns for top targets</p>
                </div>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Link Quality Factors</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">Domain Authority</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">High Impact</span>
                </div>
                <p className="text-xs text-text-muted">Higher DA domains pass more link equity</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Topical Relevance</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Critical</span>
                </div>
                <p className="text-xs text-text-muted">Links from related industries are more valuable</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Link Placement</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Context</span>
                </div>
                <p className="text-xs text-text-muted">Editorial links in content beat sidebar/footer links</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Traffic Potential</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Referral</span>
                </div>
                <p className="text-xs text-text-muted">High-traffic pages can drive direct visitors</p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default BacklinkGapFinderPage;
