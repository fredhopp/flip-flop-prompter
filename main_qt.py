#!/usr/bin/env python3
"""
FlipFlopPrompt - AI Image Generation Prompt Builder (PySide6 Version)

A tool for creating and refining prompts for AI image generation models.
"""

import sys
import argparse
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.gui.main_window_qt import MainWindow


def main():
    """Main entry point for PySide6 version."""
    parser = argparse.ArgumentParser(description="FlipFlopPrompt - AI Image Generation Prompt Builder (PySide6)")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--cli", action="store_true", help="Launch CLI mode")
    
    args = parser.parse_args()
    
    # Default to GUI if no mode specified
    if not args.gui and not args.cli:
        args.gui = True
    
    if args.gui:
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("FlipFlopPrompt")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("FlipFlopPrompt")
        
        # Enable high DPI scaling (Qt 6.x handles this automatically)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
    
    elif args.cli:
        # Launch CLI (placeholder for future implementation)
        print("CLI mode not yet implemented.")
        sys.exit(1)


if __name__ == "__main__":
    main()
