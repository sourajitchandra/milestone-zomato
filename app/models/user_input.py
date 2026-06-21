"""User input and preferences data models."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.models.restaurant import BudgetTier

class UserPreferences(BaseModel):
    """Schema representing structured user recommendation preferences."""
    location: str = Field(..., description="Target location/city name")
    budget: BudgetTier = Field(..., description="Desired budget tier: low, medium, or high")
    cuisine: Optional[str] = Field(default=None, description="Preferred cuisine (optional)")
    min_rating: Optional[float] = Field(default=3.5, ge=0.0, le=5.0, description="Minimum rating required")
    additional_preferences: Optional[str] = Field(default=None, description="Additional free-text preferences")
    top_n: Optional[int] = Field(default=5, ge=1, le=10, description="Number of recommendations to return (1-10)")

    @field_validator("location")
    @classmethod
    def validate_location_non_empty(cls, v: str) -> str:
        """Ensures that the location string is not empty or pure whitespace."""
        val = v.strip()
        if not val:
            raise ValueError("Location cannot be empty")
        return val

def validate_location(location: str, known_locations: List[str]) -> str:
    """Validates the user location against list of known locations (case-insensitive).

    If valid, returns the matching known location (original casing).
    Otherwise, raises a ValueError with a helpful message.
    """
    cleaned_loc = location.strip().lower()
    for known in known_locations:
        if known.lower() == cleaned_loc:
            return known
            
    # Location not found - provide a helpful error message with a sample of locations
    sample_cities = ", ".join(known_locations[:5])
    suffix = f" (such as: {sample_cities}...)" if known_locations else ""
    raise ValueError(
        f"Location '{location}' is not found in our dataset. Please try a different location{suffix}."
    )
