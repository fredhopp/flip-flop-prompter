"""
History manager for storing and navigating through generated prompts.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class HistoryEntry:
    """Represents a single history entry."""
    timestamp: str
    field_data: Dict[str, Any]  # All field values
    seed: int
    families: List[str]
    llm_model: str
    target_model: str
    final_prompt: str = ""  # The generated final prompt
    summary_text: str = ""  # The summary preview text at time of saving


class HistoryManager:
    """Manages prompt history storage and navigation (session-only, no persistence)."""
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.entries: List[HistoryEntry] = []
        self.current_index = -1  # -1 means no current entry
    
    def add_entry(self, field_data: Dict[str, Any], seed: int, families: List[str], 
                  llm_model: str, target_model: str, final_prompt: str = "", summary_text: str = "") -> None:
        """Add a new entry to history."""
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            field_data=field_data,
            seed=seed,
            families=families,
            llm_model=llm_model,
            target_model=target_model,
            final_prompt=final_prompt,
            summary_text=summary_text
        )
        
        # Add to beginning of list (most recent first)
        self.entries.insert(0, entry)
        
        # Limit to max entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]
        
        # Reset current index to current state (not in history)
        self.current_index = -1
    
    def get_current_entry(self) -> Optional[HistoryEntry]:
        """Get the current history entry."""
        if 0 <= self.current_index < len(self.entries):
            return self.entries[self.current_index]
        return None
    
    def navigate_back(self) -> bool:
        """Navigate to newer entry (lower numbers). Returns True if successful."""
        if self.current_index > 0:
            # Go to newer entry (lower number)
            self.current_index -= 1
            return True
        elif self.current_index == 0:
            # Currently at most recent history entry, go back to current state
            self.current_index = -1
            return True
        return False
    
    def navigate_forward(self) -> bool:
        """Navigate to older entry (higher numbers). Returns True if successful."""
        if self.current_index == -1:
            # Currently in current state, go to most recent history entry
            if self.entries:
                self.current_index = 0
                return True
        elif self.current_index < len(self.entries) - 1:
            # Go to older entry (higher number)
            self.current_index += 1
            return True
        return False
    
    def can_go_back(self) -> bool:
        """Check if we can go back (to newer entries/current state)."""
        if self.current_index == -1:
            # Can't go back from current state
            return False
        else:
            # Can go back if we're in history (to newer entry or current state)
            return True
    
    def can_go_forward(self) -> bool:
        """Check if we can go forward (to older entries)."""
        if self.current_index == -1:
            # Can go forward if there are history entries
            return len(self.entries) > 0
        else:
            # Can go forward if not at oldest entry
            return self.current_index < len(self.entries) - 1
    
    def get_navigation_info(self) -> tuple[int, int]:
        """Get current position and total count. Returns (0, total) for current state."""
        if not self.entries:
            return (0, 0)
        # For current state (not in history), return (0, total)
        # For history entries, return (position, total) where position is 1-based
        if self.current_index == -1:
            return (0, len(self.entries))
        return (self.current_index + 1, len(self.entries))
    
    def delete_current_entry(self) -> bool:
        """Delete the current entry and navigate to previous. Returns True if successful."""
        if 0 <= self.current_index < len(self.entries):
            # Remove current entry
            del self.entries[self.current_index]
            
            # Navigate to previous entry if possible
            if self.current_index >= len(self.entries):
                self.current_index = max(0, len(self.entries) - 1)
            
            return True
        return False
    
    def clear_history(self) -> None:
        """Clear all history entries."""
        self.entries.clear()
        self.current_index = -1
    
    def jump_to_position(self, position: int) -> bool:
        """Jump to specific position. Position 0 = current state, 1+ = history entries."""
        if position == 0:
            # Jump to current state
            self.current_index = -1
            return True
        elif 1 <= position <= len(self.entries):
            # Jump to history entry (1-based to 0-based)
            self.current_index = position - 1
            return True
        return False
    
    def has_history(self) -> bool:
        """Check if there are any history entries."""
        return len(self.entries) > 0
    

