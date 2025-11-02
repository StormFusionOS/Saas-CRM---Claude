/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
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

// Add response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

export const leadsAPI = {
  getLeadsBoard: async (statusFilter?: string) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const response = await apiClient.get('/leads', { params });
    return response.data;
  },

  getLead: async (leadId: number) => {
    const response = await apiClient.get(`/leads/${leadId}`);
    return response.data;
  },

  getLeadInteractions: async (leadId: number) => {
    const response = await apiClient.get(`/leads/${leadId}/interactions`);
    return response.data;
  },

  updateLeadStatus: async (leadId: number, status: string) => {
    const response = await apiClient.patch(`/leads/${leadId}/status`, { status });
    return response.data;
  },

  getUnassignedLeads: async (limit: number = 10) => {
    const response = await apiClient.get('/leads/unassigned', { params: { limit } });
    return response.data;
  },

  getFollowUpsDue: async () => {
    const response = await apiClient.get('/leads/follow-ups-due');
    return response.data;
  },

  assignLead: async (leadId: number, assignedToId: number) => {
    const response = await apiClient.patch(`/leads/${leadId}/assign`, { assigned_to_id: assignedToId });
    return response.data;
  },

  createInteraction: async (leadId: number, data: {
    contact_id: number;
    interaction_type: string;
    direction: string;
    subject?: string;
    body: string;
    metadata?: Record<string, any>;
  }) => {
    const response = await apiClient.post(`/leads/${leadId}/interactions`, data);
    return response.data;
  },
};

export const contactsAPI = {
  createContact: async (data: {
    email?: string;
    phone?: string;
    first_name?: string;
    last_name?: string;
    company?: string;
    title?: string;
    tags?: string[];
    custom_fields?: Record<string, any>;
  }) => {
    const response = await apiClient.post('/contacts', data);
    return response.data;
  },

  updateContact: async (contactId: number, data: any) => {
    const response = await apiClient.put(`/contacts/${contactId}`, data);
    return response.data;
  },

  deleteContact: async (contactId: number) => {
    await apiClient.delete(`/contacts/${contactId}`);
  },
};

export const pricebookAPI = {
  getPricebookItems: async (category?: string) => {
    const params = category ? { category } : {};
    const response = await apiClient.get('/pricebook', { params });
    return response.data;
  },

  getPricebookItem: async (itemId: number) => {
    const response = await apiClient.get(`/pricebook/${itemId}`);
    return response.data;
  },
};

export const estimatesAPI = {
  createQuote: async (data: {
    lead_id: number;
    service_ids: number[];
    inputs: Record<string, any>;
  }) => {
    const response = await apiClient.post('/estimates/quote', data);
    return response.data;
  },

  acceptEstimate: async (estimateId: number, selectedTier: string) => {
    const response = await apiClient.post(`/estimates/${estimateId}/accept`, {
      selected_tier: selectedTier,
    });
    return response.data;
  },

  getEstimate: async (estimateId: number) => {
    const response = await apiClient.get(`/estimates/${estimateId}`);
    return response.data;
  },
};

export default apiClient;
