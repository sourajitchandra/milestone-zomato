"""Dataset loading module."""

import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# The dataset is stored as Parquet (not CSV) on HuggingFace.
# These URLs are the auto-converted parquet shards from:
# https://datasets-server.huggingface.co/parquet?dataset=ManikaSaini/zomato-restaurant-recommendation
_PARQUET_URLS = [
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/refs%2Fconvert%2Fparquet/default/train/0001.parquet",
]


def load_restaurant_data() -> pd.DataFrame:
    """Loads the Zomato restaurant dataset from Hugging Face or a local Parquet cache.

    Returns:
        pd.DataFrame: The raw loaded dataset.
    """
    # Define cache path
    cache_dir = os.path.join("data", "cache")
    cache_path = os.path.join(cache_dir, "restaurants.parquet")

    # Try loading from cache first
    if os.path.exists(cache_path):
        try:
            logger.info("Loading cached dataset from %s", cache_path)
            df = pd.read_parquet(cache_path)
            logger.info("Loaded %d rows from cache.", len(df))
            return df
        except Exception as e:
            logger.warning("Failed to load dataset from cache: %s. Re-downloading.", e)

    # Download dataset from Hugging Face (parquet shards)
    logger.info(
        "Downloading %d parquet shard(s) from Hugging Face …", len(_PARQUET_URLS)
    )
    try:
        shards = []
        for i, url in enumerate(_PARQUET_URLS, start=1):
            logger.info("  Fetching shard %d/%d: %s", i, len(_PARQUET_URLS), url)
            shard = pd.read_parquet(url, storage_options={"anon": True})
            logger.info("  Shard %d: %d rows loaded.", i, len(shard))
            shards.append(shard)

        df = pd.concat(shards, ignore_index=True)
        logger.info("Total rows after merging shards: %d", len(df))

        # Persist to local cache so next startup is instant
        os.makedirs(cache_dir, exist_ok=True)
        try:
            df.to_parquet(cache_path, index=False)
            logger.info("Dataset cached to %s", cache_path)
        except Exception as cache_err:
            logger.warning("Could not write cache: %s (non-fatal)", cache_err)

        return df

    except Exception as e:
        logger.error("❌ Failed to load dataset from Hugging Face: %s", e, exc_info=True)
        raise RuntimeError(
            f"Unable to load restaurant data from Hugging Face: {e}"
        ) from e
