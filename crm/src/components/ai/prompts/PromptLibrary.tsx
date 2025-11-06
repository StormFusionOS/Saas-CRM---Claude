/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Prompt Library Component
 * Browse and manage prompt templates
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Badge } from '@/components/ui/shadcn/badge';
import { Button } from '@/components/ui/shadcn/button';
import {
  FileText,
  Plus,
  Edit,
  Trash2,
  TrendingUp,
  Star,
} from 'lucide-react';
import type { PromptTemplate } from '@/lib/ai-types';
import { cn } from '@/lib/utils';

interface PromptLibraryProps {
  templates: PromptTemplate[];
  isLoading?: boolean;
  onSelectTemplate: (template: PromptTemplate) => void;
  onCreateNew?: () => void;
}

interface TemplateCardProps {
  template: PromptTemplate;
  onClick: () => void;
}

function TemplateCard({ template, onClick }: TemplateCardProps) {
  const successRate = (template.metrics.success_count / template.metrics.total_runs) * 100 || 0;

  return (
    <Card
      className="glow-hover cursor-pointer hover:border-primary/50 transition-all"
      onClick={onClick}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-primary flex-shrink-0" />
              <h3 className="text-lg font-semibold text-text-primary truncate">
                {template.name}
              </h3>
            </div>
            <p className="text-sm text-text-muted line-clamp-2">
              {template.description}
            </p>
          </div>

          <div className="flex items-center gap-1 ml-2">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => {
              e.stopPropagation();
              // TODO: Edit template
            }}>
              <Edit className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {template.tags.slice(0, 3).map((tag) => (
            <Badge
              key={tag}
              variant="secondary"
              className="text-xs bg-primary/10 text-primary border-primary/20"
            >
              {tag}
            </Badge>
          ))}
          {template.tags.length > 3 && (
            <Badge variant="secondary" className="text-xs">
              +{template.tags.length - 3} more
            </Badge>
          )}
        </div>

        {/* Template Preview */}
        <div className="p-3 bg-white/5 rounded-lg border border-white/10">
          <p className="text-xs font-mono text-text-muted line-clamp-3">
            {template.template}
          </p>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/5">
          <div>
            <p className="text-xs text-text-muted mb-1">Success Rate</p>
            <div className="flex items-center gap-1">
              <TrendingUp className={cn(
                "w-3 h-3",
                successRate >= 80 ? "text-success" : successRate >= 60 ? "text-warning" : "text-error"
              )} />
              <p className={cn(
                "text-sm font-medium",
                successRate >= 80 ? "text-success" : successRate >= 60 ? "text-warning" : "text-error"
              )}>
                {successRate.toFixed(0)}%
              </p>
            </div>
          </div>

          <div>
            <p className="text-xs text-text-muted mb-1">Total Runs</p>
            <p className="text-sm font-medium text-text-primary">
              {template.metrics.total_runs}
            </p>
          </div>

          <div>
            <p className="text-xs text-text-muted mb-1">Avg Duration</p>
            <p className="text-sm font-medium text-text-primary">
              {(template.metrics.avg_duration / 1000).toFixed(1)}s
            </p>
          </div>
        </div>

        {/* Version & Status */}
        <div className="flex items-center justify-between pt-4 border-t border-white/5">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              v{template.version}
            </Badge>
            {template.is_active ? (
              <Badge variant="outline" className="text-xs bg-success/10 text-success border-success/20">
                Active
              </Badge>
            ) : (
              <Badge variant="secondary" className="text-xs">
                Inactive
              </Badge>
            )}
          </div>
          <p className="text-xs text-text-muted">
            Updated {new Date(template.updated_at).toLocaleDateString()}
          </p>
        </div>
      </div>
    </Card>
  );
}

export function PromptLibrary({
  templates,
  isLoading,
  onSelectTemplate,
  onCreateNew,
}: PromptLibraryProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <div className="space-y-4">
                <div className="h-6 bg-white/5 rounded w-3/4" />
                <div className="h-4 bg-white/5 rounded w-full" />
                <div className="h-20 bg-white/5 rounded" />
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-8 bg-white/5 rounded" />
                  <div className="h-8 bg-white/5 rounded" />
                  <div className="h-8 bg-white/5 rounded" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-text-primary">
          Prompt Library
        </h2>
        <Button onClick={onCreateNew} className="gap-2">
          <Plus className="w-4 h-4" />
          New Template
        </Button>
      </div>

      {templates.length === 0 ? (
        <Card className="py-12">
          <div className="text-center">
            <FileText className="w-16 h-16 mx-auto text-text-muted mb-4" />
            <p className="text-lg text-text-secondary font-medium mb-2">
              No templates yet
            </p>
            <p className="text-sm text-text-muted mb-4">
              Create your first prompt template to get started
            </p>
            <Button onClick={onCreateNew} className="gap-2">
              <Plus className="w-4 h-4" />
              Create Template
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onClick={() => onSelectTemplate(template)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
