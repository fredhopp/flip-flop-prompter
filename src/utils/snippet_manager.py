"""
Snippet management system with content rating support and JSON storage.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum


class ContentRating(Enum):
    """Content rating levels."""
    PG = "PG"
    NSFW = "NSFW"
    HENTAI = "Hentai"


class SnippetManager:
    """Manages dynamic snippets based on content rating with JSON storage."""
    
    def __init__(self):
        self.user_data_dir = self._get_user_data_dir()
        self.snippets_dir = self.user_data_dir / "snippets"
        self.snippets_dir.mkdir(parents=True, exist_ok=True)
        
        # Master snippet collection
        self.all_snippets: Dict[str, Dict[str, Any]] = {}
        
        # Available ratings (dynamically discovered)
        self.available_ratings: List[str] = ["PG"]  # Default fallback
        
        # Load all snippets
        self._load_all_snippets()
    
    def _get_user_data_dir(self) -> Path:
        """Get the appropriate user data directory for the platform."""
        system = platform.system().lower()
        
        if system == "windows":
            base_dir = Path(os.environ.get("APPDATA", ""))
            return base_dir / "FlipFlopPrompt"
        elif system == "darwin":  # macOS
            base_dir = Path.home() / "Library" / "Application Support"
            return base_dir / "FlipFlopPrompt"
        else:  # Linux and others
            base_dir = Path.home() / ".config"
            return base_dir / "FlipFlopPrompt"
    
    def _load_all_snippets(self):
        """Load all snippets from repo and user directories."""
        self.all_snippets = {}
        self.available_ratings = set()
        
        # Load repo snippets
        repo_snippets_dir = Path(__file__).parent.parent.parent / "data" / "snippets"
        if repo_snippets_dir.exists():
            self._load_snippets_from_directory(repo_snippets_dir, "repo")
        
        # Load user snippets
        if self.snippets_dir.exists():
            self._load_snippets_from_directory(self.snippets_dir, "user")
        
        # Convert ratings to sorted list with fallback
        self.available_ratings = sorted(list(self.available_ratings)) if self.available_ratings else ["PG"]
    
    def _load_snippets_from_directory(self, directory: Path, source: str):
        """Load all JSON files from a directory."""
        for json_file in directory.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle multi-field format
                if "snippets" in data:
                    for snippet_data in data["snippets"]:
                        self._process_snippet_data(snippet_data, source)
                else:
                    # Handle single snippet format
                    self._process_snippet_data(data, source)
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing {json_file} ({source}): {e}")
            except Exception as e:
                print(f"Error loading {json_file} ({source}): {e}")
                import traceback
                traceback.print_exc()
    
    def _process_snippet_data(self, snippet_data: Dict[str, Any], source: str):
        """Process a single snippet data entry."""
        field = snippet_data.get("field")
        
        # Handle both old "rating" field and new "family" field for backward compatibility
        family = snippet_data.get("family", snippet_data.get("rating", "PG"))
        llm_rating = snippet_data.get("LLM_rating", snippet_data.get("rating", "PG"))
        
        categories = snippet_data.get("categories", {})
        
        if not field or not categories:
            return
        
        # Add family to available ratings (for backward compatibility, we still call it ratings)
        self.available_ratings.add(family)
        
        # Store snippets by field and family
        field_key = f"{field}_{family}"
        if field_key not in self.all_snippets:
            self.all_snippets[field_key] = {
                "field": field,
                "family": family,
                "LLM_rating": llm_rating,
                "categories": {},
                "source": source
            }
        
        # Merge categories with deduplication
        for category_name, category_items in categories.items():
            if isinstance(category_items, list):
                # Simple list of items
                if category_name not in self.all_snippets[field_key]["categories"]:
                    self.all_snippets[field_key]["categories"][category_name] = []
                
                # Add items with deduplication
                existing_items = []
                for existing_item in self.all_snippets[field_key]["categories"][category_name]:
                    if isinstance(existing_item, str):
                        existing_items.append(existing_item)
                    elif isinstance(existing_item, dict):
                        existing_items.append(existing_item.get("name", ""))
                
                for item in category_items:
                    # Handle both string format (old) and object format (new)
                    if isinstance(item, str):
                        if item not in existing_items:
                            self.all_snippets[field_key]["categories"][category_name].append(item)
                    elif isinstance(item, dict):
                        # New key-value format
                        item_name = item.get("name", "")
                        if item_name and item_name not in existing_items:
                            self.all_snippets[field_key]["categories"][category_name].append(item)
                        
            elif isinstance(category_items, dict):
                # Nested category structure
                if category_name not in self.all_snippets[field_key]["categories"]:
                    self.all_snippets[field_key]["categories"][category_name] = {}
                
                for subcategory_name, subcategory_items in category_items.items():
                    # Handle both list format (traditional) and dict format (new instruction format)
                    if isinstance(subcategory_items, list):
                        # Traditional list format
                        if subcategory_name not in self.all_snippets[field_key]["categories"][category_name]:
                            self.all_snippets[field_key]["categories"][category_name][subcategory_name] = []
                        
                        existing_subitems = []
                        for existing_item in self.all_snippets[field_key]["categories"][category_name][subcategory_name]:
                            if isinstance(existing_item, str):
                                existing_subitems.append(existing_item)
                            elif isinstance(existing_item, dict):
                                existing_subitems.append(existing_item.get("name", ""))
                        
                        for item in subcategory_items:
                            if isinstance(item, str):
                                if item not in existing_subitems:
                                    self.all_snippets[field_key]["categories"][category_name][subcategory_name].append(item)
                            elif isinstance(item, dict):
                                item_name = item.get("name", "")
                                if item_name and item_name not in existing_subitems:
                                    self.all_snippets[field_key]["categories"][category_name][subcategory_name].append(item)
                                
                    elif isinstance(subcategory_items, dict):
                        # New instruction format with content/description
                        if subcategory_name not in self.all_snippets[field_key]["categories"][category_name]:
                            self.all_snippets[field_key]["categories"][category_name][subcategory_name] = {}
                        
                        # Store the entire object with content and description
                        self.all_snippets[field_key]["categories"][category_name][subcategory_name] = subcategory_items
    
    def get_available_ratings(self) -> List[str]:
        """Get all available ratings from loaded snippets."""
        return self.available_ratings
    
    def get_snippets_for_field(self, field_name: str, content_rating: str = "PG") -> Optional[Dict[str, List[str]]]:
        """Get snippets for a specific field based on content rating."""
        # Find all snippets for this field and rating
        matching_snippets = {}
        
        for key, snippet_data in self.all_snippets.items():
            if snippet_data.get("field") == field_name:
                snippet_family = snippet_data.get("family", snippet_data.get("rating", "PG"))
                
                # Check if this snippet's family is appropriate for the requested family filter
                if self._is_family_appropriate(snippet_family, content_rating):
                    categories = snippet_data.get("categories", {})
                    
                    # Merge categories
                    for category_name, category_items in categories.items():
                        if isinstance(category_items, list):
                            # Simple list of items
                            if category_name not in matching_snippets:
                                matching_snippets[category_name] = []
                            
                            # Add items with deduplication
                            existing_items = []
                            for existing_item in matching_snippets[category_name]:
                                if isinstance(existing_item, str):
                                    existing_items.append(existing_item)
                                elif isinstance(existing_item, dict):
                                    existing_items.append(existing_item.get("name", ""))
                            
                            for item in category_items:
                                # Handle both string format (old) and object format (new)
                                if isinstance(item, str):
                                    if item not in existing_items:
                                        matching_snippets[category_name].append(item)
                                elif isinstance(item, dict):
                                    # New key-value format
                                    item_name = item.get("name", "")
                                    if item_name and item_name not in existing_items:
                                        matching_snippets[category_name].append(item)
                                    
                        elif isinstance(category_items, dict):
                            # Nested category structure
                            if category_name not in matching_snippets:
                                matching_snippets[category_name] = {}
                            elif not isinstance(matching_snippets[category_name], dict):
                                # If it's already a list, convert to dict
                                existing_items = matching_snippets[category_name]
                                matching_snippets[category_name] = {"General": existing_items}
                            
                            for subcategory_name, subcategory_items in category_items.items():
                                if isinstance(subcategory_items, list):
                                    # Traditional list format
                                    if subcategory_name not in matching_snippets[category_name]:
                                        matching_snippets[category_name][subcategory_name] = []
                                    
                                    existing_subitems = []
                                    for existing_item in matching_snippets[category_name][subcategory_name]:
                                        if isinstance(existing_item, str):
                                            existing_subitems.append(existing_item)
                                        elif isinstance(existing_item, dict):
                                            existing_subitems.append(existing_item.get("name", ""))
                                    
                                    for item in subcategory_items:
                                        if isinstance(item, str):
                                            if item not in existing_subitems:
                                                matching_snippets[category_name][subcategory_name].append(item)
                                        elif isinstance(item, dict):
                                            item_name = item.get("name", "")
                                            if item_name and item_name not in existing_subitems:
                                                matching_snippets[category_name][subcategory_name].append(item)
                                            
                                elif isinstance(subcategory_items, dict):
                                    # New instruction format with content/description
                                    if subcategory_name not in matching_snippets[category_name]:
                                        matching_snippets[category_name][subcategory_name] = {}
                                    
                                    # Merge instruction objects
                                    matching_snippets[category_name][subcategory_name].update(subcategory_items)
        
        return matching_snippets if matching_snippets else None
    
    def _is_family_appropriate(self, snippet_family: str, requested_family: str) -> bool:
        """Check if a snippet's family is appropriate for the requested family filter."""
        # Normalize families to lowercase for comparison
        snippet_lower = snippet_family.lower()
        requested_lower = requested_family.lower()
        
        # Families should only show content from their own family
        # This is a filter, not a hierarchy - each family is independent
        return snippet_lower == requested_lower
    
    def reload_snippets(self):
        """Reload all snippets from files."""
        self._load_all_snippets()
    
    def add_snippet(self, field_name: str, category: str, snippet: str, rating: str = "PG"):
        """Add a new snippet to user snippets."""
        # This would need to be implemented to save to user files
        # For now, we'll just add to memory
        if field_name not in self.all_snippets:
            self.all_snippets[field_name] = {
                "rating": rating,
                "categories": {},
                "source": "user"
            }
        
        if category not in self.all_snippets[field_name]["categories"]:
            self.all_snippets[field_name]["categories"][category] = []
        
        if snippet not in self.all_snippets[field_name]["categories"][category]:
            self.all_snippets[field_name]["categories"][category].append(snippet)
    
    def remove_snippet(self, field_name: str, category: str, snippet: str):
        """Remove a snippet from user snippets."""
        if (field_name in self.all_snippets and 
            category in self.all_snippets[field_name]["categories"] and
            snippet in self.all_snippets[field_name]["categories"][category]):
            
            self.all_snippets[field_name]["categories"][category].remove(snippet)
    
    def get_user_data_dir(self) -> Path:
        """Get the user data directory path."""
        return self.user_data_dir
    
    def get_snippets_dir(self) -> Path:
        """Get the snippets directory path."""
        return self.snippets_dir
    
    def export_snippets(self, file_path: Path):
        """Export all user snippets to a JSON file."""
        user_snippets = {
            "snippets": []
        }
        
        for field_name, field_data in self.all_snippets.items():
            if field_data.get("source") == "user":
                user_snippets["snippets"].append({
                    "field": field_name,
                    "rating": field_data.get("rating", "PG"),
                    "categories": field_data.get("categories", {})
                })
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_snippets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error exporting snippets: {e}")
    
    def import_snippets(self, file_path: Path):
        """Import snippets from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "snippets" in data:
                for snippet_data in data["snippets"]:
                    self._process_snippet_data(snippet_data, "user")
        except Exception as e:
            print(f"Error importing snippets: {e}")
    
    def get_category_items(self, field_name: str, category_name: str, content_rating: str = "PG") -> List[str]:
        """Get all items from a specific category in a field."""
        items = []
        
        # Find snippets for this field and family
        for key, snippet_data in self.all_snippets.items():
            if snippet_data.get("field") == field_name:
                snippet_family = snippet_data.get("family", snippet_data.get("rating", "PG"))
                
                if self._is_family_appropriate(snippet_family, content_rating):
                    categories = snippet_data.get("categories", {})
                    
                    if category_name in categories:
                        category_data = categories[category_name]
                        
                        if isinstance(category_data, list):
                            # Flat list of items
                            for item in category_data:
                                if isinstance(item, dict):
                                    # New format: extract name from dictionary
                                    items.append(item.get("name", str(item)))
                                else:
                                    # Old format: use item directly
                                    items.append(item)
                        elif isinstance(category_data, dict):
                            # Nested structure - collect all items from all subcategories
                            for subcategory_items in category_data.values():
                                if isinstance(subcategory_items, list):
                                    for item in subcategory_items:
                                        if isinstance(item, dict):
                                            # New format: extract name from dictionary
                                            items.append(item.get("name", str(item)))
                                        else:
                                            # Old format: use item directly
                                            items.append(item)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        
        return unique_items
    
    def get_subcategory_items(self, field_name: str, category_name: str, subcategory_name: str, content_rating: str = "PG") -> List[str]:
        """Get all items from a specific subcategory in a field."""
        items = []
        
        # Find snippets for this field and family
        for key, snippet_data in self.all_snippets.items():
            if snippet_data.get("field") == field_name:
                snippet_family = snippet_data.get("family", snippet_data.get("rating", "PG"))
                
                if self._is_family_appropriate(snippet_family, content_rating):
                    categories = snippet_data.get("categories", {})
                    
                    if category_name in categories:
                        category_data = categories[category_name]
                        
                        if isinstance(category_data, dict) and subcategory_name in category_data:
                            subcategory_items = category_data[subcategory_name]
                            if isinstance(subcategory_items, list):
                                for item in subcategory_items:
                                    if isinstance(item, dict):
                                        # New format: extract name from dictionary
                                        items.append(item.get("name", str(item)))
                                    else:
                                        # Old format: use item directly
                                        items.append(item)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        
        return unique_items

    def create_snippet_dropdown(self, parent, field_name: str, on_select: Callable[[str], None], content_rating: str = "PG"):
        """Create a snippet dropdown widget."""
        from ..gui.snippet_widgets import SnippetDropdown
        return SnippetDropdown(parent, field_name, on_select, content_rating)


# Global snippet manager instance
snippet_manager = SnippetManager()
