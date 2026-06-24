"""Dataset loading module."""

import io
import os
import tempfile
import logging

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# The dataset is stored as Parquet shards on HuggingFace (no CSV exists).
# Source: https://datasets-server.huggingface.co/parquet?dataset=ManikaSaini/zomato-restaurant-recommendation
_PARQUET_URLS = [
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/refs%2Fconvert%2Fparquet/default/train/0001.parquet",
]

_DOWNLOAD_TIMEOUT = 300  # seconds per shard
_CHUNK_SIZE = 1024 * 1024  # 1 MB chunks for streaming download


def _download_parquet_shard(url: str, shard_index: int) -> pd.DataFrame:
    """Downloads a single parquet shard via streaming HTTP and reads it into a DataFrame."""
    logger.info("  Streaming shard %d from: %s", shard_index, url)

    headers = {"User-Agent": "python-requests/zomato-ai"}
    with requests.get(url, headers=headers, timeout=_DOWNLOAD_TIMEOUT, stream=True) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0))
        logger.info("  Shard %d size: %.1f MB", shard_index, total / 1024 / 1024)

        # Stream into an in-memory buffer
        buf = io.BytesIO()
        downloaded = 0
        for chunk in resp.iter_content(chunk_size=_CHUNK_SIZE):
            if chunk:
                buf.write(chunk)
                downloaded += len(chunk)

        logger.info("  Shard %d: downloaded %.1f MB", shard_index, downloaded / 1024 / 1024)
        buf.seek(0)
        df = pd.read_parquet(buf)
        logger.info("  Shard %d: %d rows parsed.", shard_index, len(df))
        return df


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
            logger.warning("Cache load failed: %s. Re-downloading.", e)

    # Download shards via streaming HTTP (avoids fsspec/redirect issues)
    logger.info("Downloading %d parquet shard(s) from Hugging Face …", len(_PARQUET_URLS))
    try:
        shards = []
        for i, url in enumerate(_PARQUET_URLS, start=1):
            shard = _download_parquet_shard(url, i)
            shards.append(shard)

        df = pd.concat(shards, ignore_index=True)
        logger.info("✅ Total rows after merging shards: %d", len(df))

        # Persist to local cache so next startup skips download
        os.makedirs(cache_dir, exist_ok=True)
        try:
            df.to_parquet(cache_path, index=False)
            logger.info("Dataset cached to %s", cache_path)
        except Exception as cache_err:
            logger.warning("Could not write cache (non-fatal): %s", cache_err)

        return df

    except Exception as e:
        logger.error("❌ Failed to load dataset: %s", e, exc_info=True)
        raise RuntimeError(f"Unable to load restaurant data from Hugging Face: {e}") from e

