// API client for the ZomatoAI FastAPI backend hosted on Railway

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Preferences {
  location: string;
  budget: "low" | "medium" | "high";
  cuisine?: string;
  min_rating?: number;
  additional_preferences?: string;
  top_n?: number;
}

export interface RecommendationItem {
  rank: number;
  name: string;
  cuisine: string;
  rating: number | null;
  estimated_cost: number | null;
  explanation: string;
}

export interface RecommendationMeta {
  candidates_considered: number;
  filters_applied: string[];
}

export interface RecommendationResponse {
  query: Record<string, unknown>;
  summary: string;
  recommendations: RecommendationItem[];
  meta: RecommendationMeta;
}

export interface Stats {
  total_restaurants: number;
  total_locations: number;
}

export interface HealthStatus {
  status: string;
  groq_active: boolean;
  restaurants_loaded: number;
}

// ─── API calls ────────────────────────────────────────────────────────────────

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function getLocations(): Promise<string[]> {
  const res = await fetch(`${API_URL}/locations`, {
    next: { revalidate: 3600 }, // cache for 1 hour
  });
  if (!res.ok) throw new Error("Failed to fetch locations");
  const data = await res.json();
  return data.locations as string[];
}

export async function getStats(): Promise<Stats> {
  const res = await fetch(`${API_URL}/stats`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function getRecommendations(
  prefs: Preferences
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_URL}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prefs),
    cache: "no-store",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Recommendation request failed");
  }

  return res.json();
}
