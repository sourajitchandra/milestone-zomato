"""Streamlit presentation layer — Desktop-first ZomatoAI UI (1440px).

Design based on stitch_zomatoai_restaurant_recommender/code.html:
 - Dark #0F1117 background
 - Fixed top navbar with Groq status badge
 - 30 / 70 two-column layout (sticky left preferences panel + scrollable results)
 - Glassmorphic recommendation cards in a 3-column grid
 - Crimson-to-coral gradient accents (Outfit font)
 - Staggered fade-up card animations
"""

import streamlit as st
import logging

from app.models.user_input import UserPreferences
from app.models.restaurant import BudgetTier
from app.data.repository import RestaurantRepository
from app.services.recommendation_service import RecommendationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZomatoAI — AI Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS (ported from Stitch design) ───────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    /* ── Reset & base ─────────────────────────────────── */
    html, body, [class*="css"], .stMarkdown, .stTextInput, .stSelectbox,
    .stSlider, .stTextArea, .stButton, .stForm, div, span, p, h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Kill Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; height: 0; }
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1440px !important;
        background: #0F1117;
    }
    body, .stApp { background: #0F1117 !important; color: #e2e2eb; }

    /* ── Fixed top navbar ─────────────────────────────── */
    .navbar {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 999;
        height: 64px;
        background: rgba(17,19,25,0.92);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
    }
    .navbar-logo {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #E23744 0%, #ff535a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    .navbar-tagline {
        font-size: 0.75rem;
        color: #9CA3AF;
        letter-spacing: 0.04em;
    }
    .groq-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #e2e2eb;
        text-transform: uppercase;
    }
    .groq-dot-active  { width:8px;height:8px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981; }
    .groq-dot-inactive{ width:8px;height:8px;border-radius:50%;background:#EF4444;box-shadow:0 0 6px #EF4444; }

    /* ── Glassmorphic panel ───────────────────────────── */
    .glass-panel {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        padding: 20px;
    }

    /* ── Left panel headings ──────────────────────────── */
    .panel-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e2eb;
        display: flex;
        align-items: center;
        gap: 8px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 16px;
    }
    .panel-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #9CA3AF;
        margin-bottom: 6px;
    }

    /* ── CTA Button ───────────────────────────────────── */
    div[data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        background: linear-gradient(135deg, #E23744 0%, #ff535a 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 0 !important;
        box-shadow: 0 8px 24px rgba(226,55,68,0.35) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        margin-top: 8px !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 12px 32px rgba(226,55,68,0.5) !important;
    }
    div[data-testid="stFormSubmitButton"] > button:active {
        transform: scale(0.98) !important;
    }

    /* ── Streamlit widget overrides ───────────────────── */
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stTextInput"] > div > div > input,
    div[data-testid="stTextArea"] > div > div > textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #e2e2eb !important;
        font-family: 'Outfit', sans-serif !important;
    }
    div[data-testid="stSelectbox"] > div > div:focus-within,
    div[data-testid="stTextInput"] > div > div > input:focus,
    div[data-testid="stTextArea"] > div > div > textarea:focus {
        border-color: rgba(226,55,68,0.6) !important;
        box-shadow: 0 0 0 2px rgba(226,55,68,0.25) !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {
        background: #E23744 !important;
        box-shadow: 0 0 8px rgba(226,55,68,0.5) !important;
    }
    label, .stSlider label, .stSelectbox label,
    .stTextInput label, .stTextArea label {
        color: #9CA3AF !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] [role="progressbar"] {
        background: rgba(226,55,68,0.4) !important;
    }
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 10px 14px;
    }
    div[data-testid="metric-container"] label { color: #9CA3AF !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #E23744 !important; font-weight: 700 !important;
    }

    /* ── Budget pill toggle ───────────────────────────── */
    .budget-row {
        display: flex;
        gap: 8px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 4px;
    }
    .budget-pill {
        flex: 1;
        padding: 8px 0;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
        transition: background 0.2s ease;
        color: #9CA3AF;
        border: none;
        background: transparent;
    }
    .budget-pill.active {
        background: linear-gradient(135deg,#E23744,#ff535a);
        color: #fff;
        box-shadow: 0 4px 14px rgba(226,55,68,0.35);
    }

    /* ── Preset chips ─────────────────────────────────── */
    .preset-chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:4px; }
    .preset-chip {
        padding: 5px 12px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        color: #9CA3AF;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .preset-chip:hover { border-color: rgba(226,55,68,0.5); color:#e2e2eb; }

    /* ── Stats section ────────────────────────────────── */
    .stats-row {
        display: flex;
        gap: 10px;
        margin-top: 12px;
    }
    .stat-chip {
        flex:1;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
    }
    .stat-chip-value { font-size:1.1rem;font-weight:700;color:#E23744; }
    .stat-chip-label { font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.05em; }

    /* ── AI Summary banner ────────────────────────────── */
    .ai-banner {
        display: flex;
        align-items: center;
        gap: 16px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-left: 4px solid #E23744;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .ai-banner-icon {
        width: 44px; height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg,#E23744,#ff535a);
        display:flex;align-items:center;justify-content:center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    .ai-banner-title { font-size:0.9rem;font-weight:700;color:#e2e2eb;margin-bottom:3px; }
    .ai-banner-text  { font-size:0.88rem;font-style:italic;color:#9CA3AF;line-height:1.45; }
    .ai-banner-meta  { font-size:0.72rem;color:#6B7280;margin-top:4px;letter-spacing:0.02em; }

    /* ── Restaurant cards ─────────────────────────────── */
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(3,1fr);
        gap: 16px;
    }
    .restaurant-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        overflow: hidden;
        opacity: 0;
        transform: translateY(20px);
        animation: fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) forwards;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .restaurant-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 0 30px -5px rgba(226,55,68,0.4);
        border-color: rgba(226,55,68,0.35);
    }
    @keyframes fadeUp {
        to { opacity:1; transform:translateY(0); }
    }
    .card-body { padding: 16px; }
    .card-top-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        gap: 8px;
    }
    .rank-badge {
        background: linear-gradient(135deg,#E23744,#ff535a);
        color: #fff;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 8px;
        flex-shrink: 0;
    }
    .restaurant-name {
        font-size: 1rem;
        font-weight: 700;
        color: #e2e2eb;
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .rating-pill {
        display: flex;
        align-items: center;
        gap: 3px;
        background: rgba(16,185,129,0.15);
        color: #10B981;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 4px 9px;
        border-radius: 8px;
        flex-shrink: 0;
    }
    .tags-row { display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px; }
    .cuisine-tag {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #FB7185;
        background: rgba(251,113,133,0.12);
        border: 1px solid rgba(251,113,133,0.25);
        padding: 3px 9px;
        border-radius: 6px;
    }
    .cost-tag {
        font-size: 0.72rem;
        font-weight: 600;
        color: #F59E0B;
        background: rgba(245,158,11,0.10);
        border: 1px solid rgba(245,158,11,0.20);
        padding: 3px 9px;
        border-radius: 6px;
    }
    .card-explanation {
        font-style: italic;
        font-size: 0.82rem;
        color: #9CA3AF;
        line-height: 1.5;
        border-left: 3px solid #E23744;
        padding: 6px 10px;
        border-radius: 0 6px 6px 0;
        background: rgba(226,55,68,0.05);
    }

    /* ── Empty state ──────────────────────────────────── */
    .empty-state {
        display:flex;flex-direction:column;align-items:center;
        justify-content:center;padding:60px 20px;text-align:center;
        color:#6B7280;
    }
    .empty-state-icon { font-size:3.5rem;margin-bottom:16px; }
    .empty-state-title { font-size:1.1rem;font-weight:700;color:#9CA3AF;margin-bottom:6px; }
    .empty-state-sub { font-size:0.85rem;color:#6B7280;max-width:320px;line-height:1.5; }

    /* ── Divider ──────────────────────────────────────── */
    hr { border:none; border-top:1px solid rgba(255,255,255,0.07); margin:16px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Cached backend ────────────────────────────────────────────────────────────
@st.cache_resource
def get_repository() -> RestaurantRepository:
    return RestaurantRepository()


@st.cache_resource
def get_service() -> RecommendationService:
    return RecommendationService(get_repository())


# ── Helpers ───────────────────────────────────────────────────────────────────
def _groq_status_html(active: bool) -> str:
    dot_cls = "groq-dot-active" if active else "groq-dot-inactive"
    status   = "Active" if active else "Unavailable"
    color    = "#10B981" if active else "#EF4444"
    return (
        f'<div class="groq-badge">'
        f'<div class="{dot_cls}"></div>'
        f'Groq: <span style="color:{color};margin-left:3px">{status}</span>'
        f'</div>'
    )


def _navbar_html(groq_active: bool) -> str:
    return f"""
    <div class="navbar">
      <div style="display:flex;align-items:center;gap:12px">
        <div class="navbar-logo">🍽️ ZomatoAI</div>
        <div class="navbar-tagline">AI-Powered · Groq LLM · Real Zomato Data</div>
      </div>
      {_groq_status_html(groq_active)}
    </div>
    """


def _card_html(rec, delay_s: float) -> str:
    rating_display = f"★ {rec.rating:.1f}" if rec.rating is not None else "★ N/A"
    cost_display   = f"₹{rec.estimated_cost:,} for two" if rec.estimated_cost is not None else "Cost N/A"

    # Split cuisines into individual tags
    cuisine_parts = [c.strip() for c in rec.cuisine.split(",") if c.strip()]
    cuisine_tags  = "".join(f'<span class="cuisine-tag">{c}</span>' for c in cuisine_parts[:3])

    return f"""
    <div class="restaurant-card" style="animation-delay:{delay_s:.1f}s">
      <div class="card-body">
        <div class="card-top-row">
          <span class="rank-badge">#{rec.rank}</span>
          <span class="restaurant-name">{rec.name}</span>
          <span class="rating-pill">{rating_display}</span>
        </div>
        <div class="tags-row">
          {cuisine_tags}
          <span class="cost-tag">💰 {cost_display}</span>
        </div>
        <div class="card-explanation">
          &ldquo;{rec.explanation}&rdquo;
        </div>
      </div>
    </div>
    """


def _ai_banner_html(summary: str, candidates: int, filters: list[str]) -> str:
    filters_str = ", ".join(filters) if filters else "none"
    return f"""
    <div class="ai-banner">
      <div class="ai-banner-icon">✨</div>
      <div>
        <div class="ai-banner-title">AI Recommendation Engine</div>
        <div class="ai-banner-text">{summary}</div>
        <div class="ai-banner-meta">
          {candidates} candidates considered &nbsp;·&nbsp; Filters: {filters_str}
        </div>
      </div>
    </div>
    """


def _empty_results_html(reason: str = "") -> str:
    sub = reason if reason else "Try lowering the minimum rating, changing your cuisine, or selecting a different location."
    return f"""
    <div class="empty-state">
      <div class="empty-state-icon">🍽️</div>
      <div class="empty-state-title">No restaurants found</div>
      <div class="empty-state-sub">{sub}</div>
    </div>
    """


def _initial_placeholder_html() -> str:
    return """
    <div class="empty-state">
      <div class="empty-state-icon">🔍</div>
      <div class="empty-state-title">Your AI recommendations will appear here</div>
      <div class="empty-state-sub">
        Fill in your preferences on the left and click
        <strong style="color:#E23744">Get AI Recommendations</strong>.
      </div>
    </div>
    """


def _stats_html(total: int, locations: int) -> str:
    return f"""
    <div class="stats-row">
      <div class="stat-chip">
        <div class="stat-chip-value">{total:,}</div>
        <div class="stat-chip-label">Restaurants</div>
      </div>
      <div class="stat-chip">
        <div class="stat-chip-value">{locations}</div>
        <div class="stat-chip-label">Localities</div>
      </div>
    </div>
    """


def _preset_chips_html() -> str:
    chips = [
        "🍕 Pizza · Indiranagar",
        "🍜 Chinese · Bellandur",
        "☕ Cafes · Koramangala",
        "🍔 Fast Food · BTM",
        "🌙 Late Night",
        "❤️ Date Night",
    ]
    chip_html = "".join(f'<span class="preset-chip">{c}</span>' for c in chips)
    return f'<div class="preset-chips">{chip_html}</div>'


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    # Load backend
    try:
        repo    = get_repository()
        service = get_service()
    except Exception as e:
        st.error(f"❌ Failed to initialise dataset: {e}")
        st.info("Check your internet connection or Hugging Face repository.")
        return

    stats        = repo.get_stats()
    locations    = repo.get_locations()
    groq_active  = service.groq_client is not None

    # ── Navbar ────────────────────────────────────────────────────────────────
    st.markdown(_navbar_html(groq_active), unsafe_allow_html=True)

    # ── Two-column layout: 30 % left panel / 70 % results ────────────────────
    left_col, right_col = st.columns([3, 7], gap="large")

    # ── LEFT PANEL ────────────────────────────────────────────────────────────
    with left_col:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-title">🎛️ Preferences</div>',
            unsafe_allow_html=True,
        )

        with st.form("preferences_form", border=False):

            # Location dropdown (populated from dataset)
            st.markdown('<div class="panel-label">📍 Target Locality</div>', unsafe_allow_html=True)
            location = st.selectbox(
                label="location_select",
                label_visibility="collapsed",
                options=locations,
                help="Select a neighbourhood from the Zomato dataset",
            )

            # Budget
            st.markdown('<div class="panel-label">💰 Budget Range</div>', unsafe_allow_html=True)
            budget_raw = st.selectbox(
                label="budget_select",
                label_visibility="collapsed",
                options=[tier.value for tier in BudgetTier],
                format_func=lambda x: {"low": "💰 Low  (< ₹500)", "medium": "💎 Medium  (₹500–₹1500)", "high": "🏆 High  (> ₹1500)"}[x],
                help="Low < ₹500 · Medium ₹500–₹1500 · High > ₹1500",
            )

            # Cuisine
            st.markdown('<div class="panel-label">🍽️ Cuisine (optional)</div>', unsafe_allow_html=True)
            cuisine = st.text_input(
                label="cuisine_input",
                label_visibility="collapsed",
                placeholder="e.g. Italian, Chinese, North Indian…",
                help="Leave blank for any cuisine. Partial match, case-insensitive.",
            )

            # Min Rating slider
            st.markdown('<div class="panel-label">⭐ Minimum Rating</div>', unsafe_allow_html=True)
            min_rating = st.slider(
                label="min_rating_slider",
                label_visibility="collapsed",
                min_value=0.0, max_value=5.0, value=3.5, step=0.1,
                help="Only show restaurants at or above this rating",
            )
            st.markdown(
                f'<div style="text-align:right;color:#E23744;font-weight:700;font-size:0.85rem;margin-top:-12px">'
                f'{min_rating:.1f}+ ⭐</div>',
                unsafe_allow_html=True,
            )

            # Top-N
            st.markdown('<div class="panel-label">🔢 Number of Results</div>', unsafe_allow_html=True)
            top_n = st.slider(
                label="top_n_slider",
                label_visibility="collapsed",
                min_value=1, max_value=10, value=5, step=1,
                help="How many restaurants to recommend (1–10)",
            )

            # Additional preferences
            st.markdown('<div class="panel-label">✨ AI Prompt Add-ons</div>', unsafe_allow_html=True)
            additional_preferences = st.text_area(
                label="extra_prefs",
                label_visibility="collapsed",
                placeholder="e.g. family-friendly, rooftop seating, quiet ambiance, good desserts…",
                height=90,
                help="Free-text hints passed directly to the Groq LLM for personalised ranking.",
            )

            # Submit
            submitted = st.form_submit_button(
                "✨ Get AI Recommendations",
                use_container_width=True,
            )

        # Dataset stats
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-label" style="margin-bottom:4px">📊 Dataset</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            _stats_html(stats["total_restaurants"], stats["total_locations"]),
            unsafe_allow_html=True,
        )

        # Preset chips
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-label" style="margin-bottom:6px">⚡ Quick Presets</div>',
            unsafe_allow_html=True,
        )
        st.markdown(_preset_chips_html(), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close glass-panel

    # ── RIGHT COLUMN ──────────────────────────────────────────────────────────
    with right_col:
        if not submitted:
            # Initial placeholder
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown(_initial_placeholder_html(), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            return

        # ── Build prefs & call service ────────────────────────────────────────
        prefs = UserPreferences(
            location=location,
            budget=BudgetTier(budget_raw),
            cuisine=cuisine.strip() if cuisine.strip() else None,
            min_rating=min_rating,
            additional_preferences=additional_preferences.strip() or None,
            top_n=top_n,
        )

        with st.spinner("🤖 Analyzing restaurants with Groq LLM…"):
            try:
                response = service.recommend(prefs)
            except ValueError as ve:
                st.error(f"❌ {ve}")
                return
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                logging.exception("Error during recommendation")
                return

        # ── Results ───────────────────────────────────────────────────────────
        if not response.recommendations:
            # No results state
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown(_empty_results_html(response.summary), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            return

        # AI Summary banner
        st.markdown(
            _ai_banner_html(
                response.summary,
                response.meta.candidates_considered,
                response.meta.filters_applied,
            ),
            unsafe_allow_html=True,
        )

        # If Groq fallback was triggered, show a warning strip
        if "AI ranking is temporarily unavailable" in response.summary:
            st.warning("⚠️ Groq AI ranking is unavailable — showing results sorted by rating instead.")

        # 3-column card grid
        cards_html = '<div class="cards-grid">'
        for i, rec in enumerate(response.recommendations):
            cards_html += _card_html(rec, delay_s=0.05 * (i + 1))
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
