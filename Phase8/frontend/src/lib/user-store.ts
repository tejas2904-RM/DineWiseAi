import type { PreferencePayload, RecommendationResponse } from './api';

export interface SavedSearch {
  id: string;
  timestamp: number;
  payload: PreferencePayload;
  result?: RecommendationResponse;
}

const SEARCHES_KEY = 'phase8-searches';

export function getRecentSearches(limit = 5): SavedSearch[] {
  if (typeof window === 'undefined') return [];
  const raw = localStorage.getItem(SEARCHES_KEY);
  if (!raw) return [];
  try {
    const searches: SavedSearch[] = JSON.parse(raw);
    return searches.sort((a, b) => b.timestamp - a.timestamp).slice(0, limit);
  } catch {
    return [];
  }
}

export function saveSearch(payload: PreferencePayload, result?: RecommendationResponse) {
  if (typeof window === 'undefined') return;
  const all = getRecentSearches(100);
  const entry: SavedSearch = {
    id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2),
    timestamp: Date.now(),
    payload,
    result,
  };
  // Deduplicate by location+cuisine+budget
  const filtered = all.filter(
    (s) =>
      s.payload.location !== payload.location ||
      s.payload.cuisine !== payload.cuisine ||
      s.payload.budget !== payload.budget,
  );
  filtered.unshift(entry);
  localStorage.setItem(SEARCHES_KEY, JSON.stringify(filtered.slice(0, 20)));
}
