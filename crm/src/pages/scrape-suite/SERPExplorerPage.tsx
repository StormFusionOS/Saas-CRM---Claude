/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * SERP Explorer Page - Analyze search engine result pages and ranking patterns
 */

import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  Search,
  Filter,
  Download,
  TrendingUp,
  TrendingDown,
  Minus,
  Star,
  MessageSquare,
  MapPin,
  BookOpen
} from 'lucide-react';
import scrapeApi from '@/lib/scrape-api';
import type {
  Keyword,
  SerpSnapshot,
  SerpResult
} from '@/lib/scrape-api';

const SERPExplorerPage: React.FC = () => {
  // State
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [selectedKeywordId, setSelectedKeywordId] = useState<number | null>(null);
  const [snapshots, setSnapshots] = useState<SerpSnapshot[]>([]);
  const [selectedSnapshotId, setSelectedSnapshotId] = useState<number | null>(null);
  const [results, setResults] = useState<SerpResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Load keywords on mount
  useEffect(() => {
    loadKeywords();
  }, []);

  // Load snapshots when keyword selected
  useEffect(() => {
    if (selectedKeywordId) {
      loadSnapshots(selectedKeywordId);
    } else {
      setSnapshots([]);
      setResults([]);
    }
  }, [selectedKeywordId]);

  // Load results when snapshot selected
  useEffect(() => {
    if (selectedSnapshotId) {
      loadResults(selectedSnapshotId);
    } else {
      setResults([]);
    }
  }, [selectedSnapshotId]);

  const loadKeywords = async () => {
    try {
      const response = await scrapeApi.getKeywords({ is_active: true });
      setKeywords(response.keywords);
      if (response.keywords.length > 0) {
        setSelectedKeywordId(response.keywords[0].id);
      }
    } catch (error) {
      console.error('Failed to load keywords:', error);
    }
  };

  const loadSnapshots = async (keywordId: number) => {
    try {
      setLoading(true);
      const response = await scrapeApi.getSerpSnapshots({
        keyword_id: keywordId,
        page: 1,
        page_size: 50
      });
      setSnapshots(response.snapshots);
      if (response.snapshots.length > 0) {
        setSelectedSnapshotId(response.snapshots[0].id);
      }
    } catch (error) {
      console.error('Failed to load snapshots:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadResults = async (snapshotId: number) => {
    try {
      setLoading(true);
      const response = await scrapeApi.getSerpResults(snapshotId);
      setResults(response.results);
    } catch (error) {
      console.error('Failed to load results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (results.length === 0) return;

    const csv = [
      ['Rank', 'Domain', 'URL', 'Title', 'Is Ours'].join(','),
      ...results.map(r => [
        r.rank,
        r.domain,
        r.url,
        r.title ? `"${r.title.replace(/"/g, '""')}"` : '',
        r.is_ours ? 'Yes' : 'No'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `serp-results-${selectedSnapshotId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const selectedKeyword = keywords.find(k => k.id === selectedKeywordId);
  const selectedSnapshot = snapshots.find(s => s.id === selectedSnapshotId);

  const getRankChangeIcon = (current: number | null, previous: number | null) => {
    if (!current || !previous) return <Minus className="w-4 h-4 text-neutral-500" />;
    if (current < previous) return <TrendingUp className="w-4 h-4 text-success" />;
    if (current > previous) return <TrendingDown className="w-4 h-4 text-danger" />;
    return <Minus className="w-4 h-4 text-neutral-500" />;
  };

  const getRankChangeText = (current: number | null, previous: number | null) => {
    if (!current || !previous) return 'No change';
    const diff = previous - current; // Lower rank is better
    if (diff > 0) return `+${diff} positions`;
    if (diff < 0) return `${diff} positions`;
    return 'No change';
  };

  const filteredResults = results.filter(r => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      r.domain.toLowerCase().includes(query) ||
      r.url.toLowerCase().includes(query) ||
      (r.title && r.title.toLowerCase().includes(query))
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            SERP Explorer
          </h1>
          <p className="text-neutral-400">
            Analyze search engine result pages and ranking patterns
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            icon={<Download className="w-4 h-4" />}
            onClick={handleExport}
            disabled={results.length === 0}
          >
            Export
          </Button>
        </div>
      </div>

      {/* Keyword Selector & Stats */}
      {keywords.length > 0 ? (
        <>
          <Card variant="glass" padding="md">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-neutral-400 mb-2">
                  Select Keyword
                </label>
                <select
                  value={selectedKeywordId || ''}
                  onChange={(e) => setSelectedKeywordId(Number(e.target.value))}
                  className="w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary"
                >
                  {keywords.map(keyword => (
                    <option key={keyword.id} value={keyword.id}>
                      {keyword.keyword_text} - {keyword.target_domain}
                    </option>
                  ))}
                </select>
              </div>

              {selectedKeyword && (
                <div className="flex items-center gap-6 px-6 border-l border-white/10">
                  <div>
                    <div className="text-sm text-neutral-400">Current Rank</div>
                    <div className="text-2xl font-bold text-white">
                      {selectedKeyword.current_rank || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-neutral-400">Change</div>
                    <div className="flex items-center gap-1">
                      {getRankChangeIcon(selectedKeyword.current_rank, selectedKeyword.previous_rank)}
                      <span className="text-sm font-medium text-white">
                        {getRankChangeText(selectedKeyword.current_rank, selectedKeyword.previous_rank)}
                      </span>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-neutral-400">Best Rank</div>
                    <div className="text-lg font-bold text-success">
                      {selectedKeyword.best_rank || 'N/A'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Snapshots Timeline */}
          {snapshots.length > 0 && (
            <Card variant="glass" padding="md">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-white">SERP Snapshots</h3>
                <p className="text-sm text-neutral-400">
                  {snapshots.length} snapshot{snapshots.length !== 1 ? 's' : ''} recorded
                </p>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {snapshots.map((snapshot) => {
                  const isSelected = snapshot.id === selectedSnapshotId;
                  const hasFeatures = snapshot.featured_snippet || snapshot.people_also_ask ||
                                     snapshot.local_pack || snapshot.knowledge_panel;

                  return (
                    <button
                      key={snapshot.id}
                      onClick={() => setSelectedSnapshotId(snapshot.id)}
                      className={`
                        w-full p-4 rounded-lg border transition-all text-left
                        ${isSelected
                          ? 'bg-primary/10 border-primary'
                          : 'bg-dark-800 border-white/10 hover:border-white/20'
                        }
                      `}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <div className="text-white font-medium">
                            {new Date(snapshot.search_date).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                          {snapshot.rank && (
                            <div className="text-sm text-neutral-400">
                              Rank: <span className="text-white font-semibold">#{snapshot.rank}</span>
                            </div>
                          )}
                        </div>

                        {hasFeatures && (
                          <div className="flex items-center gap-2">
                            {snapshot.featured_snippet && (
                              <div className="flex items-center gap-1 text-xs text-warning" title="Featured Snippet">
                                <Star className="w-3 h-3" />
                                <span>Snippet</span>
                              </div>
                            )}
                            {snapshot.people_also_ask && (
                              <div className="flex items-center gap-1 text-xs text-info" title="People Also Ask">
                                <MessageSquare className="w-3 h-3" />
                                <span>PAA</span>
                              </div>
                            )}
                            {snapshot.local_pack && (
                              <div className="flex items-center gap-1 text-xs text-success" title="Local Pack">
                                <MapPin className="w-3 h-3" />
                                <span>Local</span>
                              </div>
                            )}
                            {snapshot.knowledge_panel && (
                              <div className="flex items-center gap-1 text-xs text-primary" title="Knowledge Panel">
                                <BookOpen className="w-3 h-3" />
                                <span>KP</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {snapshot.url && (
                        <div className="text-xs text-neutral-500 truncate">
                          {snapshot.url}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </Card>
          )}

          {/* SERP Results */}
          {selectedSnapshot && results.length > 0 && (
            <Card variant="glass" padding="md">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">SERP Results</h3>
                  <p className="text-sm text-neutral-400">
                    {results.length} result{results.length !== 1 ? 's' : ''} found
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Search className="w-4 h-4 text-neutral-400" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Filter results..."
                      className="bg-dark-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white placeholder:text-neutral-500 focus:outline-none focus:border-primary"
                    />
                  </div>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Rank</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Domain</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">Title</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-neutral-400">URL</th>
                      <th className="px-4 py-3 text-center text-sm font-semibold text-neutral-400">Ours</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {filteredResults.map((result) => (
                      <tr
                        key={result.id}
                        className={`hover:bg-white/5 transition-colors ${
                          result.is_ours ? 'bg-primary/5' : ''
                        }`}
                      >
                        <td className="px-4 py-3">
                          <div className={`
                            inline-flex items-center justify-center w-8 h-8 rounded-full font-semibold text-sm
                            ${result.rank <= 3
                              ? 'bg-warning/20 text-warning'
                              : result.rank <= 10
                                ? 'bg-success/20 text-success'
                                : 'bg-neutral-700/20 text-neutral-400'
                            }
                          `}>
                            {result.rank}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-white">{result.domain}</div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm text-neutral-300 line-clamp-2 max-w-md">
                            {result.title || 'No title'}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary hover:underline truncate block max-w-xs"
                          >
                            {result.url}
                          </a>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {result.is_ours && (
                            <div className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary/20 text-primary text-xs font-medium">
                              <Star className="w-3 h-3" />
                              Our Site
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {filteredResults.length === 0 && (
                  <div className="text-center py-8 text-neutral-400">
                    No results match your filter
                  </div>
                )}
              </div>
            </Card>
          )}

          {loading && (
            <div className="text-center py-8 text-neutral-400">
              Loading...
            </div>
          )}
        </>
      ) : (
        /* Empty State */
        <Card variant="glass" padding="lg">
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4">
              <Search className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              No Keywords Tracked
            </h3>
            <p className="text-neutral-400 mb-6 max-w-md mx-auto">
              SERP data will appear here once you start tracking keywords. Add keywords to begin analyzing search results.
            </p>
            <Button
              variant="primary"
              onClick={() => window.location.href = '/scrape/keywords'}
            >
              Go to Keywords
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default SERPExplorerPage;
