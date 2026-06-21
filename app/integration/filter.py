"""Preference filter module for hard constraints filtering."""

from typing import List
from pydantic import BaseModel, Field
from app.config import get_settings
from app.models.restaurant import Restaurant
from app.models.user_input import UserPreferences

class FilterResult(BaseModel):
    """Result of the filtering phase containing candidates and metadata."""
    candidates: List[Restaurant] = Field(..., description="Filtered candidate restaurants")
    filters_applied: List[str] = Field(..., description="Fields that filters were applied to")
    relaxed_filters: bool = Field(..., description="True if cuisine filter was relaxed due to 0 results")

class PreferenceFilter:
    """Applies hard constraints to filter the raw restaurant set."""

    @staticmethod
    def apply(prefs: UserPreferences, restaurants: List[Restaurant]) -> FilterResult:
        """Applies location, rating, budget, and cuisine filters sequentially.

        Sorts candidates by rating descending and caps the results at MAX_CANDIDATES.
        If cuisine filter results in 0 candidates, it relaxes the cuisine filter.
        """
        settings = get_settings()
        max_candidates = settings.max_candidates
        
        filters_applied = ["location", "budget"]
        
        # 1. Location Filter (Required, case-insensitive exact match)
        candidates = [
            r for r in restaurants
            if r.location.lower() == prefs.location.lower()
        ]
        
        # 2. Min Rating Filter (Optional, rating >= min_rating, skip null ratings)
        if prefs.min_rating is not None:
            candidates = [
                r for r in candidates
                if r.rating is not None and r.rating >= prefs.min_rating
            ]
            filters_applied.append("min_rating")
            
        # 3. Budget Tier Filter (Required, exact match)
        candidates = [
            r for r in candidates
            if r.budget_tier == prefs.budget
        ]
        
        # 4. Cuisine Filter (Optional, partial match)
        cuisine_candidates = candidates
        relaxed_filters = False
        
        if prefs.cuisine:
            filters_applied.append("cuisine")
            cuisine_lower = prefs.cuisine.strip().lower()
            cuisine_candidates = [
                r for r in candidates
                if any(cuisine_lower in c.lower() for c in r.cuisines)
            ]
            
            # Zero results fallback: relax cuisine if it was the reason candidates became empty
            if not cuisine_candidates and candidates:
                cuisine_candidates = candidates
                relaxed_filters = True
                
        # Sort by rating descending (safe sort handling any potential None ratings)
        sorted_candidates = sorted(
            cuisine_candidates,
            key=lambda x: x.rating if x.rating is not None else -1.0,
            reverse=True
        )
        
        # Cap results at MAX_CANDIDATES
        final_candidates = sorted_candidates[:max_candidates]
        
        return FilterResult(
            candidates=final_candidates,
            filters_applied=filters_applied,
            relaxed_filters=relaxed_filters
        )
