"""
Preview panel for displaying generated prompts using PySide6.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QFrame, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from typing import Optional


class PreviewPanel(QWidget):
    """Panel for displaying prompt preview and final output using PySide6."""
    
    def __init__(self):
        super().__init__()
        
        self.current_text = ""
        self.is_final = False
        
        # Create widgets
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the preview panel widgets."""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(5)
        
        # Create group box with title
        self.frame = QGroupBox("Prompt Summary")
        
        # Frame layout
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(8)
        
        # No title label inside frame - will be shown as frame title
        
        # Text display area
        self.text_widget = QTextEdit()
        self.text_widget.setMinimumHeight(200)
        self.text_widget.setMaximumHeight(300)
        self.text_widget.setReadOnly(True)
        self.text_widget.setFont(QFont("Consolas", 10))
        frame_layout.addWidget(self.text_widget)
        
        # No status label inside frame - will be handled by main window
        
        # Add frame to main layout
        layout.addWidget(self.frame)
        
        # Apply initial styling
        self._apply_styling()
        
        # Set initial text
        self.text_widget.setPlainText("Enter your prompt components above to see a preview here...")
        self._set_placeholder_style()
    
    def _apply_styling(self):
        """Apply styling to the widgets."""
        # Style the frame
        self.frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fafafa;
            }
        """)
        
        # Style the text widget for normal state
        self.text_widget.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
                color: #212529;
                padding: 10px;
            }
        """)
    
    def _set_placeholder_style(self):
        """Set placeholder text styling."""
        self.text_widget.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
                color: #6c757d;
                padding: 10px;
                font-style: italic;
            }
        """)
    
    def _set_preview_style(self):
        """Set preview text styling."""
        self.text_widget.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
                color: #212529;
                padding: 10px;
            }
        """)
    
    def _set_final_style(self):
        """Set final prompt styling."""
        self.text_widget.setStyleSheet("""
            QTextEdit {
                border: 1px solid #28a745;
                border-radius: 3px;
                background-color: #e8f5e8;
                color: #1a472a;
                padding: 10px;
                font-weight: bold;
            }
        """)
    
    def update_preview(self, text: str, is_final: bool = False):
        """
        Update the preview with new text.
        
        Args:
            text: The text to display
            is_final: Whether this is the final generated prompt
        """
        self.current_text = text
        self.is_final = is_final
        
        # Update frame title based on state
        if is_final:
            self.frame.setTitle("Final Prompt")
        else:
            self.frame.setTitle("Prompt Summary")
        
        if text:
            # Update text content
            self.text_widget.setPlainText(text)
            
            # Apply appropriate styling
            if is_final:
                self._set_final_style()
            else:
                self._set_preview_style()
                
            # Count words and characters
            word_count = len(text.split()) if text.strip() else 0
            char_count = len(text)
            
        else:
            # Show placeholder text
            self.text_widget.setPlainText("Enter your prompt components above to see a preview here...")
            self._set_placeholder_style()
            word_count = 0
            char_count = 0
        
        # Store counts for external access
        self.word_count = word_count
        self.char_count = char_count
        
        # Scroll to top
        cursor = self.text_widget.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.text_widget.setTextCursor(cursor)
    
    def update_model_info(self, model_name: str):
        """
        Update the target model information display.
        (Placeholder - model info no longer displayed in preview)
        """
        pass
    
    def update_llm_info(self, llm_model: str):
        """
        Update the LLM information display.
        (Placeholder - LLM info no longer displayed in preview)
        """
        pass
    
    def get_current_text(self) -> str:
        """Get the current text content."""
        return self.current_text
    
    def get_word_count(self) -> int:
        """Get the current word count."""
        return getattr(self, 'word_count', 0)
    
    def get_char_count(self) -> int:
        """Get the current character count."""
        return getattr(self, 'char_count', 0)
    
    def clear_preview(self):
        """Clear the preview and reset to initial state."""
        self.update_preview("")
    
    def highlight_syntax(self, text: str) -> str:
        """
        Apply basic syntax highlighting to the prompt text.
        
        Args:
            text: The text to highlight
            
        Returns:
            Text with basic formatting applied
        """
        # This is a simple implementation for future enhancement
        # Qt's QTextEdit supports rich text formatting
        import re
        
        highlighted = text
        
        # Highlight camera specifications
        highlighted = re.sub(
            r'(\d+mm|lens|Arri|Alexa|RED|Canon|Sony)',
            r'<b>\1</b>',
            highlighted
        )
        
        # Highlight time references
        highlighted = re.sub(
            r'(\d+am|\d+pm|morning|afternoon|evening|night)',
            r'<i>\1</i>',
            highlighted
        )
        
        return highlighted
    
    def set_font_size(self, size: int):
        """Set the font size for the text display."""
        font = self.text_widget.font()
        font.setPointSize(size)
        self.text_widget.setFont(font)
    
    def set_font_family(self, family: str):
        """Set the font family for the text display."""
        font = self.text_widget.font()
        font.setFamily(family)
        self.text_widget.setFont(font)
