"""Deterministic fallback ranking module."""

from typing import List
from app.models.restaurant import Restaurant
from app.models.recommendation import RecommendationItem

def rank_by_rating(candidates: List[Restaurant], top_n: int) -> List[RecommendationItem]:
    """Generates a ranked list of recommendations directly using rating sorting.

    Provides a template-based explanation for each restaurant. Used when LLM ranking fails.
    """
    sorted_candidates = sorted(
        candidates,
        key=lambda x: x.rating if x.rating is not None else -1.0,
        reverse=True
    )
    
    fallback_items = []
    for rank, r in enumerate(sorted_candidates[:top_n], start=1):
        cuisines_str = ", ".join(r.cuisines) if r.cuisines else "various cuisines"
        explanation = f"Highly-rated option in {r.location} serving {cuisines_str}."
        
        fallback_items.append(
            RecommendationItem(
                rank=rank,
                name=r.name,
                cuisine=cuisines_str,
                rating=r.rating,
                estimated_cost=r.cost_for_two,
                explanation=explanation
            )
        )
    return fallback_items
