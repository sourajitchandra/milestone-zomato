"""Data preprocessing module."""

import re
import pandas as pd
from typing import Any, Dict, List
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

def parse_rating(rate_val: Any) -> float | None:
    """Parses raw rating values into floats.

    Handles values like "4.1/5", "NEW", "-", etc.
    """
    if pd.isna(rate_val):
        return None
    rate_str = str(rate_val).strip()
    if rate_str in ("NEW", "-", ""):
        return None
    if "/" in rate_str:
        rate_str = rate_str.split("/")[0].strip()
    try:
        return float(rate_str)
    except ValueError:
        return None

def parse_cost(cost_val: Any) -> int | None:
    """Parses raw cost values into integers.

    Removes commas and handles formatting.
    """
    if pd.isna(cost_val):
        return None
    cost_str = str(cost_val).strip().replace(",", "")
    if not cost_str:
        return None
    try:
        return int(float(cost_str))
    except ValueError:
        return None

def normalize_location(loc: Any) -> str:
    """Normalizes location strings to title case and handles aliases."""
    if pd.isna(loc):
        return ""
    loc_str = str(loc).strip().title()
    
    # Alias mapping
    aliases = {
        "Bengaluru": "Bangalore",
    }
    return aliases.get(loc_str, loc_str)

def clean_cuisines(cuisines_val: Any) -> List[str]:
    """Splits a comma-separated cuisines string into a clean list."""
    if pd.isna(cuisines_val):
        return []
    cuisines_str = str(cuisines_val)
    return [c.strip() for c in cuisines_str.split(",") if c.strip()]

def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses the raw Zomato DataFrame into canonical columns.

    Performs field normalization, parsing, deduplication, and budget tiering.
    """
    logger.info("Starting preprocessing of %d raw rows", len(df))
    
    # 1. Drop rows missing essential fields (name, location) in raw data
    essential_cols = ["name", "location"]
    for col in essential_cols:
        if col not in df.columns:
            logger.error("Essential column '%s' not found in raw dataset", col)
            raise KeyError(f"Missing essential column: {col}")

    processed_rows = []
    settings = get_settings()
    
    for idx, row in df.iterrows():
        # Normalise name: strip edges + collapse internal whitespace
        name = re.sub(r"\s+", " ", str(row["name"]).strip())
        raw_loc = row["location"]
        
        # Check if name or location is missing or empty
        if not name or pd.isna(raw_loc) or not str(raw_loc).strip():
            continue
            
        location = normalize_location(raw_loc)
        if not location:
            continue
            
        # Parse rating and cost
        raw_rate = row.get("rate")
        rating = parse_rating(raw_rate)
        
        raw_cost = row.get("approx_cost(for two people)")
        cost_for_two = parse_cost(raw_cost)
        
        # Derive budget tier
        if cost_for_two is None:
            budget_tier = "medium"
        elif cost_for_two <= settings.budget_low_max:
            budget_tier = "low"
        elif cost_for_two <= settings.budget_medium_max:
            budget_tier = "medium"
        else:
            budget_tier = "high"
            
        # Clean cuisines
        raw_cuisines = row.get("cuisines")
        cuisines = clean_cuisines(raw_cuisines)
        
        # Build raw metadata
        raw_metadata = {
            "address": str(row.get("address", "")).strip(),
            "online_order": str(row.get("online_order", "")).strip(),
            "book_table": str(row.get("book_table", "")).strip(),
            "votes": int(float(row.get("votes", 0))) if pd.notna(row.get("votes")) else 0,
            "rest_type": str(row.get("rest_type", "")).strip(),
            "dish_liked": str(row.get("dish_liked", "")).strip(),
            "reviews_list": str(row.get("reviews_list", "")).strip(),
            "menu_item": str(row.get("menu_item", "")).strip(),
            "listed_in_type": str(row.get("listed_in(type)", "")).strip(),
            "listed_in_city": str(row.get("listed_in(city)", "")).strip(),
        }
        
        processed_rows.append({
            "name": name,
            "location": location,
            "cuisines": cuisines,
            "rating": rating,
            "cost_for_two": cost_for_two,
            "budget_tier": budget_tier,
            "raw_metadata": raw_metadata,
        })
        
    processed_df = pd.DataFrame(processed_rows)
    
    if processed_df.empty:
        logger.warning("No rows remaining after processing")
        return pd.DataFrame(columns=["id", "name", "location", "cuisines", "rating", "cost_for_two", "budget_tier", "raw_metadata"])
        
    # ── Three-pass deduplication ─────────────────────────────────────────────
    # When duplicates exist, keep the row with the highest vote count so the
    # richest data-quality record survives.
    initial_len = len(processed_df)

    def _votes(row: dict) -> int:
        return row.get("raw_metadata", {}).get("votes", 0) or 0

    # Sort so that the highest-vote row is always first ("keep='first'" below
    # will then retain it).
    processed_df["_votes"] = processed_df["raw_metadata"].apply(
        lambda m: m.get("votes", 0) if isinstance(m, dict) else 0
    )
    processed_df = processed_df.sort_values("_votes", ascending=False)

    # Pass 1 — exact name + location (case-sensitive, as stored)
    processed_df = processed_df.drop_duplicates(
        subset=["name", "location"], keep="first"
    ).reset_index(drop=True)
    logger.info("Pass 1 (exact):            %d → %d rows", initial_len, len(processed_df))

    # Pass 2 — case-insensitive name + location
    processed_df["_name_lower"] = processed_df["name"].str.lower().str.strip()
    processed_df["_loc_lower"]  = processed_df["location"].str.lower().str.strip()
    after_pass1 = len(processed_df)
    processed_df = processed_df.drop_duplicates(
        subset=["_name_lower", "_loc_lower"], keep="first"
    ).reset_index(drop=True)
    logger.info("Pass 2 (case-insensitive): %d → %d rows", after_pass1, len(processed_df))

    # Pass 3 — normalised key: lowercase + remove all punctuation/extra spaces
    def _norm_key(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower())

    processed_df["_name_norm"] = processed_df["_name_lower"].apply(_norm_key)
    processed_df["_loc_norm"]  = processed_df["_loc_lower"].apply(_norm_key)
    after_pass2 = len(processed_df)
    processed_df = processed_df.drop_duplicates(
        subset=["_name_norm", "_loc_norm"], keep="first"
    ).reset_index(drop=True)
    logger.info("Pass 3 (normalised):       %d → %d rows", after_pass2, len(processed_df))

    # Drop helper columns
    processed_df = processed_df.drop(
        columns=["_votes", "_name_lower", "_loc_lower", "_name_norm", "_loc_norm"],
        errors="ignore",
    )

    dedup_len = len(processed_df)
    logger.info(
        "Deduplication complete: removed %d duplicate rows (%d → %d)",
        initial_len - dedup_len, initial_len, dedup_len,
    )
    
    # Add unique, stable IDs
    processed_df["id"] = [f"r_{i}" for i in range(len(processed_df))]
    
    # Reorder columns to canonical schema
    canonical_cols = ["id", "name", "location", "cuisines", "rating", "cost_for_two", "budget_tier", "raw_metadata"]
    processed_df = processed_df[canonical_cols]
    
    logger.info("Finished preprocessing. Total canonical records: %d", len(processed_df))
    return processed_df
