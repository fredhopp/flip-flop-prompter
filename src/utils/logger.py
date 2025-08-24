"""
Logging utility for FlipFlopPrompt debug mode.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum
from ..utils.theme_manager import theme_manager


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogArea(Enum):
    """Log areas for different parts of the application."""
    GENERAL = "GENERAL"
    OLLAMA = "OLLAMA"
    NAVIGATION = "NAVIGATION"
    BATCH = "BATCH"
    SNIPPETS = "SNIPPETS"
    FILTERS = "FILTERS"
    PREVIEW = "PREVIEW"
    HISTORY = "HISTORY"
    GUI = "GUI"
    LLM = "LLM"
    REFRESH = "REFRESH"
    LOAD = "LOAD"
    ERROR = "ERROR"


class FlipFlopLogger:
    """Centralized logging for FlipFlopPrompt application."""
    
    def __init__(self, debug_enabled: bool = False):
        self.debug_enabled = debug_enabled
        self.logger = None
        self.log_file = None
        
        if debug_enabled:
            self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create debug directory in user data folder
        debug_dir = theme_manager.user_data_dir / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = debug_dir / f"flipflop_debug_{timestamp}.log"
        
        # Configure logger
        self.logger = logging.getLogger('FlipFlopPrompt')
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler (for terminal output)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initial setup
        self.logger.info("FlipFlopPrompt debug logging initialized")
        self.logger.info(f"Log file: {self.log_file}")
    
    def log_gui_action(self, action: str, details: Optional[str] = None):
        """Log GUI user actions."""
        if not self.debug_enabled or not self.logger:
            return
        
        message = f"GUI ACTION: {action}"
        if details:
            message += f" - {details}"
        
        self.logger.info(message)
    
    def log_snippet_interaction(self, field: str, action: str, snippet: str, content_filter: str):
        """Log snippet-related interactions."""
        if not self.debug_enabled or not self.logger:
            return
        
        self.logger.info(f"SNIPPET: {field} | {action} | '{snippet}' | Filter: {content_filter}")
    
    def log_llm_interaction(self, model: str, action: str, details: Optional[str] = None):
        """Log LLM-related interactions."""
        if not self.debug_enabled or not self.logger:
            return
        
        message = f"LLM: {model} | {action}"
        if details:
            message += f" | {details}"
        
        self.logger.info(message)
    
    def log_error(self, error: str, context: Optional[str] = None):
        """Log errors."""
        if not self.debug_enabled or not self.logger:
            return
        
        message = f"ERROR: {error}"
        if context:
            message += f" | Context: {context}"
        
        self.logger.error(message)
    
    def log_debug(self, message: str):
        """Log debug messages."""
        if not self.debug_enabled or not self.logger:
            return
        
        self.logger.debug(message)
    
    def log_info(self, message: str):
        """Log info messages."""
        if not self.debug_enabled or not self.logger:
            return
        
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning messages."""
        if not self.debug_enabled or not self.logger:
            return
        
        self.logger.warning(message)
    
    def get_log_file_path(self) -> Optional[Path]:
        """Get the current log file path."""
        return self.log_file


# Global logger instance
flipflop_logger = None


def initialize_logger(debug_enabled: bool = False) -> FlipFlopLogger:
    """Initialize the global logger instance."""
    global flipflop_logger
    flipflop_logger = FlipFlopLogger(debug_enabled)
    return flipflop_logger


def get_logger() -> Optional[FlipFlopLogger]:
    """Get the global logger instance."""
    return flipflop_logger


# Global helper functions for easy logging
def debug(message: str, area: LogArea = LogArea.GENERAL):
    """Log a debug message."""
    if flipflop_logger:
        flipflop_logger.log_debug(f"[{area.value}] {message}")


def info(message: str, area: LogArea = LogArea.GENERAL):
    """Log an info message."""
    if flipflop_logger:
        flipflop_logger.log_info(f"[{area.value}] {message}")


def warning(message: str, area: LogArea = LogArea.GENERAL):
    """Log a warning message."""
    if flipflop_logger:
        flipflop_logger.log_warning(f"[{area.value}] {message}")


def error(message: str, area: LogArea = LogArea.ERROR):
    """Log an error message."""
    if flipflop_logger:
        flipflop_logger.log_error(f"[{area.value}] {message}")
