/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Rank/Traffic Anomaly Explainer
 * AI-powered detection and explanation of ranking and traffic anomalies
 */

import React from 'react';
import Card from '../components/ui/Card';
import { AlertTriangle, TrendingDown, Lightbulb, Clock } from 'lucide-react';

const AnomalyExplainerPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Rank/Traffic Anomaly Explainer</h1>
        <p className="text-sm text-text-muted mt-1">
          AI-powered detection and explanation of ranking and traffic anomalies
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-error/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-error" />
                <h3 className="text-sm font-medium text-text-secondary">Active Anomalies</h3>
              </div>
              <p className="text-4xl font-display font-bold text-error">0</p>
              <div className="mt-2 text-xs text-text-muted">Detected issues</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingDown className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Traffic Drops</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">Last 30 days</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Explained</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">With AI insights</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Pending Review</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Need attention</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Common Anomaly Causes</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-error/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-error">Algorithm Updates</span>
                  <span className="text-xs bg-error/10 text-error px-2 py-1 rounded">High Impact</span>
                </div>
                <p className="text-xs text-text-muted">Google core updates or specific algorithm changes affecting rankings</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Technical Issues</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Common</span>
                </div>
                <p className="text-xs text-text-muted">Crawl errors, broken links, slow page speed, mobile issues</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Content Changes</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Trackable</span>
                </div>
                <p className="text-xs text-text-muted">Major page edits, removals, or consolidations affecting traffic</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Competitor Actions</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">External</span>
                </div>
                <p className="text-xs text-text-muted">Competitors improving content or gaining authoritative backlinks</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Seasonal Trends</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Expected</span>
                </div>
                <p className="text-xs text-text-muted">Natural search volume fluctuations based on seasonality</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">AI Analysis Process</h2>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Detect Anomalies</p>
                  <p className="text-xs text-text-muted">AI monitors traffic and rankings to identify unusual patterns</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Correlate Events</p>
                  <p className="text-xs text-text-muted">Match anomalies with algorithm updates, site changes, etc.</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Analyze Context</p>
                  <p className="text-xs text-text-muted">Review page content, backlinks, technical factors, and competitors</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  4
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Generate Explanation</p>
                  <p className="text-xs text-text-muted">AI provides probable causes with confidence scores</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  5
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Recommend Actions</p>
                  <p className="text-xs text-text-muted">Suggest specific steps to address the issue</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  6
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Track Recovery</p>
                  <p className="text-xs text-text-muted">Monitor metrics after implementing fixes</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default AnomalyExplainerPage;
