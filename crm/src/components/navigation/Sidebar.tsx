/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Sidebar Component
 *
 * Responsive sidebar navigation using shadcn Sheet for mobile.
 * Features:
 * - Desktop: Fixed sidebar with smooth transitions
 * - Mobile: Sheet overlay with focus trap and ESC to close
 * - Keyboard navigation with arrow keys
 * - ARIA landmarks and labels
 * - Active route highlighting
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  Target,
  Inbox,
  FileText,
  Calendar,
  BarChart3,
  Settings,
  ChevronRight,
  Sparkles,
  Search,
  Zap,
  ShieldCheck,
} from 'lucide-react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/shadcn/sheet';

interface NavItem {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  badge?: string;
  children?: NavItem[];
}

const navigationItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    href: '/dashboard',
  },
  {
    label: 'Leads',
    icon: Target,
    href: '/leads',
  },
  {
    label: 'Contacts',
    icon: Users,
    href: '/contacts',
  },
  {
    label: 'Inbox',
    icon: Inbox,
    href: '/inbox',
    badge: '3',
  },
  {
    label: 'Quotes',
    icon: FileText,
    href: '/quotes',
  },
  {
    label: 'Calendar',
    icon: Calendar,
    href: '/calendar',
  },
  {
    label: 'Reports',
    icon: BarChart3,
    href: '/reports',
  },
];

const suiteItems: NavItem[] = [
  {
    label: 'AI Suite',
    icon: Sparkles,
    href: '/ai',
    children: [
      { label: 'Dashboard', icon: LayoutDashboard, href: '/ai/dashboard' },
      { label: 'Prompt Runner', icon: Zap, href: '/ai/prompt-runner' },
      { label: 'Governance', icon: ShieldCheck, href: '/ai/governance' },
    ],
  },
  {
    label: 'Scrape Suite',
    icon: Search,
    href: '/scrape',
    children: [
      { label: 'Dashboard', icon: LayoutDashboard, href: '/scrape/dashboard' },
      { label: 'Competitors', icon: Target, href: '/scrape/competitors' },
      { label: 'SERP Explorer', icon: Search, href: '/scrape/serp-explorer' },
    ],
  },
];

interface SidebarProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  isMobile?: boolean;
}

function NavItemComponent({
  item,
  depth = 0,
}: {
  item: NavItem;
  depth?: number;
}) {
  const location = useLocation();
  const [isExpanded, setIsExpanded] = React.useState(false);
  const isActive = location.pathname === item.href;
  const hasChildren = item.children && item.children.length > 0;

  const Icon = item.icon;

  const handleClick = (e: React.MouseEvent) => {
    if (hasChildren) {
      e.preventDefault();
      setIsExpanded(!isExpanded);
    }
  };

  return (
    <div>
      <Link
        to={item.href}
        onClick={handleClick}
        className={cn(
          'flex items-center justify-between gap-3 px-3 py-2 rounded-lg transition-all',
          'hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-primary',
          isActive && 'bg-primary/10 text-primary font-medium',
          !isActive && 'text-text-secondary hover:text-text-primary',
          depth > 0 && 'ml-4 text-sm'
        )}
        aria-current={isActive ? 'page' : undefined}
      >
        <div className="flex items-center gap-3 flex-1">
          <Icon className={cn('h-5 w-5', depth > 0 && 'h-4 w-4')} />
          <span>{item.label}</span>
        </div>
        {item.badge && (
          <span className="px-2 py-0.5 rounded-full bg-primary text-white text-xs font-medium">
            {item.badge}
          </span>
        )}
        {hasChildren && (
          <ChevronRight
            className={cn(
              'h-4 w-4 transition-transform',
              isExpanded && 'rotate-90'
            )}
          />
        )}
      </Link>

      {hasChildren && isExpanded && (
        <div className="mt-1 space-y-1">
          {item.children?.map((child) => (
            <NavItemComponent key={child.href} item={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function SidebarContent() {
  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="px-6 py-4 border-b border-border">
        <Link
          to="/"
          className="flex items-center gap-2 font-display font-bold text-xl text-gradient focus:outline-none focus:ring-2 focus:ring-primary rounded"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <span className="text-white font-bold">RC</span>
          </div>
          <span>RiverCity</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav
        className="flex-1 px-4 py-4 space-y-6 overflow-y-auto"
        aria-label="Main navigation"
      >
        {/* Main Items */}
        <div>
          <h3 className="px-3 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Main
          </h3>
          <div className="space-y-1">
            {navigationItems.map((item) => (
              <NavItemComponent key={item.href} item={item} />
            ))}
          </div>
        </div>

        {/* Suites */}
        <div>
          <h3 className="px-3 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Suites
          </h3>
          <div className="space-y-1">
            {suiteItems.map((item) => (
              <NavItemComponent key={item.href} item={item} />
            ))}
          </div>
        </div>
      </nav>

      {/* Settings */}
      <div className="px-4 py-4 border-t border-border">
        <Link
          to="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-muted/50 transition-all focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <Settings className="h-5 w-5" />
          <span>Settings</span>
        </Link>
      </div>
    </div>
  );
}

export function Sidebar({ open, onOpenChange, isMobile }: SidebarProps) {
  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent
          side="left"
          className="w-72 p-0"
          aria-label="Mobile navigation menu"
        >
          <SheetHeader className="sr-only">
            <SheetTitle>Navigation Menu</SheetTitle>
          </SheetHeader>
          <SidebarContent />
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <aside
      className="hidden lg:flex lg:flex-col w-72 border-r border-border bg-background"
      aria-label="Desktop navigation"
    >
      <SidebarContent />
    </aside>
  );
}
