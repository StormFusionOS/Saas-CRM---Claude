/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Keywords Page
 * Manage tracked keywords and view SERP snapshot history
 */

import React, { useState, useEffect } from 'react';
import scrapeApi, { Keyword, KeywordCreate, SerpSnapshot } from '@/lib/scrape-api';
import SnapshotMiniChart from '@/components/scrape/SnapshotMiniChart';

export default function KeywordsPage() {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedKeyword, setSelectedKeyword] = useState<Keyword | null>(null);
  const [snapshots, setSnapshots] = useState<SerpSnapshot[]>([]);
  const [isAddingKeyword, setIsAddingKeyword] = useState(false);
  const [newKeyword, setNewKeyword] = useState<KeywordCreate>({
    keyword_text: '',
    target_domain: '',
    intent: 'commercial',
    is_active: true,
  });

  // Load keywords
  const loadKeywords = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await scrapeApi.getKeywords({ is_active: true });
      setKeywords(response.keywords);
    } catch (err: any) {
      console.error('Failed to load keywords:', err);
      setError(err.message || 'Failed to load keywords');
    } finally {
      setLoading(false);
    }
  };

  // Load snapshots for selected keyword
  const loadSnapshots = async (keywordId: number) => {
    try {
      const response = await scrapeApi.getSerpSnapshots({
        keyword_id: keywordId,
        page_size: 30,
      });
      setSnapshots(response.snapshots);
    } catch (err: any) {
      console.error('Failed to load snapshots:', err);
    }
  };

  // Create keyword
  const handleCreateKeyword = async () => {
    if (!newKeyword.keyword_text || !newKeyword.target_domain) {
      alert('Please fill in keyword text and target domain');
      return;
    }

    try {
      await scrapeApi.createKeyword(newKeyword);
      setIsAddingKeyword(false);
      setNewKeyword({
        keyword_text: '',
        target_domain: '',
        intent: 'commercial',
        is_active: true,
      });
      loadKeywords();
    } catch (err: any) {
      console.error('Failed to create keyword:', err);
      alert(err.response?.data?.detail || err.message || 'Failed to create keyword');
    }
  };

  // Delete keyword
  const handleDeleteKeyword = async (keywordId: number) => {
    if (!confirm('Are you sure you want to delete this keyword?')) return;

    try {
      await scrapeApi.deleteKeyword(keywordId);
      loadKeywords();
      if (selectedKeyword?.id === keywordId) {
        setSelectedKeyword(null);
        setSnapshots([]);
      }
    } catch (err: any) {
      console.error('Failed to delete keyword:', err);
      alert(err.message || 'Failed to delete keyword');
    }
  };

  // Trigger snapshot now
  const handleSnapshotNow = async () => {
    try {
      await scrapeApi.triggerJob({
        type: 'serp',
        payload: {},
      });
      alert('SERP snapshot job started! Check Runs & Logs for progress.');
    } catch (err: any) {
      console.error('Failed to trigger snapshot:', err);
      alert(err.message || 'Failed to trigger snapshot');
    }
  };

  // Select keyword
  const handleSelectKeyword = (keyword: Keyword) => {
    setSelectedKeyword(keyword);
    loadSnapshots(keyword.id);
  };

  useEffect(() => {
    loadKeywords();
  }, []);

  // Get rank trend data for sparkline
  const getRankTrend = (keywordId: number) => {
    // In a real implementation, this would fetch historical data
    // For now, generate sample data based on current rank
    const keyword = keywords.find((k) => k.id === keywordId);
    if (!keyword || !keyword.current_rank) return [];

    // Generate 7 data points showing trend
    const trend = [];
    for (let i = 6; i >= 0; i--) {
      const variance = Math.floor(Math.random() * 5) - 2;
      trend.push(Math.max(1, keyword.current_rank + variance));
    }
    return trend;
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Tracked Keywords
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage keywords and monitor SERP rankings
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSnapshotNow}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
          >
            Snapshot Now
          </button>
          <button
            onClick={() => setIsAddingKeyword(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Add Keyword
          </button>
        </div>
      </div>

      {/* Add Keyword Form */}
      {isAddingKeyword && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Add New Keyword
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Keyword Text *
              </label>
              <input
                type="text"
                value={newKeyword.keyword_text}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, keyword_text: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                placeholder="pressure washing services"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Target Domain *
              </label>
              <input
                type="text"
                value={newKeyword.target_domain}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, target_domain: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                placeholder="rivercityclean.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Intent
              </label>
              <select
                value={newKeyword.intent || 'commercial'}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, intent: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
              >
                <option value="informational">Informational</option>
                <option value="commercial">Commercial</option>
                <option value="transactional">Transactional</option>
                <option value="navigational">Navigational</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Target Page (optional)
              </label>
              <input
                type="text"
                value={newKeyword.target_page || ''}
                onChange={(e) =>
                  setNewKeyword({ ...newKeyword, target_page: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                placeholder="https://rivercityclean.com/services"
              />
            </div>
          </div>
          <div className="flex items-center gap-3 mt-4">
            <button
              onClick={handleCreateKeyword}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Add Keyword
            </button>
            <button
              onClick={() => setIsAddingKeyword(false)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Keywords Table */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : error ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
          <p className="text-sm text-red-800 dark:text-red-400">{error}</p>
        </div>
      ) : keywords.length === 0 ? (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-8 text-center">
          <p className="text-gray-600 dark:text-gray-400">
            No keywords found. Add your first keyword to start tracking!
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Keyword
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Intent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Trend
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Metrics
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {keywords.map((keyword) => (
                <tr
                  key={keyword.id}
                  onClick={() => handleSelectKeyword(keyword)}
                  className={`cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                    selectedKeyword?.id === keyword.id
                      ? 'bg-blue-50 dark:bg-blue-900/20'
                      : ''
                  }`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {keyword.keyword_text}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {keyword.target_domain}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                      {keyword.intent || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {keyword.current_rank ? (
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          #{keyword.current_rank}
                        </span>
                        {keyword.previous_rank && (
                          <span
                            className={`text-xs ${
                              keyword.current_rank < keyword.previous_rank
                                ? 'text-green-600 dark:text-green-400'
                                : keyword.current_rank > keyword.previous_rank
                                ? 'text-red-600 dark:text-red-400'
                                : 'text-gray-600 dark:text-gray-400'
                            }`}
                          >
                            {keyword.current_rank < keyword.previous_rank
                              ? `↑ ${keyword.previous_rank - keyword.current_rank}`
                              : keyword.current_rank > keyword.previous_rank
                              ? `↓ ${keyword.current_rank - keyword.previous_rank}`
                              : '—'}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Not ranked
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <SnapshotMiniChart data={getRankTrend(keyword.id)} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    <div>Clicks: {keyword.clicks || 0}</div>
                    <div>Impr: {keyword.impressions || 0}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteKeyword(keyword.id);
                      }}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Snapshot History (shown when keyword selected) */}
      {selectedKeyword && (
        <div className="mt-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Snapshots for "{selectedKeyword.keyword_text}"
          </h3>
          {snapshots.length === 0 ? (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              No snapshots yet. Run a SERP snapshot to see historical data.
            </p>
          ) : (
            <div className="space-y-2">
              {snapshots.map((snapshot) => (
                <div
                  key={snapshot.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-md"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {new Date(snapshot.search_date).toLocaleDateString()}
                    </span>
                    {snapshot.rank && (
                      <span className="font-semibold text-gray-900 dark:text-white">
                        Rank: #{snapshot.rank}
                      </span>
                    )}
                    {snapshot.featured_snippet && (
                      <span className="px-2 py-1 text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 rounded">
                        Featured Snippet
                      </span>
                    )}
                  </div>
                  {snapshot.url && (
                    <a
                      href={snapshot.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      View URL
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
