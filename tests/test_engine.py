"""Unit tests for the Groq recommendation engine components."""

import pytest
from app.models.restaurant import Restaurant, BudgetTier
from app.engine.parser import ResponseParser, ParseError, ParsedGroqResponse
from app.engine.guard import HallucinationGuard
from app.engine.fallback import rank_by_rating

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

def test_parser_handles_fenced_json():
    """Verify that the parser correctly extracts JSON nested in markdown blocks."""
    fenced = """
    ```json
    {
      "summary": "These are recommendations.",
      "recommendations": [
        {
          "rank": 1,
          "restaurant_id": "r_1",
          "name": "Truffles",
          "explanation": "Great burgers."
        }
      ]
    }
    ```
    """
    result = ResponseParser.parse(fenced)
    assert result.summary == "These are recommendations."
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "r_1"

def test_parser_invalid_json():
    """Verify that malformed JSON raises a ParseError."""
    bad_json = '{"summary": "incomplete"'
    with pytest.raises(ParseError):
        ResponseParser.parse(bad_json)

def test_guard_rejects_hallucinations_and_merges():
    """Verify that the hallucination guard drops unknown restaurants and merges fields."""
    candidates = [
        make_restaurant("r_1", "Truffles", 4.6, BudgetTier.MEDIUM, ["American", "Cafe"]),
        make_restaurant("r_2", "Empire", 4.1, BudgetTier.MEDIUM, ["North Indian"]),
    ]
    
    # Mock LLM output that recommends:
    # 1. A valid restaurant (matching by ID)
    # 2. A hallucinated restaurant (which should be skipped)
    # 3. A valid restaurant with mismatched ID but matching name
    raw_response = {
        "summary": "Recommendations for you",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_id": "r_1",
                "name": "Truffles",
                "explanation": "Famous café."
            },
            {
                "rank": 2,
                "restaurant_id": "r_999",
                "name": "Ghost Kitchen",
                "explanation": "Does not exist."
            },
            {
                "rank": 3,
                "restaurant_id": "r_xyz",
                "name": "Empire",
                "explanation": "Late night food."
            }
        ]
    }
    
    parsed = ParsedGroqResponse(**raw_response)
    validated = HallucinationGuard.validate(parsed, candidates)
    
    # Ghost Kitchen should be dropped, leaving exactly 2 recommendations
    assert len(validated) == 2
    
    # Verify rank sorting and merging for Truffles
    assert validated[0].rank == 1
    assert validated[0].name == "Truffles"
    assert validated[0].cuisine == "American, Cafe"
    assert validated[0].rating == 4.6
    assert validated[0].explanation == "Famous café."
    
    # Verify rank sorting and merging for Empire (rank should shift to 2)
    assert validated[1].rank == 2
    assert validated[1].name == "Empire"
    assert validated[1].cuisine == "North Indian"
    assert validated[1].rating == 4.1
    assert validated[1].explanation == "Late night food."

def test_fallback_produces_correct_count():
    """Verify that rating fallback respects top_n limits and produces sequential ranks."""
    candidates = [
        make_restaurant("r_1", "A", 4.5, BudgetTier.MEDIUM, ["Italian"]),
        make_restaurant("r_2", "B", 4.0, BudgetTier.MEDIUM, ["Italian"]),
        make_restaurant("r_3", "C", 3.8, BudgetTier.MEDIUM, ["Italian"]),
    ]
    
    result = rank_by_rating(candidates, top_n=2)
    assert len(result) == 2
    assert result[0].rank == 1
    assert result[0].name == "A"
    assert result[1].rank == 2
    assert result[1].name == "B"
