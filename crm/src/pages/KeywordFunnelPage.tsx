/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Keyword Funnel & Prioritize
 * Organize keywords by funnel stage and prioritize for content creation
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Filter, Target, TrendingUp, Award } from 'lucide-react';

const KeywordFunnelPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Keyword Funnel & Prioritize</h1>
        <p className="text-sm text-text-muted mt-1">
          Organize keywords by funnel stage and prioritize for maximum impact
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Filter className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Total Keywords</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">Tracked keywords</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Priority Targets</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">High-value keywords</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Avg Search Volume</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">Monthly searches</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Award className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Quick Wins</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Low difficulty, high volume</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Funnel Stages</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">TOFU - Awareness</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">0 keywords</span>
                </div>
                <p className="text-xs text-text-muted mb-2">Informational searches: "what is", "how to", "guide", "tips"</p>
                <p className="text-xs text-text-muted italic">Example: "what is content marketing"</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">MOFU - Consideration</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">0 keywords</span>
                </div>
                <p className="text-xs text-text-muted mb-2">Comparison searches: "best", "vs", "alternatives", "reviews"</p>
                <p className="text-xs text-text-muted italic">Example: "best email marketing tools"</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">BOFU - Decision</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">0 keywords</span>
                </div>
                <p className="text-xs text-text-muted mb-2">Transactional searches: "buy", "pricing", "demo", brand names</p>
                <p className="text-xs text-text-muted italic">Example: "mailchimp pricing plans"</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Prioritization Framework</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-success/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-success">Priority Score</span>
                  <span className="text-xs bg-success/10 text-success px-2 py-1 rounded">Formula</span>
                </div>
                <p className="text-xs text-text-muted">
                  (Search Volume × CTR × Conversion Rate) ÷ Difficulty
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary">Search Volume</span>
                  <span className="text-text-muted">Monthly searches (0-100 scale)</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary">Keyword Difficulty</span>
                  <span className="text-text-muted">Competition level (0-100 scale)</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary">Business Value</span>
                  <span className="text-text-muted">Relevance to your product (1-10)</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary">Current Ranking</span>
                  <span className="text-text-muted">Your position or "Not ranking"</span>
                </div>
              </div>
              <div className="pt-3 border-t border-white/10">
                <p className="text-xs font-medium text-text-secondary mb-2">Quick Win Criteria:</p>
                <ul className="text-xs text-text-muted space-y-1">
                  <li>• Keyword difficulty &lt; 30</li>
                  <li>• Search volume &gt; 500/month</li>
                  <li>• High business value (7+)</li>
                  <li>• Currently not ranking or position 11-30</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default KeywordFunnelPage;
