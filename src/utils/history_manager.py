"""
History manager for storing and navigating through generated prompts.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class HistoryEntry:
    """Represents a single history entry."""
    timestamp: str
    summary_prompt: str
    final_prompt: str
    field_data: Dict[str, Any]  # All field values
    seed: int
    families: List[str]
    llm_model: str
    target_model: str


class HistoryManager:
    """Manages prompt history storage and navigation."""
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.entries: List[HistoryEntry] = []
        self.current_index = -1  # -1 means no current entry
        
        # Load existing history
        self._load_history()
    
    def add_entry(self, summary_prompt: str, final_prompt: str, field_data: Dict[str, Any], 
                  seed: int, families: List[str], llm_model: str, target_model: str) -> None:
        """Add a new entry to history."""
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            summary_prompt=summary_prompt,
            final_prompt=final_prompt,
            field_data=field_data,
            seed=seed,
            families=families,
            llm_model=llm_model,
            target_model=target_model
        )
        
        # Add to beginning of list (most recent first)
        self.entries.insert(0, entry)
        
        # Limit to max entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]
        
        # Reset current index to most recent
        self.current_index = 0
        
        # Save to file
        self._save_history()
    
    def get_current_entry(self) -> Optional[HistoryEntry]:
        """Get the current history entry."""
        if 0 <= self.current_index < len(self.entries):
            return self.entries[self.current_index]
        return None
    
    def navigate_back(self) -> bool:
        """Navigate to previous entry. Returns True if successful."""
        if self.current_index < len(self.entries) - 1:
            self.current_index += 1
            return True
        return False
    
    def navigate_forward(self) -> bool:
        """Navigate to next entry. Returns True if successful."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def can_go_back(self) -> bool:
        """Check if we can go back."""
        return self.current_index < len(self.entries) - 1
    
    def can_go_forward(self) -> bool:
        """Check if we can go forward."""
        return self.current_index > 0
    
    def get_navigation_info(self) -> tuple[int, int]:
        """Get current position and total count."""
        if not self.entries:
            return (0, 0)
        return (self.current_index + 1, len(self.entries))
    
    def delete_current_entry(self) -> bool:
        """Delete the current entry and navigate to previous. Returns True if successful."""
        if 0 <= self.current_index < len(self.entries):
            # Remove current entry
            del self.entries[self.current_index]
            
            # Navigate to previous entry if possible
            if self.current_index >= len(self.entries):
                self.current_index = max(0, len(self.entries) - 1)
            
            # Save to file
            self._save_history()
            return True
        return False
    
    def clear_history(self) -> None:
        """Clear all history entries."""
        self.entries.clear()
        self.current_index = -1
        self._save_history()
    
    def has_history(self) -> bool:
        """Check if there are any history entries."""
        return len(self.entries) > 0
    
    def _get_history_file_path(self) -> Path:
        """Get the path to the history file."""
        from .theme_manager import theme_manager
        history_dir = Path(theme_manager.user_data_dir) / "history"
        history_dir.mkdir(exist_ok=True)
        return history_dir / "prompt_history.json"
    
    def _save_history(self) -> None:
        """Save history to file."""
        try:
            history_file = self._get_history_file_path()
            data = {
                "entries": [asdict(entry) for entry in self.entries],
                "current_index": self.current_index
            }
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _load_history(self) -> None:
        """Load history from file."""
        try:
            history_file = self._get_history_file_path()
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert dict back to HistoryEntry objects
                self.entries = [HistoryEntry(**entry_data) for entry_data in data.get("entries", [])]
                self.current_index = data.get("current_index", -1)
                
                # Validate current_index
                if self.current_index >= len(self.entries):
                    self.current_index = max(0, len(self.entries) - 1)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.entries = []
            self.current_index = -1
