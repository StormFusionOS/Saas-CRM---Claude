/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import { Globe, Plus, Users, Trash2, Edit2, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { scrapeApi, Competitor } from '../../lib/scrape-api';

const CompetitorsPage: React.FC = () => {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isAddingCompetitor, setIsAddingCompetitor] = useState(false);
  const [editingCompetitor, setEditingCompetitor] = useState<Competitor | null>(null);
  const [deletingCompetitor, setDeletingCompetitor] = useState<number | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    domain: '',
    name: '',
    category: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'critical',
    is_active: true,
  });

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
  });

  useEffect(() => {
    loadCompetitors();
  }, []);

  const loadCompetitors = async () => {
    try {
      setLoading(true);
      const response = await scrapeApi.getCompetitors({ page: 1, page_size: 100 });
      setCompetitors(response.competitors);
      setTotal(response.total);

      // Calculate stats
      const active = response.competitors.filter(c => c.is_active).length;
      setStats({
        total: response.total,
        active,
        inactive: response.total - active,
      });
    } catch (error) {
      console.error('Failed to load competitors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCompetitor = async () => {
    try {
      await scrapeApi.createCompetitor({
        domain: formData.domain,
        name: formData.name,
        category: formData.category || null,
        priority: formData.priority,
        is_active: formData.is_active,
      });
      setIsAddingCompetitor(false);
      setFormData({ domain: '', name: '', category: '', priority: 'medium', is_active: true });
      loadCompetitors();
    } catch (error) {
      console.error('Failed to create competitor:', error);
    }
  };

  const handleUpdateCompetitor = async () => {
    if (!editingCompetitor) return;

    try {
      await scrapeApi.updateCompetitor(editingCompetitor.id, {
        name: formData.name,
        category: formData.category || null,
        priority: formData.priority,
        is_active: formData.is_active,
      });
      setEditingCompetitor(null);
      setFormData({ domain: '', name: '', category: '', priority: 'medium', is_active: true });
      loadCompetitors();
    } catch (error) {
      console.error('Failed to update competitor:', error);
    }
  };

  const handleDeleteCompetitor = async (id: number) => {
    try {
      await scrapeApi.deleteCompetitor(id);
      setDeletingCompetitor(null);
      loadCompetitors();
    } catch (error) {
      console.error('Failed to delete competitor:', error);
    }
  };

  const startEditing = (competitor: Competitor) => {
    setEditingCompetitor(competitor);
    setFormData({
      domain: competitor.domain,
      name: competitor.name,
      category: competitor.category || '',
      priority: (competitor.priority as 'low' | 'medium' | 'high' | 'critical') || 'medium',
      is_active: competitor.is_active,
    });
  };

  const cancelForm = () => {
    setIsAddingCompetitor(false);
    setEditingCompetitor(null);
    setFormData({ domain: '', name: '', category: '', priority: 'medium', is_active: true });
  };

  const getPriorityColor = (priority: string | null) => {
    switch (priority) {
      case 'critical': return 'bg-danger/20 text-danger';
      case 'high': return 'bg-warning/20 text-warning';
      case 'medium': return 'bg-primary/20 text-primary';
      case 'low': return 'bg-neutral-600/20 text-neutral-400';
      default: return 'bg-neutral-600/20 text-neutral-400';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Competitor Intelligence
          </h1>
          <p className="text-neutral-400">
            Monitor competitor websites and track their changes
          </p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
          onClick={() => setIsAddingCompetitor(true)}
          aria-label="Add new competitor"
          disabled={isAddingCompetitor || editingCompetitor !== null}
        >
          Add Competitor
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Total Competitors</p>
              <p className="text-2xl font-bold text-white">{stats.total}</p>
            </div>
            <div className="p-2 rounded-lg bg-warning/20">
              <Users className="w-5 h-5 text-warning" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Active Monitoring</p>
              <p className="text-2xl font-bold text-white">{stats.active}</p>
            </div>
            <div className="p-2 rounded-lg bg-success/20">
              <CheckCircle2 className="w-5 h-5 text-success" />
            </div>
          </div>
        </Card>

        <Card variant="glass" padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-neutral-400 mb-1">Inactive</p>
              <p className="text-2xl font-bold text-white">{stats.inactive}</p>
            </div>
            <div className="p-2 rounded-lg bg-neutral-600/20">
              <XCircle className="w-5 h-5 text-neutral-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Add/Edit Form */}
      {(isAddingCompetitor || editingCompetitor) && (
        <Card variant="glass" padding="lg">
          <h3 className="text-xl font-semibold text-white mb-4">
            {editingCompetitor ? 'Edit Competitor' : 'Add New Competitor'}
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Domain *
              </label>
              <input
                type="text"
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                placeholder="example.com"
                disabled={!!editingCompetitor}
                className="w-full px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:border-primary disabled:opacity-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Competitor Name"
                className="w-full px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Category
              </label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g., Direct, Indirect"
                className="w-full px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                className="w-full px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:border-primary"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-primary bg-neutral-800 border-neutral-700 rounded focus:ring-primary focus:ring-2"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-neutral-300">
                Active monitoring
              </label>
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <Button
              variant="primary"
              onClick={editingCompetitor ? handleUpdateCompetitor : handleCreateCompetitor}
              disabled={!formData.domain || !formData.name}
            >
              {editingCompetitor ? 'Update Competitor' : 'Add Competitor'}
            </Button>
            <Button variant="ghost" onClick={cancelForm}>
              Cancel
            </Button>
          </div>
        </Card>
      )}

      {/* Competitors List */}
      {loading ? (
        <Card variant="glass" padding="lg">
          <div className="text-center py-12">
            <p className="text-neutral-400">Loading competitors...</p>
          </div>
        </Card>
      ) : competitors.length === 0 ? (
        <Card variant="glass" padding="lg">
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-warning/20 mb-4">
              <Users className="w-8 h-8 text-warning" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              No Competitors Configured
            </h3>
            <p className="text-neutral-400 mb-6 max-w-md mx-auto">
              Start monitoring competitor websites to track their content changes, pricing updates, and strategic moves.
            </p>
            <Button
              variant="primary"
              icon={<Plus className="w-4 h-4" />}
              onClick={() => setIsAddingCompetitor(true)}
              aria-label="Add your first competitor"
            >
              Add Your First Competitor
            </Button>
          </div>
        </Card>
      ) : (
        <Card variant="glass" padding="lg">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-400">Domain</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-400">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-400">Category</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-400">Priority</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-400">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-neutral-400">Last Scraped</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-neutral-400">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800">
                {competitors.map((competitor) => (
                  <tr key={competitor.id} className="hover:bg-neutral-800/50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-neutral-500" />
                        <span className="text-white font-medium">{competitor.domain}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-neutral-300">{competitor.name}</td>
                    <td className="py-3 px-4">
                      {competitor.category ? (
                        <span className="px-2 py-1 rounded text-xs bg-neutral-700 text-neutral-300">
                          {competitor.category}
                        </span>
                      ) : (
                        <span className="text-neutral-500 text-sm">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${getPriorityColor(competitor.priority)}`}>
                        {competitor.priority || 'medium'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {competitor.is_active ? (
                        <span className="flex items-center gap-1 text-success text-sm">
                          <CheckCircle2 className="w-4 h-4" />
                          Active
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-neutral-500 text-sm">
                          <XCircle className="w-4 h-4" />
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-neutral-400 text-sm">
                      {formatDate(competitor.last_scraped)}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => startEditing(competitor)}
                          className="p-2 rounded-lg hover:bg-neutral-700 text-neutral-400 hover:text-white transition-colors"
                          aria-label={`Edit ${competitor.name}`}
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeletingCompetitor(competitor.id)}
                          className="p-2 rounded-lg hover:bg-danger/20 text-neutral-400 hover:text-danger transition-colors"
                          aria-label={`Delete ${competitor.name}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      {deletingCompetitor !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setDeletingCompetitor(null)}>
          <Card variant="glass" padding="lg" className="max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-full bg-danger/20">
                <AlertTriangle className="w-6 h-6 text-danger" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">Delete Competitor</h3>
                <p className="text-neutral-400 mb-6">
                  Are you sure you want to delete this competitor? This action cannot be undone.
                </p>
                <div className="flex gap-3">
                  <Button variant="danger" onClick={() => handleDeleteCompetitor(deletingCompetitor)}>
                    Delete
                  </Button>
                  <Button variant="ghost" onClick={() => setDeletingCompetitor(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Info Card */}
      <Card variant="glass" padding="md">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-info/20 flex-shrink-0">
            <Globe className="w-5 h-5 text-info" />
          </div>
          <div>
            <h4 className="font-semibold text-white mb-1">Competitor Monitoring Schedule</h4>
            <p className="text-sm text-neutral-400">
              Competitor websites are crawled weekly. Full-site crawls run monthly. Configure crawl depth and frequency in Settings.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default CompetitorsPage;
