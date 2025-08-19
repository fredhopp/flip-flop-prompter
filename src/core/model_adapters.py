"""
Model-specific adapters for prompt formatting.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .data_models import PromptData


class ModelAdapter(ABC):
    """Abstract base class for model-specific prompt adapters."""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Adapter', '').lower()
        self.description = f"Adapter for {self.name} model"
    
    @abstractmethod
    def format_prompt(self, prompt_data: PromptData) -> str:
        """Format prompt data for this specific model."""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about this model."""
        return {
            'name': self.name,
            'description': self.description,
            'supported_features': self.get_supported_features()
        }
    
    def get_supported_features(self) -> List[str]:
        """Get list of features supported by this model."""
        return ['basic_prompt', 'camera_specs', 'lighting', 'style']
    
    def validate_for_model(self, prompt_data: PromptData) -> List[str]:
        """Validate prompt data for this specific model."""
        return []  # Default: no model-specific validation


class SeedreamAdapter(ModelAdapter):
    """Adapter for Seedream 3.0 model based on technical documentation."""
    
    def __init__(self):
        super().__init__()
        self.name = "seedream"
        self.description = "Adapter for Seedream 3.0 text-to-video model"
    
    def format_prompt(self, prompt_data: PromptData) -> str:
        """
        Format prompt for Seedream 3.0.
        
        Based on Seedream technical documentation, the model responds well to:
        - Detailed scene descriptions
        - Specific camera movements
        - Lighting and atmospheric details
        - Character actions and interactions
        """
        parts = []
        
        # Scene setting
        if prompt_data.setting:
            parts.append(f"Scene: {prompt_data.setting}")
        
        if prompt_data.weather:
            parts.append(f"Atmosphere: {prompt_data.weather}")
        
        if prompt_data.date_time:
            parts.append(f"Time: {prompt_data.date_time}")
        
        # Subjects and actions
        if prompt_data.subjects:
            parts.append(f"Characters: {prompt_data.subjects}")
        
        if prompt_data.pose_action:
            parts.append(f"Action: {prompt_data.pose_action}")
        
        # Camera and technical details
        if prompt_data.camera:
            parts.append(f"Technical: {prompt_data.camera}")
        
        if prompt_data.framing_action:
            parts.append(f"Camera Movement: {prompt_data.framing_action}")
        
        # Visual style
        if prompt_data.grading:
            parts.append(f"Visual Style: {prompt_data.grading}")
        
        # Seedream-specific enhancements
        parts.append("High quality, cinematic, professional lighting")
        
        return ", ".join(parts)
    
    def get_supported_features(self) -> List[str]:
        return ['basic_prompt', 'camera_specs', 'lighting', 'style', 'cinematic', 'professional']


class VeoAdapter(ModelAdapter):
    """Adapter for Google's Veo model."""
    
    def __init__(self):
        super().__init__()
        self.name = "veo"
        self.description = "Adapter for Google Veo text-to-video model"
    
    def format_prompt(self, prompt_data: PromptData) -> str:
        """
        Format prompt for Veo model.
        
        Veo is known for:
        - High-quality video generation
        - Good understanding of complex scenes
        - Responsive to detailed descriptions
        """
        parts = []
        
        # Build a natural language description
        scene_desc = []
        
        if prompt_data.setting:
            scene_desc.append(prompt_data.setting)
        
        if prompt_data.weather:
            scene_desc.append(f"with {prompt_data.weather}")
        
        if prompt_data.date_time:
            scene_desc.append(f"at {prompt_data.date_time}")
        
        if scene_desc:
            parts.append(" ".join(scene_desc))
        
        # Subjects and actions
        if prompt_data.subjects and prompt_data.pose_action:
            parts.append(f"{prompt_data.subjects} {prompt_data.pose_action}")
        elif prompt_data.subjects:
            parts.append(prompt_data.subjects)
        elif prompt_data.pose_action:
            parts.append(prompt_data.pose_action)
        
        # Camera details
        if prompt_data.camera:
            parts.append(f"Shot with {prompt_data.camera}")
        
        if prompt_data.framing_action:
            parts.append(prompt_data.framing_action)
        
        # Style
        if prompt_data.grading:
            parts.append(prompt_data.grading)
        
        return ". ".join(parts) + "."
    
    def get_supported_features(self) -> List[str]:
        return ['basic_prompt', 'camera_specs', 'lighting', 'style', 'natural_language']


class FluxAdapter(ModelAdapter):
    """Adapter for Stability AI's Flux model."""
    
    def __init__(self):
        super().__init__()
        self.name = "flux"
        self.description = "Adapter for Stability AI Flux text-to-video model"
    
    def format_prompt(self, prompt_data: PromptData) -> str:
        """
        Format prompt for Flux model.
        
        Flux characteristics:
        - Creative and artistic output
        - Good with stylized content
        - Responsive to artistic direction
        """
        parts = []
        
        # Artistic scene description
        if prompt_data.setting:
            parts.append(f"Set in {prompt_data.setting}")
        
        if prompt_data.weather:
            parts.append(f"with {prompt_data.weather} lighting")
        
        if prompt_data.date_time:
            parts.append(f"during {prompt_data.date_time}")
        
        # Characters and action
        if prompt_data.subjects:
            parts.append(f"featuring {prompt_data.subjects}")
        
        if prompt_data.pose_action:
            parts.append(f"where {prompt_data.pose_action}")
        
        # Technical specifications
        if prompt_data.camera:
            parts.append(f"captured on {prompt_data.camera}")
        
        if prompt_data.framing_action:
            parts.append(f"with {prompt_data.framing_action}")
        
        # Artistic style
        if prompt_data.grading:
            parts.append(f"styled with {prompt_data.grading}")
        
        # Flux-specific enhancements
        parts.append("artistic, creative, visually stunning")
        
        return ", ".join(parts)
    
    def get_supported_features(self) -> List[str]:
        return ['basic_prompt', 'camera_specs', 'lighting', 'style', 'artistic', 'creative']


class WanAdapter(ModelAdapter):
    """Adapter for Wan video generation model."""
    
    def __init__(self):
        super().__init__()
        self.name = "wan"
        self.description = "Adapter for Wan text-to-video model"
    
    def format_prompt(self, prompt_data: PromptData) -> str:
        """
        Format prompt for Wan model.
        
        Wan model characteristics:
        - Focus on realistic video generation
        - Good with human interactions
        - Responsive to detailed scene descriptions
        """
        parts = []
        
        # Detailed scene description
        if prompt_data.setting:
            parts.append(f"Location: {prompt_data.setting}")
        
        if prompt_data.weather:
            parts.append(f"Conditions: {prompt_data.weather}")
        
        if prompt_data.date_time:
            parts.append(f"Time: {prompt_data.date_time}")
        
        # Human elements
        if prompt_data.subjects:
            parts.append(f"People: {prompt_data.subjects}")
        
        if prompt_data.pose_action:
            parts.append(f"Activity: {prompt_data.pose_action}")
        
        # Technical details
        if prompt_data.camera:
            parts.append(f"Equipment: {prompt_data.camera}")
        
        if prompt_data.framing_action:
            parts.append(f"Movement: {prompt_data.framing_action}")
        
        # Visual treatment
        if prompt_data.grading:
            parts.append(f"Look: {prompt_data.grading}")
        
        # Wan-specific enhancements
        parts.append("realistic, natural, high quality")
        
        return " | ".join(parts)
    
    def get_supported_features(self) -> List[str]:
        return ['basic_prompt', 'camera_specs', 'lighting', 'style', 'realistic', 'natural']


class HailuoAdapter(ModelAdapter):
    """Adapter for Hailuo text-to-video model."""
    
    def __init__(self):
        super().__init__()
        self.name = "hailuo"
        self.description = "Adapter for Hailuo text-to-video model"
    
    def format_prompt(self, prompt_data: PromptData) -> str:
        """
        Format prompt for Hailuo model.
        
        Hailuo characteristics:
        - Versatile video generation
        - Good with various styles
        - Responsive to comprehensive descriptions
        """
        parts = []
        
        # Comprehensive scene description
        scene_elements = []
        
        if prompt_data.setting:
            scene_elements.append(prompt_data.setting)
        
        if prompt_data.weather:
            scene_elements.append(prompt_data.weather)
        
        if prompt_data.date_time:
            scene_elements.append(f"at {prompt_data.date_time}")
        
        if scene_elements:
            parts.append("Scene: " + ", ".join(scene_elements))
        
        # Character and action description
        if prompt_data.subjects and prompt_data.pose_action:
            parts.append(f"Action: {prompt_data.subjects} {prompt_data.pose_action}")
        elif prompt_data.subjects:
            parts.append(f"Subjects: {prompt_data.subjects}")
        elif prompt_data.pose_action:
            parts.append(f"Action: {prompt_data.pose_action}")
        
        # Technical specifications
        tech_specs = []
        if prompt_data.camera:
            tech_specs.append(prompt_data.camera)
        if prompt_data.framing_action:
            tech_specs.append(prompt_data.framing_action)
        
        if tech_specs:
            parts.append("Technical: " + ", ".join(tech_specs))
        
        # Visual style
        if prompt_data.grading:
            parts.append(f"Style: {prompt_data.grading}")
        
        # Hailuo-specific enhancements
        parts.append("high quality, detailed, professional")
        
        return " | ".join(parts)
    
    def get_supported_features(self) -> List[str]:
        return ['basic_prompt', 'camera_specs', 'lighting', 'style', 'versatile', 'detailed']


def get_model_adapter(model_name: str) -> ModelAdapter:
    """Get the appropriate model adapter for the given model name."""
    adapters = {
        'seedream': SeedreamAdapter,
        'veo': VeoAdapter,
        'flux': FluxAdapter,
        'wan': WanAdapter,
        'hailuo': HailuoAdapter
    }
    
    adapter_class = adapters.get(model_name.lower())
    if adapter_class:
        return adapter_class()
    else:
        # Default to SeedreamAdapter if model not found
        return SeedreamAdapter()
