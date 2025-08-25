"""
LLM integration for FlipFlopPrompt.
"""

import json
import os
import requests
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from ..utils.logger import debug, info, warning, error, LogArea
from .data_models import PromptData
from datetime import datetime


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def refine_prompt(self, prompt_data: PromptData, model_name: str, target_model: str, content_rating: str = "PG", debug_enabled: bool = False) -> str:
        """Refine prompt data into a cohesive, model-optimized prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model_name: str = None, base_url: str = "http://localhost:11434", process_tracker=None):
        self.model_name = model_name
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure session for better reliability
        self.session.headers.update({
            'User-Agent': 'FlipFlopPrompt/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Set connection pooling and retry settings
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=1,  # Only retry once to avoid long delays
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.process_tracker = process_tracker  # Callback to check if Ollama process is tracked
        
        # Create debug directory in user data folder
        self.debug_dir = Path.home() / "AppData" / "Roaming" / "FlipFlopPrompt" / "debug"
        self.debug_dir.mkdir(parents=True, exist_ok=True)
    
    def is_available(self) -> bool:
        """Check if Ollama is available and the specified model is loaded."""
        import time
        check_start = time.time()
        
        try:
            debug(f"Checking availability from {self.base_url}/api/tags", LogArea.OLLAMA)
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            debug(f"Availability check response status: {response.status_code}", LogArea.OLLAMA)
            
            if response.status_code == 200:
                data = response.json()
                debug(f"Availability check response data keys: {list(data.keys())}", LogArea.OLLAMA)
                models = data.get('models', [])
                debug(f"Availability check models: {models}", LogArea.OLLAMA)
                
                # If no specific model is required, just check if Ollama is running
                if self.model_name is None:
                    debug("No model specified, checking if Ollama is running", LogArea.OLLAMA)
                    check_time = time.time() - check_start
                    info(f"STARTUP: Ollama availability check took {check_time:.3f}s", LogArea.GENERAL)
                    return True
                
                # Check if the specific model is available
                model_found = any(model.get('name') == self.model_name for model in models)
                debug(f"Model '{self.model_name}' found: {model_found}", LogArea.OLLAMA)
                check_time = time.time() - check_start
                info(f"STARTUP: Ollama availability check took {check_time:.3f}s", LogArea.GENERAL)
                return model_found
            else:
                debug(f"Availability check failed - status {response.status_code}: {response.text}", LogArea.OLLAMA)
                check_time = time.time() - check_start
                info(f"STARTUP: Ollama availability check (failed) took {check_time:.3f}s", LogArea.GENERAL)
                return False
        except Exception as e:
            debug(f"Exception in availability check: {str(e)}", LogArea.OLLAMA)
            check_time = time.time() - check_start
            info(f"STARTUP: Ollama availability check (exception) took {check_time:.3f}s", LogArea.GENERAL)
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        import time
        models_start = time.time()
        
        try:
            debug(f"Getting available models from {self.base_url}/api/tags", LogArea.OLLAMA)
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            debug(f"Response status: {response.status_code}", LogArea.OLLAMA)
            
            if response.status_code == 200:
                data = response.json()
                debug(f"Response data keys: {list(data.keys())}", LogArea.OLLAMA)
                models = data.get('models', [])
                debug(f"Raw models data: {models}", LogArea.OLLAMA)
                debug(f"Number of models in raw data: {len(models)}", LogArea.OLLAMA)
                
                model_names = [model.get('name', '') for model in models if model.get('name')]
                debug(f"Extracted model names: {model_names}", LogArea.OLLAMA)
                debug(f"Number of models extracted: {len(model_names)}", LogArea.OLLAMA)
                debug(f"About to return model names: {model_names}", LogArea.OLLAMA)
                
                models_time = time.time() - models_start
                info(f"STARTUP: Ollama get_available_models took {models_time:.3f}s", LogArea.GENERAL)
                return model_names
            else:
                debug(f"Failed to get models - status {response.status_code}: {response.text}", LogArea.OLLAMA)
                models_time = time.time() - models_start
                info(f"STARTUP: Ollama get_available_models (failed) took {models_time:.3f}s", LogArea.GENERAL)
                return []
        except Exception as e:
            debug(f"Exception getting available models: {str(e)}", LogArea.OLLAMA)
            models_time = time.time() - models_start
            info(f"STARTUP: Ollama get_available_models (exception) took {models_time:.3f}s", LogArea.GENERAL)
            return []

    def unload_model_from_vram(self, target_model: str) -> bool:
        """Attempt to unload a model from VRAM to free up memory."""
        try:
            debug(f"Attempting to unload model from VRAM: {target_model}", LogArea.OLLAMA)
            
            # Method 1: Try the unload API endpoint
            try:
                response = requests.post(
                    f"{self.base_url}/api/unload",
                    json={"name": target_model},
                    timeout=10
                )
                
                if response.status_code == 200:
                    debug(f"Successfully unloaded model from VRAM: {target_model}", LogArea.OLLAMA)
                    return True
                else:
                    debug(f"Method 1 failed, trying chat API...", LogArea.OLLAMA)
                    
            except Exception as e:
                debug(f"Method 1 failed, trying chat API...", LogArea.OLLAMA)
            
            # Method 2: Try using the chat API with a minimal request to trigger unloading
            try:
                # Send a minimal chat request that might trigger model unloading
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": target_model,
                        "messages": [{"role": "user", "content": "test"}],
                        "stream": False
                    },
                    timeout=5
                )
                
                # Even if this fails, it might have triggered unloading
                debug(f"Successfully unloaded model from VRAM using chat API: {target_model}", LogArea.OLLAMA)
                return True
                
            except Exception as e:
                # This is expected - the model might not be loaded or might be stuck
                pass
            
            # If we get here, the model might be stuck in VRAM (known Ollama issue)
            debug(f"Failed to unload model {target_model} - known Ollama VRAM issue", LogArea.OLLAMA)
            debug("Model may be stuck in VRAM. Consider restarting Ollama service.", LogArea.OLLAMA)
            debug(f"Response: {response.status_code} - {response.text}", LogArea.OLLAMA)
            return False
            
        except Exception as e:
            debug(f"Error unloading model {target_model}: {str(e)}", LogArea.OLLAMA)
            return False
    
    def refine_prompt(self, prompt_data: PromptData, model_name: str, target_model: str, content_rating: str = "PG", debug_enabled: bool = False) -> str:
        """Refine prompt using Ollama."""
        
        # Add verbose debug logging
        debug("PROMPT: LLM refine_prompt() called", LogArea.PROMPT)
        debug(f"PROMPT: model_name parameter: {model_name}", LogArea.PROMPT)
        debug(f"PROMPT: self.model_name: {self.model_name}", LogArea.PROMPT)
        debug(f"PROMPT: target_model: {target_model}", LogArea.PROMPT)
        debug(f"PROMPT: content_rating: {content_rating}", LogArea.PROMPT)
        
        # Use the model_name parameter if provided, otherwise use self.model_name
        # If both are None, we can't proceed
        llm_model = model_name if model_name is not None else self.model_name
        debug(f"PROMPT: Using LLM model: {llm_model}", LogArea.PROMPT)
        
        # Create debug folder with timestamp if debug is enabled
        debug_folder = None
        if debug_enabled:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            debug_folder = self.debug_dir / timestamp
            debug_folder.mkdir(exist_ok=True)
            debug(f"PROMPT: Created debug folder: {debug_folder}", LogArea.PROMPT)
        
        # Check if custom LLM instructions are provided
        if prompt_data.llm_instructions.strip():
            debug(f"PROMPT: Using custom LLM instructions: '{prompt_data.llm_instructions[:100]}{'...' if len(prompt_data.llm_instructions) > 100 else ''}'", LogArea.PROMPT)
            # Parse custom instruction (check for special format: name|content)
            if '|' in prompt_data.llm_instructions:
                # Extract content from instruction tag format
                instruction_content = prompt_data.llm_instructions.split('|', 1)[1]
                debug(f"PROMPT: Extracted instruction content from tag format", LogArea.PROMPT)
            else:
                # Use as-is if not in special format
                instruction_content = prompt_data.llm_instructions
                debug(f"PROMPT: Using instruction content as-is", LogArea.PROMPT)
            
            # Replace placeholders in the instruction with actual data
            custom_instruction = instruction_content.format(
                setting=prompt_data.setting,
                weather=prompt_data.weather,
                date_time=prompt_data.date_time,
                subjects=prompt_data.subjects,
                pose_action=prompt_data.pose_action,
                camera=prompt_data.camera,
                framing_action=prompt_data.framing_action,
                grading=prompt_data.grading,
                style=prompt_data.style,
                details=prompt_data.details
            )
            debug(f"PROMPT: Custom instruction with placeholders replaced", LogArea.PROMPT)
            
            # Add content rating information to custom instruction
            content_rating_note = ""
            if content_rating == "NSFW":
                content_rating_note = "\n\nCONTENT RATING: NSFW - This prompt may contain adult content, nudity, or mature themes."
            elif content_rating == "Hentai":
                content_rating_note = "\n\nCONTENT RATING: HENTAI - This prompt is for explicit adult content and hentai-style art."
            else:
                content_rating_note = "\n\nCONTENT RATING: PG - Keep content family-friendly and appropriate for all audiences."
            
            system_prompt = custom_instruction + content_rating_note
            debug(f"PROMPT: Using custom system prompt with content rating", LogArea.PROMPT)
        else:
            # Use default system prompt
            debug(f"PROMPT: No custom LLM instructions, using default system prompt", LogArea.PROMPT)
            system_prompt = self._create_system_prompt(target_model, content_rating)
        
        # Create the user prompt
        user_prompt = self._create_user_prompt(prompt_data, target_model)
        debug(f"PROMPT: Created user prompt, length: {len(user_prompt)}", LogArea.PROMPT)
        debug(f"PROMPT: User prompt: '{user_prompt[:200]}{'...' if len(user_prompt) > 200 else ''}'", LogArea.PROMPT)
        
        # Save debug files if enabled
        if debug_enabled and debug_folder:
            self._save_debug_file(debug_folder, "01_input_to_llm.txt", user_prompt)
            self._save_debug_file(debug_folder, "02_system_prompt.txt", system_prompt)
            debug(f"PROMPT: Saved debug files to {debug_folder}", LogArea.PROMPT)
        
        # Call Ollama API
        payload = {
            "model": llm_model,  # Use the validated model name
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
        
        debug("PROMPT: Preparing to call Ollama API", LogArea.PROMPT)
        debug(f"PROMPT: API endpoint: {self.base_url}/api/chat", LogArea.PROMPT)
        debug(f"PROMPT: Model: {llm_model}", LogArea.PROMPT)
        debug(f"PROMPT: Payload keys: {list(payload.keys())}", LogArea.PROMPT)
        
        # Check if we have a process tracker and if Ollama is running
        if self.process_tracker:
            debug("PROMPT: Checking process tracker before API call", LogArea.PROMPT)
            if not self.process_tracker():
                debug("PROMPT: Process tracker indicates Ollama is not running, attempting to start it", LogArea.PROMPT)
                # The process tracker should handle starting Ollama if needed
                # We'll continue with the API call and let it fail naturally if Ollama is still not available
        
        try:
            debug("PROMPT: Making POST request to Ollama API...", LogArea.PROMPT)
            api_start_time = time.time()
            
            response = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=30)
            
            api_time = time.time() - api_start_time
            debug(f"PROMPT: Ollama API call completed in {api_time:.2f} seconds", LogArea.PROMPT)
            
            debug(f"PROMPT: Received response - status: {response.status_code}", LogArea.PROMPT)
            
            response.raise_for_status()
            result = response.json()
            
            debug("PROMPT: Parsed JSON response", LogArea.PROMPT)
            debug(f"PROMPT: Response keys: {list(result.keys())}", LogArea.PROMPT)
            
            raw_content = result["message"]["content"].strip()
            
            debug(f"PROMPT: Extracted raw content (length: {len(raw_content)})", LogArea.PROMPT)
            
            # Save raw LLM output if debug is enabled
            if debug_enabled and debug_folder:
                self._save_debug_file(debug_folder, "03_raw_llm_output.txt", raw_content)
                debug(f"PROMPT: Saved raw LLM output to debug file", LogArea.PROMPT)
            
            # Clean and save final prompt
            final_prompt = self._clean_prompt_output(raw_content)
            
            debug(f"PROMPT: Cleaned final prompt (length: {len(final_prompt)})", LogArea.PROMPT)
            debug(f"PROMPT: Final prompt: '{final_prompt[:200]}{'...' if len(final_prompt) > 200 else ''}'", LogArea.PROMPT)
            
            if debug_enabled and debug_folder:
                self._save_debug_file(debug_folder, "04_final_prompt.txt", final_prompt)
                debug(f"PROMPT: Saved final prompt to debug file", LogArea.PROMPT)
            
            debug("PROMPT: Returning final prompt", LogArea.PROMPT)
            
            return final_prompt
        except requests.exceptions.Timeout:
            debug("PROMPT: Ollama API request timed out after 30 seconds", LogArea.PROMPT)
            if debug_enabled and debug_folder:
                error_info = f"Timeout Error: Request timed out after 30 seconds\nPayload: {json.dumps(payload, indent=2)}"
                self._save_debug_file(debug_folder, "timeout_error.txt", error_info)
            raise Exception("Ollama API request timed out. The server may be overloaded or unresponsive.")
        except requests.exceptions.ConnectionError as e:
            debug(f"PROMPT: Connection error to Ollama API: {str(e)}", LogArea.PROMPT)
            if debug_enabled and debug_folder:
                error_info = f"Connection Error: {str(e)}\nPayload: {json.dumps(payload, indent=2)}"
                self._save_debug_file(debug_folder, "connection_error.txt", error_info)
            raise Exception(f"Failed to connect to Ollama API: {str(e)}")
        except Exception as e:
            debug(f"PROMPT: Error occurred: {str(e)}", LogArea.PROMPT)
            
            # Save error information if debug is enabled
            if debug_enabled and debug_folder:
                error_info = f"Error: {str(e)}\nPayload: {json.dumps(payload, indent=2)}"
                self._save_debug_file(debug_folder, "error.txt", error_info)
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _save_debug_file(self, debug_folder: Path, filename: str, content: str):
        """Save debug content to a file."""
        try:
            filepath = debug_folder / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            warning(f"Could not save debug file {filename}: {e}", LogArea.OLLAMA)
    
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

IMPORTANT: Respond with ONLY the refined prompt. Do not include any introductory text, explanations, or meta-commentary. Start directly with the prompt content.

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

IMPORTANT: Respond with ONLY the refined prompt. Do not include any introductory text, explanations, or meta-commentary. Start directly with the prompt content.

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

IMPORTANT: Respond with ONLY the refined prompt. Do not include any introductory text, explanations, or meta-commentary. Start directly with the prompt content.

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

IMPORTANT: Respond with ONLY the refined prompt. Do not include any introductory text, explanations, or meta-commentary. Start directly with the prompt content.

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

IMPORTANT: Respond with ONLY the refined prompt. Do not include any introductory text, explanations, or meta-commentary. Start directly with the prompt content.

FORMAT: Comprehensive, detailed descriptions with technical precision.
"""
        }
        
        return model_guides.get(target_model.lower(), f"""
You are an expert prompt engineer for AI text-to-video generation.

{content_instructions}

IMPORTANT: Respond with ONLY the refined prompt. Do not include any introductory text, explanations, or meta-commentary. Start directly with the prompt content.

Create natural, cohesive prompts that flow well and are optimized for the target model.
""")
    
    def _create_user_prompt(self, prompt_data: PromptData, target_model: str) -> str:
        """Create user prompt from prompt data."""
        
        parts = []
        
        # Build scene description
        scene_elements = []
        if prompt_data.setting:
            scene_elements.append(f"Environment: {prompt_data.setting}")
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
            "Okay, here is the refined",
            "Okay,",
            "Here's",
            "Here is",
            "Here are",
            "I'll create",
            "I'll generate",
            "Let me create",
            "Let me generate",
            "I've created",
            "I've generated",
            "Here's a prompt:",
            "Here is a prompt:",
            "Here's the prompt:",
            "Here is the prompt:"
        ]
        
        for prefix in prefixes_to_remove:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # Also remove common patterns that might appear at the start
        # Remove "Okay" followed by any punctuation and common phrases
        content = re.sub(r'^Okay[,\s]*.*?(?:here|here\'s|here is|I\'ll|Let me|I\'ve).*?(?:prompt|create|generate)[:\s]*', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove any remaining "Okay," at the start
        content = re.sub(r'^Okay[,\s]*', '', content, flags=re.IGNORECASE)
        
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
        if '### Enhancements' in content:
            content = content.split('### Enhancements')[0].strip()
        if '###' in content:
            content = content.split('###')[0].strip()
        
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
    
    def __init__(self, preferred_provider: str = "auto", llm_model: str = None, process_tracker=None):
        self.preferred_provider = preferred_provider
        self.llm_model = llm_model
        self.process_tracker = process_tracker
        self.providers = {
            "ollama": OllamaProvider(model_name=llm_model, process_tracker=process_tracker)
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
    
    def refine_prompt(self, prompt_data: PromptData, model_name: str, target_model: str, content_rating: str = "PG", debug_enabled: bool = False) -> str:
        """Refine prompt using the active provider."""
        if not self.active_provider:
            raise Exception("No LLM provider available. Install Ollama to use LLM features.")
        
        # Pass the model_name parameter to the provider's refine_prompt method
        return self.active_provider.refine_prompt(prompt_data, model_name, target_model, content_rating, debug_enabled)
    
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
        self.providers["ollama"].model_name = model_name
        # Update the process tracker in the provider as well
        self.providers["ollama"].process_tracker = self.process_tracker
        self._select_provider()
    
    def get_available_models(self) -> List[str]:
        """Get available models from the active provider."""
        debug("LLMManager.get_available_models() called", LogArea.OLLAMA)
        debug("Checking if Ollama service is running...", LogArea.OLLAMA)
        
        try:
            # Check if Ollama service is responding
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                debug("Ollama service is running, getting models...", LogArea.OLLAMA)
                models = self.active_provider.get_available_models()
                debug(f"LLMManager returning models: {models}", LogArea.OLLAMA)
                return models
            else:
                debug(f"Ollama service not responding - status {response.status_code}", LogArea.OLLAMA)
                return []
        except Exception as e:
            debug(f"Ollama service not available: {str(e)}", LogArea.OLLAMA)
            return []

    def unload_model_from_vram(self, model_name: str) -> bool:
        """Unload a model from VRAM to free up memory."""
        if not self.active_provider:
            debug("No active provider to unload model from", LogArea.OLLAMA)
            return False
        
        try:
            return self.active_provider.unload_model_from_vram(model_name)
        except Exception as e:
            debug(f"Error unloading model from provider: {str(e)}", LogArea.OLLAMA)
            return False
