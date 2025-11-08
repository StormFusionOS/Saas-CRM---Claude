/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Node Integration Card
 * Configure AI Node settings with React Hook Form + Zod validation
 */

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Wifi, WifiOff, Save, Loader2, Eye, EyeOff, Check, X } from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import { integrationsApi, type AINodeConfig } from '../../lib/integrations-api';
import { useToast } from '../ui/shadcn/use-toast';

// Zod validation schema
const aiNodeSchema = z.object({
  base_url: z
    .string()
    .url('Must be a valid URL')
    .refine((url) => url.startsWith('http://') || url.startsWith('https://'), {
      message: 'URL must start with http:// or https://',
    }),
  bearer_token: z
    .string()
    .optional()
    .refine((val) => !val || val.length >= 10, {
      message: 'Bearer token must be at least 10 characters',
    }),
  review_mode: z.boolean(),
});

type AINodeFormData = z.infer<typeof aiNodeSchema>;

const AINodeCard: React.FC = () => {
  const [config, setConfig] = useState<AINodeConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isPinging, setIsPinging] = useState(false);
  const [showToken, setShowToken] = useState(false);
  const [tokenChanged, setTokenChanged] = useState(false);
  const [lastPingResult, setLastPingResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
    watch,
    setValue,
  } = useForm<AINodeFormData>({
    resolver: zodResolver(aiNodeSchema),
    defaultValues: {
      base_url: '',
      bearer_token: '',
      review_mode: true,
    },
  });

  // Load initial config
  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setIsLoading(true);
      const data = await integrationsApi.getAINodeConfig();
      setConfig(data);

      // Reset form with loaded config
      reset({
        base_url: data.base_url || '',
        bearer_token: '', // Never populate - user must enter if changing
        review_mode: data.review_mode,
      });

      // Show last ping result if available
      if (data.last_ping_status) {
        setLastPingResult({
          success: data.last_ping_status === 'success',
          message:
            data.last_ping_status === 'success'
              ? `Connected (${data.last_ping_latency_ms}ms)`
              : 'Last ping failed',
        });
      }
    } catch (error: any) {
      console.error('Failed to load AI Node config:', error);
      toast({
        title: 'Error',
        description: 'Failed to load AI Node configuration',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = async (data: AINodeFormData) => {
    try {
      setIsSaving(true);

      // Optimistic update
      const optimisticConfig: AINodeConfig = {
        base_url: data.base_url,
        bearer_token_set: !!(data.bearer_token || config?.bearer_token_set),
        review_mode: data.review_mode,
        last_updated: new Date().toISOString(),
        last_ping_status: config?.last_ping_status || null,
        last_ping_latency_ms: config?.last_ping_latency_ms || null,
      };
      setConfig(optimisticConfig);

      // Prepare payload - only include bearer_token if it was changed
      const payload: any = {
        base_url: data.base_url,
        review_mode: data.review_mode,
      };

      if (data.bearer_token && data.bearer_token.trim() !== '') {
        payload.bearer_token = data.bearer_token;
      }

      // Save config
      const updatedConfig = await integrationsApi.updateAINodeConfig(payload);
      setConfig(updatedConfig);

      // Reset form to mark as clean
      reset({
        base_url: updatedConfig.base_url,
        bearer_token: '', // Clear token field
        review_mode: updatedConfig.review_mode,
      });
      setTokenChanged(false);

      toast({
        title: 'Success',
        description: 'AI Node configuration saved successfully',
      });
    } catch (error: any) {
      console.error('Failed to save AI Node config:', error);

      // Revert optimistic update
      await loadConfig();

      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Failed to save configuration',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    try {
      setIsPinging(true);
      setLastPingResult(null);

      const result = await integrationsApi.pingAINode();

      setLastPingResult({
        success: result.success,
        message: result.success
          ? `Connected (${result.latency_ms}ms)`
          : result.error_message || 'Connection failed',
      });

      toast({
        title: result.success ? 'Success' : 'Connection Failed',
        description: result.success
          ? `AI Node is responding (${result.latency_ms}ms)`
          : result.error_message || 'Failed to connect to AI Node',
        variant: result.success ? 'default' : 'destructive',
      });

      // Reload config to get updated ping stats
      await loadConfig();
    } catch (error: any) {
      console.error('Failed to ping AI Node:', error);

      setLastPingResult({
        success: false,
        message: 'Connection test failed',
      });

      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Failed to test connection',
        variant: 'destructive',
      });
    } finally {
      setIsPinging(false);
    }
  };

  const handleTokenChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTokenChanged(e.target.value.length > 0);
  };

  if (isLoading) {
    return (
      <Card padding="lg">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg">
      {/* Card Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-xl font-display font-bold text-text-primary mb-1">
            AI Node Integration
          </h3>
          <p className="text-sm text-text-muted">
            Configure connection to your AI Node service for automated SEO optimization
          </p>
        </div>

        {/* Connection Status Badge */}
        {lastPingResult && (
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${
              lastPingResult.success
                ? 'bg-success/20 text-success'
                : 'bg-error/20 text-error'
            }`}
          >
            {lastPingResult.success ? (
              <>
                <Wifi className="w-4 h-4" />
                {lastPingResult.message}
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4" />
                {lastPingResult.message}
              </>
            )}
          </div>
        )}
      </div>

      {/* Configuration Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* AI Base URL */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            AI Base URL <span className="text-error">*</span>
          </label>
          <input
            type="text"
            placeholder="https://ai-node.example.com"
            disabled={isSaving || isPinging}
            {...register('base_url')}
            className={`w-full px-4 py-2.5 bg-bg-base border rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50 disabled:cursor-not-allowed ${
              errors.base_url ? 'border-error' : 'border-white/10'
            }`}
          />
          {errors.base_url && (
            <p className="mt-1.5 text-sm text-error">{errors.base_url.message}</p>
          )}
          <p className="mt-1.5 text-xs text-text-muted">
            The base URL of your AI Node service (e.g., https://ai.yourdomain.com)
          </p>
        </div>

        {/* Bearer Token */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Bearer Token
            {config?.bearer_token_set && !tokenChanged && (
              <span className="ml-2 text-xs text-success">(Configured)</span>
            )}
          </label>
          <div className="relative">
            <input
              type={showToken ? 'text' : 'password'}
              placeholder={
                config?.bearer_token_set && !tokenChanged
                  ? '••••••••••••••••'
                  : 'Enter bearer token (optional)'
              }
              disabled={isSaving || isPinging}
              {...register('bearer_token')}
              onChange={handleTokenChange}
              className={`w-full px-4 py-2.5 pr-12 bg-bg-base border rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50 disabled:cursor-not-allowed ${
                errors.bearer_token ? 'border-error' : 'border-white/10'
              }`}
            />
            <button
              type="button"
              onClick={() => setShowToken(!showToken)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary transition-colors"
            >
              {showToken ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.bearer_token && (
            <p className="mt-1.5 text-sm text-error">{errors.bearer_token.message}</p>
          )}
          <p className="mt-1.5 text-xs text-text-muted">
            {config?.bearer_token_set && !tokenChanged
              ? 'Leave blank to keep existing token, or enter a new one to update'
              : 'Bearer token for authentication (minimum 10 characters)'}
          </p>
        </div>

        {/* Review Mode Toggle */}
        <div className="flex items-center justify-between p-4 bg-bg-base rounded-lg border border-white/10">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">
              Review Mode
            </label>
            <p className="text-xs text-text-muted">
              Require human review before applying AI-suggested changes
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              disabled={isSaving || isPinging}
              {...register('review_mode')}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-white/20 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 pt-4 border-t border-white/10">
          <Button
            type="button"
            variant="outline"
            onClick={handleTestConnection}
            disabled={
              isSaving ||
              isPinging ||
              !watch('base_url') ||
              !!errors.base_url
            }
            className="gap-2"
          >
            {isPinging ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Wifi className="w-4 h-4" />
                Test Connection
              </>
            )}
          </Button>

          <Button
            type="submit"
            variant="primary"
            disabled={isSaving || isPinging || !isDirty}
            className="gap-2"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Configuration
              </>
            )}
          </Button>

          {config?.last_updated && (
            <span className="ml-auto text-xs text-text-muted">
              Last updated: {new Date(config.last_updated).toLocaleString()}
            </span>
          )}
        </div>
      </form>
    </Card>
  );
};

export default AINodeCard;
