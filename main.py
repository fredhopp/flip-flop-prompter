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
from PySide6.QtCore import Qt, QMessageLogContext, QMessageLogger
from PySide6.QtCore import qInstallMessageHandler, QTimer
from src.gui.main_window_qt import MainWindow
from src.utils.logger import initialize_logger


def qt_message_handler(message_type, context, message):
    """Custom Qt message handler to suppress harmless debug messages."""
    # Suppress QPainter debug messages and other harmless warnings
    if any(suppressed in message for suppressed in [
        "QPainter::begin: Paint device returned engine == 0",
        "QPainter::setCompositionMode: Painter not active",
        "QPainter::fillRect: Painter not active",
        "QPainter::setBrush: Painter not active",
        "QPainter::setPen: Painter not active",
        "QPainter::drawPath: Painter not active",
        "QPainter::setFont: Painter not active",
        "QPainter::end: Painter not active",
        "QPainter::begin: Paint device returned engine == 0, type: 3"
    ]):
        return
    
    # For other messages, you can optionally print them or handle them differently
    # Uncomment the line below if you want to see other Qt messages
    # print(f"Qt Message: {message}")


def main():
    """Main entry point for PySide6 version."""
    parser = argparse.ArgumentParser(description="FlipFlopPrompt - AI Image Generation Prompt Builder (PySide6)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-t", "--load-template", dest="load_template", help="Load a template JSON file at startup")
    
    args = parser.parse_args()
    
    # Initialize logger with debug mode
    logger = initialize_logger(args.debug)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Install custom message handler to suppress QPainter messages
    if not args.debug:
        qInstallMessageHandler(qt_message_handler)
    
    # Set application properties
    app.setApplicationName("FlipFlopPrompt")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("FlipFlopPrompt")
    
    # Enable high DPI scaling (Qt 6.x handles this automatically)
    
    # Create and show main window
    window = MainWindow(debug_enabled=args.debug)
    window.show()

    # Auto-load template at startup if provided, but only after UI becomes ready
    if args.load_template:
        template_path = args.load_template.lstrip('@')
        def _deferred_load():
            # Extra delay to allow Ollama/model checks to settle
            QTimer.singleShot(300, lambda: window._load_template(template_path, show_messages=False))
        # Primary trigger
        window.ui_ready.connect(_deferred_load)
        # Fallback trigger in case ui_ready is delayed or missed
        QTimer.singleShot(1500, lambda: window._load_template(template_path, show_messages=False))
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
