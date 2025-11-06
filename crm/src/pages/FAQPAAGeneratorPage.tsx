/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * FAQ & PAA Generator
 * Generate FAQ sections and optimize for People Also Ask
 */

import React from 'react';
import Card from '../components/ui/Card';
import { HelpCircle, MessageSquare, TrendingUp, CheckCircle2 } from 'lucide-react';

const FAQPAAGeneratorPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">FAQ & PAA Generator</h1>
        <p className="text-sm text-text-muted mt-1">
          Generate FAQ sections and optimize for People Also Ask features
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <HelpCircle className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Questions Generated</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">This month</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">PAA Keywords</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Tracked keywords</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">PAA Appearances</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">In search results</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">FAQ Sections</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Published</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Question Types</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">What Questions</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">Definition</span>
                </div>
                <p className="text-xs text-text-muted">Answer what something is, how it works, or why it matters</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">How Questions</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Process</span>
                </div>
                <p className="text-xs text-text-muted">Step-by-step instructions and process explanations</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">When Questions</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Timing</span>
                </div>
                <p className="text-xs text-text-muted">Best times, schedules, and timing recommendations</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Why Questions</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Reasoning</span>
                </div>
                <p className="text-xs text-text-muted">Explain benefits, reasons, and rationale</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">PAA Optimization</h2>
            <div className="space-y-4 text-sm text-text-secondary">
              <div className="flex gap-3">
                <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Track PAA Questions</p>
                  <p className="text-xs text-text-muted">Monitor People Also Ask boxes for target keywords</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Answer Directly</p>
                  <p className="text-xs text-text-muted">Provide clear, concise answers in 40-60 words</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Use FAQ Schema</p>
                  <p className="text-xs text-text-muted">Implement FAQPage schema markup for better visibility</p>
                </div>
              </div>
              <div className="flex gap-3">
                <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-text-primary mb-1">Group Related Questions</p>
                  <p className="text-xs text-text-muted">Create comprehensive FAQ sections by topic</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default FAQPAAGeneratorPage;
