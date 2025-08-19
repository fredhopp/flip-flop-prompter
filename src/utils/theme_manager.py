"""
Simplified theme manager for basic color scheme.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class ThemeManager:
    """Simplified theme manager with basic, clear colors."""
    
    def __init__(self):
        self.user_data_dir = self._get_user_data_dir()
        self.themes_dir = self.user_data_dir / "themes"
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Basic color scheme for clear readability
        self.basic_colors = {
            "bg": "#f0f0f0",              # Light gray background
            "text_bg": "#ffffff",         # White text background
            "text_fg": "#000000",         # Black text
            "entry_bg": "#ffffff",        # White entry background
            "button_bg": "#0066cc",       # Blue buttons
            "button_fg": "#ffffff",       # White button text
            "placeholder_fg": "#666666",  # Gray placeholder text
            "menu_bg": "#f0f0f0",         # Menu background
            "menu_fg": "#000000",         # Menu text
            "menu_selection_bg": "#0066cc", # Menu selection background
            "menu_selection_fg": "#ffffff"  # Menu selection text
        }
    
    def _get_user_data_dir(self) -> Path:
        """Get user data directory."""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        elif os.name == 'posix':  # macOS/Linux
            base_dir = Path.home() / '.config'
        else:
            base_dir = Path.home()
        
        return base_dir / "FlipFlopPrompt"
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get colors for the specified theme (always returns basic colors)."""
        return self.basic_colors.copy()
    
    def get_current_theme(self) -> str:
        """Get current theme name (always 'basic')."""
        return "basic"
    
    def get_available_themes(self) -> List[str]:
        """Get available themes (only basic for now)."""
        return ["basic"]
    
    def set_current_theme(self, theme_name: str):
        """Set current theme (ignored, always uses basic)."""
        pass
    
    def reload_themes(self):
        """Reload themes (no-op for basic theme)."""
        pass


# Global instance
theme_manager = ThemeManager()
