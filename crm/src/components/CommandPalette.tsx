/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Fuse from 'fuse.js';
import { leadsAPI } from '../lib/api';

interface CommandItem {
  id: string;
  type: 'action' | 'lead' | 'contact' | 'page' | 'quote';
  title: string;
  subtitle?: string;
  icon: string;
  action: () => void;
  keywords?: string[];
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [leads, setLeads] = useState<any[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load leads data
  useEffect(() => {
    if (isOpen) {
      loadLeads();
    }
  }, [isOpen]);

  const loadLeads = async () => {
    try {
      const response = await leadsAPI.getLeadsBoard();
      const allLeads = Object.values(response).flat();
      setLeads(allLeads);
    } catch (err) {
      console.error('Failed to load leads:', err);
    }
  };

  // Define static pages
  const pages: CommandItem[] = [
    {
      id: 'page-dashboard',
      type: 'page',
      title: 'Dashboard',
      subtitle: 'View overview and metrics',
      icon: '📊',
      action: () => {
        navigate('/dashboard');
        onClose();
      },
      keywords: ['home', 'overview', 'metrics'],
    },
    {
      id: 'page-leads',
      type: 'page',
      title: 'Leads Pipeline',
      subtitle: 'Manage sales leads',
      icon: '🎯',
      action: () => {
        navigate('/leads');
        onClose();
      },
      keywords: ['pipeline', 'kanban', 'sales'],
    },
    {
      id: 'page-inbox',
      type: 'page',
      title: 'Unified Inbox',
      subtitle: 'Messages and communications',
      icon: '📧',
      action: () => {
        navigate('/inbox');
        onClose();
      },
      keywords: ['messages', 'email', 'sms', 'communications'],
    },
    {
      id: 'page-calendar',
      type: 'page',
      title: 'Calendar',
      subtitle: 'Schedule and appointments',
      icon: '📅',
      action: () => {
        navigate('/calendar');
        onClose();
      },
      keywords: ['schedule', 'appointments', 'events'],
    },
    {
      id: 'page-reports',
      type: 'page',
      title: 'Reports',
      subtitle: 'Analytics and insights',
      icon: '📈',
      action: () => {
        navigate('/reports');
        onClose();
      },
      keywords: ['analytics', 'insights', 'data'],
    },
    {
      id: 'page-seo',
      type: 'page',
      title: 'SEO Tools',
      subtitle: 'Search engine optimization',
      icon: '🔍',
      action: () => {
        navigate('/seo');
        onClose();
      },
      keywords: ['search', 'google', 'optimization'],
    },
    {
      id: 'page-settings',
      type: 'page',
      title: 'Settings',
      subtitle: 'Configure your account',
      icon: '⚙️',
      action: () => {
        navigate('/settings');
        onClose();
      },
      keywords: ['preferences', 'config', 'account'],
    },
  ];

  // Define quick actions
  const actions: CommandItem[] = [
    {
      id: 'action-new-lead',
      type: 'action',
      title: 'New Lead',
      subtitle: 'Create a new sales lead',
      icon: '➕',
      action: () => {
        // TODO: Open new lead modal
        navigate('/leads');
        onClose();
        alert('New Lead creation (stub)');
      },
      keywords: ['create', 'add'],
    },
    {
      id: 'action-new-estimate',
      type: 'action',
      title: 'New Estimate',
      subtitle: 'Generate pricing quote',
      icon: '💰',
      action: () => {
        navigate('/estimator');
        onClose();
      },
      keywords: ['quote', 'pricing', 'proposal'],
    },
    {
      id: 'action-send-message',
      type: 'action',
      title: 'Send Message',
      subtitle: 'Compose email or SMS',
      icon: '✉️',
      action: () => {
        navigate('/inbox');
        onClose();
        alert('Compose message (stub)');
      },
      keywords: ['compose', 'email', 'sms', 'text'],
    },
    {
      id: 'action-schedule',
      type: 'action',
      title: 'Schedule Appointment',
      subtitle: 'Book time on calendar',
      icon: '🗓️',
      action: () => {
        navigate('/calendar');
        onClose();
        alert('Schedule appointment (stub)');
      },
      keywords: ['book', 'meeting', 'appointment'],
    },
    {
      id: 'action-seo-audit',
      type: 'action',
      title: 'Run SEO Audit',
      subtitle: 'Analyze website performance',
      icon: '🔎',
      action: () => {
        navigate('/seo');
        onClose();
        alert('Running SEO audit (stub)');
      },
      keywords: ['analyze', 'scan', 'performance', 'website'],
    },
  ];

  // Convert leads to command items
  const leadItems: CommandItem[] = useMemo(
    () =>
      leads.map((lead: any) => ({
        id: `lead-${lead.id}`,
        type: 'lead' as const,
        title: lead.contact?.first_name
          ? `${lead.contact.first_name} ${lead.contact.last_name || ''}`.trim()
          : lead.contact?.email || `Lead #${lead.id}`,
        subtitle: `${lead.status} • ${lead.contact?.company || lead.contact?.email || ''}`,
        icon: '👤',
        action: () => {
          navigate(`/leads?focus=${lead.id}`);
          onClose();
        },
        keywords: [
          lead.contact?.email,
          lead.contact?.phone,
          lead.contact?.company,
          lead.status,
        ].filter(Boolean),
      })),
    [leads, navigate, onClose]
  );

  // Combine all items
  const allItems = useMemo(
    () => [...actions, ...pages, ...leadItems],
    [leadItems]
  );

  // Fuzzy search
  const fuse = useMemo(
    () =>
      new Fuse(allItems, {
        keys: ['title', 'subtitle', 'keywords'],
        threshold: 0.3,
        includeScore: true,
      }),
    [allItems]
  );

  const filteredItems = useMemo(() => {
    if (!query.trim()) {
      // Show actions and pages when no query
      return [...actions, ...pages].slice(0, 10);
    }
    return fuse.search(query).map((result) => result.item).slice(0, 10);
  }, [query, fuse, actions, pages]);

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [filteredItems]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
    }
  }, [isOpen]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredItems.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev === 0 ? filteredItems.length - 1 : prev - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredItems[selectedIndex]) {
          filteredItems[selectedIndex].action();
        }
        break;
      case 'Escape':
        e.preventDefault();
        onClose();
        break;
    }
  };

  if (!isOpen) return null;

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'action':
        return 'text-primary';
      case 'lead':
        return 'text-blue-400';
      case 'page':
        return 'text-purple-400';
      case 'quote':
        return 'text-green-400';
      default:
        return 'text-text-secondary';
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
        onClick={onClose}
      />

      {/* Command Palette */}
      <div className="fixed top-[20%] left-1/2 transform -translate-x-1/2 w-full max-w-2xl z-50">
        <div className="bg-bg-elevated border border-white/10 rounded-lg shadow-2xl overflow-hidden">
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
            <span className="text-xl">🔍</span>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search or type a command..."
              className="flex-1 bg-transparent border-none outline-none text-text-primary text-lg placeholder-text-secondary"
            />
            <kbd className="px-2 py-1 bg-white/5 border border-white/10 rounded text-xs text-text-secondary">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <div className="max-h-96 overflow-y-auto">
            {filteredItems.length === 0 ? (
              <div className="px-4 py-8 text-center text-text-secondary">
                No results found for "{query}"
              </div>
            ) : (
              <div className="py-2">
                {filteredItems.map((item, index) => (
                  <button
                    key={item.id}
                    onClick={() => item.action()}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                      index === selectedIndex
                        ? 'bg-primary/20 border-l-2 border-primary'
                        : 'hover:bg-white/5'
                    }`}
                  >
                    <span className="text-2xl">{item.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-text-primary truncate">
                        {item.title}
                      </div>
                      {item.subtitle && (
                        <div className="text-sm text-text-secondary truncate">
                          {item.subtitle}
                        </div>
                      )}
                    </div>
                    <span
                      className={`text-xs font-medium uppercase ${getTypeColor(
                        item.type
                      )}`}
                    >
                      {item.type}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-2 border-t border-white/10 bg-white/5 text-xs text-text-secondary">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white/10 border border-white/10 rounded">
                  ↑
                </kbd>
                <kbd className="px-1.5 py-0.5 bg-white/10 border border-white/10 rounded">
                  ↓
                </kbd>
                Navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white/10 border border-white/10 rounded">
                  ↵
                </kbd>
                Select
              </span>
            </div>
            <div>
              {filteredItems.length} result{filteredItems.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CommandPalette;
