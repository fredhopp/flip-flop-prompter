#!/usr/bin/env python3
"""
FlipFlopPrompt - AI Image Generation Prompt Builder (PySide6 Version)

A tool for creating and refining prompts for AI image generation models.
"""

import sys
import argparse
import time
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QMessageLogContext, QMessageLogger
from PySide6.QtCore import qInstallMessageHandler, QTimer
from src.gui.main_window_qt import MainWindow
from src.utils.logger import initialize_logger, info, LogArea


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
    startup_start = time.time()
    
    parser = argparse.ArgumentParser(description="FlipFlopPrompt - AI Image Generation Prompt Builder (PySide6)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-t", "--load-template", dest="load_template", help="Load a template JSON file at startup")
    
    args = parser.parse_args()
    
    # Initialize logger with debug mode
    logger_start = time.time()
    logger = initialize_logger(args.debug)
    logger_time = time.time() - logger_start
    info(f"STARTUP: Logger initialization took {logger_time:.3f}s", LogArea.GENERAL)
    
    # Create QApplication
    app_start = time.time()
    app = QApplication(sys.argv)
    app_time = time.time() - app_start
    info(f"STARTUP: QApplication creation took {app_time:.3f}s", LogArea.GENERAL)
    
    # Install custom message handler to suppress QPainter messages
    if not args.debug:
        qInstallMessageHandler(qt_message_handler)
    
    # Set application properties
    app.setApplicationName("FlipFlopPrompt")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("FlipFlopPrompt")
    
    # Enable high DPI scaling (Qt 6.x handles this automatically)
    
    # Create and show main window
    window_start = time.time()
    window = MainWindow(debug_enabled=args.debug)
    window_creation_time = time.time() - window_start
    info(f"STARTUP: MainWindow creation took {window_creation_time:.3f}s", LogArea.GENERAL)
    
    # Show the window
    show_start = time.time()
    window.show()
    show_time = time.time() - show_start
    info(f"STARTUP: Window.show() took {show_time:.3f}s", LogArea.GENERAL)
    
    # Check UI responsiveness after a short delay
    QTimer.singleShot(100, window._check_ui_responsiveness)
    
    # Fire ui_ready signal after window is shown
    QTimer.singleShot(300, window._emit_ui_ready)
    
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
    
    total_startup_time = time.time() - startup_start
    info(f"STARTUP: Total startup time: {total_startup_time:.3f}s", LogArea.GENERAL)
    info(f"STARTUP: Breakdown - Logger: {logger_time:.3f}s, QApp: {app_time:.3f}s, Window: {window_creation_time:.3f}s, Show: {show_time:.3f}s", LogArea.GENERAL)
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
