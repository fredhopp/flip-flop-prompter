"""
Preview panel for displaying generated prompts using PySide6 (tabbed layout with Summary and Final Prompt).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QFrame, QScrollArea, QGroupBox, QPushButton, QLineEdit, QTabWidget
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
    ERROR = "error" # Added for error messages


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
    
    # New signal for realize button
    realize_requested = Signal()
    
    def __init__(self):
        super().__init__()
        
        # State management
        self.current_text = ""
        self.summary_text = ""
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
        
        # Create group box without title
        self.frame = QGroupBox()
        
        # Frame layout
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(8)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(200)
        self.tab_widget.setMaximumHeight(300)
        
        # Create Summary tab
        self._create_summary_tab()
        
        # Create Final Prompt tab
        self._create_final_prompt_tab()
        
        # Add tab widget to frame
        frame_layout.addWidget(self.tab_widget)
        
        # Create navigation controls
        self._create_navigation_controls(frame_layout)
        
        # Add frame to main layout
        layout.addWidget(self.frame)
        
        # Set initial text and styling
        self._set_initial_state()
        
        # Apply initial styling
        self._apply_styling()
    
    def _create_summary_tab(self):
        """Create the Prompt Summary tab."""
        # Create summary tab widget
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(5, 5, 5, 5)
        summary_layout.setSpacing(8)
        
        # Summary text area
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Consolas", 10))
        summary_layout.addWidget(self.summary_text)
        
        # Realize button
        self.realize_button = QPushButton("Realize")
        self.realize_button.clicked.connect(self.realize_requested.emit)
        summary_layout.addWidget(self.realize_button)
        
        # Add tab
        self.tab_widget.addTab(summary_widget, "Prompt Summary")
    
    def _create_final_prompt_tab(self):
        """Create the Final Prompt tab."""
        # Create final prompt tab widget
        final_widget = QWidget()
        final_layout = QVBoxLayout(final_widget)
        final_layout.setContentsMargins(5, 5, 5, 5)
        final_layout.setSpacing(8)
        
        # Final Prompt text area
        self.final_text = QTextEdit()
        self.final_text.setReadOnly(True)
        self.final_text.setFont(QFont("Consolas", 10))
        final_layout.addWidget(self.final_text)
        
        # Add tab
        self.tab_widget.addTab(final_widget, "Final Prompt")
        
        # Store reference to final widget for styling
        self.final_widget = final_widget
        
        # Apply blue background immediately
        try:
            colors = theme_manager.get_theme_colors()
            final_widget_style = f"""
                QWidget {{
                    background-color: {colors.get('preview_final_bg', '#e6f3ff')};
                    border: none;
                }}
            """
            self.final_widget.setStyleSheet(final_widget_style)
        except Exception as e:
            error(f"Error applying initial final widget styling: {e}", LogArea.GENERAL)
    
    def _set_initial_state(self):
        """Set the initial state with placeholder text."""
        self.summary_text.setPlainText("Enter tags to see the raw prompt summary here...")
        self.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
        self.summary_state = PreviewState.PLACEHOLDER
        self.final_state = PreviewState.PLACEHOLDER
    
    def _create_navigation_controls(self, parent_layout):
        """Create navigation controls for history."""
        # Create horizontal layout for navigation
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 5, 0, 0)
        
        # Navigation buttons
        self.back_button = QPushButton()
        self.back_button.setIcon(qta.icon('fa5s.chevron-left'))
        self.back_button.setToolTip("Previous prompt")
        self.back_button.clicked.connect(self.history_back_requested.emit)
        nav_layout.addWidget(self.back_button)
        
        # History position display
        self.history_label = QLabel("0/0")
        self.history_label.setAlignment(Qt.AlignCenter)
        self.history_label.setMinimumWidth(60)
        nav_layout.addWidget(self.history_label)
        
        # Forward button
        self.forward_button = QPushButton()
        self.forward_button.setIcon(qta.icon('fa5s.chevron-right'))
        self.forward_button.setToolTip("Next prompt")
        self.forward_button.clicked.connect(self.history_forward_requested.emit)
        nav_layout.addWidget(self.forward_button)
        
        # Jump to position input
        self.jump_input = QLineEdit()
        self.jump_input.setPlaceholderText("Jump to...")
        self.jump_input.setMaximumWidth(80)
        self.jump_input.returnPressed.connect(self._on_jump_requested)
        nav_layout.addWidget(self.jump_input)
        
        # Spacer
        nav_layout.addStretch()
        
        # Action buttons
        self.copy_button = QPushButton()
        self.copy_button.setIcon(qta.icon('fa5s.copy'))
        self.copy_button.setToolTip("Copy to clipboard")
        self.copy_button.clicked.connect(self.copy_requested.emit)
        nav_layout.addWidget(self.copy_button)
        
        self.save_button = QPushButton()
        self.save_button.setIcon(qta.icon('fa5s.save'))
        self.save_button.setToolTip("Save prompt")
        self.save_button.clicked.connect(self.save_requested.emit)
        nav_layout.addWidget(self.save_button)
        
        self.save_all_button = QPushButton()
        self.save_all_button.setIcon(qta.icon('fa5s.save'))
        self.save_all_button.setToolTip("Save all prompts")
        self.save_all_button.clicked.connect(self.save_all_requested.emit)
        nav_layout.addWidget(self.save_all_button)
        
        # Add navigation layout to parent
        parent_layout.addLayout(nav_layout)
    
    def _on_jump_requested(self):
        """Handle jump to position request."""
        try:
            position = int(self.jump_input.text())
            self.history_jump_requested.emit(position)
            self.jump_input.clear()
        except ValueError:
            pass
    
    def set_summary_text(self, text: str):
        """Set the summary text in the Prompt Summary tab."""
        self.summary_text.setPlainText(text)
        if text.strip():
            self.summary_state = PreviewState.PREVIEW
        else:
            self.summary_state = PreviewState.PLACEHOLDER
        self._apply_styling()
    
    def set_final_prompt(self, text: str):
        """Set the final prompt text in the Final Prompt tab."""
        self.final_text.setPlainText(text)
        # Check if this is an error message
        if text.strip().startswith("[ERROR:"):
            self.final_state = PreviewState.ERROR
        elif text.strip():
            self.final_state = PreviewState.FINAL
        else:
            self.final_state = PreviewState.PLACEHOLDER
        self._apply_styling()
    
    def update_preview(self, text: str):
        """Update the preview text (legacy method - now updates summary)."""
        self.set_summary_text(text)
    
    def set_history_state(self, is_history: bool, total_count: int):
        """Set the history state for the preview panel."""
        if is_history:
            self.final_state = PreviewState.HISTORY
        else:
            self.final_state = PreviewState.PLACEHOLDER
        self._apply_styling()
    
    def update_navigation_controls(self, current_pos: int, total_count: int, can_go_back: bool, can_go_forward: bool):
        """Update navigation controls state."""
        self.history_label.setText(f"{current_pos}/{total_count}")
        self.back_button.setEnabled(can_go_back)
        self.forward_button.setEnabled(can_go_forward)
    
    def get_current_text(self) -> str:
        """Get the current text from the active tab."""
        if self.tab_widget.currentIndex() == 0:  # Summary tab
            return self.summary_text.toPlainText()
        else:  # Final Prompt tab
            return self.final_text.toPlainText()
    
    def get_final_prompt(self) -> str:
        """Get the final prompt text."""
        return self.final_text.toPlainText()
    
    def get_word_count(self) -> int:
        """Get word count of current text."""
        text = self.get_current_text()
        return len(text.split()) if text.strip() else 0
    
    def get_char_count(self) -> int:
        """Get character count of current text."""
        return len(self.get_current_text())
    
    def update_llm_info(self, llm_name: str):
        """Update LLM information (placeholder for future use)."""
        pass
    
    def refresh_navigation_styling(self):
        """Refresh navigation styling."""
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling based on current state."""
        self._styling_timer.start(50)  # Debounce styling updates
    
    def _apply_state_styling_delayed(self):
        """Apply state-based styling with debouncing."""
        try:
            colors = theme_manager.get_theme_colors()
            
            # Style summary text
            if self.summary_state == PreviewState.PLACEHOLDER:
                summary_style = f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('placeholder_bg', '#f5f5f5')};
                        color: {colors.get('placeholder_fg', '#666666')};
                        padding: 10px;
                        font-style: italic;
                    }}
                """
            else:
                summary_style = f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('preview_bg', '#ffffff')};
                        color: {colors.get('preview_fg', '#000000')};
                        padding: 10px;
                    }}
                """
            self.summary_text.setStyleSheet(summary_style)
            
            # Style final text
            final_style = self._get_style_for_state(self.final_state)
            self.final_text.setStyleSheet(final_style)
            
            # Style final widget container with blue background (always blue)
            try:
                final_widget_style = f"""
                    QWidget {{
                        background-color: {colors.get('preview_final_bg', '#e6f3ff')};
                        border: none;
                    }}
                """
                self.final_widget.setStyleSheet(final_widget_style)
            except Exception as e:
                error(f"Error styling final widget: {e}", LogArea.GENERAL)
            
            # Style tab widget to give Final Prompt tab blue background
            try:
                tab_style = f"""
                    QTabWidget::pane {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                    }}
                    QTabWidget::tab-bar {{
                        alignment: left;
                    }}
                    QTabBar::tab {{
                        background-color: {colors.get('text_bg', '#ffffff')};
                        color: {colors.get('text_fg', '#000000')};
                        padding: 8px 12px;
                        margin-right: 2px;
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-bottom: none;
                        border-top-left-radius: 3px;
                        border-top-right-radius: 3px;
                    }}
                    QTabBar::tab:selected {{
                        background-color: {colors.get('text_bg', '#ffffff')};
                        border-bottom: 1px solid {colors.get('text_bg', '#ffffff')};
                    }}
                    QTabBar::tab:selected:last {{
                        background-color: {colors.get('preview_final_bg', '#e6f3ff')};
                        color: {colors.get('preview_final_fg', '#0066cc')};
                        border-bottom: 1px solid {colors.get('preview_final_bg', '#e6f3ff')};
                    }}
                    QTabBar::tab:hover {{
                        background-color: {colors.get('button_hover_bg', '#f0f0f0')};
                    }}
                """
                self.tab_widget.setStyleSheet(tab_style)
            except Exception as e:
                error(f"Error styling tab widget: {e}", LogArea.GENERAL)
            
            # Style realize button
            realize_style = f"""
                QPushButton {{
                    background-color: {colors.get('button_bg', '#4a90e2')};
                    color: {colors.get('button_fg', '#ffffff')};
                    border: 1px solid {colors.get('button_border', '#357abd')};
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('button_hover_bg', '#357abd')};
                }}
                QPushButton:pressed {{
                    background-color: {colors.get('button_pressed_bg', '#2e6da4')};
                }}
            """
            self.realize_button.setStyleSheet(realize_style)
            
            # Style navigation buttons
            nav_button_style = f"""
                QPushButton {{
                    background-color: {colors.get('button_bg', '#4a90e2')};
                    color: {colors.get('button_fg', '#ffffff')};
                    border: 1px solid {colors.get('button_border', '#357abd')};
                    border-radius: 3px;
                    padding: 5px;
                    min-width: 30px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('button_hover_bg', '#357abd')};
                }}
                QPushButton:pressed {{
                    background-color: {colors.get('button_pressed_bg', '#2e6da4')};
                }}
                QPushButton:disabled {{
                    background-color: {colors.get('button_disabled_bg', '#cccccc')};
                    color: {colors.get('button_disabled_fg', '#666666')};
                }}
            """
            self.back_button.setStyleSheet(nav_button_style)
            self.forward_button.setStyleSheet(nav_button_style)
            self.copy_button.setStyleSheet(nav_button_style)
            self.save_button.setStyleSheet(nav_button_style)
            self.save_all_button.setStyleSheet(nav_button_style)
            
            # Style history label
            history_label_style = f"""
                QLabel {{
                    color: {colors.get('text_fg', '#000000')};
                    font-weight: bold;
                    padding: 5px;
                }}
            """
            self.history_label.setStyleSheet(history_label_style)
            
            # Style jump input
            jump_input_style = f"""
                QLineEdit {{
                    border: 1px solid {colors.get('input_border', '#cccccc')};
                    border-radius: 3px;
                    padding: 3px 5px;
                    background-color: {colors.get('input_bg', '#ffffff')};
                    color: {colors.get('input_fg', '#000000')};
                }}
            """
            self.jump_input.setStyleSheet(jump_input_style)
        except Exception as e:
            error(f"Error applying styling: {e}", LogArea.GENERAL)
    
    def _get_style_for_state(self, state: PreviewState) -> str:
        """Get the style for a specific preview state."""
        try:
            colors = theme_manager.get_theme_colors()
            
            if state == PreviewState.PLACEHOLDER:
                return f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('placeholder_bg', '#f5f5f5')};
                        color: {colors.get('placeholder_fg', '#666666')};
                        padding: 10px;
                        font-style: italic;
                    }}
                """
            elif state == PreviewState.PREVIEW:
                return f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('preview_bg', '#ffffff')};
                        color: {colors.get('preview_fg', '#000000')};
                        padding: 10px;
                    }}
                """
            elif state == PreviewState.FINAL:
                return f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('preview_final_bg', '#e6f3ff')};
                        color: {colors.get('preview_final_fg', '#0066cc')};
                        padding: 10px;
                        font-weight: bold;
                    }}
                """
            elif state == PreviewState.HISTORY:
                return f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('history_bg', '#f0f0f0')};
                        color: {colors.get('history_fg', '#333333')};
                        padding: 10px;
                    }}
                """
            elif state == PreviewState.ERROR:
                return f"""
                    QTextEdit {{
                        border: 1px solid {colors.get('tag_border', '#cccccc')};
                        border-radius: 3px;
                        background-color: {colors.get('error_bg', '#ffebee')};
                        color: {colors.get('error_fg', '#c62828')};
                        padding: 10px;
                        font-weight: bold;
                    }}
                """
            else:
                return ""
        except Exception as e:
            error(f"Error getting style for state {state}: {e}", LogArea.GENERAL)
            return ""
