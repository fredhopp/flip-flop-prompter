#!/usr/bin/env python3
"""
FlipFlopPrompt - AI Image Generation Prompt Builder

A tool for creating and refining prompts for AI image generation models.
"""

import sys
import argparse
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import tkinter as tk
from src.gui.main_window import MainWindow


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FlipFlopPrompt - AI Image Generation Prompt Builder")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--cli", action="store_true", help="Launch CLI mode")
    
    args = parser.parse_args()
    
    # Default to GUI if no mode specified
    if not args.gui and not args.cli:
        args.gui = True
    
    if args.gui:
        # Launch GUI
        root = tk.Tk()
        app = MainWindow(root)
        
        # Handle window closing
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        root.mainloop()
    
    elif args.cli:
        # Launch CLI (placeholder for future implementation)
        print("CLI mode not yet implemented.")
        sys.exit(1)


if __name__ == "__main__":
    main()
