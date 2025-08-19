#!/usr/bin/env python3
"""
Test script for the snippet manager.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.snippet_manager import snippet_manager, ContentRating

def test_snippet_manager():
    """Test the snippet manager functionality."""
    print("Testing Snippet Manager...")
    
    # Test getting snippets for different fields and ratings
    fields = ["subjects_pose_and_action", "environment", "color_grading_&_mood"]
    ratings = ["PG", "NSFW", "Hentai"]
    
    for field in fields:
        print(f"\nField: {field}")
        for rating in ratings:
            snippets = snippet_manager.get_snippets_for_field(field, rating)
            if snippets:
                print(f"  {rating}: {len(snippets)} categories")
                for category, items in snippets.items():
                    if isinstance(items, list):
                        print(f"    {category}: {len(items)} items")
                    elif isinstance(items, dict):
                        total_items = sum(len(subitems) if isinstance(subitems, list) else 0 
                                        for subitems in items.values())
                        print(f"    {category}: {total_items} total items")
            else:
                print(f"  {rating}: No snippets available")
    
    print(f"\nSnippets directory: {snippet_manager.snippets_dir}")
    print("Test completed!")

if __name__ == "__main__":
    test_snippet_manager()
