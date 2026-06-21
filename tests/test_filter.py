"""Unit tests for the preference filter."""

import pytest
from app.models.restaurant import Restaurant, BudgetTier
from app.models.user_input import UserPreferences
from app.integration.filter import PreferenceFilter

def make_restaurant(id_val: str, location: str, rating: float | None, budget_tier: BudgetTier, cuisines: list[str]) -> Restaurant:
    """Helper function to create a Restaurant model instance."""
    return Restaurant(
        id=id_val,
        name=f"Restaurant {id_val}",
        location=location,
        cuisines=cuisines,
        rating=rating,
        cost_for_two=1000 if budget_tier == BudgetTier.MEDIUM else (300 if budget_tier == BudgetTier.LOW else 2000),
        budget_tier=budget_tier,
        raw_metadata={}
    )

def test_location_filter():
    """Verify that the location filter reduces the restaurant set correctly."""
    restaurants = [
        make_restaurant("r1", "Bangalore", 4.0, BudgetTier.MEDIUM, ["Italian"]),
        make_restaurant("r2", "Delhi", 4.5, BudgetTier.MEDIUM, ["Italian"]),
        make_restaurant("r3", "Bangalore", 3.8, BudgetTier.MEDIUM, ["Indian"]),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetTier.MEDIUM,
        min_rating=3.5,
        cuisine=None,
        top_n=5
    )
    result = PreferenceFilter.apply(prefs, restaurants)
    assert len(result.candidates) == 2
    assert all(r.location == "Bangalore" for r in result.candidates)
    assert result.relaxed_filters is False

def test_cuisine_relaxation():
    """Verify that zero results triggers cuisine relaxation when other constraints match."""
    restaurants = [
        make_restaurant("r1", "Bangalore", 4.2, BudgetTier.MEDIUM, ["Indian"]),
        make_restaurant("r2", "Bangalore", 4.5, BudgetTier.MEDIUM, ["Chinese"]),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetTier.MEDIUM,
        min_rating=4.0,
        cuisine="Italian",
        top_n=5
    )
    result = PreferenceFilter.apply(prefs, restaurants)
    # The cuisine constraint was relaxed because no Italian restaurants exist in Bangalore,
    # returning Indian and Chinese restaurants instead.
    assert len(result.candidates) == 2
    assert result.relaxed_filters is True

def test_candidates_cap_and_sort():
    """Verify that >50 candidates are sorted by rating descending and capped to 50."""
    restaurants = []
    for i in range(60):
        # ratings range from 1.0 to 3.95
        rating = 1.0 + (i * 0.05)
        restaurants.append(
            make_restaurant(f"r{i}", "Bangalore", rating, BudgetTier.MEDIUM, ["Italian"])
        )
    
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetTier.MEDIUM,
        min_rating=1.0,
        cuisine="Italian",
        top_n=5
    )
    result = PreferenceFilter.apply(prefs, restaurants)
    
    # Cap should limit the results to 50
    assert len(result.candidates) == 50
    # First candidate should be the one with highest rating (r59)
    assert result.candidates[0].id == "r59"
    assert result.candidates[0].rating > result.candidates[1].rating
