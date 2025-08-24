"""
Core prompt generation engine for FlipFlopPrompt.
"""

import json
from typing import Dict, Any, Optional, List
from .data_models import PromptData
from .model_adapters import ModelAdapter
from .llm_integration import LLMManager
from ..utils.logger import debug, info, warning, error, LogArea


class PromptEngine:
    """Main engine for generating prompts for different AI models."""
    
    def __init__(self, use_llm: bool = True):
        self.model_adapters: Dict[str, ModelAdapter] = {}
        self.use_llm = use_llm
        self.llm_manager = LLMManager() if use_llm else None
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """Initialize model-specific adapters."""
        from .model_adapters import (
            SeedreamAdapter, VeoAdapter, FluxAdapter, 
            WanAdapter, HailuoAdapter
        )
        
        self.model_adapters = {
            'seedream': SeedreamAdapter(),
            'veo': VeoAdapter(),
            'flux': FluxAdapter(),
            'wan': WanAdapter(),
            'hailuo': HailuoAdapter()
        }
    
    def generate_prompt(self, model: str, prompt_data: PromptData, content_rating: str = "PG", debug_enabled: bool = False, llm_model: str = None) -> str:
        """
        Generate a formatted prompt for the specified model.

        Args:
            model: Target model name (seedream, veo, flux, wan, hailuo)
            prompt_data: Prompt components data
            content_rating: Content rating (PG, NSFW, Hentai)
            debug_enabled: Whether to enable debug file generation
            llm_model: Specific LLM model to use for refinement (optional)

        Returns:
            Formatted prompt string
        """
        if model.lower() not in self.model_adapters:
            raise ValueError(f"Unsupported model: {model}")

        # Try LLM refinement first if available
        if self.use_llm and self.llm_manager and self.llm_manager.is_available():
            try:
                # Pass the llm_model parameter to refine_prompt
                return self.llm_manager.refine_prompt(prompt_data, llm_model, model, content_rating, debug_enabled)
            except Exception as e:
                # Fall back to adapter if LLM fails
                info(r"LLM refinement failed, using adapter: {str(e)}", LogArea.GENERAL)

        # Use model adapter as fallback
        adapter = self.model_adapters[model.lower()]
        return adapter.format_prompt(prompt_data)
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        return list(self.model_adapters.keys())
    
    def is_llm_available(self) -> bool:
        """Check if LLM refinement is available."""
        return self.llm_manager is not None and self.llm_manager.is_available()
    
    def get_llm_info(self) -> Dict[str, Any]:
        """Get LLM provider information."""
        if self.llm_manager:
            return self.llm_manager.get_provider_info()
        return {"available": False, "provider": None}
    
    def update_llm_model(self, model_name: str):
        """Update the LLM model being used."""
        if self.llm_manager:
            self.llm_manager.update_llm_model(model_name)
    
    def unload_llm_model(self, model_name: str = None) -> bool:
        """Unload the current LLM model to free up VRAM."""
        if self.llm_manager:
            return self.llm_manager.unload_model(model_name)
        return False
    
    def validate_prompt_data(self, prompt_data: PromptData) -> List[str]:
        """
        Validate prompt data and return list of validation errors.
        
        Args:
            prompt_data: Prompt data to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        if not prompt_data.setting.strip():
            errors.append("Setting is required")
        
        if not prompt_data.subjects.strip():
            errors.append("Subjects are required")
        
        if not prompt_data.pose_action.strip():
            errors.append("Subject pose and action is required")
        
        # Optional validation
        if prompt_data.setting and len(prompt_data.setting) < 3:
            errors.append("Setting description should be more detailed")
        
        if prompt_data.subjects and len(prompt_data.subjects) < 5:
            errors.append("Subject description should be more detailed")
        
        return errors
    
    def get_prompt_preview(self, prompt_data: PromptData) -> str:
        """
        Generate a basic preview of the prompt without model-specific formatting.
        
        Args:
            prompt_data: Prompt components data
            
        Returns:
            Basic prompt preview
        """
        parts = []
        
        # Setting and weather
        if prompt_data.setting:
            parts.append(f"Setting: {prompt_data.setting}")
        if prompt_data.weather:
            parts.append(f"Weather: {prompt_data.weather}")
        
        # Time
        if prompt_data.date_time:
            parts.append(f"Time: {prompt_data.date_time}")
        
        # Subjects and actions
        if prompt_data.subjects:
            parts.append(f"Subjects: {prompt_data.subjects}")
        if prompt_data.pose_action:
            parts.append(f"Action: {prompt_data.pose_action}")
        
        # Camera details
        if prompt_data.camera:
            parts.append(f"Camera: {prompt_data.camera}")
        if prompt_data.framing_action:
            parts.append(f"Camera Action: {prompt_data.framing_action}")
        
        # Grading
        if prompt_data.grading:
            parts.append(f"Style: {prompt_data.grading}")
        
        return "\n".join(parts)
    
    def export_prompt_data(self, prompt_data: PromptData, format: str = 'json') -> str:
        """
        Export prompt data in specified format.
        
        Args:
            prompt_data: Prompt data to export
            format: Export format ('json', 'text', 'yaml')
            
        Returns:
            Exported data as string
        """
        if format.lower() == 'json':
            return json.dumps(prompt_data.to_dict(), indent=2)
        elif format.lower() == 'text':
            return self.get_prompt_preview(prompt_data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_prompt_data(self, data: str, format: str = 'json') -> PromptData:
        """
        Import prompt data from specified format.
        
        Args:
            data: Data to import
            format: Import format ('json', 'text', 'yaml')
            
        Returns:
            PromptData object
        """
        if format.lower() == 'json':
            return PromptData.from_dict(json.loads(data))
        else:
            raise ValueError(f"Unsupported import format: {format}")
