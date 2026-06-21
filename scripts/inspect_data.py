"""Smoke script to inspect the preprocessed Zomato dataset."""

import os
import sys
from collections import Counter

# Add project root to sys.path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from app.data.repository import RestaurantRepository

# Set up logging to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def main():
    print("=== Zomato Dataset Inspection ===")
    try:
        repo = RestaurantRepository()
        stats = repo.get_stats()
        records = repo.get_all()
        
        print(f"\nTotal Restaurants Loaded: {stats['total_restaurants']}")
        print(f"Total Unique Locations: {stats['total_locations']}")
        
        if records:
            print("\n--- Sample Record ---")
            sample = records[0]
            # Convert to dictionary for easy display
            sample_dict = sample.model_dump()
            for key, val in sample_dict.items():
                if key == "raw_metadata":
                    print(f"raw_metadata (subset of keys): {list(val.keys())}")
                else:
                    print(f"{key}: {val}")
            
            # Budget distribution
            tiers = [r.budget_tier.value for r in records]
            tier_dist = Counter(tiers)
            print("\n--- Budget Tier Distribution ---")
            for tier, count in tier_dist.items():
                print(f"  {tier}: {count}")
                
            # Available locations sample
            locations = repo.get_locations()
            print("\n--- Available Locations (Sample first 10) ---")
            for loc in locations[:10]:
                print(f"  - {loc}")
            if len(locations) > 10:
                print(f"  ... and {len(locations) - 10} more")
        else:
            print("\nNo records loaded!")
            
    except Exception as e:
        print(f"\nError inspecting data: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
