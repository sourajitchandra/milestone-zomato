"""JSON response parser module for LLM recommendations."""

import json
import re
import logging
from typing import List
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

class ParseError(Exception):
    """Exception raised when JSON decoding or validation fails."""
    pass

class RawRecommendationItem(BaseModel):
    """Temporary model representing recommendation items returned by the LLM."""
    rank: int = Field(..., ge=1)
    restaurant_id: str = Field(..., description="Target restaurant ID")
    name: str = Field(..., description="Target restaurant name")
    explanation: str = Field(..., description="AI explanation")

class ParsedGroqResponse(BaseModel):
    """Temporary model representing the full response structure returned by the LLM."""
    summary: str = Field(..., description="AI summary overview")
    recommendations: List[RawRecommendationItem] = Field(default_factory=list)

class ResponseParser:
    """Parses and validates raw LLM JSON completions."""

    @staticmethod
    def parse(raw_text: str) -> ParsedGroqResponse:
        """Strips markdown formatting, decodes JSON, and validates it against the schema.

        Args:
            raw_text (str): Raw string response from the LLM.

        Returns:
            ParsedGroqResponse: The structured parsed response.

        Raises:
            ParseError: If parsing or validation fails.
        """
        cleaned_text = raw_text.strip()
        
        # Strip markdown JSON fences (e.g. ```json ... ```)
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
            cleaned_text = cleaned_text.strip()
            
        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON from text: %s", cleaned_text[:200])
            raise ParseError(f"Invalid JSON format: {e}") from e
            
        try:
            return ParsedGroqResponse(**parsed_json)
        except ValidationError as e:
            logger.error("JSON schema validation failed: %s", e)
            raise ParseError(f"JSON schema mismatch: {e}") from e
