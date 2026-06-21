"""Recommendation service orchestrator module."""

import time
import logging
from typing import Any, Dict
from app.models.user_input import UserPreferences, validate_location
from app.models.recommendation import RecommendationResponse, RecommendationMeta, RecommendationItem
from app.data.repository import RestaurantRepository
from app.integration.filter import PreferenceFilter
from app.integration.prompt_builder import PromptBuilder
from app.engine.groq_client import GroqClient
from app.engine.parser import ResponseParser
from app.engine.guard import HallucinationGuard
from app.engine.fallback import rank_by_rating

logger = logging.getLogger(__name__)

class RecommendationService:
    """Orchestrates the end-to-end flow from input preferences to ranked recommendations."""

    def __init__(self, repository: RestaurantRepository) -> None:
        """Initializes the service with a data repository and Groq API client."""
        self.repository = repository
        try:
            self.groq_client = GroqClient()
        except ValueError as e:
            logger.warning("GroqClient initialization warning: %s. Fallback mode will be active.", e)
            self.groq_client = None

    def recommend(self, prefs: UserPreferences) -> RecommendationResponse:
        """Runs the recommendation pipeline.

        Applies constraints, runs the LLM ranker, verifies outputs against grounding criteria,
        and defaults to deterministic ranking fallbacks if API limits or parsing failures occur.

        Args:
            prefs (UserPreferences): Validated user input preferences.

        Returns:
            RecommendationResponse: Clean structured DTO containing final ranked choices.
        """
        # 1. Validate location against repository city indexes
        try:
            standardized_location = validate_location(prefs.location, self.repository.get_locations())
            prefs.location = standardized_location
        except ValueError as e:
            logger.error("Location validation failed: %s", e)
            raise

        # 2. Retrieve base restaurants set
        restaurants = self.repository.get_all()

        # 3. Filter candidates by hard constraints
        filter_result = PreferenceFilter.apply(prefs, restaurants)
        candidate_count = len(filter_result.candidates)
        logger.info("Candidates considered after filtering: %d", candidate_count)

        # 4. Handle empty candidate pools early
        if candidate_count == 0:
            cuisine_note = f" for '{prefs.cuisine}'" if prefs.cuisine else ""
            summary = (
                f"We couldn't find any restaurants matching your budget/rating criteria in {prefs.location}{cuisine_note}. "
                "Try relaxing your filters (e.g. lowering minimum rating or widening your budget)."
            )
            return RecommendationResponse(
                query=prefs.model_dump(),
                summary=summary,
                recommendations=[],
                meta=RecommendationMeta(
                    candidates_considered=0,
                    filters_applied=filter_result.filters_applied
                )
            )

        # 5. Build prompt pairs
        system_prompt, user_prompt = PromptBuilder.build(prefs, filter_result.candidates)

        # 6. Execute recommendation pipeline
        recommendations = []
        summary = ""
        used_fallback = False
        fallback_reason = ""
        
        start_time = time.time()
        
        if self.groq_client is not None:
            try:
                # Call Groq API
                raw_response = self.groq_client.complete(system_prompt, user_prompt)
                
                # Parse JSON output
                parsed_response = ResponseParser.parse(raw_response)
                summary = parsed_response.summary
                
                # Filter through hallucination checks and merge data fields
                recommendations = HallucinationGuard.validate(parsed_response, filter_result.candidates)
                
                latency = time.time() - start_time
                logger.info("Groq recommendation engine call succeeded in %.2fs", latency)
                
                if not recommendations:
                    used_fallback = True
                    fallback_reason = "All recommended restaurants were hallucinated."
                    
            except Exception as e:
                logger.error("Groq recommendation pipeline failed: %s. Reverting to fallback.", e)
                used_fallback = True
                fallback_reason = str(e)
        else:
            used_fallback = True
            fallback_reason = "Groq API key not configured."

        # 7. Apply rating fallback if service execution failed
        if used_fallback:
            logger.info("Triggering deterministic fallback due to: %s", fallback_reason)
            top_n = prefs.top_n if prefs.top_n is not None else 5
            recommendations = rank_by_rating(filter_result.candidates, top_n)
            
            # Format fallback explanation header
            note_prefix = "AI ranking is temporarily unavailable (reason: {}). ".format(
                "API key missing" if "api key" in fallback_reason.lower() else "API error"
            )
            summary = note_prefix + f"Here are the top-rated {prefs.budget.value} budget restaurants in {prefs.location} sorted by rating."

        # 8. Assemble structured response
        return RecommendationResponse(
            query=prefs.model_dump(),
            summary=summary,
            recommendations=recommendations,
            meta=RecommendationMeta(
                candidates_considered=candidate_count,
                filters_applied=filter_result.filters_applied
            )
        )
