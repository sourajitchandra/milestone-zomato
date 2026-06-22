"""ZomatoAI FastAPI backend.

Exposes the recommendation engine as a REST API to be consumed
by the Next.js frontend deployed on Vercel.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.data.repository import RestaurantRepository
from app.models.user_input import UserPreferences
from app.services.recommendation_service import RecommendationService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Allowed frontend origins — updated with your Vercel URL after first deploy
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",           # local Next.js dev server
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", ""),    # set in Railway env: https://your-app.vercel.app
]

# ---------------------------------------------------------------------------
# App-level singletons (created once at startup)
# ---------------------------------------------------------------------------
_repo: RestaurantRepository | None = None
_service: RecommendationService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the dataset once at startup; tear down cleanly on shutdown."""
    global _repo, _service
    logger.info("🚀 Startup: loading RestaurantRepository …")
    _repo = RestaurantRepository()
    _service = RecommendationService(_repo)
    logger.info("✅ Repository loaded — %d records.", len(_repo.get_all()))
    yield
    logger.info("🛑 Shutdown: releasing resources.")
    _repo = None
    _service = None


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ZomatoAI API",
    description="AI-powered restaurant recommendation service backed by Groq LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in ALLOWED_ORIGINS if o],  # drop empty strings
    allow_origin_regex=r"https://.*\.vercel\.app",     # allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------
def _get_service() -> RecommendationService:
    if _service is None:
        raise HTTPException(status_code=503, detail="Service not yet initialised.")
    return _service


def _get_repo() -> RestaurantRepository:
    if _repo is None:
        raise HTTPException(status_code=503, detail="Repository not yet initialised.")
    return _repo


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"])
def health() -> Dict[str, Any]:
    """Liveness probe used by Railway health-checks."""
    svc = _get_service()
    return {
        "status": "ok",
        "groq_active": svc.groq_client is not None,
        "restaurants_loaded": len(_get_repo().get_all()) if _repo else 0,
    }


@app.get("/locations", tags=["data"])
def get_locations() -> Dict[str, List[str]]:
    """Returns the sorted list of all unique restaurant locations in the dataset."""
    repo = _get_repo()
    return {"locations": repo.get_locations()}


@app.get("/stats", tags=["data"])
def get_stats() -> Dict[str, Any]:
    """Returns high-level dataset statistics (total restaurants, total locations)."""
    repo = _get_repo()
    return repo.get_stats()


@app.post("/recommend", tags=["recommend"])
def recommend(prefs: UserPreferences) -> Dict[str, Any]:
    """Core recommendation endpoint.

    Accepts user preferences and returns a ranked list of AI-generated
    restaurant recommendations.

    Request body (JSON):
        - location (str): Target locality, must match a value from /locations
        - budget (str): "low" | "medium" | "high"
        - cuisine (str | null): Optional cuisine filter
        - min_rating (float): Minimum rating threshold (0.0–5.0, default 3.5)
        - additional_preferences (str | null): Free-text hints for the LLM
        - top_n (int): Number of results to return (1–10, default 5)

    Returns:
        RecommendationResponse: Ranked list with AI-generated explanations.
    """
    svc = _get_service()
    try:
        result = svc.recommend(prefs)
        return result.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /recommend: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc
