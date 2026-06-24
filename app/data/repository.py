"""Restaurant repository module."""

from typing import Any, Dict, List
import math
import logging
from app.data.loader import load_restaurant_data
from app.data.preprocessor import preprocess_dataset
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


def _sanitize(row: dict) -> dict:
    """Replace float NaN values with None so Pydantic Optional fields validate cleanly.

    Pandas stores Python None as float('nan') when building DataFrames. Pydantic's
    ge/le validators reject nan even on Optional[float] fields, so we convert them
    back to None before model construction.
    """
    return {
        k: (None if isinstance(v, float) and math.isnan(v) else v)
        for k, v in row.items()
    }


class RestaurantRepository:
    """In-memory repository for processed restaurant records."""

    def __init__(self) -> None:
        """Initializes the repository by loading, preprocessing, and validating the dataset."""
        logger.info("Initializing RestaurantRepository...")
        raw_df = load_restaurant_data()
        processed_df = preprocess_dataset(raw_df)

        # Load and validate records as Restaurant Pydantic models
        self._records: List[Restaurant] = []
        skipped = 0
        for r in processed_df.to_dict(orient="records"):
            try:
                self._records.append(Restaurant(**_sanitize(r)))
            except Exception as e:
                skipped += 1
                logger.debug("Skipping restaurant %s: %s", r.get("name"), e)

        if skipped:
            logger.warning("Skipped %d restaurant(s) with invalid data.", skipped)

        self._locations: List[str] = sorted(list(processed_df["location"].unique()))
        logger.info("✅ RestaurantRepository ready: %d valid records, %d locations.",
                    len(self._records), len(self._locations))

    def get_all(self) -> List[Restaurant]:
        """Returns all preprocessed restaurant records."""
        return self._records

    def get_locations(self) -> List[str]:
        """Returns a sorted list of unique locations."""
        return self._locations

    def get_stats(self) -> Dict[str, Any]:
        """Returns repository stats."""
        return {
            "total_restaurants": len(self._records),
            "total_locations": len(self._locations),
        }
