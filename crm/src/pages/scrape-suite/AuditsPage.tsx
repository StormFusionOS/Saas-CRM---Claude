/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Site Audits Page - Technical SEO and content audits
 */

import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  ClipboardCheck,
  AlertCircle,
  CheckCircle,
  Play,
  XCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronRight,
  Calendar,
  Globe
} from 'lucide-react';
import scrapeApi from '@/lib/scrape-api';
import type { PageAudit } from '@/lib/scrape-api';

const AuditsPage: React.FC = () => {
  // State
  const [audits, setAudits] = useState<PageAudit[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedAudits, setExpandedAudits] = useState<Set<number>>(new Set());
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [fixedFilter, setFixedFilter] = useState<string>('all');

  // Stats
  const [stats, setStats] = useState({
    totalAudits: 0,
    totalIssues: 0,
    criticalIssues: 0,
    fixedIssues: 0,
    pagesAudited: 0
  });

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    try {
      setLoading(true);
      const response = await scrapeApi.getPageAudits({
        page: 1,
        page_size: 50
      });
      setAudits(response.audits);

      // Calculate stats
      const totalIssues = response.audits.reduce((sum, audit) => sum + audit.issues_found, 0);
      const allIssues = response.audits.flatMap(a => a.issues);
      const criticalIssues = allIssues.filter(i => i.severity === 'critical').length;
      const fixedIssues = allIssues.filter(i => i.fixed).length;

      setStats({
        totalAudits: response.total,
        totalIssues,
        criticalIssues,
        fixedIssues,
        pagesAudited: response.audits.length
      });
    } catch (error) {
      console.error('Failed to load audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleAuditExpansion = (auditId: number) => {
    const newExpanded = new Set(expandedAudits);
    if (newExpanded.has(auditId)) {
      newExpanded.delete(auditId);
    } else {
      newExpanded.add(auditId);
    }
    setExpandedAudits(newExpanded);
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="w-4 h-4 text-danger" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-danger" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case 'info':
        return <Info className="w-4 h-4 text-info" />;
      default:
        return <Info className="w-4 h-4 text-neutral-400" />;
    }
  };

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'error':
        return 'bg-danger/20 text-danger';
      case 'warning':
        return 'bg-warning/20 text-warning';
      case 'info':
        return 'bg-info/20 text-info';
      default:
        return 'bg-neutral-700/20 text-neutral-400';
    }
  };

  const filteredAudits = audits.map(audit => {
    const filteredIssues = audit.issues.filter(issue => {
      if (severityFilter !== 'all' && issue.severity !== severityFilter) {
        return false;
      }
      if (fixedFilter === 'fixed' && !issue.fixed) {
        return false;
      }
      if (fixedFilter === 'unfixed' && issue.fixed) {
        return false;
      }
      return true;
    });

    return {
      ...audit,
      filteredIssues,
      filteredIssuesCount: filteredIssues.length
    };
  }).filter(audit => audit.filteredIssuesCount > 0 || (severityFilter === 'all' && fixedFilter === 'all'));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Site Audits
          </h1>
          <p className="text-neutral-400">
            Technical SEO and content audits for monitored sites
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Total Audits</p>
              <p className="text-2xl font-bold text-white">{stats.totalAudits}</p>
              <p className="text-xs text-neutral-500 mt-1">{stats.pagesAudited} pages</p>
            </div>
            <div className="p-2 rounded-lg bg-primary/20">
              <ClipboardCheck className="w-5 h-5 text-primary" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Total Issues</p>
              <p className="text-2xl font-bold text-white">{stats.totalIssues}</p>
              <p className="text-xs text-danger mt-1">{stats.criticalIssues} critical</p>
            </div>
            <div className="p-2 rounded-lg bg-warning/20">
              <AlertCircle className="w-5 h-5 text-warning" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Fixed Issues</p>
              <p className="text-2xl font-bold text-white">{stats.fixedIssues}</p>
              <p className="text-xs text-success mt-1">
                {stats.totalIssues > 0
                  ? Math.round((stats.fixedIssues / stats.totalIssues) * 100)
                  : 0}% resolved
              </p>
            </div>
            <div className="p-2 rounded-lg bg-success/20">
              <CheckCircle className="w-5 h-5 text-success" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Open Issues</p>
              <p className="text-2xl font-bold text-white">{stats.totalIssues - stats.fixedIssues}</p>
              <p className="text-xs text-neutral-500 mt-1">Need attention</p>
            </div>
            <div className="p-2 rounded-lg bg-info/20">
              <AlertTriangle className="w-5 h-5 text-info" />
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      {audits.length > 0 && (
        <Card variant="glass" padding="md">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-neutral-400">Severity:</span>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-neutral-400">Status:</span>
              <select
                value={fixedFilter}
                onChange={(e) => setFixedFilter(e.target.value)}
                className="bg-dark-800 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary"
              >
                <option value="all">All Issues</option>
                <option value="unfixed">Open</option>
                <option value="fixed">Fixed</option>
              </select>
            </div>

            <div className="ml-auto text-sm text-neutral-400">
              Showing {filteredAudits.length} of {audits.length} audits
            </div>
          </div>
        </Card>
      )}

      {/* Audits List */}
      {filteredAudits.length > 0 ? (
        <div className="space-y-4">
          {filteredAudits.map((audit) => {
            const isExpanded = expandedAudits.has(audit.id);
            const issuesGroupedBySeverity = {
              critical: audit.filteredIssues.filter(i => i.severity === 'critical'),
              error: audit.filteredIssues.filter(i => i.severity === 'error'),
              warning: audit.filteredIssues.filter(i => i.severity === 'warning'),
              info: audit.filteredIssues.filter(i => i.severity === 'info')
            };

            return (
              <Card key={audit.id} variant="glass" padding="none">
                <button
                  onClick={() => toggleAuditExpansion(audit.id)}
                  className="w-full p-6 text-left hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="p-2 rounded-lg bg-primary/20 flex-shrink-0">
                        <Globe className="w-5 h-5 text-primary" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-white truncate">
                            {audit.page_url}
                          </h3>
                          {audit.status_code && (
                            <span className={`
                              inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
                              ${audit.status_code >= 200 && audit.status_code < 300
                                ? 'bg-success/20 text-success'
                                : audit.status_code >= 400
                                  ? 'bg-danger/20 text-danger'
                                  : 'bg-warning/20 text-warning'
                              }
                            `}>
                              {audit.status_code}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-neutral-400">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>
                              {new Date(audit.audit_date).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric'
                              })}
                            </span>
                          </div>

                          <div className="flex items-center gap-3">
                            {issuesGroupedBySeverity.critical.length > 0 && (
                              <span className="text-danger">
                                {issuesGroupedBySeverity.critical.length} critical
                              </span>
                            )}
                            {issuesGroupedBySeverity.error.length > 0 && (
                              <span className="text-danger">
                                {issuesGroupedBySeverity.error.length} errors
                              </span>
                            )}
                            {issuesGroupedBySeverity.warning.length > 0 && (
                              <span className="text-warning">
                                {issuesGroupedBySeverity.warning.length} warnings
                              </span>
                            )}
                            {audit.filteredIssuesCount === 0 && (
                              <span className="text-success flex items-center gap-1">
                                <CheckCircle className="w-4 h-4" />
                                No issues
                              </span>
                            )}
                          </div>
                        </div>

                        {audit.notes && (
                          <p className="text-sm text-neutral-500 mt-2">
                            {audit.notes}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 ml-4">
                      <div className="text-right">
                        <div className="text-2xl font-bold text-white">
                          {audit.filteredIssuesCount}
                        </div>
                        <div className="text-xs text-neutral-400">
                          {audit.filteredIssuesCount === 1 ? 'issue' : 'issues'}
                        </div>
                      </div>

                      {isExpanded ? (
                        <ChevronDown className="w-5 h-5 text-neutral-400 flex-shrink-0" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-neutral-400 flex-shrink-0" />
                      )}
                    </div>
                  </div>
                </button>

                {/* Expanded Issues */}
                {isExpanded && audit.filteredIssues.length > 0 && (
                  <div className="border-t border-white/10 p-6 pt-4">
                    <h4 className="text-sm font-semibold text-white mb-4">Issues Found</h4>
                    <div className="space-y-3">
                      {audit.filteredIssues.map((issue) => (
                        <div
                          key={issue.id}
                          className="flex items-start gap-3 p-4 rounded-lg bg-dark-800/50 border border-white/5"
                        >
                          <div className="flex-shrink-0 mt-0.5">
                            {getSeverityIcon(issue.severity)}
                          </div>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-3 mb-2">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <span className={`
                                    inline-flex items-center px-2 py-0.5 rounded text-xs font-medium uppercase
                                    ${getSeverityBadgeClass(issue.severity)}
                                  `}>
                                    {issue.severity}
                                  </span>
                                  <span className="text-sm font-medium text-white">
                                    {issue.type}
                                  </span>
                                </div>
                                {issue.description && (
                                  <p className="text-sm text-neutral-300">
                                    {issue.description}
                                  </p>
                                )}
                              </div>

                              {issue.fixed && (
                                <div className="flex items-center gap-2 text-xs text-success flex-shrink-0">
                                  <CheckCircle className="w-4 h-4" />
                                  <div>
                                    <div>Fixed</div>
                                    {issue.fixed_date && (
                                      <div className="text-neutral-500">
                                        {new Date(issue.fixed_date).toLocaleDateString()}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      ) : loading ? (
        <Card variant="glass" padding="lg">
          <div className="text-center py-12 text-neutral-400">
            Loading audits...
          </div>
        </Card>
      ) : audits.length === 0 ? (
        /* Empty State - No audits */
        <Card variant="glass" padding="lg">
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4">
              <ClipboardCheck className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              No Audits Run Yet
            </h3>
            <p className="text-neutral-400 mb-6 max-w-md mx-auto">
              Run comprehensive technical SEO audits on competitor sites to identify opportunities and analyze their strategies.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button
                variant="secondary"
                onClick={() => window.location.href = '/scrape/competitors'}
              >
                View Competitors
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        /* No results with current filters */
        <Card variant="glass" padding="lg">
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-neutral-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">
              No Issues Match Filters
            </h3>
            <p className="text-neutral-400 mb-4">
              Try adjusting your filters to see more results
            </p>
            <Button
              variant="secondary"
              onClick={() => {
                setSeverityFilter('all');
                setFixedFilter('all');
              }}
            >
              Clear Filters
            </Button>
          </div>
        </Card>
      )}

      {/* Info Cards */}
      {audits.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card variant="glass" padding="md">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-info/20 flex-shrink-0">
                <ClipboardCheck className="w-5 h-5 text-info" />
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1">Audit Features</h4>
                <ul className="text-sm text-neutral-400 space-y-1">
                  <li>• Technical SEO analysis</li>
                  <li>• Page speed metrics</li>
                  <li>• Mobile responsiveness</li>
                  <li>• Schema markup validation</li>
                </ul>
              </div>
            </div>
          </Card>

          <Card variant="glass" padding="md">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-warning/20 flex-shrink-0">
                <AlertCircle className="w-5 h-5 text-warning" />
              </div>
              <div>
                <h4 className="font-semibold text-white mb-1">Issue Detection</h4>
                <ul className="text-sm text-neutral-400 space-y-1">
                  <li>• Broken links and redirects</li>
                  <li>• Missing meta tags</li>
                  <li>• Duplicate content</li>
                  <li>• Accessibility issues</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AuditsPage;
