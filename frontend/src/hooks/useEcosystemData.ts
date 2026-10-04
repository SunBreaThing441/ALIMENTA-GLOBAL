/**
 * ALIMENTA GLOBAL — Data Integration Hooks
 * Connects frontend views to dynamic REST APIs (/api/v2/*) and compiled JSON datasets.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, ApiResponseEnvelope } from '../services/api.client';
import type { ReuseEntity, ScanPartyWorkshop, ScientificPublication } from '../types';

export interface PressReviewMention {
  id: string;
  date: string;
  source: string;
  title: string;
  link: string;
  type: 'article' | 'video' | 'podcast' | 'study';
  media_scope?: string;
  verbatim?: string;
}

export interface FaqItem {
  id: string;
  title: string;
  icon?: string;
  questions: {
    id: string;
    question: string;
    answer_html: string;
  }[];
}

// 1. Reuses Hook with dynamic search, pagination, and debounce
export function useReuses(searchQuery = '', limit = 12, page = 0) {
  const [data, setData] = useState<ApiResponseEnvelope<ReuseEntity> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReuses = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(page * limit),
      });
      if (searchQuery.trim()) {
        params.set('search', searchQuery.trim());
      }
      const result = await apiClient.get<ApiResponseEnvelope<ReuseEntity>>(
        `/api/v2/reuses?${params.toString()}`,
        { fallbackToStaticJson: '/data/reuses.json' }
      );
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load ecosystem reusers');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, limit, page]);

  useEffect(() => {
    fetchReuses();
  }, [fetchReuses]);

  return { data, loading, error, refetch: fetchReuses };
}

// 2. Press Review Hook with type and media scope filtering
export function usePressReview(typeFilter = '', searchQuery = '', limit = 10, page = 0) {
  const [data, setData] = useState<ApiResponseEnvelope<PressReviewMention> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPress = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(page * limit),
      });
      if (typeFilter && typeFilter !== 'all') {
        params.set('type', typeFilter);
      }
      if (searchQuery.trim()) {
        params.set('search', searchQuery.trim());
      }
      const result = await apiClient.get<ApiResponseEnvelope<PressReviewMention>>(
        `/api/v2/press?${params.toString()}`,
        { fallbackToStaticJson: '/data/press-review-merged.json' }
      );
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load press clippings');
    } finally {
      setLoading(false);
    }
  }, [typeFilter, searchQuery, limit, page]);

  useEffect(() => {
    fetchPress();
  }, [fetchPress]);

  return { data, loading, error, refetch: fetchPress };
}

// 3. Scan Parties & Civic Observatories Hook
export function useScanParties() {
  const [data, setData] = useState<ScanPartyWorkshop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScanParties = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.get<{ total: number; results: ScanPartyWorkshop[] }>(
        '/api/v2/scan-parties',
        { fallbackToStaticJson: '/data/scan_parties.json' }
      );
      setData(result.results || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load civic observatories');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchScanParties();
  }, [fetchScanParties]);

  return { data, loading, error, refetch: fetchScanParties };
}

// 4. Scientific Publications Hook
export function usePublications(limit = 12) {
  const [data, setData] = useState<ScientificPublication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPublications = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.get<{ total: number; results: ScientificPublication[] }>(
        `/api/v2/publications?limit=${limit}`,
        { fallbackToStaticJson: '/data/scientific_publications.json' }
      );
      setData(result.results || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load scientific publications');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchPublications();
  }, [fetchPublications]);

  return { data, loading, error, refetch: fetchPublications };
}

// 5. FAQ Knowledge Base Hook
export function useFaq(lang = 'en') {
  const [categories, setCategories] = useState<FaqItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFaq = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.get<Record<string, FaqItem[]>>(
        `/api/v2/faq?lang=${lang}`,
        { fallbackToStaticJson: '/data/faq.json' }
      );
      setCategories(result[lang] || result['en'] || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load FAQ knowledge base');
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    fetchFaq();
  }, [fetchFaq]);

  return { categories, loading, error, refetch: fetchFaq };
}
