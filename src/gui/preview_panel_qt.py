"""
Preview panel for displaying generated prompts using PySide6 with tabbed interface.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QFrame, QScrollArea, QGroupBox, QTabWidget, QPushButton, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor
from typing import Optional
from enum import Enum
import qtawesome as qta  # Font Awesome icons for Qt
from ..utils.theme_manager import theme_manager
from ..utils.logger import debug, info, warning, error, LogArea


class PreviewState(Enum):
    """Enum for preview panel states."""
    PLACEHOLDER = "placeholder"
    PREVIEW = "preview" 
    FINAL = "final"
    HISTORY = "history"


class PreviewPanel(QWidget):
    """Panel for displaying prompt preview and final output using PySide6 with tabs."""
    
    # Signals for history navigation
    history_back_requested = Signal()
    history_forward_requested = Signal()
    history_delete_requested = Signal()
    history_clear_requested = Signal()
    load_preview_requested = Signal()
    history_jump_requested = Signal(int)  # Signal for jumping to specific history position
    
    # New signals for action buttons
    copy_requested = Signal()
    save_requested = Signal()
    save_all_requested = Signal()
    
    def __init__(self):
        super().__init__()
        
        # State management
        self.current_text = ""
        self.summary_state = PreviewState.PLACEHOLDER
        self.final_state = PreviewState.PLACEHOLDER
        
        # Add debounce timer for styling to prevent flashing
        self._styling_timer = QTimer()
        self._styling_timer.setSingleShot(True)
        self._styling_timer.timeout.connect(self._apply_state_styling_delayed)
        
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
        
        # Set initial text and styling
        self._set_initial_state()
        
        # Apply initial styling
        self._apply_styling()
    
    def _set_initial_state(self):
        """Set the initial state with placeholder text."""
        self.summary_text.setPlainText("Enter your prompt components above to see a preview here...")
        self.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
        self.summary_state = PreviewState.PLACEHOLDER
        self.final_state = PreviewState.PLACEHOLDER
    
    def _create_navigation_controls(self, parent_layout):
        """Create navigation controls for history."""
        # Create horizontal layout for navigation
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 5, 0, 0)
        nav_layout.setSpacing(10)
        
        # Left side: Action buttons with Font Awesome icons
        # Copy to Clipboard button
        self.copy_button = QPushButton()
        self.copy_button.setIcon(qta.icon('fa5s.copy', color='white'))
        self.copy_button.setFixedSize(35, 35)
        self.copy_button.setToolTip("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_requested.emit)
        
        # Save Prompt button
        self.save_button = QPushButton()
        self.save_button.setIcon(qta.icon('fa5s.save', color='white'))
        self.save_button.setFixedSize(35, 35)
        self.save_button.setToolTip("Save Prompt")
        self.save_button.clicked.connect(self.save_requested.emit)
        
        # Save All Prompts button
        self.save_all_button = QPushButton()
        self.save_all_button.setIcon(qta.icon('fa5s.folder-plus', color='white'))
        self.save_all_button.setFixedSize(35, 35)
        self.save_all_button.setToolTip("Save All Prompts")
        self.save_all_button.clicked.connect(self.save_all_requested.emit)
        
        # Add left side buttons
        nav_layout.addWidget(self.copy_button)
        nav_layout.addWidget(self.save_button)
        nav_layout.addWidget(self.save_all_button)
        
        # Add stretch to separate left and right sides
        nav_layout.addStretch()
        
        # Right side: Navigation controls
        # Back button
        self.back_button = QPushButton()
        self.back_button.setIcon(qta.icon('fa5s.arrow-left', color='white'))
        self.back_button.setFixedSize(35, 35)
        self.back_button.setToolTip("Go to previous prompt")
        self.back_button.clicked.connect(self.history_back_requested.emit)
        
        # Forward button
        self.forward_button = QPushButton()
        self.forward_button.setIcon(qta.icon('fa5s.arrow-right', color='white'))
        self.forward_button.setFixedSize(35, 35)
        self.forward_button.setToolTip("Go to next prompt")
        self.forward_button.clicked.connect(self.history_forward_requested.emit)
        
        # Counter input (editable)
        self.counter_input = QLineEdit("0/0")
        self.counter_input.setFixedSize(60, 35)
        self.counter_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_input.setToolTip("Click to edit, press Enter to jump")
        self.counter_input.returnPressed.connect(self._on_counter_submit)
        
        # Load button (hidden for now)
        self.load_button = QPushButton()
        self.load_button.setIcon(qta.icon('fa5s.redo-alt', color='white'))
        self.load_button.setFixedSize(35, 35)
        self.load_button.setToolTip("Restore preview into fields")
        self.load_button.clicked.connect(self.load_preview_requested.emit)
        self.load_button.setVisible(False)  # Hide the button
        
        # Delete button
        self.delete_button = QPushButton()
        self.delete_button.setIcon(qta.icon('fa5s.trash', color='white'))
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
        
        # Add right side buttons to layout
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.counter_input)
        nav_layout.addWidget(self.load_button)
        nav_layout.addWidget(self.delete_button)
        nav_layout.addWidget(self.clear_button)
        
        # Add navigation layout to parent
        parent_layout.addLayout(nav_layout)
    
    def _apply_styling(self):
        """Apply theme-aware styling to the widgets."""
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
            QTabBar::tab:last {{
                background-color: {colors.get('preview_final_bg', '#e6f3ff')} !important;
                color: {colors.get('preview_final_fg', '#0066cc')} !important;
            }}
            QTabBar::tab:last:selected {{
                background-color: {colors.get('preview_final_bg', '#e6f3ff')} !important;
                color: {colors.get('preview_final_fg', '#0066cc')} !important;
            }}
        """)
        
        # Apply current state styling
        self._apply_state_styling_debounced()
        
        # Apply navigation styling
        self._apply_navigation_styling()
    
    def _apply_state_styling(self):
        """Apply styling based on current states."""
        colors = theme_manager.get_theme_colors()
        
        # Style summary text based on state
        summary_style = self._get_style_for_state(self.summary_state, colors)
        self.summary_text.setStyleSheet(summary_style)
        
        # Style final text based on state - special handling for Final Prompt
        if self.final_state == PreviewState.PLACEHOLDER:
            # Final Prompt placeholder should use blue background
            final_style = f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors['placeholder_fg']};
                    padding: 10px;
                    font-style: italic;
                }}
            """
        elif self.final_state == PreviewState.FINAL:
            # Final Prompt content should also use blue background
            final_style = f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors.get('preview_final_fg', colors['text_fg'])};
                    padding: 10px;
                    font-weight: bold;
                }}
            """
        elif self.final_state == PreviewState.HISTORY:
            # Final Prompt in history should also use blue background
            final_style = f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors.get('preview_final_fg', colors['text_fg'])};
                    padding: 10px;
                }}
            """
        else:
            final_style = self._get_style_for_state(self.final_state, colors)
        
        self.final_text.setStyleSheet(final_style)
    
    def _apply_state_styling_delayed(self):
        """Apply styling with a delay to prevent flashing."""
        colors = theme_manager.get_theme_colors()
        
        # Style summary text based on state
        summary_style = self._get_style_for_state(self.summary_state, colors)
        self.summary_text.setStyleSheet(summary_style)
        
        # Style final text based on state - special handling for Final Prompt
        if self.final_state == PreviewState.PLACEHOLDER:
            # Final Prompt placeholder should use blue background
            final_style = f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors['placeholder_fg']};
                    padding: 10px;
                    font-style: italic;
                }}
            """
        elif self.final_state == PreviewState.FINAL:
            # Final Prompt content should also use blue background
            final_style = f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors.get('preview_final_fg', colors['text_fg'])};
                    padding: 10px;
                    font-weight: bold;
                }}
            """
        elif self.final_state == PreviewState.HISTORY:
            # Final Prompt in history should also use blue background
            final_style = f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors.get('preview_final_fg', colors['text_fg'])};
                    padding: 10px;
                }}
            """
        else:
            final_style = self._get_style_for_state(self.final_state, colors)
        
        self.final_text.setStyleSheet(final_style)
    
    def _apply_state_styling_debounced(self):
        """Apply styling with debouncing to prevent rapid changes."""
        self._styling_timer.start(50)  # 50ms delay
    
    def _get_style_for_state(self, state: PreviewState, colors: dict) -> str:
        """Get the appropriate style for a given state."""
        if state == PreviewState.PLACEHOLDER:
            return f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors['text_bg']};
                    color: {colors['placeholder_fg']};
                    padding: 10px;
                    font-style: italic;
                }}
            """
        elif state == PreviewState.PREVIEW:
            return f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors['text_bg']};
                    color: {colors['text_fg']};
                    padding: 10px;
                }}
            """
        elif state == PreviewState.FINAL:
            return f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors.get('preview_final_bg', colors['text_bg'])};
                    color: {colors.get('preview_final_fg', colors['text_fg'])};
                    padding: 10px;
                    font-weight: bold;
                }}
            """
        elif state == PreviewState.HISTORY:
            history_bg = colors.get('preview_summary_history_bg', colors['text_bg'])
            return f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {history_bg};
                    color: {colors['text_fg']};
                    padding: 10px;
                }}
            """
        else:
            # Fallback to preview style
            return f"""
                QTextEdit {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 3px;
                    background-color: {colors['text_bg']};
                    color: {colors['text_fg']};
                    padding: 10px;
                }}
            """
    
    def _apply_navigation_styling(self):
        """Apply styling to navigation controls."""
        colors = theme_manager.get_theme_colors()
        
        nav_style = f"""
            QPushButton {{
                background-color: {colors['button_bg']};
                color: {colors['button_fg']};
                border: 1px solid {colors['tag_border']};
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('button_hover_bg', colors['button_bg'])};
            }}
            QPushButton:pressed {{
                background-color: {colors.get('button_pressed_bg', colors['button_bg'])};
            }}
            QPushButton:disabled {{
                background-color: {colors.get('button_disabled_bg', colors['button_bg'])};
                color: {colors.get('button_disabled_fg', colors['button_fg'])};
            }}
            QLineEdit {{
                background-color: {colors['text_bg']};
                color: {colors['text_fg']};
                border: 1px solid {colors['tag_border']};
                border-radius: 3px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border: 2px solid {colors.get('focus_color', colors['button_bg'])};
            }}
        """
        
        # Apply to all navigation widgets
        for widget in [self.copy_button, self.save_button, self.save_all_button,
                      self.back_button, self.forward_button, self.counter_input, 
                      self.load_button, self.delete_button, self.clear_button]:
            widget.setStyleSheet(nav_style)
    
    def refresh_navigation_styling(self):
        """Refresh navigation styling (called after theme changes)."""
        self._apply_navigation_styling()
    
    def _on_counter_submit(self):
        """Handle counter input submission."""
        try:
            text = self.counter_input.text()
            # Accept both "Z" and "Z/X" formats
            if '/' in text:
                position = int(text.split('/')[0])
            else:
                position = int(text)
            self.history_jump_requested.emit(position)
        except (ValueError, IndexError):
            pass  # Ignore invalid input
    
    def update_preview(self, text: str, is_final: bool = False, preserve_tab: bool = False):
        """
        Update the preview with new text.
        
        Args:
            text: The text to display
            is_final: Whether this is the final generated prompt
            preserve_tab: Whether to preserve the current tab selection
        """
        self.current_text = text
        
        debug(r"update_preview called - text='{text[:100]}{'...' if len(text) > 100 else ''}', is_final={is_final}, preserve_tab={preserve_tab}", LogArea.NAVIGATION)
        
        if is_final:
            # Update Final Prompt tab
            self.final_text.setPlainText(text)
            self.final_state = PreviewState.FINAL
            debug(r"Updated final text, state={self.final_state}", LogArea.NAVIGATION)
            
            # Set regular font for generated content
            font = self.final_text.font()
            font.setItalic(False)
            self.final_text.setFont(font)
            
            if not preserve_tab:
                self.tab_widget.setCurrentIndex(1)  # Switch to Final Prompt tab
        else:
            # Update Prompt Summary tab
            self.summary_text.setPlainText(text)
            
            # Determine state based on content
            if text.strip():
                self.summary_state = PreviewState.PREVIEW
            else:
                self.summary_state = PreviewState.PLACEHOLDER
                # Restore placeholder text
                self.summary_text.setPlainText("Enter your prompt components above to see a preview here...")
            
            debug(r"Updated summary text, state={self.summary_state}", LogArea.NAVIGATION)
            
            if not preserve_tab:
                self.tab_widget.setCurrentIndex(0)  # Switch to Prompt Summary tab
        
        # Apply updated styling with debouncing
        self._apply_state_styling_debounced()
        
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
    
    def set_history_state(self, is_history: bool, total_count: int = 0):
        """Set the preview state to history mode."""
        if is_history:
            self.summary_state = PreviewState.HISTORY
            self.final_state = PreviewState.HISTORY
        else:
            # Reset to appropriate states for current state (0/X)
            if self.summary_text.toPlainText().strip() and not self.summary_text.toPlainText().startswith("Enter your prompt"):
                self.summary_state = PreviewState.PREVIEW
            else:
                self.summary_state = PreviewState.PLACEHOLDER
                # Ensure placeholder text is set
                if not self.summary_text.toPlainText().startswith("Enter your prompt"):
                    self.summary_text.setPlainText("Enter your prompt components above to see a preview here...")
            
            # For Final Prompt, show dynamic placeholder in current state (0/X)
            self.final_state = PreviewState.PLACEHOLDER
            if not self.final_text.toPlainText().startswith("Generate a final prompt"):
                if total_count > 0:
                    self.final_text.setPlainText(f"Generate a final prompt to see the LLM-refined version here... (Navigate to 1/{total_count} to see the latest LLM generation)")
                else:
                    self.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
        
        self._apply_state_styling_debounced()
    
    def update_model_info(self, model_name: str):
        """Update the target model information display."""
        pass
    
    def update_llm_info(self, llm_model: str):
        """Update the LLM information display."""
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
    
    def get_summary_text(self) -> str:
        """Get the current summary text."""
        return self.summary_text.toPlainText()
    
    def clear_preview(self):
        """Clear the preview and reset to initial state."""
        self._set_initial_state()
        self._apply_state_styling_debounced()
        self.tab_widget.setCurrentIndex(0)
    
    def highlight_syntax(self, text: str) -> str:
        """Apply basic syntax highlighting to the prompt text."""
        # This is a simple implementation for future enhancement
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
                                  current_position: int, total_count: int, has_history: bool, is_current_state: bool = True):
        """Update navigation controls state."""
        self.back_button.setEnabled(can_go_back)
        self.forward_button.setEnabled(can_go_forward)
        self.delete_button.setEnabled(has_history and not is_current_state)  # Can't delete current state
        self.clear_button.setEnabled(has_history)
        
        # Update counter display
        self.counter_input.setText(f"{current_position}/{total_count}")
        
        # Keep load button hidden for now (future use)
        self.load_button.setVisible(False)
