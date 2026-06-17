const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '/api/v1';
const USER_ID_KEY = 'phase8-user-id';

export interface PreferencePayload {
  location: string;
  budget: string;
  cuisine: string;
  minRating: number;
  tags?: string[];
  topK?: number;
  userId?: string;
}

export interface RecommendationItem {
  rank: number;
  restaurantId: string;
  name: string;
  cuisine: string;
  rating: number;
  estimatedCost: number;
  reason: string;
}

export interface RecommendationResponse {
  requestId: string;
  recommendations: RecommendationItem[];
  summary?: string;
  usedFallback: boolean;
  latencyMs: number;
  fallbackReason?: string;
  circuitBreakerState?: string;
}

export interface UserProfile {
  userId: string;
  name: string;
  email?: string | null;
  createdAt: string;
}

export interface HistoryEntry {
  requestId: string;
  timestamp: string;
  userId: string;
  location: string;
  budget: string;
  cuisine: string;
  minRating: number;
  recommendations: RecommendationItem[];
}

export interface FavoriteItem {
  restaurantId: string;
  name: string;
  cuisine: string;
  rating: number;
  estimatedCost: number;
  addedAt: string;
}

const DEFAULT_API_KEY = 'phase7-demo-key';

export function getUserId(): string {
  if (typeof window === 'undefined') return 'anonymous';
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = 'user-' + Math.random().toString(36).slice(2, 10);
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}

function authHeaders(): Record<string, string> {
  const apiKey =
    (typeof window !== 'undefined' && localStorage.getItem('phase8-api-key')) ||
    DEFAULT_API_KEY;
  return {
    Authorization: `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  };
}

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, { ...init, headers: { ...authHeaders(), ...(init?.headers || {}) } });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}

// Recommendations ---------------------------------------------------------
export async function getRecommendations(payload: PreferencePayload): Promise<RecommendationResponse> {
  return jsonFetch<RecommendationResponse>(`${API_BASE}/recommendations`, {
    method: 'POST',
    body: JSON.stringify({ ...payload, userId: payload.userId || getUserId() }),
  });
}

// Locations --------------------------------------------------------------
export interface LocationsResponse {
  count: number;
  locations: string[];
}

export async function getLocations(): Promise<string[]> {
  const res = await jsonFetch<LocationsResponse>(`${API_BASE}/locations`);
  return res.locations;
}

// Cuisines ---------------------------------------------------------------
export interface CuisinesResponse {
  count: number;
  cuisines: string[];
}

export async function getCuisines(): Promise<string[]> {
  const res = await jsonFetch<CuisinesResponse>(`${API_BASE}/cuisines`);
  return res.cuisines;
}

// User --------------------------------------------------------------------
export async function getUserProfile(userId?: string): Promise<UserProfile> {
  const id = userId || getUserId();
  return jsonFetch<UserProfile>(`${API_BASE}/users/${id}`);
}

export async function updateUserProfile(name: string, email?: string): Promise<UserProfile> {
  const id = getUserId();
  return jsonFetch<UserProfile>(`${API_BASE}/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ name, email }),
  });
}

// History -----------------------------------------------------------------
export async function getHistory(limit = 20): Promise<HistoryEntry[]> {
  const id = getUserId();
  return jsonFetch<HistoryEntry[]>(`${API_BASE}/history?userId=${id}&limit=${limit}`);
}

// Favorites ---------------------------------------------------------------
export async function getFavorites(): Promise<FavoriteItem[]> {
  const id = getUserId();
  return jsonFetch<FavoriteItem[]>(`${API_BASE}/favorites?userId=${id}`);
}

export async function addFavorite(item: Omit<FavoriteItem, 'addedAt'>): Promise<FavoriteItem> {
  const id = getUserId();
  return jsonFetch<FavoriteItem>(`${API_BASE}/favorites`, {
    method: 'POST',
    body: JSON.stringify({ ...item, userId: id }),
  });
}

export async function removeFavorite(restaurantId: string): Promise<void> {
  const id = getUserId();
  await fetch(`${API_BASE}/favorites/${encodeURIComponent(restaurantId)}?userId=${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
}

// Feedback ----------------------------------------------------------------
export async function sendFeedback(requestId: string, restaurantId: string, helpful: boolean, comment?: string): Promise<void> {
  await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ requestId, restaurantId, helpful, comment, userId: getUserId() }),
  });
}
