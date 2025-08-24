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
from ..utils.logger import get_logger, debug, LogArea
from ..utils.logger import debug, info, warning, error, LogArea


class InlineTagWidget(QWidget):
    """A single inline tag widget that can be edited."""
    
    # Signals
    remove_requested = Signal(object)  # Emits the Tag object
    edit_requested = Signal(object)    # Emits the Tag object for editing
    
    def __init__(self, tag: Tag, parent=None):
        super().__init__(parent)
        self.tag = tag
        self.is_editing = False
        self.setObjectName("InlineTagWidget")  # Give it a unique name
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the tag UI."""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 2, 8, 2)
        self.layout.setSpacing(6)
        
        # Tag text label
        self.text_label = QLabel(self.tag.text)
        self.text_label.setFont(QFont("Arial", 9))
        
        # Remove button (X)
        self.remove_button = QPushButton("×")
        self.remove_button.setFixedSize(14, 14)
        self.remove_button.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.tag))
        
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.remove_button)
        
        # Set minimum size based on content
        font_metrics = QFontMetrics(self.text_label.font())
        text_width = font_metrics.horizontalAdvance(self.tag.text)
        self.setFixedWidth(text_width + 40)  # 40px for remove button, padding, and margins
        self.setFixedHeight(20)  # Consistent height
    
    def _apply_styling(self):
        """Apply styling based on tag type using theme colors."""
        # Import theme manager
        from ..utils.theme_manager import theme_manager
        
        # Get current theme colors
        theme_colors = theme_manager.get_theme_colors()
        
        # Color mapping for tag types using theme colors
        colors = {
            TagType.SNIPPET: theme_colors["snippet_bg"],      # Blue - static snippet content
            TagType.USER_TEXT: theme_colors["user_text_bg"],  # Purple - user-created static content
            TagType.CATEGORY: theme_colors["category_bg"],    # Orange - randomized category content
            TagType.SUBCATEGORY: theme_colors["subcategory_bg"], # Yellow - randomized subcategory content
            TagType.MISSING: theme_colors["missing_tag_bg"]   # Red - missing category/subcategory
        }
        
        border_colors = {
            TagType.SNIPPET: theme_colors["snippet_border"],      # Blue border
            TagType.USER_TEXT: theme_colors["user_text_border"],  # Purple border
            TagType.CATEGORY: theme_colors["category_border"],    # Orange border
            TagType.SUBCATEGORY: theme_colors["subcategory_border"], # Yellow border
            TagType.MISSING: theme_colors["missing_tag_border"]   # Red border
        }
        
        text_colors = {
            TagType.SNIPPET: theme_colors["snippet_fg"],      # Black/white text
            TagType.USER_TEXT: theme_colors["user_text_fg"],  # Black/white text
            TagType.CATEGORY: theme_colors["category_fg"],    # Black/white text
            TagType.SUBCATEGORY: theme_colors["subcategory_fg"], # Black/white text
            TagType.MISSING: theme_colors["missing_tag_fg"]   # Black/white text
        }
        
        # Handle missing tags - override with missing tag colors
        if self.tag.is_missing:
            self.bg_color = QColor(colors[TagType.MISSING])
            self.border_color = QColor(border_colors[TagType.MISSING])
            self.text_color = QColor(text_colors[TagType.MISSING])
        else:
            self.bg_color = QColor(colors.get(self.tag.tag_type, theme_colors["tag_bg"]))
            self.border_color = QColor(border_colors.get(self.tag.tag_type, theme_colors["tag_border"]))
            self.text_color = QColor(text_colors.get(self.tag.tag_type, theme_colors["tag_fg"]))
        
        # Apply comprehensive styling with theme colors
        tag_style = f"""
            QWidget {{
                background-color: {self.bg_color.name()} !important;
                border: 1px solid {self.border_color.name()} !important;
                border-radius: 8px !important;
                margin: 1px !important;
            }}
            /* Removed hover effect - no highlighting needed */
            QLabel {{
                background-color: transparent;
                border: none;
                color: {self.text_color.name()} !important;
            }}
        """
        
        # Remove button styling
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid #ccc;
                color: {colors.get('placeholder_fg', '#666666')};
                font-weight: bold;
                border-radius: 7px;
            }
            QPushButton:hover {
                            background-color: {colors.get('user_text_bg', '#FF6B6B')};
            color: {colors.get('user_text_fg', '#000000')};
            border: 1px solid {colors.get('user_text_border', '#FF6B6B')};
            }
        """
        
        self.setStyleSheet(tag_style)
        self.remove_button.setStyleSheet(button_style)
        
        # Set up tooltip
        self._setup_tooltip()
    
    def _setup_tooltip(self):
        """Set up tooltip for the tag based on its type and state."""
        if self.tag.is_missing:
            tooltip = f"This category/subcategory '{self.tag.text}' is not available in your current snippet files.\n\nYou may need to add the missing snippet files or remove this tag."
        else:
            # Tooltips for different tag types
            tooltips = {
                TagType.SNIPPET: "Snippet tag - Static content that will be included as-is",
                TagType.USER_TEXT: "User text - Custom text you've added",
                TagType.CATEGORY: "Category tag - Will be randomized to a specific item from this category",
                TagType.SUBCATEGORY: "Subcategory tag - Will be randomized to a specific item from this subcategory",
                TagType.CUSTOM: "Custom tag - Special tag with custom behavior"
            }
            tooltip = tooltips.get(self.tag.tag_type, "Tag")
        
        self.setToolTip(tooltip)
    
    def refresh_theme(self):
        """Refresh the styling when theme changes."""
        self._apply_styling()
        # Force repaint to ensure colors are applied
        self.update()
        self.repaint()
    

    
    def paintEvent(self, event):
        """Custom paint event to draw background color."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Call parent paint event for other elements
        super().paintEvent(event)
    
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
        self.scroll_area.setFixedHeight(40)  # Increased from 30 to 40 to better accommodate tags
        
        # Content widget for tags and input
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 2, 20, 2)  # Increased right margin from 15 to 20 to provide more space for scrollbar
        self.content_layout.setSpacing(2)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Text input (always visible)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(self.placeholder)
        self.text_input.setStyleSheet("QLineEdit { border: none; background: transparent; min-width: 100px; }")
        self.text_input.returnPressed.connect(self._create_tag_from_input)
        self.text_input.textChanged.connect(self._on_text_changed)
        
        # Install event filter for focus events
        self.text_input.installEventFilter(self)
        
        self.content_layout.addWidget(self.text_input)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)
        
        # Install event filter for double-click on empty space
        self.scroll_area.installEventFilter(self)
        self.content_widget.installEventFilter(self)
        
        # Timer for delayed tag creation on focus loss
        self.focus_timer = QTimer()
        self.focus_timer.setSingleShot(True)
        self.focus_timer.timeout.connect(self._create_tag_from_input)
    
    def _apply_styling(self):
        """Apply styling to the widget."""
        style = """
            QScrollArea {
                border: 1px solid {colors.get('tag_border', '#D0D0D0')};
                border-radius: 4px;
                background-color: white;
            }
            QScrollArea:focus {
                border: 2px solid {colors.get('focus_color', '#0066cc')};
            }
        """
        self.setStyleSheet(style)
    
    def eventFilter(self, obj, event):
        """Filter events for focus management and double-click handling."""
        if obj == self.text_input:
            if event.type() == QEvent.Type.FocusOut:
                # Start timer for delayed tag creation
                if self.text_input.text().strip():
                    self.focus_timer.start(100)  # 100ms delay
            elif event.type() == QEvent.Type.FocusIn:
                # Cancel timer if focus returns
                self.focus_timer.stop()
        elif obj in [self.scroll_area, self.content_widget]:
            if event.type() == QEvent.Type.MouseButtonDblClick:
                # Double-click on empty space - focus text input
                self.text_input.setFocus()
                return True
        
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
                # Update existing tag and add it back
                old_text = self.editing_tag.text
                self.editing_tag.text = text
                self.add_tag(self.editing_tag)
                # Log user-defined tag edit
                try:
                    if self.editing_tag.tag_type == TagType.USER_TEXT:
                        logger = get_logger()
                        if logger:
                            field_name = getattr(self, '_field_name', 'unknown')
                            logger.log_gui_action("User tag edited", f"Field: {field_name}, Old: '{old_text}', New: '{text}'")
                except Exception:
                    pass
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
            # Detect if this add is part of an edit operation
            is_edit_readd = getattr(self, 'editing_tag', None) is tag
            self.tags.append(tag)
            self._refresh_layout()
            self.tags_changed.emit()
            self.value_changed.emit()
            # Log user-defined tag addition (exclude re-add during edit to avoid duplication)
            if tag.tag_type == TagType.USER_TEXT and not is_edit_readd:
                try:
                    logger = get_logger()
                    if logger:
                        field_name = getattr(self, '_field_name', 'unknown')
                        logger.log_gui_action("User tag added", f"Field: {field_name}, Tag: '{tag.text}'")
                except Exception:
                    pass
    
    def remove_tag(self, tag: Tag):
        """Remove a tag from the input."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._refresh_layout()
            self.tags_changed.emit()
            self.value_changed.emit()
            # Log user-defined tag removal
            if tag.tag_type == TagType.USER_TEXT:
                try:
                    logger = get_logger()
                    if logger:
                        field_name = getattr(self, '_field_name', 'unknown')
                        logger.log_gui_action("User tag removed", f"Field: {field_name}, Tag: '{tag.text}'")
                except Exception:
                    pass
    
    def edit_tag(self, tag: Tag):
        """Start editing a tag (convert back to text)."""
        try:
            if tag in self.tags and tag.tag_type == TagType.USER_TEXT:
                # Store the tag being edited
                self.editing_tag = tag
                
                # Set text and focus
                self.text_input.setText(tag.text)
                self.text_input.setFocus()
                self.text_input.selectAll()
                
                # Remove from tags list
                self.tags.remove(tag)
                
                # Refresh layout
                self._refresh_layout()
                
                # Emit signals
                self.tags_changed.emit()
                self.value_changed.emit()
        except Exception as e:
            error(r"editing tag: {e}", LogArea.ERROR)
            # Reset state on error
            self.editing_tag = None
    
    def _refresh_layout(self):
        """Refresh the layout with current tags and text input."""
        # Store text input to prevent deletion
        text_input_was_in_layout = self.text_input.parent() is not None
        if text_input_was_in_layout:
            self.content_layout.removeWidget(self.text_input)
        
        # Clear current tag widgets only
        widgets_to_delete = []
        for i in range(self.content_layout.count() - 1, -1, -1):
            child = self.content_layout.itemAt(i)
            if child and child.widget() and isinstance(child.widget(), InlineTagWidget):
                widget = self.content_layout.takeAt(i).widget()
                widgets_to_delete.append(widget)
        
        # Delete old tag widgets safely
        for widget in widgets_to_delete:
            widget.setParent(None)
            widget.deleteLater()
        
        # Add tag widgets
        for tag in self.tags:
            tag_widget = InlineTagWidget(tag)
            tag_widget.remove_requested.connect(self.remove_tag)
            tag_widget.edit_requested.connect(self.edit_tag)
            self.content_layout.insertWidget(self.content_layout.count() - 1, tag_widget)
        
        # Ensure text input is at the end
        if not text_input_was_in_layout:
            self.content_layout.insertWidget(self.content_layout.count() - 1, self.text_input)
        else:
            self.content_layout.insertWidget(self.content_layout.count() - 1, self.text_input)
        
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
    
    def generate_random_text(self, seed: int, snippet_manager, selected_filters: List[str] = None) -> str:
        """Generate randomized text based on tags and seed."""
        import random
        result_texts = []
        
        for tag in self.tags:
            if tag.tag_type == TagType.CATEGORY:
                # Get random item from category
                if len(tag.category_path) >= 1:
                    field_name = getattr(self, '_field_name', 'subjects')
                    filters = selected_filters
                    category_items = []
                    for filter_name in filters:
                        items = snippet_manager.get_category_items(field_name, tag.category_path[0], filter_name)
                        category_items.extend(items)
                    if category_items:
                        # Use the SAME deterministic seed logic as realization
                        field_hash = hash(field_name)
                        tag_hash = hash(tag.text)
                        deterministic_seed = seed + field_hash + tag_hash
                        random.seed(deterministic_seed)
                        result_texts.append(random.choice(category_items))
            elif tag.tag_type == TagType.SUBCATEGORY:
                # Get random item from subcategory
                if len(tag.category_path) >= 2:
                    field_name = getattr(self, '_field_name', 'subjects')
                    filters = selected_filters
                    subcategory_items = []
                    for filter_name in filters:
                        items = snippet_manager.get_subcategory_items(
                            field_name, tag.category_path[0], tag.category_path[1], filter_name
                        )
                        subcategory_items.extend(items)
                    if subcategory_items:
                        # Use the SAME deterministic seed logic as realization
                        field_hash = hash(field_name)
                        tag_hash = hash(tag.text)
                        deterministic_seed = seed + field_hash + tag_hash
                        random.seed(deterministic_seed)
                        result_texts.append(random.choice(subcategory_items))
            else:
                # Static tag or user text
                result_texts.append(tag.text)
        
        # Add any current typed text
        current_text = self.text_input.text().strip()
        if current_text:
            result_texts.append(current_text)
        
        return ", ".join(result_texts)
    
    def set_field_name(self, field_name: str):
        """Set the field name for this widget."""
        self._field_name = field_name
    
    def refresh_tags(self):
        """Refresh existing tags to check if they're still missing after snippet reload."""
        # Get field name from parent widget
        field_name = getattr(self, '_field_name', 'subjects')  # Default fallback
        
        # Debug logging
        debug_enabled = False
        try:
            from PySide6.QtWidgets import QApplication
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'debug_enabled'):
                    debug_enabled = widget.debug_enabled
                    break
        except:
            pass
        
        if debug_enabled:
            debug(r"Refreshing tags for field '{field_name}' with {len(self.tags)} tags", LogArea.REFRESH)
        
        for tag in self.tags:
            if debug_enabled:
                debug(r"Processing tag '{tag.text}' (type: {tag.tag_type.value})", LogArea.REFRESH)
            
            if tag.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY, TagType.SNIPPET]:
                # Check if the tag is still missing
                old_missing_state = tag.is_missing
                tag.is_missing = tag.check_if_missing(field_name)
                
                if debug_enabled:
                    debug(r"Tag '{tag.text}' state: {'missing' if tag.is_missing else 'valid'}", LogArea.REFRESH)
                
                if debug_enabled and old_missing_state != tag.is_missing:
                    debug(r"Tag '{tag.text}' changed from {'missing' if old_missing_state else 'valid'} to {'missing' if tag.is_missing else 'valid'}", LogArea.REFRESH)
                
                # If the missing state changed, update the tag widget
                if old_missing_state != tag.is_missing:
                    # Find and update the corresponding tag widget
                    for i in range(self.content_layout.count()):
                        item = self.content_layout.itemAt(i)
                        if item and item.widget():
                            widget = item.widget()
                            if hasattr(widget, 'tag') and widget.tag == tag:
                                widget._apply_styling()
                                widget._setup_tooltip()
                                widget.update()  # Force repaint
                                if debug_enabled:
                                    debug(r"Updated widget for tag '{tag.text}'", LogArea.REFRESH)
                                break
            elif tag.tag_type == TagType.USER_TEXT:
                if debug_enabled:
                    debug(r"User-defined tag '{tag.text}' - no validation needed", LogArea.REFRESH)
    
    def refresh_theme(self):
        """Refresh the styling when theme changes."""
        # Refresh all tag widgets
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'refresh_theme'):
                    widget.refresh_theme()
    
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
