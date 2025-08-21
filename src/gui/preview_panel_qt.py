"""
Preview panel for displaying generated prompts using PySide6 with tabbed interface.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QFrame, QScrollArea, QGroupBox, QTabWidget, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from typing import Optional
from ..utils.theme_manager import theme_manager


class PreviewPanel(QWidget):
    """Panel for displaying prompt preview and final output using PySide6 with tabs."""
    
    # Signals for history navigation
    history_back_requested = Signal()
    history_forward_requested = Signal()
    history_delete_requested = Signal()
    history_clear_requested = Signal()
    
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
        self.frame = QGroupBox("Preview")
        
        # Frame layout
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(8)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create Prompt Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setMinimumHeight(200)
        self.summary_text.setMaximumHeight(300)
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.summary_text, "Prompt Summary")
        
        # Create Final Prompt tab
        self.final_text = QTextEdit()
        self.final_text.setMinimumHeight(200)
        self.final_text.setMaximumHeight(300)
        self.final_text.setReadOnly(True)
        self.final_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.final_text, "Final Prompt")
        
        frame_layout.addWidget(self.tab_widget)
        
        # Create navigation controls
        self._create_navigation_controls(frame_layout)
        
        # Add frame to main layout
        layout.addWidget(self.frame)
        
        # Set initial text
        self.summary_text.setPlainText("Enter your prompt components above to see a preview here...")
        self.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
        self._set_placeholder_style()
        
        # Apply initial styling (after setting text)
        self._apply_styling()
        
        # Force navigation styling to be applied
        self._apply_navigation_styling()
    
    def _create_navigation_controls(self, parent_layout):
        """Create navigation controls for history."""
        # Create horizontal layout for navigation
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 5, 0, 0)
        nav_layout.setSpacing(10)
        
        # Back button
        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(35, 35)
        self.back_button.setToolTip("Go to previous prompt")
        self.back_button.clicked.connect(self.history_back_requested.emit)
        self.back_button.setEnabled(True)  # Enable for testing
        
        # Forward button
        self.forward_button = QPushButton("→")
        self.forward_button.setFixedSize(35, 35)
        self.forward_button.setToolTip("Go to next prompt")
        self.forward_button.clicked.connect(self.history_forward_requested.emit)
        self.forward_button.setEnabled(True)  # Enable for testing
        
        # Counter label
        self.counter_label = QLabel("0/0")
        self.counter_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.counter_label.setMinimumWidth(60)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Delete button
        self.delete_button = QPushButton("🗑")
        self.delete_button.setFixedSize(35, 35)
        self.delete_button.setToolTip("Delete current prompt")
        self.delete_button.clicked.connect(self.history_delete_requested.emit)
        self.delete_button.setEnabled(True)  # Enable for testing
        
        # Clear history button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedSize(60, 35)
        self.clear_button.setToolTip("Clear all history")
        self.clear_button.clicked.connect(self.history_clear_requested.emit)
        self.clear_button.setEnabled(True)  # Enable for testing
        
        # Add stretch to push controls to the left
        nav_layout.addStretch()
        
        # Add buttons to layout
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.counter_label)
        nav_layout.addWidget(self.delete_button)
        nav_layout.addWidget(self.clear_button)
        
        # Add navigation layout to parent
        parent_layout.addLayout(nav_layout)
    
    def _apply_styling(self):
        """Apply theme-aware styling to the widgets."""
        # Get current theme colors
        colors = theme_manager.get_theme_colors()
        
        # Style the frame
        self.frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {colors['tag_border']};
                border-radius: 5px;
                background-color: {colors['text_bg']};
            }}
        """)
        
        # Style the tab widget
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {colors['tag_border']};
                border-radius: 3px;
                background-color: {colors['text_bg']};
            }}
            QTabBar::tab {{
                background-color: {colors['bg']};
                border: 1px solid {colors['tag_border']};
                padding: 8px 16px;
                margin-right: 2px;
                color: {colors['text_fg']};
            }}
            QTabBar::tab:selected {{
                background-color: {colors['text_bg']};
                border-bottom: 1px solid {colors['text_bg']};
                color: {colors['text_fg']};
            }}
        """)
        
        # Style the text widgets for normal state
        text_style = f"""
            QTextEdit {{
                border: 1px solid {colors['tag_border']};
                border-radius: 3px;
                background-color: {colors['text_bg']};
                color: {colors['text_fg']};
                padding: 10px;
            }}
        """
        self.summary_text.setStyleSheet(text_style)
        self.final_text.setStyleSheet(text_style)
        
        # Apply navigation styling
        self._apply_navigation_styling()
    
    def _set_placeholder_style(self):
        """Set placeholder text styling."""
        colors = theme_manager.get_theme_colors()
        placeholder_style = f"""
            QTextEdit {{
                border: 1px solid {colors['tag_border']};
                border-radius: 3px;
                background-color: {colors['text_bg']};
                color: {colors['placeholder_fg']};
                padding: 10px;
                font-style: italic;
            }}
        """
        self.summary_text.setStyleSheet(placeholder_style)
        self.final_text.setStyleSheet(placeholder_style)
    
    def _set_preview_style(self):
        """Set preview text styling."""
        colors = theme_manager.get_theme_colors()
        preview_style = f"""
            QTextEdit {{
                border: 1px solid {colors['tag_border']};
                border-radius: 3px;
                background-color: {colors['text_bg']};
                color: {colors['text_fg']};
                padding: 10px;
            }}
        """
        self.summary_text.setStyleSheet(preview_style)
    
    def _set_final_style(self):
        """Set final prompt styling."""
        colors = theme_manager.get_theme_colors()
        final_style = f"""
            QTextEdit {{
                border: 1px solid {colors['snippet_border']};
                border-radius: 3px;
                background-color: {colors['snippet_bg']};
                color: {colors['snippet_fg']};
                padding: 10px;
                font-weight: bold;
            }}
        """
        self.final_text.setStyleSheet(final_style)
    
    def update_preview(self, text: str, is_final: bool = False):
        """
        Update the preview with new text.
        
        Args:
            text: The text to display
            is_final: Whether this is the final generated prompt
        """
        self.current_text = text
        self.is_final = is_final
        
        if is_final:
            # Update Final Prompt tab
            self.final_text.setPlainText(text)
            self.tab_widget.setCurrentIndex(1)  # Switch to Final Prompt tab
            self._set_final_style()
        else:
            # Update Prompt Summary tab
            self.summary_text.setPlainText(text)
            self.tab_widget.setCurrentIndex(0)  # Switch to Prompt Summary tab
            if text.strip():
                self._set_preview_style()
            else:
                self._set_placeholder_style()
        
        # Count words and characters
        word_count = len(text.split()) if text.strip() else 0
        char_count = len(text)
        
        # Store counts for external access
        self.word_count = word_count
        self.char_count = char_count
        
        # Scroll to top
        if is_final:
            cursor = self.final_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            self.final_text.setTextCursor(cursor)
        else:
            cursor = self.summary_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            self.summary_text.setTextCursor(cursor)
    
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
        self.summary_text.setPlainText("Enter your prompt components above to see a preview here...")
        self.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
        self._set_placeholder_style()
        self.tab_widget.setCurrentIndex(0)
    
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
        font = self.summary_text.font()
        font.setPointSize(size)
        self.summary_text.setFont(font)
        self.final_text.setFont(font)
    
    def set_font_family(self, family: str):
        """Set the font family for the text display."""
        font = self.summary_text.font()
        font.setFamily(family)
        self.summary_text.setFont(font)
        self.final_text.setFont(font)
    
    def update_navigation_controls(self, can_go_back: bool, can_go_forward: bool, 
                                  current_position: int, total_count: int, has_history: bool):
        """Update navigation controls state."""
        self.back_button.setEnabled(can_go_back)
        self.forward_button.setEnabled(can_go_forward)
        self.delete_button.setEnabled(has_history)
        self.clear_button.setEnabled(has_history)
        
        # Update counter
        if total_count > 0:
            self.counter_label.setText(f"{current_position}/{total_count}")
        else:
            self.counter_label.setText("0/0")
    
    def _apply_navigation_styling(self):
        """Apply styling to navigation controls using the same blue color as other buttons."""
        colors = theme_manager.get_theme_colors()
        
        # Use explicit blue color for buttons to ensure they're visible
        button_bg = "#0066cc"  # Same blue as other buttons
        button_fg = "#ffffff"  # White text
        button_hover = "#0052a3"  # Darker blue on hover
        button_pressed = "#003d7a"  # Even darker on press
        disabled_bg = "#cccccc"  # Light gray when disabled
        disabled_fg = "#666666"  # Dark gray text when disabled
    
    def refresh_navigation_styling(self):
        """Refresh navigation controls styling - can be called when theme changes."""
        self._apply_navigation_styling()
        
        # Use the same button styling as other buttons in the app
        nav_style = f"""
            QPushButton {{
                background-color: {button_bg};
                color: {button_fg};
                border: 2px solid {button_bg};
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
                border-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_pressed};
                border-color: {button_pressed};
            }}
            QPushButton:disabled {{
                background-color: {disabled_bg};
                border-color: {disabled_bg};
                color: {disabled_fg};
            }}
        """
        
        # Apply styling to navigation buttons
        if hasattr(self, 'back_button'):
            self.back_button.setStyleSheet(nav_style)
        if hasattr(self, 'forward_button'):
            self.forward_button.setStyleSheet(nav_style)
        if hasattr(self, 'delete_button'):
            self.delete_button.setStyleSheet(nav_style)
        if hasattr(self, 'clear_button'):
            self.clear_button.setStyleSheet(nav_style)
        
        # Style the counter label
        if hasattr(self, 'counter_label'):
            self.counter_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors['text_fg']};
                    background-color: {colors['text_bg']};
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    padding: 2px 6px;
                    font-weight: bold;
                }}
            """)
