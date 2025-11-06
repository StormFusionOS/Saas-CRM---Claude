/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Content Cluster Planner
 * Plan topic clusters and pillar content strategy
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Network, FileText, Link2, Target } from 'lucide-react';

const ContentClusterPlannerPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Content Cluster Planner</h1>
        <p className="text-sm text-text-muted mt-1">
          Plan topic clusters and pillar content strategy for better SEO
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Network className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Active Clusters</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">0</p>
              <div className="mt-2 text-xs text-text-muted">Topic clusters</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Pillar Pages</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Published</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Link2 className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Supporting Content</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">Cluster articles</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Content Gaps</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Opportunities</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Cluster Architecture</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">Pillar Page</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">Core</span>
                </div>
                <p className="text-xs text-text-muted">Comprehensive guide covering the main topic broadly (3,000-5,000 words)</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Cluster Content</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Supporting</span>
                </div>
                <p className="text-xs text-text-muted">8-12 in-depth articles on specific subtopics (1,500-2,500 words each)</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Internal Links</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Connections</span>
                </div>
                <p className="text-xs text-text-muted">Bidirectional links between pillar and cluster content using relevant anchor text</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">URL Structure</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Hierarchy</span>
                </div>
                <p className="text-xs text-text-muted">Organize URLs: /topic/ (pillar) → /topic/subtopic/ (cluster)</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Cluster Planning Steps</h2>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Choose Core Topic</p>
                  <p className="text-xs text-text-muted">Select a broad topic central to your business</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Research Subtopics</p>
                  <p className="text-xs text-text-muted">Identify 8-12 related subtopics with search volume</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Create Pillar Content</p>
                  <p className="text-xs text-text-muted">Write comprehensive pillar page first</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  4
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Build Cluster Content</p>
                  <p className="text-xs text-text-muted">Create detailed articles for each subtopic</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  5
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Interlink Everything</p>
                  <p className="text-xs text-text-muted">Add contextual links between all cluster content</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  6
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Monitor & Expand</p>
                  <p className="text-xs text-text-muted">Track performance and fill content gaps</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default ContentClusterPlannerPage;
