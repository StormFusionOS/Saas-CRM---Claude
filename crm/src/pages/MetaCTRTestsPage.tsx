/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Meta Rewrite & CTR Tests
 * A/B test meta descriptions and titles for CTR improvement
 */

import React from 'react';
import Card from '../components/ui/Card';
import { TestTube, TrendingUp, BarChart3, Trophy } from 'lucide-react';

const MetaCTRTestsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Meta Rewrite & CTR Tests</h1>
        <p className="text-sm text-text-muted mt-1">
          A/B test meta descriptions and titles for click-through rate improvement
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TestTube className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Active Tests</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">Running now</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Trophy className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Winners Applied</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Winning variants</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Avg CTR Lift</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0%</p>
              <div className="mt-2 text-xs text-text-muted">From tests</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Pages Tested</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Total pages</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">CTR Optimization Tactics</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">Numbers & Data</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">+15% CTR</span>
                </div>
                <p className="text-xs text-text-muted">Include specific numbers, stats, or years in titles</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Power Words</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">+12% CTR</span>
                </div>
                <p className="text-xs text-text-muted">Ultimate, Essential, Proven, Complete, Best</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Emotional Triggers</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">+10% CTR</span>
                </div>
                <p className="text-xs text-text-muted">Create curiosity, urgency, or solve pain points</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Questions</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">+8% CTR</span>
                </div>
                <p className="text-xs text-text-muted">Frame titles as questions to engage curiosity</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Testing Best Practices</h2>
            <div className="space-y-4 text-sm text-text-secondary">
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <p className="font-medium text-text-primary mb-2">Test Duration</p>
                <p className="text-xs text-text-muted mb-2">Run tests for minimum 2-4 weeks to gather statistically significant data</p>
                <div className="flex items-center gap-2">
                  <div className="h-2 flex-1 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full w-0 bg-primary rounded-full" />
                  </div>
                  <span className="text-xs text-text-muted">0 days</span>
                </div>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <p className="font-medium text-text-primary mb-2">Sample Size</p>
                <p className="text-xs text-text-muted">Minimum 1,000 impressions per variant for reliable results</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <p className="font-medium text-text-primary mb-2">Confidence Level</p>
                <p className="text-xs text-text-muted">Aim for 95% statistical confidence before declaring a winner</p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default MetaCTRTestsPage;
