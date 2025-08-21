"""
Theme manager for loading and managing JSON-based theme files.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class ThemeManager:
    """Theme manager that loads themes from JSON files."""
    
    def __init__(self):
        self.user_data_dir = self._get_user_data_dir()
        self.themes_dir = self.user_data_dir / "themes"
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Preferences file
        self.preferences_file = self.user_data_dir / "preferences.json"
        self.preferences = self._load_preferences()
        
        # Load themes from JSON files
        self.themes = self._load_themes()
        
        # Current theme (default to light)
        self.current_theme = self.preferences.get("theme", "light")
    
    def _get_user_data_dir(self) -> Path:
        """Get user data directory."""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        elif os.name == 'posix':  # macOS/Linux
            base_dir = Path.home() / '.config'
        else:
            base_dir = Path.home()
        
        return base_dir / "FlipFlopPrompt"
    
    def _load_themes(self) -> Dict[str, Dict[str, str]]:
        """Load themes from JSON files."""
        themes = {}
        
        # Load built-in themes from data/themes directory
        builtin_themes_dir = Path(__file__).parent.parent.parent / "data" / "themes"
        
        # Load user themes from user data directory
        user_themes_dir = self.themes_dir
        
        # Combine both directories
        theme_dirs = [builtin_themes_dir, user_themes_dir]
        
        for theme_dir in theme_dirs:
            if theme_dir.exists():
                for theme_file in theme_dir.glob("*.json"):
                    try:
                        with open(theme_file, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                        
                        # Extract theme name and colors
                        theme_name = theme_data.get("name", theme_file.stem)
                        colors = theme_data.get("colors", {})
                        
                        # Use filename as key for consistency
                        theme_key = theme_file.stem
                        themes[theme_key] = colors
                        
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Warning: Could not load theme {theme_file}: {e}")
        
        # Ensure we have at least light and dark themes
        if not themes:
            print("Warning: No themes found, using fallback colors")
            themes = self._get_fallback_themes()
        
        return themes
    
    def _get_fallback_themes(self) -> Dict[str, Dict[str, str]]:
        """Provide fallback themes if JSON loading fails."""
        return {
            "light": {
                "bg": "#f0f0f0",
                "text_bg": "#ffffff",
                "text_fg": "#000000",
                "button_bg": "#0066cc",
                "button_fg": "#ffffff"
            },
            "dark": {
                "bg": "#2b2b2b",
                "text_bg": "#3c3c3c",
                "text_fg": "#ffffff",
                "button_bg": "#4a9eff",
                "button_fg": "#ffffff"
            }
        }
    
    def _load_preferences(self) -> Dict:
        """Load user preferences."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_preferences(self):
        """Save user preferences."""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save preferences: {e}")
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get colors for the specified theme."""
        if theme_name is None:
            theme_name = self.current_theme
        
        # Get theme colors, fallback to light if not found
        theme_colors = self.themes.get(theme_name, self.themes.get("light", {}))
        
        # Ensure all required colors are present
        required_colors = [
            "bg", "text_bg", "text_fg", "button_bg", "button_fg",
            "category_bg", "category_fg", "category_border",
            "subcategory_bg", "subcategory_fg", "subcategory_border",
            "snippet_bg", "snippet_fg", "snippet_border",
            "user_text_bg", "user_text_fg", "user_text_border",
            "tag_bg", "tag_fg", "tag_border"
        ]
        
        # Use fallback colors for missing values
        fallback_colors = self.themes.get("light", {})
        for color_key in required_colors:
            if color_key not in theme_colors:
                theme_colors[color_key] = fallback_colors.get(color_key, "#000000")
        
        return theme_colors.copy()
    
    def get_current_theme(self) -> str:
        """Get current theme name."""
        return self.current_theme
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def set_current_theme(self, theme_name: str):
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.preferences["theme"] = theme_name
            self._save_preferences()
        else:
            print(f"Warning: Theme '{theme_name}' not found")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.current_theme == "light":
            self.set_current_theme("dark")
        else:
            self.set_current_theme("light")
    
    def reload_themes(self):
        """Reload themes from JSON files."""
        self.themes = self._load_themes()
    
    def save_preferences(self, preferences: Dict):
        """Save user preferences to file."""
        try:
            # Update current preferences
            self.preferences.update(preferences)
            
            # Save to file
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")
    
    def get_preference(self, key: str, default=None):
        """Get a preference value."""
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a preference value and save."""
        self.preferences[key] = value
        self.save_preferences({})


# Global theme manager instance
theme_manager = ThemeManager()
