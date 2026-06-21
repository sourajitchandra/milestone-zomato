"""Restaurant data models."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BudgetTier(str, Enum):
    """Budget tiers for restaurant recommendations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Restaurant(BaseModel):
    """Canonical model representing a restaurant record."""
    id: str = Field(..., description="Unique stable restaurant identifier")
    name: str = Field(..., description="Name of the restaurant")
    location: str = Field(..., description="Normalized city or locality name")
    cuisines: List[str] = Field(default_factory=list, description="List of cuisines served")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Dine-in rating out of 5")
    cost_for_two: Optional[int] = Field(default=None, ge=0, description="Approximate cost for two people")
    budget_tier: BudgetTier = Field(..., description="Budget tier derived from cost")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional uncleaned metadata fields")
