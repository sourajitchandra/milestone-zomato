"""Hallucination guard module to validate and ground LLM outputs."""

from typing import Dict, List
import logging
from app.models.restaurant import Restaurant
from app.models.recommendation import RecommendationItem
from app.engine.parser import ParsedGroqResponse

logger = logging.getLogger(__name__)

class HallucinationGuard:
    """Verifies that all recommended restaurants exist within the filtered candidate pool."""

    @staticmethod
    def validate(parsed: ParsedGroqResponse, candidates: List[Restaurant]) -> List[RecommendationItem]:
        """Validates recommended items against candidates.

        Matches by ID first, then case-insensitive name. Drops hallucinated entries
        and merges explanations with ground truth dataset features (rating, cost, cuisines).
        Recalculates sequential ranking indices.
        """
        # Create lookups
        id_map: Dict[str, Restaurant] = {c.id: c for c in candidates}
        name_map: Dict[str, Restaurant] = {c.name.lower().strip(): c for c in candidates}
        
        validated_items: List[RecommendationItem] = []
        current_rank = 1
        
        for item in parsed.recommendations:
            matched_restaurant = None
            
            # Match by ID
            if item.restaurant_id in id_map:
                matched_restaurant = id_map[item.restaurant_id]
            # Match by name (case-insensitive)
            else:
                cleaned_name = item.name.lower().strip()
                if cleaned_name in name_map:
                    matched_restaurant = name_map[cleaned_name]
                    
            if matched_restaurant is None:
                logger.warning(
                    "Hallucination Guard dropped restaurant: id='%s', name='%s' (not in candidate pool)",
                    item.restaurant_id, item.name
                )
                continue
                
            # Merge explanation with ground-truth fields from dataset
            validated_item = RecommendationItem(
                rank=current_rank,
                name=matched_restaurant.name,
                cuisine=", ".join(matched_restaurant.cuisines),
                rating=matched_restaurant.rating,
                estimated_cost=matched_restaurant.cost_for_two,
                explanation=item.explanation.strip()
            )
            validated_items.append(validated_item)
            current_rank += 1
            
        logger.info(
            "Hallucination Guard validation complete. Retained %d of %d recommendations.",
            len(validated_items), len(parsed.recommendations)
        )
        return validated_items
