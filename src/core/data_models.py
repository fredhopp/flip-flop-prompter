"""
Data models for FlipFlopPrompt.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class PromptData:
    """Data structure for prompt components."""
    environment: str = ""
    weather: str = ""
    date_time: str = ""
    subjects: str = ""
    pose_action: str = ""
    camera: str = ""
    framing_action: str = ""
    grading: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            'environment': self.environment,
            'weather': self.weather,
            'date_time': self.date_time,
            'subjects': self.subjects,
            'pose_action': self.pose_action,
            'camera': self.camera,
            'framing_action': self.framing_action,
            'grading': self.grading
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PromptData':
        """Create from dictionary."""
        return cls(**data)
