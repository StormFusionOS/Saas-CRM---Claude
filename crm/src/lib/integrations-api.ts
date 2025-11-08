/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Integrations API Client
 * API calls for admin integration settings (AI Node, etc.)
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_CRM_API_URL ?? 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export interface AINodeConfig {
  base_url: string;
  bearer_token_set: boolean;
  review_mode: boolean;
  last_updated: string | null;
  last_ping_status: string | null;
  last_ping_latency_ms: number | null;
}

export interface AINodeConfigUpdate {
  base_url: string;
  bearer_token?: string; // Optional - only send if changing
  review_mode: boolean;
}

export interface PingResponse {
  success: boolean;
  status_code: number | null;
  latency_ms: number | null;
  error_message: string | null;
  timestamp: string;
}

export const integrationsApi = {
  /**
   * Get AI Node configuration
   */
  getAINodeConfig: async (): Promise<AINodeConfig> => {
    const response = await apiClient.get('/admin/integrations/ai-node/config');
    return response.data;
  },

  /**
   * Update AI Node configuration
   */
  updateAINodeConfig: async (config: AINodeConfigUpdate): Promise<AINodeConfig> => {
    const response = await apiClient.post('/admin/integrations/ai-node/config', config);
    return response.data;
  },

  /**
   * Test connection to AI Node (ping)
   */
  pingAINode: async (): Promise<PingResponse> => {
    const response = await apiClient.post('/admin/integrations/ai-node/ping');
    return response.data;
  },
};
