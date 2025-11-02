/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

interface SEOMetric {
  label: string;
  value: string;
  status: 'excellent' | 'good' | 'warning' | 'error';
  icon: string;
  trend?: string;
}

interface IntegrationLog {
  id: string;
  timestamp: string;
  source: string;
  action: string;
  status: 'success' | 'warning' | 'error';
  message: string;
}

const SEOPage: React.FC = () => {
  const [showPromptModal, setShowPromptModal] = useState(false);
  const [promptInput, setPromptInput] = useState('');

  const seoMetrics: SEOMetric[] = [
    {
      label: 'Site Health',
      value: '94/100',
      status: 'excellent',
      icon: '🏥',
      trend: '+2',
    },
    {
      label: 'Index Coverage',
      value: '1,247 pages',
      status: 'good',
      icon: '📑',
      trend: '+18',
    },
    {
      label: 'CWV Pass %',
      value: '87%',
      status: 'good',
      icon: '⚡',
      trend: '+5%',
    },
    {
      label: 'Citation Score',
      value: '76/100',
      status: 'warning',
      icon: '📍',
      trend: '-3',
    },
    {
      label: 'New Backlinks',
      value: '42',
      status: 'excellent',
      icon: '🔗',
      trend: '+12',
    },
    {
      label: 'Rank Movement',
      value: '+8 positions',
      status: 'excellent',
      icon: '📈',
      trend: '+8',
    },
  ];

  const integrationLogs: IntegrationLog[] = [
    {
      id: '1',
      timestamp: '2025-11-02 15:45:23',
      source: 'Google Search Console',
      action: 'Fetch Index Data',
      status: 'success',
      message: 'Successfully retrieved 1,247 indexed pages',
    },
    {
      id: '2',
      timestamp: '2025-11-02 15:30:15',
      source: 'Google Analytics',
      action: 'Sync Traffic Data',
      status: 'success',
      message: 'Imported 30 days of organic traffic metrics',
    },
    {
      id: '3',
      timestamp: '2025-11-02 15:15:42',
      source: 'Ahrefs API',
      action: 'Backlink Crawl',
      status: 'success',
      message: 'Found 42 new backlinks, 3 lost backlinks',
    },
    {
      id: '4',
      timestamp: '2025-11-02 15:00:08',
      source: 'PageSpeed Insights',
      action: 'CWV Assessment',
      status: 'warning',
      message: 'CWV pass rate 87% - Mobile LCP needs improvement',
    },
    {
      id: '5',
      timestamp: '2025-11-02 14:45:33',
      source: 'Moz API',
      action: 'Citation Audit',
      status: 'warning',
      message: 'Citation consistency at 76% - 8 discrepancies found',
    },
    {
      id: '6',
      timestamp: '2025-11-02 14:30:19',
      source: 'SEMrush',
      action: 'Rank Tracking',
      status: 'success',
      message: 'Average position improved by 8 ranks across 156 keywords',
    },
    {
      id: '7',
      timestamp: '2025-11-02 14:15:55',
      source: 'Screaming Frog',
      action: 'Site Crawl',
      status: 'error',
      message: 'Crawl timeout - Server response time exceeded 5s on 23 pages',
    },
    {
      id: '8',
      timestamp: '2025-11-02 14:00:27',
      source: 'Google My Business',
      action: 'Review Sync',
      status: 'success',
      message: 'Synced 15 new reviews, average rating 4.8/5.0',
    },
    {
      id: '9',
      timestamp: '2025-11-02 13:45:41',
      source: 'BrightLocal',
      action: 'Local SEO Check',
      status: 'success',
      message: 'NAP consistency verified across 47 directories',
    },
    {
      id: '10',
      timestamp: '2025-11-02 13:30:12',
      source: 'WordPress Plugin',
      action: 'Content Analysis',
      status: 'success',
      message: 'Analyzed 18 new blog posts, avg SEO score 82/100',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'text-success';
      case 'good':
        return 'text-primary';
      case 'warning':
        return 'text-warning';
      case 'error':
        return 'text-error';
      default:
        return 'text-text-primary';
    }
  };

  const getLogStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-success/20 text-success';
      case 'warning':
        return 'bg-warning/20 text-warning';
      case 'error':
        return 'bg-error/20 text-error';
      default:
        return 'bg-primary/20 text-primary';
    }
  };

  const handlePromptSubmit = () => {
    alert(`Prompt submitted: ${promptInput}\n\nThis will generate an FAQ based on your service description. API integration coming soon!`);
    setPromptInput('');
    setShowPromptModal(false);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">SEO Dashboard</h1>
          <p className="text-text-secondary mt-1">Search engine optimization and visibility metrics</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="lg"
            onClick={() => setShowPromptModal(true)}
          >
            🤖 AI Prompt Runner
          </Button>
          <Button variant="primary" size="lg">Run Audit</Button>
        </div>
      </div>

      {/* SEO Metric Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {seoMetrics.map((metric, i) => (
          <Card key={i} variant="neon" padding="md" hover>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-text-muted text-sm mb-2">{metric.label}</p>
                <p className={`text-3xl font-bold ${getStatusColor(metric.status)} mb-1`}>
                  {metric.value}
                </p>
                {metric.trend && (
                  <p className={`text-sm ${metric.trend.startsWith('+') ? 'text-success' : 'text-error'}`}>
                    {metric.trend.startsWith('+') ? '↑' : '↓'} {metric.trend}
                  </p>
                )}
              </div>
              <div className="text-4xl">{metric.icon}</div>
            </div>
          </Card>
        ))}
      </div>

      {/* Integration Logs */}
      <Card variant="glass" padding="lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-text-primary">Integration Logs</h2>
          <button className="text-sm text-primary hover:text-primary-light transition-colors">
            View All →
          </button>
        </div>

        <div className="overflow-y-auto max-h-96 border border-white/10 rounded-lg">
          <table className="w-full">
            <thead className="sticky top-0 bg-bg-elevated border-b border-white/10">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Source
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Action
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Status
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Message
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {integrationLogs.map((log) => (
                <tr key={log.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm text-text-secondary font-mono whitespace-nowrap">
                    {log.timestamp}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-primary whitespace-nowrap">
                    {log.source}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary whitespace-nowrap">
                    {log.action}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${getLogStatusColor(log.status)}`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    {log.message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Prompt Runner Modal */}
      {showPromptModal && (
        <>
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={() => setShowPromptModal(false)}
          />
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <Card variant="neon" className="w-full max-w-2xl">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-display font-bold text-gradient">
                    🤖 AI Prompt Runner
                  </h2>
                  <button
                    onClick={() => setShowPromptModal(false)}
                    className="text-text-muted hover:text-text-primary transition-colors"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Service Description
                    </label>
                    <textarea
                      value={promptInput}
                      onChange={(e) => setPromptInput(e.target.value)}
                      placeholder="Describe your service... e.g., 'Residential window cleaning for homes in Portland, OR'"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all min-h-32 resize-y"
                    />
                  </div>

                  <div className="bg-primary/10 border border-primary/30 rounded-lg p-4">
                    <p className="text-sm text-text-secondary">
                      <strong className="text-primary">Prompt:</strong> Generate FAQ for this service
                    </p>
                    <p className="text-xs text-text-muted mt-2">
                      This will use AI to create frequently asked questions based on your service description.
                    </p>
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-4">
                    <Button
                      variant="secondary"
                      size="md"
                      onClick={() => setShowPromptModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      size="md"
                      onClick={handlePromptSubmit}
                      disabled={!promptInput.trim()}
                    >
                      Generate FAQ
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};

export default SEOPage;
