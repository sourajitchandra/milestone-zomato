"""CLI recommendation smoke test script."""

import os
import sys
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.user_input import UserPreferences
from app.models.restaurant import BudgetTier
from app.data.repository import RestaurantRepository
from app.services.recommendation_service import RecommendationService

# Set up logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def run_cli_test():
    """Runs a CLI-based pipeline smoke test to verify all layers."""
    print("=== AI Restaurant Recommendation Service CLI Smoke Test ===")
    
    # 1. Initialize Repository (loads and cleans dataset)
    print("\nLoading dataset and initializing repository...")
    try:
        repo = RestaurantRepository()
        print("Success! Repository stats:")
        print(repo.get_stats())
    except Exception as e:
        print(f"Error loading repository: {e}")
        sys.exit(1)
        
    # Get a valid location from the repo to use in our query
    known_locations = repo.get_locations()
    if not known_locations:
        print("Error: No locations found in the dataset.")
        sys.exit(1)
        
    test_location = "Indiranagar" if "Indiranagar" in known_locations else known_locations[0]
    print(f"Using test location: {test_location}")
    
    # 2. Instantiate Recommendation Service
    service = RecommendationService(repo)
    
    # 3. Formulate query preferences
    prefs = UserPreferences(
        location=test_location,
        budget=BudgetTier.MEDIUM,
        cuisine="Cafe",
        min_rating=4.0,
        additional_preferences="quiet place with good desserts",
        top_n=3
    )
    
    print("\nSending Query Preferences:")
    print(prefs.model_dump())
    
    # 4. Run recommend pipeline
    print("\nRunning recommendation pipeline...")
    try:
        response = service.recommend(prefs)
        
        print("\n=== RESPONSE SUMMARY ===")
        print(response.summary)
        
        print("\n=== RECOMMENDATIONS ===")
        for rec in response.recommendations:
            print(f"\n{rec.rank}. {rec.name} (★ {rec.rating or 'N/A'})")
            print(f"   Cuisines: {rec.cuisine}")
            print(f"   Est. Cost for Two: ₹{rec.estimated_cost or 'N/A'}")
            print(f"   AI Explanation: {rec.explanation}")
            
        print("\n=== METADATA ===")
        print(response.meta.model_dump())
        
    except Exception as e:
        print(f"Error during recommendation query: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli_test()
