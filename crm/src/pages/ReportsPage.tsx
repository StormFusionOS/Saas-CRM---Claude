/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { leadsAPI } from '../lib/api';

interface Lead {
  id: number;
  status: string;
  source?: string;
  contact?: {
    first_name?: string;
    last_name?: string;
    email?: string;
    company?: string;
  };
  created_at: string;
  updated_at: string;
}

interface SourceData {
  source: string;
  count: number;
  percentage: number;
  color: string;
}

interface FunnelStage {
  stage: string;
  count: number;
  percentage: number;
  color: string;
}

const ReportsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [sourceData, setSourceData] = useState<SourceData[]>([]);
  const [funnelData, setFunnelData] = useState<FunnelStage[]>([]);

  useEffect(() => {
    fetchLeadsData();
  }, []);

  const fetchLeadsData = async () => {
    try {
      setIsLoading(true);
      const response = await leadsAPI.getLeadsBoard();
      const leadsData = response.leads || [];
      setLeads(leadsData);

      // Process Leads by Source
      const sourceMap: { [key: string]: number } = {};
      leadsData.forEach((lead: Lead) => {
        const source = lead.source || 'Unknown';
        sourceMap[source] = (sourceMap[source] || 0) + 1;
      });

      const totalLeads = leadsData.length || 1;
      const sources: SourceData[] = Object.entries(sourceMap).map(([source, count], index) => ({
        source,
        count,
        percentage: Math.round((count / totalLeads) * 100),
        color: ['#00D9FF', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#6366F1'][index % 6],
      }));
      setSourceData(sources);

      // Process Conversion Funnel
      const statusMap: { [key: string]: number } = {};
      leadsData.forEach((lead: Lead) => {
        statusMap[lead.status] = (statusMap[lead.status] || 0) + 1;
      });

      const funnelStages: FunnelStage[] = [
        {
          stage: 'New',
          count: statusMap['NEW'] || 0,
          percentage: 100,
          color: '#00D9FF',
        },
        {
          stage: 'Contacted',
          count: statusMap['CONTACTED'] || 0,
          percentage: Math.round(((statusMap['CONTACTED'] || 0) / totalLeads) * 100),
          color: '#8B5CF6',
        },
        {
          stage: 'Qualified',
          count: statusMap['QUALIFIED'] || 0,
          percentage: Math.round(((statusMap['QUALIFIED'] || 0) / totalLeads) * 100),
          color: '#10B981',
        },
        {
          stage: 'Proposal',
          count: statusMap['PROPOSAL_SENT'] || 0,
          percentage: Math.round(((statusMap['PROPOSAL_SENT'] || 0) / totalLeads) * 100),
          color: '#F59E0B',
        },
        {
          stage: 'Won',
          count: statusMap['WON'] || 0,
          percentage: Math.round(((statusMap['WON'] || 0) / totalLeads) * 100),
          color: '#10B981',
        },
      ];
      setFunnelData(funnelStages);
    } catch (error) {
      console.error('Error fetching leads data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = () => {
    const headers = ['ID', 'Name', 'Email', 'Company', 'Status', 'Source', 'Created At', 'Updated At'];

    const csvRows = [
      headers.join(','),
      ...leads.map((lead) => {
        const name = `${lead.contact?.first_name || ''} ${lead.contact?.last_name || ''}`.trim() || 'N/A';
        const email = lead.contact?.email || 'N/A';
        const company = lead.contact?.company || 'N/A';
        const source = lead.source || 'Unknown';
        const createdAt = new Date(lead.created_at).toLocaleDateString();
        const updatedAt = new Date(lead.updated_at).toLocaleDateString();

        return [
          lead.id,
          `"${name}"`,
          `"${email}"`,
          `"${company}"`,
          lead.status,
          source,
          createdAt,
          updatedAt,
        ].join(',');
      }),
    ];

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `leads-report-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">Reports & Analytics</h1>
          <p className="text-text-secondary mt-1">CRM and SEO performance insights</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="lg" onClick={exportToCSV}>
            📥 Export CSV
          </Button>
          <Button variant="primary" size="lg" onClick={fetchLeadsData}>
            🔄 Refresh
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Leads', value: leads.length.toString(), change: `${sourceData.length} sources`, trend: 'neutral' },
          { label: 'Conversion Rate', value: `${Math.round((funnelData.find(f => f.stage === 'Won')?.count || 0) / (leads.length || 1) * 100)}%`, change: 'Leads to Won', trend: 'up' },
          { label: 'Top Source', value: sourceData[0]?.source || 'N/A', change: `${sourceData[0]?.count || 0} leads`, trend: 'neutral' },
          { label: 'Active Leads', value: (leads.length - (funnelData.find(f => f.stage === 'Won')?.count || 0)).toString(), change: 'In pipeline', trend: 'neutral' },
        ].map((kpi, i) => (
          <Card key={i} variant="glass" padding="md" hover>
            <p className="text-text-muted text-sm">{kpi.label}</p>
            <p className="text-2xl font-bold text-text-primary mt-1">{kpi.value}</p>
            <p className={`text-sm mt-1 ${kpi.trend === 'up' ? 'text-success' : 'text-text-secondary'}`}>
              {kpi.change}
            </p>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leads by Source */}
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-6">Leads by Source</h2>

          <div className="space-y-4">
            {sourceData.map((source, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-text-primary font-medium">{source.source}</span>
                  <span className="text-sm text-text-secondary">
                    {source.count} ({source.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-3 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${source.percentage}%`,
                      backgroundColor: source.color,
                      boxShadow: `0 0 10px ${source.color}50`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {sourceData.length === 0 && (
            <div className="text-center py-8 text-text-muted">
              No source data available
            </div>
          )}
        </Card>

        {/* Conversion Funnel */}
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-6">Conversion Funnel</h2>

          <div className="space-y-2">
            {funnelData.map((stage, index) => (
              <div key={index} className="relative">
                <div
                  className="rounded-lg p-4 transition-all duration-500"
                  style={{
                    width: `${Math.max(stage.percentage, 15)}%`,
                    backgroundColor: `${stage.color}20`,
                    borderLeft: `4px solid ${stage.color}`,
                    marginLeft: `${index * 3}%`,
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-text-primary">{stage.stage}</span>
                    <span className="text-sm text-text-secondary">
                      {stage.count} ({stage.percentage}%)
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {funnelData.length === 0 && (
            <div className="text-center py-8 text-text-muted">
              No funnel data available
            </div>
          )}
        </Card>
      </div>

      {/* Leads Table */}
      <Card variant="glass" padding="lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-text-primary">Leads Report</h2>
          <span className="text-sm text-text-muted">{leads.length} total leads</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-white/10">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  ID
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Name
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Email
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Company
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Status
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Source
                </th>
                <th className="text-left px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {leads.slice(0, 10).map((lead) => (
                <tr key={lead.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    #{lead.id}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-primary">
                    {`${lead.contact?.first_name || ''} ${lead.contact?.last_name || ''}`.trim() || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    {lead.contact?.email || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    {lead.contact?.company || 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 text-xs rounded-full bg-primary/20 text-primary">
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    {lead.source || 'Unknown'}
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {leads.length > 10 && (
            <div className="mt-4 text-center text-sm text-text-muted">
              Showing 10 of {leads.length} leads. Export CSV to see all data.
            </div>
          )}

          {leads.length === 0 && (
            <div className="text-center py-8 text-text-muted">
              No leads data available
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default ReportsPage;
