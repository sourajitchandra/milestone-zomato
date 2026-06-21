"""Integration tests for the recommendation service orchestrator."""

import pytest
from unittest.mock import MagicMock, patch
from app.models.user_input import UserPreferences
from app.models.restaurant import Restaurant, BudgetTier
from app.models.recommendation import RecommendationResponse
from app.data.repository import RestaurantRepository
from app.services.recommendation_service import RecommendationService

def make_restaurant(id_val: str, name: str, rating: float, budget_tier: BudgetTier, cuisines: list[str]) -> Restaurant:
    """Helper function to create a Restaurant model instance."""
    return Restaurant(
        id=id_val,
        name=name,
        location="Indiranagar",
        cuisines=cuisines,
        rating=rating,
        cost_for_two=500,
        budget_tier=budget_tier,
        raw_metadata={}
    )

@pytest.fixture
def mock_repo():
    """Fixture providing a mocked RestaurantRepository."""
    repo = MagicMock(spec=RestaurantRepository)
    repo.get_locations.return_value = ["Indiranagar", "Bellandur"]
    repo.get_all.return_value = [
        make_restaurant("r_1", "Truffles", 4.6, BudgetTier.MEDIUM, ["American", "Cafe"]),
        make_restaurant("r_2", "Empire", 4.1, BudgetTier.MEDIUM, ["North Indian"]),
        make_restaurant("r_3", "Corner House", 4.7, BudgetTier.LOW, ["Desserts"]),
    ]
    return repo

@patch("app.services.recommendation_service.GroqClient")
def test_recommendation_pipeline_success(mock_groq_class, mock_repo):
    """Verify that the service successfully runs the pipeline with a valid LLM response."""
    # Mock GroqClient complete output
    mock_groq_instance = MagicMock()
    mock_groq_instance.complete.return_value = """
    {
      "summary": "AI selected cafes matching your taste.",
      "recommendations": [
        {
          "rank": 1,
          "restaurant_id": "r_1",
          "name": "Truffles",
          "explanation": "Top burger joint."
        }
      ]
    }
    """
    mock_groq_class.return_value = mock_groq_instance
    
    service = RecommendationService(mock_repo)
    
    prefs = UserPreferences(
        location="Indiranagar",
        budget=BudgetTier.MEDIUM,
        cuisine="Cafe",
        min_rating=4.0,
        top_n=3
    )
    
    response = service.recommend(prefs)
    
    assert isinstance(response, RecommendationResponse)
    assert response.summary == "AI selected cafes matching your taste."
    assert len(response.recommendations) == 1
    assert response.recommendations[0].name == "Truffles"
    assert response.recommendations[0].cuisine == "American, Cafe"
    assert response.meta.candidates_considered == 1
    assert "location" in response.meta.filters_applied

@patch("app.services.recommendation_service.GroqClient")
def test_recommendation_pipeline_empty_candidates(mock_groq_class, mock_repo):
    """Verify that queries matching zero candidates return empty results gracefully."""
    service = RecommendationService(mock_repo)
    
    prefs = UserPreferences(
        location="Indiranagar",
        budget=BudgetTier.HIGH,  # No High tier in mock repo
        cuisine="Cafe",
        min_rating=4.0,
        top_n=3
    )
    
    response = service.recommend(prefs)
    assert len(response.recommendations) == 0
    assert "couldn't find any restaurants" in response.summary
    assert response.meta.candidates_considered == 0

@patch("app.services.recommendation_service.GroqClient")
def test_recommendation_pipeline_fallback_on_error(mock_groq_class, mock_repo):
    """Verify that exceptions in the LLM pipeline trigger rating fallback recommendations."""
    # Mock GroqClient to fail
    mock_groq_instance = MagicMock()
    mock_groq_instance.complete.side_effect = Exception("Groq API error")
    mock_groq_class.return_value = mock_groq_instance
    
    service = RecommendationService(mock_repo)
    
    prefs = UserPreferences(
        location="Indiranagar",
        budget=BudgetTier.MEDIUM,
        cuisine=None,
        min_rating=4.0,
        top_n=2
    )
    
    response = service.recommend(prefs)
    
    # Check that fallback is triggered and populates recommendations sorted by rating
    assert len(response.recommendations) == 2
    assert "AI ranking is temporarily unavailable" in response.summary
    assert response.recommendations[0].name == "Truffles"
    assert response.recommendations[1].name == "Empire"
