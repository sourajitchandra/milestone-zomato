"""Context formatter module to serialize candidate data for LLM consumption."""

import json
from typing import List
from app.models.restaurant import Restaurant

class ContextFormatter:
    """Serializes candidate lists into compact JSON context for LLM prompts."""

    @staticmethod
    def to_json(candidates: List[Restaurant]) -> str:
        """Serializes candidates to a compact JSON string to minimize prompt tokens."""
        formatted_list = []
        for r in candidates:
            formatted_list.append({
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines,
                "rating": r.rating,
                "cost_for_two": r.cost_for_two,
                "budget_tier": r.budget_tier.value if hasattr(r.budget_tier, "value") else r.budget_tier,
            })
        return json.dumps(formatted_list, ensure_ascii=False)
