#!/usr/bin/env python3
"""
FlipFlopPrompt - AI Model Prompt Formulation Tool

Main entry point for the application.
Supports both GUI and CLI modes.
"""

import sys
import argparse
import tkinter as tk
from tkinter import ttk

# Add src to path for imports
sys.path.insert(0, 'src')

from src.cli.command_line import CLIInterface
from src.gui.main_window import MainWindow


def main():
    """Main entry point for FlipFlopPrompt."""
    
    # Check if GUI mode is requested
    if len(sys.argv) == 1 or '--gui' in sys.argv:
        run_gui()
    else:
        run_cli()


def run_gui():
    """Run the GUI version of the application."""
    try:
        # Create the main window
        root = tk.Tk()
        
        # Set up the application
        app = MainWindow(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting GUI: {e}", file=sys.stderr)
        print("Falling back to CLI mode...", file=sys.stderr)
        run_cli()


def run_cli():
    """Run the CLI version of the application."""
    try:
        cli = CLIInterface()
        sys.exit(cli.run())
        
    except Exception as e:
        print(f"Error running CLI: {e}", file=sys.stderr)
        sys.exit(1)


def show_help():
    """Show help information."""
    help_text = """
FlipFlopPrompt - AI Model Prompt Formulation Tool

USAGE:
  python main.py                    # Start GUI mode
  python main.py --gui              # Start GUI mode (explicit)
  python main.py --help             # Show CLI help
  python main.py --list-models      # List supported models

GUI MODE:
  The GUI provides a user-friendly interface for creating prompts
  with all the required fields and real-time preview.

CLI MODE:
  Use command-line arguments to generate prompts programmatically.
  Useful for automation and ComfyUI integration.

EXAMPLES:
  # GUI mode
  python main.py

  # CLI mode - generate a prompt
  python main.py --model seedream --environment "hotel lobby" --subjects "20yo man"

  # CLI mode - JSON output for ComfyUI
  python main.py --model veo --json --environment "interior" --weather "sunny"

  # CLI mode - list supported models
  python main.py --list-models

For more information, see the README.md file.
    """
    print(help_text)


if __name__ == "__main__":
    # Handle help request
    if '--help' in sys.argv or '-h' in sys.argv:
        show_help()
        sys.exit(0)
    
    main()
