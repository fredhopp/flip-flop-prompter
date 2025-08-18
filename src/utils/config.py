"""
Configuration management for FlipFlopPrompt.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for FlipFlopPrompt."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_default_config()
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".flipflopprompt"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            'gui': {
                'window_size': '1000x800',
                'theme': 'default',
                'auto_save': True,
                'auto_save_interval': 300,  # seconds
                'recent_files': [],
                'max_recent_files': 10
            },
            'models': {
                'default_model': 'seedream',
                'auto_validate': True,
                'show_preview': True
            },
            'output': {
                'default_format': 'text',
                'auto_copy': False,
                'save_history': True,
                'history_size': 100
            },
            'advanced': {
                'enable_llm': False,
                'llm_api_key': '',
                'llm_model': 'gpt-3.5-turbo',
                'debug_mode': False,
                'log_level': 'INFO'
            }
        }
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Merge with defaults
                self._merge_config(self.config, file_config)
                
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Recursively merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Get GUI-specific configuration."""
        return self.config.get('gui', {})
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration."""
        return self.config.get('models', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output-specific configuration."""
        return self.config.get('output', {})
    
    def get_advanced_config(self) -> Dict[str, Any]:
        """Get advanced configuration."""
        return self.config.get('advanced', {})
    
    def add_recent_file(self, file_path: str):
        """Add a file to the recent files list."""
        recent_files = self.get('gui.recent_files', [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Limit size
        max_files = self.get('gui.max_recent_files', 10)
        recent_files = recent_files[:max_files]
        
        self.set('gui.recent_files', recent_files)
        self.save_config()
    
    def get_recent_files(self) -> list:
        """Get list of recent files."""
        return self.get('gui.recent_files', [])
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.set('gui.recent_files', [])
        self.save_config()
    
    def is_llm_enabled(self) -> bool:
        """Check if LLM integration is enabled."""
        return self.get('advanced.enable_llm', False)
    
    def get_llm_api_key(self) -> str:
        """Get the LLM API key."""
        return self.get('advanced.llm_api_key', '')
    
    def set_llm_api_key(self, api_key: str):
        """Set the LLM API key."""
        self.set('advanced.llm_api_key', api_key)
        self.save_config()
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('advanced.debug_mode', False)
    
    def get_log_level(self) -> str:
        """Get the log level."""
        return self.get('advanced.log_level', 'INFO')
