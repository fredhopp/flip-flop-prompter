"""
Data models for the FlipFlopPrompt application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


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


@dataclass
class PromptState:
    """Unified state management for prompt data, tags, metadata, and generated content."""
    
    # Core field values (display text)
    field_values: Dict[str, str] = field(default_factory=dict)
    
    # Tag data for each field (preserves tag structure and metadata)
    field_tags: Dict[str, List[Any]] = field(default_factory=dict)
    
    # Metadata
    seed: int = 0
    filters: List[str] = field(default_factory=list)
    llm_model: str = ""
    target_model: str = ""
    
    # Generated content
    summary_text: str = ""
    final_prompt: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Optional metadata
    name: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'field_values': self.field_values,
            'field_tags': self._serialize_tags(),
            'seed': self.seed,
            'filters': self.filters,
            'llm_model': self.llm_model,
            'target_model': self.target_model,
            'summary_text': self.summary_text,
            'final_prompt': self.final_prompt,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'name': self.name,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptState':
        """Create from dictionary."""
        return cls(
            field_values=data.get('field_values', {}),
            field_tags=cls._deserialize_tags(data.get('field_tags', {})),
            seed=data.get('seed', 0),
            filters=data.get('filters', []),
            llm_model=data.get('llm_model', ''),
            target_model=data.get('target_model', ''),
            summary_text=data.get('summary_text', ''),
            final_prompt=data.get('final_prompt', ''),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            name=data.get('name', ''),
            description=data.get('description', '')
        )
    
    def _serialize_tags(self) -> Dict[str, List[Dict[str, Any]]]:
        """Serialize tag objects to dictionaries."""
        serialized = {}
        for field_name, tags in self.field_tags.items():
            serialized[field_name] = []
            for tag in tags:
                if hasattr(tag, 'to_dict'):
                    serialized[field_name].append(tag.to_dict())
                else:
                    # Fallback for tag objects without to_dict method
                    serialized[field_name].append({
                        'text': getattr(tag, 'text', str(tag)),
                        'tag_type': getattr(tag, 'tag_type', 'unknown'),
                        'category_path': getattr(tag, 'category_path', []),
                        'data': getattr(tag, 'data', None),
                        'is_missing': getattr(tag, 'is_missing', False)
                    })
        return serialized
    
    @classmethod
    def _deserialize_tags(cls, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Any]]:
        """Deserialize tag dictionaries back to tag objects."""
        try:
            # Import Tag class here to avoid circular imports
            from ..gui.tag_widgets_qt import Tag
            
            deserialized = {}
            for field_name, tag_data_list in data.items():
                deserialized[field_name] = []
                for tag_data in tag_data_list:
                    if isinstance(tag_data, dict) and 'tag_type' in tag_data:
                        # Create Tag object from dictionary
                        tag = Tag.from_dict(tag_data)
                        deserialized[field_name].append(tag)
                    else:
                        # Fallback for unknown tag format
                        deserialized[field_name].append(tag_data)
            return deserialized
        except ImportError:
            # If Tag class is not available, return raw data
            return data
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
    
    def get_field_value(self, field_name: str) -> str:
        """Get the display value for a field."""
        return self.field_values.get(field_name, '')
    
    def set_field_value(self, field_name: str, value: str):
        """Set the display value for a field."""
        self.field_values[field_name] = value
        self.update_timestamp()
    
    def get_field_tags(self, field_name: str) -> List[Any]:
        """Get the tags for a field."""
        return self.field_tags.get(field_name, [])
    
    def set_field_tags(self, field_name: str, tags: List[Any]):
        """Set the tags for a field."""
        self.field_tags[field_name] = tags
        self.update_timestamp()
    
    def is_empty(self) -> bool:
        """Check if the state has any content."""
        return not any(self.field_values.values()) and not any(self.field_tags.values())
    
    def copy(self) -> 'PromptState':
        """Create a deep copy of this state."""
        return PromptState(
            field_values=self.field_values.copy(),
            field_tags={k: v.copy() for k, v in self.field_tags.items()},
            seed=self.seed,
            filters=self.filters.copy(),
            llm_model=self.llm_model,
            target_model=self.target_model,
            summary_text=self.summary_text,
            final_prompt=self.final_prompt,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            description=self.description
        )
