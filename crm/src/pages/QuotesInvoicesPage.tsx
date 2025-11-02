/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const QuotesInvoicesPage: React.FC = () => {
  const [isLoading] = useState(false);
  const [hasError] = useState(false);

  // Sample data - would come from API
  const kpis = [
    { label: 'Total Revenue', value: '$45,230', change: '+12.5%', trend: 'up' },
    { label: 'Pending Quotes', value: '8', change: '-2', trend: 'down' },
    { label: 'Avg Quote Value', value: '$2,850', change: '+5.2%', trend: 'up' },
    { label: 'Conversion Rate', value: '68%', change: '+3%', trend: 'up' },
  ];

  const recentQuotes = [
    { id: 'Q-1234', client: 'Acme Corp', amount: '$3,500', status: 'pending', date: '2025-11-01' },
    { id: 'Q-1235', client: 'Tech Solutions', amount: '$2,800', status: 'approved', date: '2025-11-01' },
    { id: 'Q-1236', client: 'Green Industries', amount: '$4,200', status: 'pending', date: '2025-10-31' },
  ];

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-text-secondary">Loading quotes and invoices...</p>
          </div>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="p-6">
        <Card variant="glass" padding="lg">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-text-primary mb-2">Failed to Load Data</h2>
            <p className="text-text-secondary mb-6">There was an error loading quotes and invoices.</p>
            <Button variant="primary" onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">Quotes & Invoices</h1>
          <p className="text-text-secondary mt-1">Manage financial documents and track revenue</p>
        </div>
        <Button variant="primary" size="lg">
          + New Quote
        </Button>
      </div>

      {/* KPIs - Above the Fold */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <Card key={index} variant="glass" padding="md" hover>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-text-muted text-sm">{kpi.label}</p>
                <p className="text-2xl font-bold text-text-primary mt-1">{kpi.value}</p>
                <p className={`text-sm mt-1 ${kpi.trend === 'up' ? 'text-success' : 'text-warning'}`}>
                  {kpi.change} from last month
                </p>
              </div>
              <div className={`text-2xl ${kpi.trend === 'up' ? 'text-success' : 'text-warning'}`}>
                {kpi.trend === 'up' ? '📈' : '📉'}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Filters and Tabs */}
      <div className="flex items-center gap-4">
        <Button variant="secondary" size="sm">All</Button>
        <Button variant="ghost" size="sm">Quotes</Button>
        <Button variant="ghost" size="sm">Invoices</Button>
        <Button variant="ghost" size="sm">Paid</Button>
        <Button variant="ghost" size="sm">Pending</Button>
      </div>

      {/* Recent Quotes Table */}
      <Card variant="glass" padding="none">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-semibold text-text-primary">Recent Quotes</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Quote ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {recentQuotes.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="text-6xl mb-4">📄</div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">No Quotes Yet</h3>
                    <p className="text-text-secondary mb-4">Create your first quote to get started</p>
                    <Button variant="primary">+ Create Quote</Button>
                  </td>
                </tr>
              ) : (
                recentQuotes.map((quote) => (
                  <tr key={quote.id} className="hover:bg-white/5 transition-colors cursor-pointer">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary">
                      {quote.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-primary">
                      {quote.client}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-text-primary">
                      {quote.amount}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          quote.status === 'approved'
                            ? 'bg-success/10 text-success'
                            : quote.status === 'pending'
                            ? 'bg-warning/10 text-warning'
                            : 'bg-error/10 text-error'
                        }`}
                      >
                        {quote.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">
                      {quote.date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Button variant="ghost" size="sm">View</Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default QuotesInvoicesPage;
