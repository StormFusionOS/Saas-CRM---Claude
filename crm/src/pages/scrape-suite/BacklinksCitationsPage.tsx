/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Backlinks & Citations Page - Analyze backlink profiles and citation patterns
 */

import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Tabs from '@/components/ui/Tabs';
import {
  Link,
  ExternalLink,
  TrendingUp,
  Download,
  Filter,
  CheckCircle,
  XCircle,
  Globe,
  MapPin
} from 'lucide-react';
import scrapeApi from '@/lib/scrape-api';
import type {
  Backlink,
  ReferringDomain,
  Citation
} from '@/lib/scrape-api';

const BacklinksCitationsPage: React.FC = () => {
  // State
  const [activeTab, setActiveTab] = useState('backlinks');
  const [backlinks, setBacklinks] = useState<Backlink[]>([]);
  const [referringDomains, setReferringDomains] = useState<ReferringDomain[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);
  const [backlinkFilter, setBacklinkFilter] = useState({
    domain: '',
    dofollow: undefined as boolean | undefined,
    alive: undefined as boolean | undefined
  });
  const [citationFilter, setCitationFilter] = useState({
    listed: undefined as boolean | undefined,
    napMatch: undefined as boolean | undefined
  });

  // Stats
  const [stats, setStats] = useState({
    totalBacklinks: 0,
    activeBacklinks: 0,
    lostBacklinks: 0,
    dofollowBacklinks: 0,
    referringDomains: 0,
    totalCitations: 0,
    activeCitations: 0,
    napMatches: 0
  });

  useEffect(() => {
    if (activeTab === 'backlinks') {
      loadBacklinks();
      loadReferringDomains();
    } else {
      loadCitations();
    }
  }, [activeTab]);

  const loadBacklinks = async () => {
    try {
      setLoading(true);
      const response = await scrapeApi.getBacklinks({
        page: 1,
        page_size: 100
      });
      setBacklinks(response.backlinks);

      // Calculate stats
      setStats(prev => ({
        ...prev,
        totalBacklinks: response.total,
        activeBacklinks: response.backlinks.filter(b => !b.is_lost).length,
        lostBacklinks: response.backlinks.filter(b => b.is_lost).length,
        dofollowBacklinks: response.backlinks.filter(b => b.is_dofollow).length
      }));
    } catch (error) {
      console.error('Failed to load backlinks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadReferringDomains = async () => {
    try {
      const response = await scrapeApi.getReferringDomains();
      setReferringDomains(response.domains);
      setStats(prev => ({
        ...prev,
        referringDomains: response.total
      }));
    } catch (error) {
      console.error('Failed to load referring domains:', error);
    }
  };

  const loadCitations = async () => {
    try {
      setLoading(true);
      const response = await scrapeApi.getCitations();
      setCitations(response.citations);

      // Calculate stats
      setStats(prev => ({
        ...prev,
        totalCitations: response.total,
        activeCitations: response.citations.filter(c => c.is_listed).length,
        napMatches: response.citations.filter(c => c.nap_match).length
      }));
    } catch (error) {
      console.error('Failed to load citations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportBacklinks = () => {
    if (filteredBacklinks.length === 0) return;

    const csv = [
      ['Source Domain', 'Source URL', 'Target URL', 'Anchor Text', 'DoFollow', 'In Body', 'Status', 'First Seen', 'Last Seen'].join(','),
      ...filteredBacklinks.map(b => [
        b.source_domain,
        b.source_url,
        b.target_url,
        b.anchor_text ? `"${b.anchor_text.replace(/"/g, '""')}"` : '',
        b.is_dofollow ? 'Yes' : 'No',
        b.is_inbody ? 'Yes' : 'No',
        b.is_lost ? 'Lost' : 'Active',
        b.first_seen || '',
        b.last_seen || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backlinks-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCitations = () => {
    if (filteredCitations.length === 0) return;

    const csv = [
      ['Platform', 'Listing URL', 'Listed', 'Name', 'Address', 'Phone', 'NAP Match', 'Last Checked'].join(','),
      ...filteredCitations.map(c => [
        c.platform,
        c.listing_url || '',
        c.is_listed ? 'Yes' : 'No',
        c.name_found || '',
        c.address_found || '',
        c.phone_found || '',
        c.nap_match ? 'Yes' : 'No',
        c.last_checked || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `citations-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredBacklinks = backlinks.filter(b => {
    if (backlinkFilter.domain && !b.source_domain.toLowerCase().includes(backlinkFilter.domain.toLowerCase())) {
      return false;
    }
    if (backlinkFilter.dofollow !== undefined && b.is_dofollow !== backlinkFilter.dofollow) {
      return false;
    }
    if (backlinkFilter.alive !== undefined) {
      const isAlive = !b.is_lost;
      if (isAlive !== backlinkFilter.alive) {
        return false;
      }
    }
    return true;
  });

  const filteredCitations = citations.filter(c => {
    if (citationFilter.listed !== undefined && c.is_listed !== citationFilter.listed) {
      return false;
    }
    if (citationFilter.napMatch !== undefined && c.nap_match !== citationFilter.napMatch) {
      return false;
    }
    return true;
  });

  const tabs = [
    { id: 'backlinks', label: 'Backlinks' },
    { id: 'domains', label: 'Referring Domains' },
    { id: 'citations', label: 'Citations' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Backlinks & Citations
          </h1>
          <p className="text-neutral-400">
            Monitor backlink profiles and business citations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            icon={<Download className="w-4 h-4" />}
            onClick={activeTab === 'citations' ? handleExportCitations : handleExportBacklinks}
            disabled={activeTab === 'backlinks' ? filteredBacklinks.length === 0 : activeTab === 'citations' ? filteredCitations.length === 0 : true}
          >
            Export
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Total Backlinks</p>
              <p className="text-2xl font-bold text-white">{stats.totalBacklinks}</p>
              <p className="text-xs text-success mt-1">{stats.dofollowBacklinks} dofollow</p>
            </div>
            <div className="p-2 rounded-lg bg-primary/20">
              <Link className="w-5 h-5 text-primary" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Referring Domains</p>
              <p className="text-2xl font-bold text-white">{stats.referringDomains}</p>
              <p className="text-xs text-neutral-500 mt-1">Unique sources</p>
            </div>
            <div className="p-2 rounded-lg bg-success/20">
              <Globe className="w-5 h-5 text-success" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Active / Lost</p>
              <p className="text-2xl font-bold text-white">
                {stats.activeBacklinks} / {stats.lostBacklinks}
              </p>
              <p className="text-xs text-neutral-500 mt-1">Link status</p>
            </div>
            <div className="p-2 rounded-lg bg-info/20">
              <TrendingUp className="w-5 h-5 text-info" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Citations</p>
              <p className="text-2xl font-bold text-white">{stats.totalCitations}</p>
              <p className="text-xs text-success mt-1">{stats.napMatches} NAP matches</p>
            </div>
            <div className="p-2 rounded-lg bg-warning/20">
              <MapPin className="w-5 h-5 text-warning" />
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <Card variant="glass" padding="none">
        <div className="px-6 pt-4">
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        <div className="p-6">
          {/* Backlinks Tab */}
          {activeTab === 'backlinks' && (
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  placeholder="Filter by domain..."
                  value={backlinkFilter.domain}
                  onChange={(e) => setBacklinkFilter(prev => ({ ...prev, domain: e.target.value }))}
                  className="flex-1 bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-neutral-500 focus:outline-none focus:border-primary"
                />
                <select
                  value={backlinkFilter.dofollow === undefined ? 'all' : backlinkFilter.dofollow ? 'dofollow' : 'nofollow'}
                  onChange={(e) => setBacklinkFilter(prev => ({
                    ...prev,
                    dofollow: e.target.value === 'all' ? undefined : e.target.value === 'dofollow'
                  }))}
                  className="bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
                >
                  <option value="all">All Links</option>
                  <option value="dofollow">DoFollow</option>
                  <option value="nofollow">NoFollow</option>
                </select>
                <select
                  value={backlinkFilter.alive === undefined ? 'all' : backlinkFilter.alive ? 'active' : 'lost'}
                  onChange={(e) => setBacklinkFilter(prev => ({
                    ...prev,
                    alive: e.target.value === 'all' ? undefined : e.target.value === 'active'
                  }))}
                  className="bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="lost">Lost</option>
                </select>
              </div>

              {/* Backlinks Table */}
              {filteredBacklinks.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Source Domain</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Anchor Text</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Target URL</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">Type</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">Status</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Last Seen</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {filteredBacklinks.map((backlink) => (
                        <tr key={backlink.id} className="hover:bg-white/5 transition-colors">
                          <td className="px-4 py-3">
                            <div className="font-medium text-white">{backlink.source_domain}</div>
                            <a
                              href={backlink.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-primary hover:underline truncate block max-w-xs"
                            >
                              {backlink.source_url}
                            </a>
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-neutral-300 max-w-xs truncate">
                              {backlink.anchor_text || 'No anchor text'}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <a
                              href={backlink.target_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-primary hover:underline truncate block max-w-xs"
                            >
                              {backlink.target_url}
                            </a>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <div className="flex flex-col gap-1">
                              {backlink.is_dofollow && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success/20 text-success">
                                  DoFollow
                                </span>
                              )}
                              {backlink.is_inbody && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-info/20 text-info">
                                  In Body
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-center">
                            {backlink.is_lost ? (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-danger/20 text-danger text-xs font-medium">
                                <XCircle className="w-3 h-3" />
                                Lost
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-success/20 text-success text-xs font-medium">
                                <CheckCircle className="w-3 h-3" />
                                Active
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-neutral-400">
                              {backlink.last_seen
                                ? new Date(backlink.last_seen).toLocaleDateString()
                                : 'Unknown'}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-neutral-400">
                  {loading ? 'Loading backlinks...' : 'No backlinks found'}
                </div>
              )}
            </div>
          )}

          {/* Referring Domains Tab */}
          {activeTab === 'domains' && (
            <div className="space-y-4">
              {referringDomains.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Domain</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">Total Links</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">In-Body Links</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">Authority Score</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Last Updated</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {referringDomains.map((domain) => (
                        <tr key={domain.id} className="hover:bg-white/5 transition-colors">
                          <td className="px-4 py-3">
                            <div className="font-medium text-white">{domain.domain}</div>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="text-white font-semibold">{domain.backlink_count}</span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="text-success font-semibold">{domain.inbody_link_count}</span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            {domain.authority_score ? (
                              <div className={`
                                inline-flex items-center justify-center px-3 py-1 rounded-full font-semibold text-sm
                                ${domain.authority_score >= 70
                                  ? 'bg-success/20 text-success'
                                  : domain.authority_score >= 40
                                    ? 'bg-warning/20 text-warning'
                                    : 'bg-neutral-700/20 text-neutral-400'
                                }
                              `}>
                                {domain.authority_score}
                              </div>
                            ) : (
                              <span className="text-neutral-500">N/A</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-neutral-400">
                              {domain.last_updated
                                ? new Date(domain.last_updated).toLocaleDateString()
                                : 'Unknown'}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-neutral-400">
                  {loading ? 'Loading referring domains...' : 'No referring domains found'}
                </div>
              )}
            </div>
          )}

          {/* Citations Tab */}
          {activeTab === 'citations' && (
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex items-center gap-3">
                <select
                  value={citationFilter.listed === undefined ? 'all' : citationFilter.listed ? 'listed' : 'unlisted'}
                  onChange={(e) => setCitationFilter(prev => ({
                    ...prev,
                    listed: e.target.value === 'all' ? undefined : e.target.value === 'listed'
                  }))}
                  className="bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
                >
                  <option value="all">All Citations</option>
                  <option value="listed">Listed</option>
                  <option value="unlisted">Not Listed</option>
                </select>
                <select
                  value={citationFilter.napMatch === undefined ? 'all' : citationFilter.napMatch ? 'match' : 'mismatch'}
                  onChange={(e) => setCitationFilter(prev => ({
                    ...prev,
                    napMatch: e.target.value === 'all' ? undefined : e.target.value === 'match'
                  }))}
                  className="bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
                >
                  <option value="all">All NAP Status</option>
                  <option value="match">NAP Match</option>
                  <option value="mismatch">NAP Mismatch</option>
                </select>
              </div>

              {/* Citations Table */}
              {filteredCitations.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Platform</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Name</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Phone</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">Listed</th>
                        <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">NAP Match</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Last Checked</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {filteredCitations.map((citation) => (
                        <tr key={citation.id} className="hover:bg-white/5 transition-colors">
                          <td className="px-4 py-3">
                            <div className="font-medium text-white">{citation.platform}</div>
                            {citation.listing_url && (
                              <a
                                href={citation.listing_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-primary hover:underline flex items-center gap-1 mt-1"
                              >
                                <ExternalLink className="w-3 h-3" />
                                View Listing
                              </a>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-neutral-300">
                              {citation.name_found || 'Not found'}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-neutral-300">
                              {citation.phone_found || 'Not found'}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-center">
                            {citation.is_listed ? (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-success/20 text-success text-xs font-medium">
                                <CheckCircle className="w-3 h-3" />
                                Listed
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-neutral-700/20 text-neutral-400 text-xs font-medium">
                                <XCircle className="w-3 h-3" />
                                Not Listed
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {citation.nap_match ? (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-success/20 text-success text-xs font-medium">
                                <CheckCircle className="w-3 h-3" />
                                Match
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-warning/20 text-warning text-xs font-medium">
                                <XCircle className="w-3 h-3" />
                                Mismatch
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-neutral-400">
                              {citation.last_checked
                                ? new Date(citation.last_checked).toLocaleDateString()
                                : 'Never'}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-neutral-400">
                  {loading ? 'Loading citations...' : 'No citations found'}
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default BacklinksCitationsPage;
