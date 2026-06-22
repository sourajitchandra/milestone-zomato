"use client";

import { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import RestaurantCard from "@/components/RestaurantCard";
import AIBanner from "@/components/AIBanner";
import EmptyState, { LoadingState } from "@/components/EmptyState";
import {
  getHealth,
  getLocations,
  getStats,
  getRecommendations,
  type Preferences,
  type RecommendationResponse,
  type Stats,
} from "@/lib/api";

// ─── Preset definitions ───────────────────────────────────────────────────────
const PRESETS = [
  { label: "🍕 Pizza · Indiranagar", location: "Indiranagar", cuisine: "Pizza" },
  { label: "🍜 Chinese · Bellandur", location: "Bellandur", cuisine: "Chinese" },
  { label: "☕ Cafes · Koramangala", location: "Koramangala", cuisine: "Cafe" },
  { label: "🍔 Fast Food · BTM", location: "BTM", cuisine: "Fast Food" },
  { label: "🌙 Late Night", location: "", cuisine: "" },
  { label: "❤️ Date Night", location: "", cuisine: "", extra: "romantic, fine dining, quiet" },
];

const BUDGET_OPTIONS = [
  { value: "low", label: "💰 Low", sub: "< ₹500" },
  { value: "medium", label: "💎 Medium", sub: "₹500–₹1500" },
  { value: "high", label: "🏆 High", sub: "> ₹1500" },
] as const;

type BudgetTier = "low" | "medium" | "high";

// ─── App page ─────────────────────────────────────────────────────────────────
export default function Home() {
  // Metadata state
  const [groqActive, setGroqActive] = useState(false);
  const [locations, setLocations] = useState<string[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [metaError, setMetaError] = useState("");

  // Form state
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState<BudgetTier>("medium");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState(3.5);
  const [topN, setTopN] = useState(5);
  const [additionalPrefs, setAdditionalPrefs] = useState("");

  // Results state
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  // ── Load metadata on mount ──────────────────────────────────────────────────
  useEffect(() => {
    async function loadMeta() {
      try {
        const [health, locs, st] = await Promise.all([
          getHealth(),
          getLocations(),
          getStats(),
        ]);
        setGroqActive(health.groq_active);
        setLocations(locs);
        setStats(st);
        if (locs.length > 0) setLocation(locs[0]);
      } catch {
        setMetaError("Could not connect to the backend. Is Railway deployed?");
      }
    }
    loadMeta();
  }, []);

  // ── Submit handler ──────────────────────────────────────────────────────────
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!location) return;

      setLoading(true);
      setError("");
      setResult(null);
      setSubmitted(true);

      const prefs: Preferences = {
        location,
        budget,
        cuisine: cuisine.trim() || undefined,
        min_rating: minRating,
        additional_preferences: additionalPrefs.trim() || undefined,
        top_n: topN,
      };

      try {
        const data = await getRecommendations(prefs);
        setResult(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Something went wrong.");
      } finally {
        setLoading(false);
      }
    },
    [location, budget, cuisine, minRating, additionalPrefs, topN]
  );

  // ── Apply a quick preset ────────────────────────────────────────────────────
  const applyPreset = (preset: (typeof PRESETS)[number]) => {
    if (preset.location && locations.includes(preset.location)) {
      setLocation(preset.location);
    }
    if (preset.cuisine) setCuisine(preset.cuisine);
    if ("extra" in preset && preset.extra) setAdditionalPrefs(preset.extra);
  };

  // ─── Render ─────────────────────────────────────────────────────────────────
  const isFallback = result?.summary.includes("AI ranking is temporarily unavailable");

  return (
    <>
      <Navbar groqActive={groqActive} />

      <main className="app-layout">
        {/* ── LEFT PANEL ── */}
        <aside className="left-panel" aria-label="Preferences">
          <div className="glass-panel">
            <div className="panel-title">🎛️ Preferences</div>

            {metaError && (
              <div className="error-banner" role="alert">
                ⚠️ {metaError}
              </div>
            )}

            <form id="preferences-form" onSubmit={handleSubmit} noValidate>
              {/* Location */}
              <div className="panel-label">📍 Target Locality</div>
              <div className="select-wrapper">
                <select
                  id="location-select"
                  className="form-select"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  required
                  aria-label="Select location"
                >
                  {locations.length === 0 && (
                    <option value="">Loading locations…</option>
                  )}
                  {locations.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))}
                </select>
              </div>

              {/* Budget */}
              <div className="panel-label">💰 Budget Range</div>
              <div className="budget-row" role="group" aria-label="Budget tier">
                {BUDGET_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    id={`budget-${opt.value}`}
                    className={`budget-pill${budget === opt.value ? " active" : ""}`}
                    onClick={() => setBudget(opt.value)}
                    aria-pressed={budget === opt.value}
                  >
                    {opt.label}
                    <br />
                    <span style={{ fontSize: "0.65rem", opacity: 0.7 }}>{opt.sub}</span>
                  </button>
                ))}
              </div>

              {/* Cuisine */}
              <div className="panel-label">🍽️ Cuisine (optional)</div>
              <input
                id="cuisine-input"
                type="text"
                className="form-input"
                placeholder="e.g. Italian, Chinese, North Indian…"
                value={cuisine}
                onChange={(e) => setCuisine(e.target.value)}
                aria-label="Cuisine preference"
              />

              {/* Min Rating */}
              <div className="panel-label">⭐ Minimum Rating</div>
              <div className="slider-wrapper">
                <input
                  id="min-rating-slider"
                  type="range"
                  className="form-slider"
                  min={0}
                  max={5}
                  step={0.1}
                  value={minRating}
                  onChange={(e) => setMinRating(parseFloat(e.target.value))}
                  aria-label={`Minimum rating: ${minRating.toFixed(1)}`}
                />
                <div className="slider-value">{minRating.toFixed(1)}+ ⭐</div>
              </div>

              {/* Top N */}
              <div className="panel-label">🔢 Number of Results</div>
              <div className="slider-wrapper">
                <input
                  id="top-n-slider"
                  type="range"
                  className="form-slider"
                  min={1}
                  max={10}
                  step={1}
                  value={topN}
                  onChange={(e) => setTopN(parseInt(e.target.value, 10))}
                  aria-label={`Number of results: ${topN}`}
                />
                <div className="slider-value">{topN} restaurants</div>
              </div>

              {/* Additional prefs */}
              <div className="panel-label">✨ AI Prompt Add-ons</div>
              <textarea
                id="additional-prefs"
                className="form-textarea"
                placeholder="e.g. family-friendly, rooftop seating, quiet ambiance, good desserts…"
                value={additionalPrefs}
                onChange={(e) => setAdditionalPrefs(e.target.value)}
                aria-label="Additional preferences for AI"
              />

              <button
                id="submit-recommendations"
                type="submit"
                className="cta-button"
                disabled={loading || locations.length === 0}
              >
                {loading ? "⏳ Finding restaurants…" : "✨ Get AI Recommendations"}
              </button>
            </form>

            <hr className="divider" />

            {/* Dataset stats */}
            <div className="panel-label" style={{ marginBottom: "4px" }}>
              📊 Dataset
            </div>
            {stats ? (
              <div className="stats-row">
                <div className="stat-chip">
                  <div className="stat-chip-value">
                    {stats.total_restaurants.toLocaleString("en-IN")}
                  </div>
                  <div className="stat-chip-label">Restaurants</div>
                </div>
                <div className="stat-chip">
                  <div className="stat-chip-value">{stats.total_locations}</div>
                  <div className="stat-chip-label">Localities</div>
                </div>
              </div>
            ) : (
              <div style={{ color: "var(--text-faint)", fontSize: "0.8rem" }}>
                Loading…
              </div>
            )}

            <hr className="divider" />

            {/* Quick presets */}
            <div className="panel-label" style={{ marginBottom: "6px" }}>
              ⚡ Quick Presets
            </div>
            <div className="preset-chips" role="list">
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  type="button"
                  className="preset-chip"
                  role="listitem"
                  onClick={() => applyPreset(p)}
                  aria-label={`Apply preset: ${p.label}`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* ── RIGHT COLUMN ── */}
        <section aria-label="Recommendations" aria-live="polite">
          {/* Placeholder before first submit */}
          {!submitted && (
            <div className="glass-panel">
              <EmptyState
                icon="🔍"
                title="Your AI recommendations will appear here"
                subtitle='Fill in your preferences on the left and click "Get AI Recommendations".'
              />
            </div>
          )}

          {/* Loading */}
          {submitted && loading && (
            <div className="glass-panel">
              <LoadingState />
            </div>
          )}

          {/* Error */}
          {submitted && !loading && error && (
            <div className="glass-panel">
              <div className="error-banner" role="alert">
                ❌ {error}
              </div>
              <EmptyState
                icon="😕"
                title="Something went wrong"
                subtitle="Check your backend connection or try again with different filters."
              />
            </div>
          )}

          {/* Results */}
          {submitted && !loading && result && (
            <>
              {/* Fallback warning */}
              {isFallback && (
                <div className="warning-banner" role="alert">
                  ⚠️ Groq AI ranking is unavailable — showing results sorted by
                  rating instead.
                </div>
              )}

              {/* AI summary banner */}
              {result.recommendations.length > 0 && (
                <AIBanner
                  summary={result.summary}
                  candidatesConsidered={result.meta.candidates_considered}
                  filtersApplied={result.meta.filters_applied}
                />
              )}

              {/* No results */}
              {result.recommendations.length === 0 && (
                <div className="glass-panel">
                  <EmptyState
                    icon="🍽️"
                    title="No restaurants found"
                    subtitle={
                      result.summary ||
                      "Try lowering the minimum rating, changing your cuisine, or selecting a different location."
                    }
                  />
                </div>
              )}

              {/* Cards grid */}
              {result.recommendations.length > 0 && (
                <div className="cards-grid">
                  {result.recommendations.map((rec, i) => (
                    <RestaurantCard key={rec.rank} rec={rec} delayIndex={i} />
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </>
  );
}
