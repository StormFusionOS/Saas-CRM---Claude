/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Scrape Suite API Client
 * Provides methods for interacting with Scrape Suite endpoints
 */

import apiClient from './api';

// ==============================================================================
// Types & Interfaces
// ==============================================================================

export interface JobTriggerRequest {
  type: 'serp' | 'crawl' | 'backlinks' | 'citations';
  payload: Record<string, any>;
}

export interface JobStatus {
  job_id: string;
  task_id: string | null;
  status: string;
  task_name: string | null;
  queued_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  items_processed: number;
  items_succeeded: number;
  items_failed: number;
  error_message: string | null;
  output_summary: Record<string, any> | null;
}

export interface SerpSnapshot {
  id: number;
  keyword_id: number;
  search_date: string;
  rank: number | null;
  url: string | null;
  featured_snippet: boolean;
  people_also_ask: boolean;
  local_pack: boolean;
  knowledge_panel: boolean;
  serp_features: string[];
  created_at: string | null;
}

export interface SerpResult {
  id: number;
  snapshot_id: number;
  rank: number;
  url: string;
  domain: string;
  title: string | null;
  snippet: string | null;
  is_ours: boolean;
  created_at: string | null;
}

export interface Competitor {
  id: number;
  domain: string;
  name: string;
  category: string | null;
  priority: string | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
  last_scraped: string | null;
}

export interface CompetitorPage {
  id: number;
  site_id: number;
  url: string;
  title: string | null;
  page_type: string | null;
  content_hash: string | null;
  status_code: number | null;
  first_seen: string | null;
  last_seen: string | null;
  last_modified: string | null;
  is_changed: boolean;
}

export interface Backlink {
  id: number;
  source_url: string;
  source_domain: string;
  target_url: string;
  anchor_text: string | null;
  is_dofollow: boolean;
  is_inbody: boolean;
  first_seen: string | null;
  last_seen: string | null;
  last_checked: string | null;
  is_lost: boolean;
}

export interface ReferringDomain {
  id: number;
  domain: string;
  backlink_count: number;
  inbody_link_count: number;
  authority_score: number | null;
  last_updated: string | null;
}

export interface Citation {
  id: number;
  platform: string;
  listing_url: string | null;
  is_listed: boolean;
  name_found: string | null;
  address_found: string | null;
  phone_found: string | null;
  nap_match: boolean;
  first_checked: string | null;
  last_checked: string | null;
}

export interface PageAuditIssue {
  id: number;
  audit_id: number;
  type: string;
  description: string | null;
  severity: string;
  fixed: boolean;
  fixed_date: string | null;
  created_at: string | null;
}

export interface PageAudit {
  id: number;
  page_url: string;
  audit_date: string;
  status_code: number | null;
  performance_proxy: Record<string, any> | null;
  issues_found: number;
  notes: string | null;
  created_at: string | null;
  issues: PageAuditIssue[];
}

export interface ScrapeSettings {
  review_mode: boolean;
  daily_serp_enabled: boolean;
  weekly_crawl_enabled: boolean;
  monthly_crawl_enabled: boolean;
  backlinks_refresh_days: number;
  citations_refresh_days: number;
  max_pages_per_crawl: number;
  proxy_pool_enabled: boolean;
}

export interface DashboardStats {
  serp_snapshots_count: number;
  competitors_tracked: number;
  pages_monitored: number;
  backlinks_count: number;
  citations_count: number;
  recent_changes: number;
  pending_reviews: number;
  last_serp_snapshot: string | null;
  last_competitor_crawl: string | null;
  last_backlinks_refresh: string | null;
}

// Keyword types
export interface Keyword {
  id: number;
  keyword_text: string;
  target_domain: string;
  target_page: string | null;
  search_volume: number | null;
  difficulty: number | null;
  intent: string | null;
  current_rank: number | null;
  previous_rank: number | null;
  best_rank: number | null;
  worst_rank: number | null;
  ctr: number | null;
  impressions: number;
  clicks: number;
  is_active: boolean;
  last_checked_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface KeywordCreate {
  keyword_text: string;
  target_domain: string;
  target_page?: string | null;
  intent?: string | null;
  search_volume?: number | null;
  difficulty?: number | null;
  is_active?: boolean;
}

export interface KeywordUpdate {
  keyword_text?: string;
  target_domain?: string;
  target_page?: string | null;
  intent?: string | null;
  search_volume?: number | null;
  difficulty?: number | null;
  is_active?: boolean;
}

// Paginated responses
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
}

export interface SerpSnapshotList extends PaginatedResponse<SerpSnapshot> {
  snapshots: SerpSnapshot[];
}

export interface SerpResultList {
  results: SerpResult[];
  snapshot_id: number;
  total: number;
}

export interface CompetitorList {
  competitors: Competitor[];
  total: number;
  page: number;
  page_size: number;
}

export interface CompetitorPageList extends PaginatedResponse<CompetitorPage> {
  pages: CompetitorPage[];
}

export interface BacklinkList extends PaginatedResponse<Backlink> {
  backlinks: Backlink[];
}

export interface ReferringDomainList {
  domains: ReferringDomain[];
  total: number;
}

export interface CitationList {
  citations: Citation[];
  total: number;
}

export interface PageAuditList extends PaginatedResponse<PageAudit> {
  audits: PageAudit[];
}

export interface KeywordList extends PaginatedResponse<Keyword> {
  keywords: Keyword[];
}

// ==============================================================================
// API Client Methods
// ==============================================================================

/**
 * Scrape Suite API client.
 * All methods return promises and handle auth automatically via apiClient.
 */
export const scrapeApi = {
  // ==========================================================================
  // Job Management
  // ==========================================================================

  /**
   * Trigger a scrape job manually.
   */
  async triggerJob(request: JobTriggerRequest): Promise<JobStatus> {
    const response = await apiClient.post('/scrape/jobs', request);
    return response.data;
  },

  /**
   * Get job status by ID.
   */
  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await apiClient.get(`/scrape/jobs/${jobId}`);
    return response.data;
  },

  // ==========================================================================
  // Keywords
  // ==========================================================================

  /**
   * Get list of tracked keywords.
   */
  async getKeywords(params?: {
    is_active?: boolean;
    intent?: string;
    page?: number;
    page_size?: number;
  }): Promise<KeywordList> {
    const response = await apiClient.get('/scrape/keywords', { params });
    return response.data;
  },

  /**
   * Create a new keyword.
   */
  async createKeyword(keyword: KeywordCreate): Promise<Keyword> {
    const response = await apiClient.post('/scrape/keywords', keyword);
    return response.data;
  },

  /**
   * Get keyword by ID.
   */
  async getKeyword(keywordId: number): Promise<Keyword> {
    const response = await apiClient.get(`/scrape/keywords/${keywordId}`);
    return response.data;
  },

  /**
   * Update keyword.
   */
  async updateKeyword(
    keywordId: number,
    update: KeywordUpdate
  ): Promise<Keyword> {
    const response = await apiClient.put(
      `/scrape/keywords/${keywordId}`,
      update
    );
    return response.data;
  },

  /**
   * Delete keyword.
   */
  async deleteKeyword(keywordId: number): Promise<void> {
    await apiClient.delete(`/scrape/keywords/${keywordId}`);
  },

  // ==========================================================================
  // SERP Snapshots & Results
  // ==========================================================================

  /**
   * Get SERP snapshots with filters and pagination.
   */
  async getSerpSnapshots(params?: {
    keyword_id?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<SerpSnapshotList> {
    const response = await apiClient.get('/scrape/serp/snapshots', { params });
    return response.data;
  },

  /**
   * Get SERP results for a specific snapshot.
   */
  async getSerpResults(snapshotId: number): Promise<SerpResultList> {
    const response = await apiClient.get('/scrape/serp/results', {
      params: { snapshot_id: snapshotId },
    });
    return response.data;
  },

  // ==========================================================================
  // Competitors
  // ==========================================================================

  /**
   * Get list of tracked competitors with pagination.
   */
  async getCompetitors(params?: {
    is_active?: boolean;
    category?: string;
    priority?: string;
    page?: number;
    page_size?: number;
  }): Promise<CompetitorList> {
    const response = await apiClient.get('/scrape/competitors', { params });
    return response.data;
  },

  /**
   * Create a new competitor to track.
   */
  async createCompetitor(competitor: {
    domain: string;
    name: string;
    category?: string | null;
    priority?: 'low' | 'medium' | 'high' | 'critical';
    is_active?: boolean;
  }): Promise<Competitor> {
    const response = await apiClient.post('/scrape/competitors', competitor);
    return response.data;
  },

  /**
   * Update a competitor's details.
   */
  async updateCompetitor(competitorId: number, updates: {
    name?: string;
    category?: string | null;
    priority?: 'low' | 'medium' | 'high' | 'critical';
    is_active?: boolean;
  }): Promise<Competitor> {
    const response = await apiClient.put(`/scrape/competitors/${competitorId}`, updates);
    return response.data;
  },

  /**
   * Delete a competitor.
   */
  async deleteCompetitor(competitorId: number): Promise<void> {
    await apiClient.delete(`/scrape/competitors/${competitorId}`);
  },

  /**
   * Get competitor pages with filters and pagination.
   */
  async getCompetitorPages(params?: {
    site_id?: number;
    changed_only?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<CompetitorPageList> {
    const response = await apiClient.get('/scrape/pages', { params });
    return response.data;
  },

  // ==========================================================================
  // Backlinks
  // ==========================================================================

  /**
   * Get backlinks with filters and pagination.
   */
  async getBacklinks(params?: {
    domain?: string;
    alive?: boolean;
    dofollow?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<BacklinkList> {
    const response = await apiClient.get('/scrape/backlinks', { params });
    return response.data;
  },

  /**
   * Get referring domains (aggregated backlink sources).
   */
  async getReferringDomains(params?: {
    min_authority?: number;
  }): Promise<ReferringDomainList> {
    const response = await apiClient.get('/scrape/referring-domains', {
      params,
    });
    return response.data;
  },

  // ==========================================================================
  // Citations
  // ==========================================================================

  /**
   * Get business citations.
   */
  async getCitations(params?: {
    listed?: boolean;
    nap_match?: boolean;
  }): Promise<CitationList> {
    const response = await apiClient.get('/scrape/citations', { params });
    return response.data;
  },

  // ==========================================================================
  // Page Audits
  // ==========================================================================

  /**
   * Get page audits with filters and pagination.
   */
  async getPageAudits(params?: {
    severity?: string;
    fixed?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PageAuditList> {
    const response = await apiClient.get('/scrape/audits', { params });
    return response.data;
  },

  // ==========================================================================
  // Settings
  // ==========================================================================

  /**
   * Get Scrape Suite settings.
   */
  async getSettings(): Promise<ScrapeSettings> {
    const response = await apiClient.get('/scrape/settings');
    return response.data;
  },

  /**
   * Update Scrape Suite settings.
   */
  async updateSettings(
    settings: Partial<ScrapeSettings>
  ): Promise<ScrapeSettings> {
    const response = await apiClient.put('/scrape/settings', settings);
    return response.data;
  },

  // ==========================================================================
  // Dashboard
  // ==========================================================================

  /**
   * Get dashboard statistics.
   */
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await apiClient.get('/scrape/dashboard');
    return response.data;
  },
};

export default scrapeApi;
