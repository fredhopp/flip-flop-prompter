"""
Data models for the FlipFlopPrompt application.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PromptData:
    """Data structure for prompt information."""
    style: str = ""
    setting: str = ""  # renamed from environment
    weather: str = ""
    date_time: str = ""
    subjects: str = ""
    pose_action: str = ""
    camera: str = ""
    framing_action: str = ""
    grading: str = ""
    details: str = ""
    llm_instructions: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            'style': self.style,
            'setting': self.setting,  # renamed from environment
            'weather': self.weather,
            'date_time': self.date_time,
            'subjects': self.subjects,
            'pose_action': self.pose_action,
            'camera': self.camera,
            'framing_action': self.framing_action,
            'grading': self.grading,
            'details': self.details,
            'llm_instructions': self.llm_instructions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PromptData':
        """Create from dictionary."""
        return cls(
            style=data.get('style', ''),
            setting=data.get('setting', ''),  # renamed from environment
            weather=data.get('weather', ''),
            date_time=data.get('date_time', ''),
            subjects=data.get('subjects', ''),
            pose_action=data.get('pose_action', ''),
            camera=data.get('camera', ''),
            framing_action=data.get('framing_action', ''),
            grading=data.get('grading', ''),
            details=data.get('details', ''),
            llm_instructions=data.get('llm_instructions', '')
        )
