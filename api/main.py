"""ZomatoAI FastAPI backend.

Exposes the recommendation engine as a REST API to be consumed
by the Next.js frontend deployed on Vercel.
"""

from __future__ import annotations

import logging
import os
import threading
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
_startup_complete: bool = False
_startup_error: str | None = None


def _load_in_background() -> None:
    """Load the dataset in a background thread so the server starts immediately."""
    global _repo, _service, _startup_complete, _startup_error
    try:
        logger.info("🚀 Background: loading RestaurantRepository …")
        _repo = RestaurantRepository()
        _service = RecommendationService(_repo)
        logger.info("✅ Repository loaded — %d records.", len(_repo.get_all()))
    except Exception as exc:  # noqa: BLE001
        logger.exception("❌ Failed to load repository: %s", exc)
        _startup_error = str(exc)
    finally:
        _startup_complete = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Kick off background loading; tear down cleanly on shutdown."""
    t = threading.Thread(target=_load_in_background, daemon=True)
    t.start()
    logger.info("🚀 Server started — dataset loading in background thread.")
    yield
    logger.info("🛑 Shutdown: releasing resources.")
    global _repo, _service
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
    """Liveness probe used by Railway health-checks.

    Returns 200 immediately — even while the dataset is still loading —
    so Railway does not kill the deployment before it is ready.
    Once loading is complete the status reflects the real state.
    """
    if _startup_error:
        # Loading finished but with an error — still 200 so Railway keeps
        # the replica alive; operators can inspect via /health response body.
        return {
            "status": "degraded",
            "ready": False,
            "error": _startup_error,
            "groq_active": False,
            "restaurants_loaded": 0,
        }

    if not _startup_complete or _service is None:
        # Still initialising — return 200 so health check passes
        return {
            "status": "starting",
            "ready": False,
            "groq_active": False,
            "restaurants_loaded": 0,
        }

    return {
        "status": "ok",
        "ready": True,
        "groq_active": _service.groq_client is not None,
        "restaurants_loaded": len(_repo.get_all()) if _repo else 0,
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
