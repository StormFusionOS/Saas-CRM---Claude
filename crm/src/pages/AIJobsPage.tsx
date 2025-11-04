/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Jobs Page
 * Manual triggers and monitoring for AI automation jobs
 */

import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const AIJobsPage: React.FC = () => {
  const [triggering, setTriggering] = useState(false);
  const [lastJobResult, setLastJobResult] = useState<any>(null);

  const handleTriggerSEOJob = async () => {
    setTriggering(true);
    try {
      // TODO: Implement API call to trigger SEO Meta Optimizer
      // const response = await fetch('http://localhost:8000/api/v1/ai-jobs/seo-meta-optimizer', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ limit: 10 })
      // });
      // const result = await response.json();
      // setLastJobResult(result);

      alert('SEO Meta Optimizer job would be triggered here');
    } catch (error) {
      console.error('Failed to trigger job:', error);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">AI Jobs</h1>
        <p className="text-sm text-text-muted mt-1">
          Manual triggers and monitoring for AI automation jobs
        </p>
      </div>

      {/* Main Content */}
      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* SEO Meta Optimizer Job */}
          <Card padding="lg" className="glow-hover">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-display font-semibold mb-2">SEO Meta Optimizer</h2>
                <p className="text-sm text-text-muted">
                  Analyzes WordPress pages and generates optimized meta titles and descriptions
                </p>
              </div>
              <span className="px-3 py-1 bg-success/20 text-success text-xs rounded-full">Active</span>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary">Operating Mode</span>
                <span className="text-primary font-mono">Review</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary">Confidence Threshold</span>
                <span className="text-text-primary font-mono">0.70</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary">Last Run</span>
                <span className="text-text-muted">Never</span>
              </div>
            </div>

            <Button
              variant="primary"
              onClick={handleTriggerSEOJob}
              disabled={triggering}
              className="w-full"
            >
              {triggering ? 'Triggering...' : 'Trigger Job'}
            </Button>
          </Card>

          {/* Placeholder for Future Jobs */}
          <Card padding="lg" className="border-dashed border-white/10">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-lg font-display font-semibold mb-2">More Jobs Coming Soon</h3>
              <p className="text-sm text-text-muted">
                Additional AI automation jobs will be added here
              </p>
            </div>
          </Card>
        </div>

        {/* Recent Jobs Table */}
        <Card padding="lg" className="mt-6">
          <h2 className="text-xl font-display font-semibold mb-4">Recent Job Runs</h2>
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-text-secondary font-medium mb-2">No recent jobs</p>
            <p className="text-sm text-text-muted">
              Job history will appear here once you trigger a job
            </p>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default AIJobsPage;
