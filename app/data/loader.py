"""Dataset loading module."""

import os
import pandas as pd
from datasets import load_dataset
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

def load_restaurant_data() -> pd.DataFrame:
    """Loads the Zomato restaurant dataset from Hugging Face or a local Parquet cache.

    Returns:
        pd.DataFrame: The raw loaded dataset.
    """
    settings = get_settings()
    dataset_name = settings.hf_dataset_name
    
    # Define cache path
    cache_dir = os.path.join("data", "cache")
    cache_path = os.path.join(cache_dir, "restaurants.parquet")
    
    # Try loading from cache first
    if os.path.exists(cache_path):
        try:
            logger.info("Loading cached dataset from %s", cache_path)
            return pd.read_parquet(cache_path)
        except Exception as e:
            logger.warning("Failed to load dataset from cache: %s. Re-downloading.", e)
            
    # Download dataset from Hugging Face
    logger.info("Downloading dataset '%s' from Hugging Face", dataset_name)
    try:
        # Load from Hugging Face datasets
        dataset = load_dataset(dataset_name, split="train")
        df = dataset.to_pandas()
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Save to cache
        try:
            df.to_parquet(cache_path, index=False)
            logger.info("Successfully cached dataset to %s", cache_path)
        except Exception as e:
            logger.warning("Failed to cache dataset: %s", e)
            
        return df
    except Exception as e:
        logger.error("Failed to load dataset from Hugging Face: %s", e)
        raise RuntimeError(f"Unable to load restaurant data from Hugging Face: {e}") from e
