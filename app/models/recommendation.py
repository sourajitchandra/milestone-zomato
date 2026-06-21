"""Recommendation response data models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class RecommendationItem(BaseModel):
    """Ranked recommendation result entry."""
    rank: int = Field(..., ge=1, description="Rank position of the recommendation")
    name: str = Field(..., description="Restaurant name")
    cuisine: str = Field(..., description="Display string listing the cuisines")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Dine-in rating")
    estimated_cost: Optional[int] = Field(default=None, ge=0, description="Estimated cost for two people")
    explanation: str = Field(..., description="AI explanation of why this restaurant matches the user preferences")

class RecommendationMeta(BaseModel):
    """Metadata detailing candidate pool size and filters applied."""
    candidates_considered: int = Field(default=0, ge=0, description="Number of candidate restaurants after filtering")
    filters_applied: List[str] = Field(default_factory=list, description="List of fields filtered on")

class RecommendationResponse(BaseModel):
    """Encapsulated final recommendation response DTO."""
    query: Dict[str, Any] = Field(..., description="The original user preferences query details")
    summary: str = Field(..., description="AI-generated summary introducing the top choices")
    recommendations: List[RecommendationItem] = Field(default_factory=list, description="Ranked list of recommendation items")
    meta: RecommendationMeta = Field(..., description="Metadata on search matching execution")
