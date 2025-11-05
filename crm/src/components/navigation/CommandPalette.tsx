/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Command Palette Component
 *
 * Quick navigation and search with fuzzy matching using fuse.js.
 * Features:
 * - Cmd+K / Ctrl+K to open
 * - ESC to close
 * - Fuzzy search with fuse.js
 * - Keyboard navigation (arrow keys, enter)
 * - Recent items
 * - Quick actions
 * - Focus trap and portal
 * - ARIA attributes
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Fuse from 'fuse.js';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/shadcn/command';
import {
  LayoutDashboard,
  Users,
  Target,
  Inbox,
  FileText,
  Calendar,
  BarChart3,
  Settings,
  Sparkles,
  Search,
  Plus,
  FileEdit,
} from 'lucide-react';

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  href?: string;
  action?: () => void;
  keywords?: string[];
  group: 'navigation' | 'actions' | 'recent';
}

const navigationCommands: CommandItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    description: 'View your dashboard',
    icon: LayoutDashboard,
    href: '/dashboard',
    keywords: ['home', 'overview'],
    group: 'navigation',
  },
  {
    id: 'leads',
    label: 'Leads',
    description: 'Manage your leads pipeline',
    icon: Target,
    href: '/leads',
    keywords: ['sales', 'pipeline'],
    group: 'navigation',
  },
  {
    id: 'contacts',
    label: 'Contacts',
    description: 'View and manage contacts',
    icon: Users,
    href: '/contacts',
    keywords: ['people', 'customers'],
    group: 'navigation',
  },
  {
    id: 'inbox',
    label: 'Inbox',
    description: 'Check your messages',
    icon: Inbox,
    href: '/inbox',
    keywords: ['messages', 'email'],
    group: 'navigation',
  },
  {
    id: 'quotes',
    label: 'Quotes & Invoices',
    description: 'Manage quotes and invoices',
    icon: FileText,
    href: '/quotes',
    keywords: ['billing', 'invoices', 'estimates'],
    group: 'navigation',
  },
  {
    id: 'calendar',
    label: 'Calendar',
    description: 'View your schedule',
    icon: Calendar,
    href: '/calendar',
    keywords: ['schedule', 'appointments', 'meetings'],
    group: 'navigation',
  },
  {
    id: 'reports',
    label: 'Reports',
    description: 'View analytics and reports',
    icon: BarChart3,
    href: '/reports',
    keywords: ['analytics', 'insights', 'data'],
    group: 'navigation',
  },
  {
    id: 'ai-suite',
    label: 'AI Suite',
    description: 'AI-powered tools',
    icon: Sparkles,
    href: '/ai',
    keywords: ['artificial intelligence', 'automation'],
    group: 'navigation',
  },
  {
    id: 'scrape-suite',
    label: 'Scrape Suite',
    description: 'Web scraping and SEO tools',
    icon: Search,
    href: '/scrape',
    keywords: ['seo', 'web scraping', 'competitors'],
    group: 'navigation',
  },
  {
    id: 'settings',
    label: 'Settings',
    description: 'Manage your preferences',
    icon: Settings,
    href: '/settings',
    keywords: ['preferences', 'configuration'],
    group: 'navigation',
  },
];

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const navigate = useNavigate();
  const [search, setSearch] = React.useState('');
  const [items, setItems] = React.useState<CommandItem[]>(navigationCommands);

  // Quick actions
  const quickActions: CommandItem[] = [
    {
      id: 'new-contact',
      label: 'Create Contact',
      description: 'Add a new contact',
      icon: Plus,
      action: () => {
        navigate('/contacts');
        onOpenChange(false);
        // Trigger contact form open - would be done via context or callback
      },
      keywords: ['add', 'new contact'],
      group: 'actions',
    },
    {
      id: 'new-quote',
      label: 'Create Quote',
      description: 'Generate a new quote',
      icon: FileEdit,
      action: () => {
        navigate('/quotes');
        onOpenChange(false);
      },
      keywords: ['add', 'new quote', 'estimate'],
      group: 'actions',
    },
  ];

  // Fuzzy search with fuse.js
  const fuse = React.useMemo(() => {
    const allItems = [...navigationCommands, ...quickActions];
    return new Fuse(allItems, {
      keys: [
        { name: 'label', weight: 2 },
        { name: 'description', weight: 1 },
        { name: 'keywords', weight: 1.5 },
      ],
      threshold: 0.3,
      ignoreLocation: true,
    });
  }, []);

  React.useEffect(() => {
    if (search.trim() === '') {
      setItems([...quickActions, ...navigationCommands]);
    } else {
      const results = fuse.search(search);
      setItems(results.map((r) => r.item));
    }
  }, [search, fuse]);

  const handleSelect = (item: CommandItem) => {
    if (item.action) {
      item.action();
    } else if (item.href) {
      navigate(item.href);
      onOpenChange(false);
    }
  };

  // Group items by category
  const groupedItems = React.useMemo(() => {
    const groups: Record<string, CommandItem[]> = {};
    items.forEach((item) => {
      if (!groups[item.group]) {
        groups[item.group] = [];
      }
      groups[item.group].push(item);
    });
    return groups;
  }, [items]);

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="Type a command or search..."
        value={search}
        onValueChange={setSearch}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        {groupedItems.actions && groupedItems.actions.length > 0 && (
          <>
            <CommandGroup heading="Quick Actions">
              {groupedItems.actions.map((item) => {
                const Icon = item.icon;
                return (
                  <CommandItem
                    key={item.id}
                    value={item.label}
                    onSelect={() => handleSelect(item)}
                  >
                    {Icon && <Icon className="mr-2 h-4 w-4" />}
                    <div className="flex flex-col">
                      <span>{item.label}</span>
                      {item.description && (
                        <span className="text-xs text-muted-foreground">
                          {item.description}
                        </span>
                      )}
                    </div>
                  </CommandItem>
                );
              })}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {groupedItems.navigation && groupedItems.navigation.length > 0 && (
          <CommandGroup heading="Navigation">
            {groupedItems.navigation.map((item) => {
              const Icon = item.icon;
              return (
                <CommandItem
                  key={item.id}
                  value={item.label}
                  onSelect={() => handleSelect(item)}
                >
                  {Icon && <Icon className="mr-2 h-4 w-4" />}
                  <div className="flex flex-col">
                    <span>{item.label}</span>
                    {item.description && (
                      <span className="text-xs text-muted-foreground">
                        {item.description}
                      </span>
                    )}
                  </div>
                </CommandItem>
              );
            })}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  );
}

/**
 * Hook to manage command palette state and keyboard shortcuts
 */
export function useCommandPalette() {
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  return { open, setOpen };
}
