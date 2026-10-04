/**
 * ALIMENTA GLOBAL — Unified REST & Data Ingestion Client
 * Handles live REST API requests, compiled JSON dataset fallbacks, caching, and retries.
 */

export interface ApiResponseEnvelope<T> {
  total: number;
  limit?: number;
  offset?: number;
  results: T[];
}

export interface ApiFetchOptions extends RequestInit {
  timeoutMs?: number;
  retries?: number;
  fallbackToStaticJson?: string; // e.g. '/data/reuses.json' if /api/v2/reuses fails
}

class ApiClient {
  private static instance: ApiClient;
  private cache: Map<string, { data: any; expiry: number }> = new Map();
  private readonly DEFAULT_CACHE_TTL_MS = 60 * 1000; // 1-minute TTL

  private constructor() {}

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  public async get<T>(url: string, options: ApiFetchOptions = {}): Promise<T> {
    const {
      timeoutMs = 8000,
      retries = 2,
      fallbackToStaticJson,
      ...fetchOptions
    } = options;

    // Check in-memory cache
    const cached = this.cache.get(url);
    if (cached && cached.expiry > Date.now()) {
      return cached.data as T;
    }

    let attempt = 0;
    while (attempt <= retries) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

        const response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            ...(fetchOptions.headers || {}),
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.cache.set(url, { data, expiry: Date.now() + this.DEFAULT_CACHE_TTL_MS });
        return data as T;
      } catch (err: any) {
        attempt++;
        if (attempt > retries) {
          if (fallbackToStaticJson) {
            console.warn(`[DATA INGESTION] REST API (${url}) unreachable. Falling back to static JSON: ${fallbackToStaticJson}`);
            const staticRes = await fetch(fallbackToStaticJson);
            if (staticRes.ok) {
              const staticData = await staticRes.json();
              return staticData as T;
            }
          }
          throw new Error(`API Request to ${url} failed after ${retries} retries: ${err.message}`);
        }
        // Exponential backoff
        await new Promise((r) => setTimeout(r, Math.pow(2, attempt) * 200));
      }
    }

    throw new Error(`Exhausted retries for ${url}`);
  }

  public invalidateCache(urlPattern?: string): void {
    if (!urlPattern) {
      this.cache.clear();
      return;
    }
    for (const key of this.cache.keys()) {
      if (key.includes(urlPattern)) {
        this.cache.delete(key);
      }
    }
  }
}

export const apiClient = ApiClient.getInstance();
