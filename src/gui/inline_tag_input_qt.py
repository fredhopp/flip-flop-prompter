"""
Inline tag input widget for the FlipFlopPrompt application using PySide6.
Combines text input and tags in a single unified field.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, 
    QScrollArea, QSizePolicy, QLineEdit, QApplication
)
from PySide6.QtCore import Qt, Signal, QEvent, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor, QFontMetrics
from typing import List, Callable, Optional
from .tag_widgets_qt import Tag, TagType
import sys


class InlineTagWidget(QWidget):
    """A single inline tag widget that can be edited."""
    
    # Signals
    remove_requested = Signal(object)  # Emits the Tag object
    edit_requested = Signal(object)    # Emits the Tag object for editing
    
    def __init__(self, tag: Tag, parent=None):
        super().__init__(parent)
        self.tag = tag
        self.is_editing = False
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the tag UI."""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        
        # Tag text label
        self.text_label = QLabel(self.tag.text)
        self.text_label.setFont(QFont("Arial", 9))
        
        # Remove button (X)
        self.remove_button = QPushButton("×")
        self.remove_button.setFixedSize(16, 16)
        self.remove_button.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.tag))
        
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.remove_button)
        
        # Set fixed height based on content
        font_metrics = QFontMetrics(self.text_label.font())
        text_width = font_metrics.horizontalAdvance(self.tag.text)
        self.setFixedSize(text_width + 30, 22)  # 30px for remove button and padding
    
    def _apply_styling(self):
        """Apply styling based on tag type."""
        # Color mapping for tag types
        colors = {
            TagType.SNIPPET: "#E3F2FD",      # Very light blue
            TagType.USER_TEXT: "#E8F5E8",    # Very light green
            TagType.CATEGORY: "#FFF3E0",     # Pale orange
            TagType.SUBCATEGORY: "#FFFDE7"   # Pale yellow
        }
        
        bg_color = colors.get(self.tag.tag_type, "#F5F5F5")
        
        # Tag widget styling
        tag_style = f"""
            InlineTagWidget {{
                background-color: {bg_color};
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                margin: 1px 2px;
            }}
            InlineTagWidget:hover {{
                border: 2px solid #0066cc;
            }}
        """
        
        # Remove button styling
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FF6B6B;
                color: white;
            }
        """
        
        self.setStyleSheet(tag_style)
        self.remove_button.setStyleSheet(button_style)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click for editing user text tags."""
        if self.tag.tag_type == TagType.USER_TEXT:
            self.edit_requested.emit(self.tag)
        super().mouseDoubleClickEvent(event)


class InlineTagInputWidget(QWidget):
    """Widget that combines tags and text input in a single line."""
    
    # Signals
    tags_changed = Signal()
    value_changed = Signal()
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.tags: List[Tag] = []
        self.current_text = ""
        self.editing_tag = None  # Tag being edited
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the input widget UI."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        
        # Scrollable content area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFixedHeight(30)
        
        # Content widget for tags and input
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 2, 4, 2)
        self.content_layout.setSpacing(2)
        
        # Text input (initially visible)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(self.placeholder)
        self.text_input.setStyleSheet("QLineEdit { border: none; background: transparent; }")
        self.text_input.returnPressed.connect(self._create_tag_from_input)
        self.text_input.textChanged.connect(self._on_text_changed)
        
        # Install event filter for focus events
        self.text_input.installEventFilter(self)
        
        self.content_layout.addWidget(self.text_input)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)
        
        # Timer for delayed tag creation on focus loss
        self.focus_timer = QTimer()
        self.focus_timer.setSingleShot(True)
        self.focus_timer.timeout.connect(self._create_tag_from_input)
    
    def _apply_styling(self):
        """Apply styling to the widget."""
        style = """
            QScrollArea {
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background-color: white;
            }
            QScrollArea:focus {
                border: 2px solid #0066cc;
            }
        """
        self.setStyleSheet(style)
    
    def eventFilter(self, obj, event):
        """Filter events for focus management."""
        if obj == self.text_input:
            if event.type() == QEvent.Type.FocusOut:
                # Start timer for delayed tag creation
                if self.text_input.text().strip():
                    self.focus_timer.start(100)  # 100ms delay
            elif event.type() == QEvent.Type.FocusIn:
                # Cancel timer if focus returns
                self.focus_timer.stop()
        
        return super().eventFilter(obj, event)
    
    def _on_text_changed(self, text: str):
        """Handle text input changes."""
        self.current_text = text
        self.value_changed.emit()
    
    def _create_tag_from_input(self):
        """Create a tag from current text input."""
        text = self.text_input.text().strip()
        if text:
            if self.editing_tag:
                # Update existing tag
                self.editing_tag.text = text
                self.editing_tag = None
            else:
                # Create new tag
                tag = Tag(text, TagType.USER_TEXT)
                self.add_tag(tag)
            
            self.text_input.clear()
            self.current_text = ""
            self._refresh_layout()
    
    def add_tag(self, tag: Tag):
        """Add a tag to the input."""
        if tag not in self.tags:
            self.tags.append(tag)
            self._refresh_layout()
            self.tags_changed.emit()
            self.value_changed.emit()
    
    def remove_tag(self, tag: Tag):
        """Remove a tag from the input."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._refresh_layout()
            self.tags_changed.emit()
            self.value_changed.emit()
    
    def edit_tag(self, tag: Tag):
        """Start editing a tag (convert back to text)."""
        if tag in self.tags and tag.tag_type == TagType.USER_TEXT:
            self.text_input.setText(tag.text)
            self.text_input.setFocus()
            self.text_input.selectAll()
            self.editing_tag = tag
            self.tags.remove(tag)
            self._refresh_layout()
    
    def _refresh_layout(self):
        """Refresh the layout with current tags and text input."""
        # Clear current layout (except stretch)
        while self.content_layout.count() > 0:
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add tag widgets
        for tag in self.tags:
            tag_widget = InlineTagWidget(tag)
            tag_widget.remove_requested.connect(self.remove_tag)
            tag_widget.edit_requested.connect(self.edit_tag)
            self.content_layout.addWidget(tag_widget)
        
        # Add text input
        self.content_layout.addWidget(self.text_input)
        self.content_layout.addStretch()
        
        # Update scroll area
        self.content_widget.adjustSize()
    
    def get_tags(self) -> List[Tag]:
        """Get all current tags."""
        return self.tags.copy()
    
    def set_tags(self, tags: List[Tag]):
        """Set tags (for loading from templates)."""
        self.tags = tags.copy()
        self._refresh_layout()
        self.tags_changed.emit()
        self.value_changed.emit()
    
    def clear_tags(self):
        """Remove all tags."""
        self.tags.clear()
        self.text_input.clear()
        self.current_text = ""
        self._refresh_layout()
        self.tags_changed.emit()
        self.value_changed.emit()
    
    def get_display_text(self) -> str:
        """Get text representation of all tags plus current input."""
        tag_texts = []
        for tag in self.tags:
            if tag.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY]:
                # For random tags, show placeholder text
                tag_texts.append(f"[RANDOM {tag.text.upper()}]")
            else:
                tag_texts.append(tag.text)
        
        # Add any current typed text
        current_text = self.text_input.text().strip()
        if current_text:
            tag_texts.append(current_text)
        
        return ", ".join(tag_texts)
    
    def generate_random_text(self, seed: int, snippet_manager, selected_families: List[str] = None) -> str:
        """Generate randomized text based on tags and seed."""
        import random
        random.seed(seed)
        result_texts = []
        
        for tag in self.tags:
            if tag.tag_type == TagType.CATEGORY:
                # Get random item from category
                if len(tag.category_path) >= 1:
                    field_name = getattr(self, '_field_name', 'subjects')
                    families = selected_families or ["PG"]
                    category_items = []
                    for family in families:
                        items = snippet_manager.get_category_items(field_name, tag.category_path[0], family)
                        category_items.extend(items)
                    if category_items:
                        result_texts.append(random.choice(category_items))
            elif tag.tag_type == TagType.SUBCATEGORY:
                # Get random item from subcategory
                if len(tag.category_path) >= 2:
                    field_name = getattr(self, '_field_name', 'subjects')
                    families = selected_families or ["PG"]
                    subcategory_items = []
                    for family in families:
                        items = snippet_manager.get_subcategory_items(
                            field_name, tag.category_path[0], tag.category_path[1], family
                        )
                        subcategory_items.extend(items)
                    if subcategory_items:
                        result_texts.append(random.choice(subcategory_items))
            else:
                # Static tag or user text
                result_texts.append(tag.text)
        
        # Add any current typed text
        current_text = self.text_input.text().strip()
        if current_text:
            result_texts.append(current_text)
        
        return ", ".join(result_texts)
    
    def set_value(self, value: str):
        """Set the field value (for backwards compatibility)."""
        self.clear_tags()
        if value.strip():
            # Split by commas and create tags
            parts = [part.strip() for part in value.split(',')]
            for part in parts:
                if part:
                    tag = Tag(part, TagType.USER_TEXT)
                    self.add_tag(tag)
