/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Prompt Executor Component
 * Run prompts with configuration and validation
 */

import React from 'react';
import Card from '@/components/ui/Card';
import { Button } from '@/components/ui/shadcn/button';
import { Badge } from '@/components/ui/shadcn/badge';
import { Input } from '@/components/ui/shadcn/input';
import { Label } from '@/components/ui/label';
import {
  Play,
  Loader2,
  AlertCircle,
  CheckCircle,
  FileText,
  X,
} from 'lucide-react';
import type { PromptTemplate, PromptRunRequest } from '@/lib/ai-types';
import { cn } from '@/lib/utils';
import { useRunPrompt, useValidatePrompt } from '@/lib/ai-queries';
import { useToast } from '@/components/ui/shadcn/use-toast';

interface PromptExecutorProps {
  selectedTemplate: PromptTemplate | null;
  onClearTemplate: () => void;
  onSuccess?: () => void;
}

export function PromptExecutor({
  selectedTemplate,
  onClearTemplate,
  onSuccess,
}: PromptExecutorProps) {
  const [promptText, setPromptText] = React.useState('');
  const [context, setContext] = React.useState<Record<string, string>>({});
  const [model, setModel] = React.useState('gpt-4');
  const [temperature, setTemperature] = React.useState(0.7);
  const [maxTokens, setMaxTokens] = React.useState(2000);
  const [autoSave, setAutoSave] = React.useState(true);

  const { mutate: runPrompt, isPending: isRunning } = useRunPrompt();
  const { mutate: validatePrompt, isPending: isValidating, data: validationResult } = useValidatePrompt();
  const { toast } = useToast();

  React.useEffect(() => {
    if (selectedTemplate) {
      setPromptText(selectedTemplate.template);
    }
  }, [selectedTemplate]);

  const handleRun = () => {
    if (!selectedTemplate || !promptText.trim()) return;

    const request: PromptRunRequest = {
      template_id: selectedTemplate.id,
      context,
      prompt_override: promptText !== selectedTemplate.template ? promptText : undefined,
      model,
      temperature,
      max_tokens: maxTokens,
    };

    runPrompt(request, {
      onSuccess: (response) => {
        toast({
          title: 'Prompt executed successfully',
          description: `Job ${response.job_id} created`,
        });
        if (onSuccess) onSuccess();
      },
      onError: (error) => {
        toast({
          title: 'Failed to execute prompt',
          description: error.message,
          variant: 'destructive',
        });
      },
    });
  };

  const handleValidate = () => {
    if (!selectedTemplate || !promptText.trim()) return;

    const request: PromptRunRequest = {
      template_id: selectedTemplate.id,
      context,
      prompt_override: promptText !== selectedTemplate.template ? promptText : undefined,
      model,
      temperature,
      max_tokens: maxTokens,
    };

    validatePrompt(request);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Executor */}
      <div className="lg:col-span-2">
        <Card>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-text-primary">
                Execute Prompt
              </h2>
              {selectedTemplate && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleValidate}
                  disabled={isValidating}
                >
                  {isValidating ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    'Validate'
                  )}
                </Button>
              )}
            </div>

            {selectedTemplate ? (
              <div className="space-y-4">
                {/* Template Info */}
                <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <FileText className="w-4 h-4 text-primary" />
                        <span className="font-semibold text-text-primary">
                          {selectedTemplate.name}
                        </span>
                      </div>
                      <p className="text-sm text-text-muted">
                        {selectedTemplate.description}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={onClearTemplate}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="flex gap-2 mt-3">
                    {selectedTemplate.tags.slice(0, 3).map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="text-xs"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Validation Result */}
                {validationResult && (
                  <div className={cn(
                    "p-4 rounded-lg border flex items-start gap-3",
                    validationResult.is_valid
                      ? "bg-success/10 border-success/20"
                      : "bg-error/10 border-error/20"
                  )}>
                    {validationResult.is_valid ? (
                      <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className={cn(
                        "text-sm font-medium mb-1",
                        validationResult.is_valid ? "text-success" : "text-error"
                      )}>
                        {validationResult.is_valid ? 'Validation Passed' : 'Validation Failed'}
                      </p>
                      {validationResult.issues.length > 0 && (
                        <ul className="text-sm text-text-muted space-y-1">
                          {validationResult.issues.map((issue, i) => (
                            <li key={i}>• {issue}</li>
                          ))}
                        </ul>
                      )}
                      {validationResult.suggestions.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs font-medium text-text-secondary mb-1">
                            Suggestions:
                          </p>
                          <ul className="text-xs text-text-muted space-y-1">
                            {validationResult.suggestions.map((suggestion, i) => (
                              <li key={i}>• {suggestion}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Prompt Input */}
                <div>
                  <Label className="text-sm font-medium text-text-secondary mb-2">
                    Prompt Text
                  </Label>
                  <textarea
                    value={promptText}
                    onChange={(e) => setPromptText(e.target.value)}
                    className="w-full h-64 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:border-primary/50 font-mono text-sm resize-none"
                    placeholder="Enter your prompt or modify the template..."
                  />
                  <p className="text-xs text-text-muted mt-2">
                    Variables: Use {'{'}variable_name{'}'} syntax for dynamic values
                  </p>
                </div>

                {/* Context Variables */}
                {promptText.match(/\{([^}]+)\}/g)?.length > 0 && (
                  <div>
                    <Label className="text-sm font-medium text-text-secondary mb-2">
                      Context Variables
                    </Label>
                    <div className="space-y-2">
                      {Array.from(new Set(promptText.match(/\{([^}]+)\}/g))).map((match) => {
                        const varName = match.slice(1, -1);
                        return (
                          <div key={varName}>
                            <Label className="text-xs text-text-muted mb-1">
                              {varName}
                            </Label>
                            <Input
                              type="text"
                              value={context[varName] || ''}
                              onChange={(e) => setContext({ ...context, [varName]: e.target.value })}
                              placeholder={`Enter ${varName}...`}
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t border-white/5">
                  <Button
                    onClick={handleRun}
                    disabled={isRunning || !promptText.trim()}
                    className="flex-1"
                  >
                    {isRunning ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Run Prompt
                      </>
                    )}
                  </Button>
                  <Button variant="outline" disabled={isRunning}>
                    Save Draft
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 mx-auto text-text-muted mb-4" />
                <p className="text-lg text-text-secondary font-medium mb-2">
                  No Template Selected
                </p>
                <p className="text-sm text-text-muted">
                  Select a template from the library to get started
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Configuration Sidebar */}
      <div>
        <Card>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-text-primary">
              Configuration
            </h3>

            {/* Model Selection */}
            <div>
              <Label className="text-sm font-medium text-text-secondary mb-2">
                Model
              </Label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary/50"
                disabled={isRunning}
              >
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
              </select>
            </div>

            {/* Temperature */}
            <div>
              <Label className="text-sm font-medium text-text-secondary mb-2">
                Temperature: {temperature.toFixed(1)}
              </Label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full"
                disabled={isRunning}
              />
              <div className="flex justify-between text-xs text-text-muted mt-1">
                <span>Precise</span>
                <span>Creative</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div>
              <Label className="text-sm font-medium text-text-secondary mb-2">
                Max Tokens
              </Label>
              <Input
                type="number"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                min={100}
                max={8000}
                step={100}
                disabled={isRunning}
              />
            </div>

            {/* Auto-save Option */}
            <div className="pt-4 border-t border-white/10">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoSave}
                  onChange={(e) => setAutoSave(e.target.checked)}
                  className="w-4 h-4"
                  disabled={isRunning}
                />
                <span className="text-sm text-text-secondary">
                  Auto-save results to history
                </span>
              </label>
            </div>

            {/* Estimated Cost */}
            {selectedTemplate && (
              <div className="pt-4 border-t border-white/10">
                <p className="text-xs font-medium text-text-secondary mb-2">
                  Estimated Cost
                </p>
                <p className="text-2xl font-bold text-primary">
                  ~$0.02
                </p>
                <p className="text-xs text-text-muted mt-1">
                  Based on {model} pricing
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
