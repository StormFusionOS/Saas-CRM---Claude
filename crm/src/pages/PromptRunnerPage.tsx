/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Prompt Runner Page
 * Master prompt library with execution, validation, and history
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Badge } from '@/components/ui/shadcn/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { usePromptTemplates } from '@/lib/ai-queries';
import { PromptLibrary } from '@/components/ai/prompts/PromptLibrary';
import { PromptExecutor } from '@/components/ai/prompts/PromptExecutor';
import type { PromptTemplate } from '@/lib/ai-types';
import {
  FileText,
  Play,
  Clock,
  Database,
} from 'lucide-react';

const PromptRunnerPage: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = React.useState<PromptTemplate | null>(null);
  const [activeTab, setActiveTab] = React.useState('library');

  // Fetch templates with TanStack Query
  const { data: templates, isLoading } = usePromptTemplates();

  const handleSelectTemplate = (template: PromptTemplate) => {
    setSelectedTemplate(template);
    setActiveTab('runner');
  };

  const handleClearTemplate = () => {
    setSelectedTemplate(null);
  };

  const handleSuccess = () => {
    // Navigate to history tab after successful execution
    setActiveTab('history');
  };

  // Calculate stats
  const totalTemplates = templates?.length || 0;
  const activeTemplates = templates?.filter(t => t.is_active).length || 0;
  const totalRuns = templates?.reduce((sum, t) => sum + t.metrics.total_runs, 0) || 0;
  const avgSuccessRate = templates?.length > 0
    ? templates.reduce((sum, t) => sum + (t.metrics.success_count / (t.metrics.total_runs || 1)), 0) / templates.length * 100
    : 0;

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">
          Prompt Runner
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Master prompt library with execution, validation, and history
        </p>
      </div>

      {/* Main Content */}
      <main className="p-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">
                  Total Templates
                </h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">
                {totalTemplates}
              </p>
              <div className="mt-2 text-xs text-text-muted">
                {activeTemplates} active
              </div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Play className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">
                  Total Runs
                </h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">
                {totalRuns}
              </p>
              <div className="mt-2 text-xs text-text-muted">All time</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">
                  Success Rate
                </h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">
                {avgSuccessRate.toFixed(0)}%
              </p>
              <div className="mt-2 text-xs text-text-muted">Average</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">
                  Avg Duration
                </h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">
                {templates?.length > 0
                  ? (templates.reduce((sum, t) => sum + t.metrics.avg_duration, 0) / templates.length / 1000).toFixed(1)
                  : '0.0'}s
              </p>
              <div className="mt-2 text-xs text-text-muted">Per execution</div>
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="library">
              <FileText className="w-4 h-4 mr-2" />
              Library
            </TabsTrigger>
            <TabsTrigger value="runner">
              <Play className="w-4 h-4 mr-2" />
              Run Prompt
            </TabsTrigger>
            <TabsTrigger value="history">
              <Clock className="w-4 h-4 mr-2" />
              History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="library">
            <PromptLibrary
              templates={templates || []}
              isLoading={isLoading}
              onSelectTemplate={handleSelectTemplate}
              onCreateNew={() => {
                // TODO: Implement create new template
                alert('Create new template feature coming soon!');
              }}
            />
          </TabsContent>

          <TabsContent value="runner">
            <PromptExecutor
              selectedTemplate={selectedTemplate}
              onClearTemplate={handleClearTemplate}
              onSuccess={handleSuccess}
            />
          </TabsContent>

          <TabsContent value="history">
            <Card className="py-12">
              <div className="text-center">
                <Clock className="w-16 h-16 mx-auto text-text-muted mb-4" />
                <p className="text-lg text-text-secondary font-medium mb-2">
                  Execution History
                </p>
                <p className="text-sm text-text-muted">
                  View your prompt execution history and results here
                </p>
                <p className="text-xs text-text-muted mt-2">
                  (Feature coming soon - will integrate with Jobs page)
                </p>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default PromptRunnerPage;
