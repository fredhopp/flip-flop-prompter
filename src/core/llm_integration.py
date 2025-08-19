"""
LLM integration for prompt refinement and optimization.
"""

import json
import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import requests
from .data_models import PromptData


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def refine_prompt(self, prompt_data: PromptData, model_name: str, target_model: str) -> str:
        """Refine prompt data into a cohesive, model-optimized prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model_name: str = "deepseek-r1:8b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.model_name in model.get("name", "") for model in models)
            return False
        except:
            return False
    
    def refine_prompt(self, prompt_data: PromptData, model_name: str, target_model: str, content_rating: str = "PG") -> str:
        """Refine prompt using Ollama."""
        
        # Create the system prompt
        system_prompt = self._create_system_prompt(target_model, content_rating)
        
        # Create the user prompt
        user_prompt = self._create_user_prompt(prompt_data, target_model)
        
        # Call Ollama API
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            raw_content = result["message"]["content"].strip()
            return self._clean_prompt_output(raw_content)
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _create_system_prompt(self, target_model: str, content_rating: str = "PG") -> str:
        """Create system prompt for the target model."""
        
        # Add content rating instructions
        content_instructions = ""
        if content_rating == "NSFW":
            content_instructions = """
CONTENT RATING: NSFW
- This prompt may contain adult content, nudity, or mature themes
- Use appropriate language and descriptions for adult content
- Maintain artistic and professional quality
"""
        elif content_rating == "Hentai":
            content_instructions = """
CONTENT RATING: HENTAI
- This prompt is for explicit adult content and hentai-style art
- Use explicit language and detailed descriptions for adult content
- Focus on artistic quality and detailed anatomy
- Include appropriate adult content descriptors
"""
        else:
            content_instructions = """
CONTENT RATING: PG
- Keep content family-friendly and appropriate for all audiences
- Avoid explicit language or adult content
- Focus on artistic and cinematic quality
"""
        
        model_guides = {
            "seedream": f"""
You are an expert prompt engineer specializing in Seedream 3.0 text-to-video generation.

{content_instructions}

SEEDREAM 3.0 GUIDELINES:
- Use detailed, cinematic descriptions
- Include specific camera movements and angles
- Emphasize lighting and atmospheric details
- Focus on character actions and interactions
- Use technical film terminology
- Keep prompts concise but descriptive
- Include quality modifiers like "high quality", "cinematic", "professional lighting"

FORMAT: Natural, flowing description with technical details integrated naturally.
""",
            "veo": f"""
You are an expert prompt engineer specializing in Google Veo text-to-video generation.

{content_instructions}

VEO GUIDELINES:
- Use natural, conversational language
- Focus on scene composition and storytelling
- Include emotional context and atmosphere
- Be specific about character details and actions
- Use descriptive but accessible language
- Emphasize visual quality and realism

FORMAT: Flowing narrative style with natural transitions.
""",
            "flux": f"""
You are an expert prompt engineer specializing in Stability AI Flux text-to-video generation.

{content_instructions}

FLUX GUIDELINES:
- Emphasize artistic and creative elements
- Use stylized and expressive language
- Focus on visual aesthetics and mood
- Include artistic direction and style references
- Be creative with descriptions and metaphors
- Emphasize unique visual qualities

FORMAT: Artistic, expressive descriptions with creative flair.
""",
            "wan": f"""
You are an expert prompt engineer specializing in Wan text-to-video generation.

{content_instructions}

WAN GUIDELINES:
- Focus on realistic and natural scenes
- Emphasize human interactions and emotions
- Use detailed, precise descriptions
- Include environmental and atmospheric details
- Focus on authenticity and believability
- Use clear, straightforward language

FORMAT: Realistic, detailed descriptions with natural flow.
""",
            "hailuo": f"""
You are an expert prompt engineer specializing in Hailuo text-to-video generation.

{content_instructions}

HAILUO GUIDELINES:
- Use comprehensive, detailed descriptions
- Include multiple visual elements and layers
- Emphasize technical precision and quality
- Focus on versatility and adaptability
- Use structured but natural language
- Include quality and style specifications

FORMAT: Comprehensive, detailed descriptions with technical precision.
"""
        }
        
        return model_guides.get(target_model.lower(), """
You are an expert prompt engineer for AI text-to-video generation.
Create natural, cohesive prompts that flow well and are optimized for the target model.
""")
    
    def _create_user_prompt(self, prompt_data: PromptData, target_model: str) -> str:
        """Create user prompt from prompt data."""
        
        parts = []
        
        # Build scene description
        scene_elements = []
        if prompt_data.environment:
            scene_elements.append(f"Environment: {prompt_data.environment}")
        if prompt_data.weather:
            scene_elements.append(f"Weather: {prompt_data.weather}")
        if prompt_data.date_time:
            scene_elements.append(f"Time: {prompt_data.date_time}")
        
        if scene_elements:
            parts.append("Scene: " + ", ".join(scene_elements))
        
        # Add subjects and actions
        if prompt_data.subjects:
            parts.append(f"Subjects: {prompt_data.subjects}")
        if prompt_data.pose_action:
            parts.append(f"Action: {prompt_data.pose_action}")
        
        # Add technical details
        if prompt_data.camera:
            parts.append(f"Camera: {prompt_data.camera}")
        if prompt_data.framing_action:
            parts.append(f"Camera Movement: {prompt_data.framing_action}")
        
        # Add style
        if prompt_data.grading:
            parts.append(f"Style: {prompt_data.grading}")
        
        raw_prompt = "\n".join(parts)
        
        return f"""
Please refine this raw prompt data into a cohesive, natural prompt optimized for {target_model.upper()}:

RAW PROMPT DATA:
{raw_prompt}

Create a single, flowing prompt that incorporates all the elements naturally and is optimized for {target_model.upper()}. 
Make it sound natural and professional, not like a list of components.
"""
    
    def _clean_prompt_output(self, raw_content: str) -> str:
        """Clean the raw LLM output to extract only the actual prompt."""
        
        # Remove <think> sections
        import re
        
        # Remove <think>...</think> blocks
        content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL)
        
        # Normalize smart quotes and dashes to ASCII
        content = content.replace('\u2019', "'").replace('’', "'")
        content = content.replace('\u201C', '"').replace('\u201D', '"').replace('“', '"').replace('”', '"')
        content = content.replace('\u2013', '-').replace('\u2014', '-').replace('—', '-')
        
        # Remove markdown formatting
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Remove **bold**
        content = re.sub(r'\*([^*]+)\*', r'\1', content)      # Remove *italic*
        content = re.sub(r'__([^_]+)__', r'\1', content)      # Remove __underline__
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Okay, here is a refined prompt:",
            "Here's a refined prompt:",
            "Here is the refined prompt:",
            "**Prompt:**",
            "Prompt:",
            "### Optimized Prompt",
            "### Prompt",
            "**Optimized Prompt**",
            "**Prompt**",
            "Okay, here are a couple of flowing options optimized for",
            "Okay, here's a refined prompt designed for",
            "Okay, here's that raw data synthesized into a single, flowing prompt optimized for",
            "Okay, here is the refined"
        ]
        
        for prefix in prefixes_to_remove:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes_to_remove = [
            "### Breakdown of how this fits",
            "### Breakdown",
            "Breakdown:",
            "This prompt incorporates",
            "The prompt follows",
            "Key elements:",
            "Elements included:",
            "---Why this works for",
            "To help me refine this further",
            "Natural Language:",
            "Scene Composition:",
            "Emotional Context:",
            "Character Detail:",
            "Descriptive Language:",
            "Emphasis on Visual Quality:",
            "Narrative Flow:",
            "Detailed Cinematic Language:",
            "Technical Film Terminology:",
            "Lighting Emphasis:",
            "Character Focus:",
            "Quality Modifiers:",
            "Breakdown of why it works:",
            "Rationale & Why This Works for FLUX:",
            "Rationale & Why This Works:"
        ]
        
        for suffix in suffixes_to_remove:
            if suffix in content:
                content = content.split(suffix)[0].strip()
        
        # Clean up extra whitespace and newlines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Remove excessive newlines
        content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)  # Trim lines
        
        # Remove everything after "---" (common in gemma3 outputs)
        if '---' in content:
            content = content.split('---')[0].strip()
        
        # Remove everything after "To help me refine" (gemma3 follow-up questions)
        if 'To help me refine' in content:
            content = content.split('To help me refine')[0].strip()
        
        # Handle multiple options format (deepseek)
        if 'Option 1' in content and 'Option 2' in content:
            # Take the first option and clean it
            option1_start = content.find('Option 1')
            option2_start = content.find('Option 2')
            content = content[option1_start:option2_start].strip()
            # Remove "Option 1 (Focus on Mood first):" prefix
            content = re.sub(r'^Option 1.*?:', '', content).strip()
        
        # Remove specific patterns from deepseek output
        content = re.sub(r'^Refined Prompt:', '', content).strip()
        
        # Remove specific patterns from gemma3 output
        content = re.sub(r'^Prompt:', '', content).strip()
        
        # Remove common patterns with regex
        content = re.sub(r'^Okay, here is the refined.*?Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined.*?cinematic description:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here is that raw information synthesized.*?Optimized Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here is a refined.*?Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here is a refined prompt incorporating.*?:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt for.*?Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt designed for.*?cinematic description:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined.*?prompt incorporating.*?naturally:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt for.*?designed to leverage.*?Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt incorporating.*?naturally for.*?Refined Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt for.*?designed to leverage.*?based on your raw data:Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt for.*?designed to leverage.*?adhere to the guidelines.*?result:Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt for.*?designed to leverage.*?system\'s strengths.*?cinematic scene:Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt for.*?designed to leverage.*?platform\'s strengths.*?cinematic result:Prompt:', '', content, flags=re.DOTALL).strip()
        
        # Remove everything after "Reasoning:" or "Breakdown:"
        if 'Reasoning:' in content:
            content = content.split('Reasoning:')[0].strip()
        if 'Breakdown:' in content:
            content = content.split('Breakdown:')[0].strip()
        
        # Handle FLUX-style intro lines
        content = re.sub(r"^Okay, let[\'’]s translate .*? refined version:.*?Prompt:", '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^.*?\bFLUX Prompt:\s*', '', content, flags=re.DOTALL).strip()

        # Generic catch-alls for intro patterns
        content = re.sub(r"^Okay, here[\'’]s.*?Prompt:", '', content, flags=re.DOTALL).strip()
        content = re.sub(r"^Okay, let[\'’]s.*?Prompt:", '', content, flags=re.DOTALL).strip()
        content = re.sub(r"^Here[\'’]s the refined version:.*?Prompt:", '', content, flags=re.DOTALL).strip()

        # Remove leading model label like "SEEDREAM Prompt:" or "HAILUO Prompt:"
        content = re.sub(r'^[A-Z][A-Za-z ]+ Prompt:\s*', '', content).strip()
        content = re.sub(r'^Okay, here\'s a refined, cohesive prompt.*?designed to leverage.*?capabilities.*?video:Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined, cohesive prompt.*?incorporating.*?elements.*?style.*?detail:Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined, cohesive prompt.*?designed for.*?incorporating.*?elements.*?storytelling\.HAILUO Prompt:', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'^Okay, here\'s a refined prompt optimized for.*?designed to produce.*?raw data\. I\'ve focused.*?capabilities for detail and quality\.', '', content, flags=re.DOTALL).strip()
        
        # Remove everything before the first quote if it starts with a quote
        if content.startswith('"'):
            # Find the end of the first quoted section
            quote_end = content.find('"', 1)
            if quote_end != -1:
                content = content[1:quote_end].strip()
        
        # Remove trailing quotes if they exist (including smart quotes)
        content = re.sub(r'^["\u201C\u201D\'](.*?)["\u201C\u201D\']$', r'\1', content).strip()
        
        return content.strip()





class LLMManager:
    """Manager for LLM providers."""
    
    def __init__(self, preferred_provider: str = "auto", llm_model: str = "deepseek-r1:8b"):
        self.preferred_provider = preferred_provider
        self.llm_model = llm_model
        self.providers = {
            "ollama": OllamaProvider(model_name=llm_model)
        }
        self.active_provider = None
        self._select_provider()
    
    def _select_provider(self):
        """Select the best available provider."""
        if self.preferred_provider == "auto":
            # Try Ollama (local, free)
            if self.providers["ollama"].is_available():
                self.active_provider = self.providers["ollama"]
            else:
                self.active_provider = None
        else:
            self.active_provider = self.providers.get(self.preferred_provider)
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        return self.active_provider is not None
    
    def refine_prompt(self, prompt_data: PromptData, model_name: str, target_model: str, content_rating: str = "PG") -> str:
        """Refine prompt using the active provider."""
        if not self.active_provider:
            raise Exception("No LLM provider available. Install Ollama to use LLM features.")
        
        return self.active_provider.refine_prompt(prompt_data, model_name, target_model, content_rating)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the active provider."""
        if not self.active_provider:
            return {"available": False, "provider": None}
        
        return {
            "available": True,
            "provider": self.active_provider.__class__.__name__,
            "ollama_available": self.providers["ollama"].is_available()
        }
    
    def update_llm_model(self, model_name: str):
        """Update the LLM model being used."""
        self.llm_model = model_name
        if self.active_provider and hasattr(self.active_provider, 'model_name'):
            self.active_provider.model_name = model_name
