"""
Field widgets for the FlipFlopPrompt application using PySide6.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QTextOption
from ..utils.theme_manager import theme_manager
from typing import Callable, Optional


class FieldWidget(QWidget):
    """Base class for field widgets using PySide6."""
    
    # Signal emitted when the field value changes
    value_changed = Signal()
    
    def __init__(self, label: str, placeholder: str = "", change_callback: Optional[Callable] = None):
        super().__init__()
        
        self.label_text = label
        self.placeholder = placeholder
        self.change_callback = change_callback
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 2, 0, 2)
        self.layout.setSpacing(2)
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.value_changed.connect(self.change_callback)
    
    def _create_widgets(self):
        """Create the widget components. Override in subclasses."""
        pass
    
    def _trigger_change(self):
        """Trigger the change callback."""
        self.value_changed.emit()
    
    def get_value(self) -> str:
        """Get the current field value. Override in subclasses."""
        return ""
    
    def set_value(self, value: str):
        """Set the field value. Override in subclasses."""
        pass
    
    def clear(self):
        """Clear the field value."""
        self.set_value("")
    
    def _get_field_name_from_label(self, label: str) -> str:
        """Convert label to field name for snippet lookup."""
        # Remove colon and convert to lowercase with underscores
        field_name = label.replace(":", "").strip().lower().replace(" ", "_")
        
        # Handle special cases - match the actual field names in snippet data
        field_mappings = {
            "date_and_time": "date_time",
            "subjects_pose_and_action": "subjects_pose_and_action",
            "camera_framing_and_action": "camera_framing_and_action",
            "color_grading_&_mood": "color_grading_&_mood",
            "additional_details": "details"
        }
        
        return field_mappings.get(field_name, field_name)


class TextFieldWidget(FieldWidget):
    """Single-line text field widget with snippet dropdown."""
    
    def __init__(self, label: str, placeholder: str = "", change_callback: Optional[Callable] = None):
        super().__init__(label, placeholder, change_callback)
    
    def _create_widgets(self):
        """Create the text field widgets."""
        # Create label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.layout.addWidget(self.label)
        
        # Create horizontal layout for input and snippet button
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)
        
        # Create text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(self.placeholder)
        self.text_input.textChanged.connect(self._on_text_changed)
        
        # Add focus events for placeholder behavior
        self.text_input.focusInEvent = self._on_focus_in
        self.text_input.focusOutEvent = self._on_focus_out
        
        input_layout.addWidget(self.text_input)
        
        # Create snippet button (placeholder for now)
        self.snippet_button = QPushButton("Snippets")
        self.snippet_button.setMinimumWidth(90)  # Ensure enough width for "Snippets"
        self.snippet_button.clicked.connect(self._show_snippets)
        input_layout.addWidget(self.snippet_button)
        
        # Add input layout to main layout
        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        self.layout.addWidget(input_widget)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the widgets."""
        colors = theme_manager.get_theme_colors()
        
        # Style the text input
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px;
                border: 1px solid {colors.get('tag_border', '#ccc')};
                border-radius: 3px;
                font-size: 11px;
                background-color: {colors.get('text_bg', '#ffffff')};
                color: {colors.get('text_fg', '#000000')};
            }}
            QLineEdit:focus {{
                border-color: {colors.get('focus_color', '#0066cc')};
            }}
        """)
        
        # Style the snippet button
        self.snippet_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.get('button_bg', '#0066cc')};
                color: {colors.get('button_fg', '#ffffff')};
                border: 2px solid {colors.get('button_bg', '#0066cc')};
                border-radius: 3px;
                padding: 6px 8px;
                font-weight: bold;
                font-size: 8px;
            }}
            QPushButton:hover {{
                background-color: {colors.get('button_hover_bg', '#0052a3')};
                border-color: {colors.get('button_hover_bg', '#0052a3')};
            }}
            QPushButton:pressed {{
                background-color: {colors.get('button_pressed_bg', '#003d7a')};
                border-color: {colors.get('button_pressed_bg', '#003d7a')};
            }}
        """)
    
    def _on_text_changed(self, text):
        """Handle text changes."""
        self._trigger_change()
    
    def _show_snippets(self):
        """Show snippet selection dialog."""
        from .snippet_widgets_qt import SnippetPopup
        
        # Get field name for snippet lookup
        field_name = self._get_field_name_from_label(self.label_text)
        
        # Get selected filters from main window (if available)
        main_window = None
        widget = self
        
        # Walk up the widget hierarchy to find the main window
        while widget and not main_window:
            widget = widget.parent()
            if hasattr(widget, '_get_selected_filters'):
                main_window = widget
                break
        
        if main_window:
            selected_filters = main_window._get_selected_filters()
        else:
            selected_filters = []  # No default
        
        # Create and show snippet popup
        popup = SnippetPopup(self, field_name, selected_filters, self._on_snippet_select)
        popup.show_popup()
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        current_value = self.text_input.text()
        
        # Toggle behavior: if snippet is already in the field, remove it
        if snippet in current_value:
            # Remove the snippet and clean up extra spaces/commas
            new_value = current_value.replace(snippet, "").strip()
            new_value = new_value.replace(",,", ",").strip(",")
        else:
            # Add the snippet
            if current_value:
                new_value = f"{current_value}, {snippet}"
            else:
                new_value = snippet
        
        # Set the new value
        self.text_input.setText(new_value)
        self._trigger_change()
    
    def get_value(self) -> str:
        """Get the current text value."""
        return self.text_input.text()
    
    def set_value(self, value: str):
        """Set the text value."""
        self.text_input.setText(value)
    
    def _on_focus_in(self, event):
        """Handle focus in event."""
        # Call the original focus in event
        QLineEdit.focusInEvent(self.text_input, event)
    
    def _on_focus_out(self, event):
        """Handle focus out event."""
        # Call the original focus out event
        QLineEdit.focusOutEvent(self.text_input, event)


class TextAreaWidget(FieldWidget):
    """Multi-line text area widget."""
    
    def __init__(self, label: str, placeholder: str = "", change_callback: Optional[Callable] = None):
        super().__init__(label, placeholder, change_callback)
    
    def _create_widgets(self):
        """Create the text area widgets."""
        # Create label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.layout.addWidget(self.label)
        
        # Create text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.placeholder)
        
        # Calculate line height for auto-sizing
        font_metrics = self.text_edit.fontMetrics()
        line_height = font_metrics.lineSpacing()
        
        # Start with 2 line height + padding to prevent placeholder clipping
        min_height = (line_height * 2) + 12   # 2 lines + padding
        max_height = (line_height * 4) + 12   # 4 lines + padding
        
        self.text_edit.setMinimumHeight(min_height)
        self.text_edit.setMaximumHeight(max_height)
        
        # Enable word wrap and connect signals
        self.text_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.textChanged.connect(self._resize_to_content)
        
        self.layout.addWidget(self.text_edit)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the text area."""
        colors = theme_manager.get_theme_colors()
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                padding: 6px;
                border: 1px solid {colors.get('tag_border', '#ccc')};
                border-radius: 3px;
                font-size: 11px;
                font-family: 'Consolas', 'Courier New', monospace;
                background-color: {colors.get('text_bg', '#ffffff')};
                color: {colors.get('text_fg', '#000000')};
            }}
            QTextEdit:focus {{
                border-color: {colors.get('focus_color', '#0066cc')};
            }}
        """)
    
    def _on_text_changed(self):
        """Handle text changes."""
        self._trigger_change()
    
    def _resize_to_content(self):
        """Resize the text edit to fit content up to max 4 lines."""
        document = self.text_edit.document()
        document_height = document.size().height()
        
        # Calculate single line height
        font_metrics = self.text_edit.fontMetrics()
        line_height = font_metrics.lineSpacing()
        
        # Calculate required height with padding
        padding = 12  # 6px top + 6px bottom
        content_height = int(document_height) + padding
        
        # Ensure we stay within min/max bounds
        min_height = (line_height * 2) + padding  # 2 lines minimum
        max_height = (line_height * 4) + padding
        
        new_height = max(min_height, min(content_height, max_height))
        self.text_edit.setFixedHeight(new_height)
    
    def get_value(self) -> str:
        """Get the current text value."""
        return self.text_edit.toPlainText()
    
    def set_value(self, value: str):
        """Set the text value."""
        self.text_edit.setPlainText(value)
        self._resize_to_content()  # Resize after setting value
    
    def clear(self):
        """Clear the text area."""
        self.text_edit.clear()
        self._resize_to_content()  # Resize after clearing


class DateTimeWidget(FieldWidget):
    """Date and time selection widget."""
    
    def __init__(self, label: str, placeholder: str = "", change_callback: Optional[Callable] = None):
        super().__init__(label, placeholder, change_callback)
    
    def _create_widgets(self):
        """Create the datetime widgets."""
        # For now, use a simple text field
        # Later this can be enhanced with proper date/time pickers
        
        # Create label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.layout.addWidget(self.label)
        
        # Create text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(self.placeholder)
        self.text_input.textChanged.connect(self._on_text_changed)
        self.layout.addWidget(self.text_input)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the datetime input."""
        colors = theme_manager.get_theme_colors()
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px;
                border: 1px solid {colors.get('tag_border', '#ccc')};
                border-radius: 3px;
                font-size: 11px;
                background-color: {colors.get('text_bg', '#ffffff')};
                color: {colors.get('text_fg', '#000000')};
            }}
            QLineEdit:focus {{
                border-color: {colors.get('focus_color', '#0066cc')};
            }}
        """)
    
    def _on_text_changed(self, text):
        """Handle text changes."""
        self._trigger_change()
    
    def get_value(self) -> str:
        """Get the current datetime value."""
        return self.text_input.text()
    
    def set_value(self, value: str):
        """Set the datetime value."""
        self.text_input.setText(value)
