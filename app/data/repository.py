"""Restaurant repository module."""

from typing import Any, Dict, List
import logging
from app.data.loader import load_restaurant_data
from app.data.preprocessor import preprocess_dataset
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

class RestaurantRepository:
    """In-memory repository for processed restaurant records."""

    def __init__(self) -> None:
        """Initializes the repository by loading, preprocessing, and validating the dataset."""
        logger.info("Initializing RestaurantRepository...")
        raw_df = load_restaurant_data()
        processed_df = preprocess_dataset(raw_df)
        
        # Load and validate records as Restaurant Pydantic models
        self._records: List[Restaurant] = []
        for r in processed_df.to_dict(orient="records"):
            try:
                self._records.append(Restaurant(**r))
            except Exception as e:
                logger.error("Validation error loading restaurant %s: %s", r.get("name"), e)
                
        self._locations: List[str] = sorted(list(processed_df["location"].unique()))
        logger.info("RestaurantRepository initialized with %d valid records.", len(self._records))

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
