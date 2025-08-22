"""
Tag system widgets for the FlipFlopPrompt application using PySide6.
Implements visual tag blocks with removal functionality.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QScrollArea, QSizePolicy, QLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QFont, QPalette, QPixmap, QPainter, QIcon
from typing import List, Callable, Optional, Dict
from enum import Enum
import random


class TagType(Enum):
    """Types of tags with their associated colors."""
    SNIPPET = "snippet"          # Very light blue (static content)
    USER_TEXT = "user_text"      # Very light green (typed text)
    CATEGORY = "category"        # Pale orange (random from category)
    SUBCATEGORY = "subcategory"  # Pale yellow (random from subcategory)
    CUSTOM = "custom"            # Custom tags (loaded from preview)
    MISSING = "missing"          # Red - missing category/subcategory


class Tag:
    """Data model for a tag."""
    
    def __init__(self, text: str, tag_type: TagType, category_path: Optional[List[str]] = None, data: Optional[str] = None, is_missing: bool = False):
        self.text = text
        self.tag_type = tag_type
        self.category_path = category_path or []  # For category/subcategory tags: ["Human", "Gender"]
        self.data = data  # For special data like LLM instructions with full content
        self.is_missing = is_missing  # Flag for missing category/subcategory
        self.id = f"{tag_type.value}_{text}_{hash(str(category_path))}"
    
    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return (self.text == other.text and 
                self.tag_type == other.tag_type and 
                self.category_path == other.category_path)
    
    def __hash__(self):
        return hash(self.id)
    
    def check_if_missing(self, field_name: str) -> bool:
        """Check if this tag references a missing category/subcategory."""
        if self.tag_type not in [TagType.CATEGORY, TagType.SUBCATEGORY, TagType.SNIPPET]:
            return False
        
        # Import snippet manager here to avoid circular imports
        from ..utils.snippet_manager import snippet_manager
        
        try:
            # Get currently selected filters from the main window
            # We need to access the main window to get the current filter selection
            from PySide6.QtWidgets import QApplication
            main_window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'filter_actions'):
                    main_window = widget
                    break
            
            # Get currently selected filters
            selected_filters = []
            if main_window and hasattr(main_window, 'filter_actions'):
                for filter_name, action in main_window.filter_actions.items():
                    if action.isChecked():
                        selected_filters.append(filter_name)
            
            # If no filters are selected, ALL tags should be missing (red)
            if not selected_filters:
                if self.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY, TagType.SNIPPET]:
                    return True  # Mark as missing when no filters are selected
                return False  # User-defined tags remain valid
            
            # Debug logging
            debug_enabled = hasattr(main_window, 'debug_enabled') and main_window.debug_enabled
            if debug_enabled:
                print(f"DEBUG TAG: Checking '{self.text}' in field '{field_name}' with filters: {selected_filters}")
                if self.tag_type == TagType.USER_TEXT:
                    print(f"DEBUG TAG: User-defined tag '{self.text}' - no validation needed")
            
            if self.tag_type == TagType.CATEGORY:
                # Check if category exists in any of the selected filters
                for filter_name in selected_filters:
                    items = snippet_manager.get_category_items(field_name, self.category_path[0], filter_name)
                    if debug_enabled:
                        print(f"DEBUG TAG: Category '{self.text}' in filter '{filter_name}' - found {len(items) if items else 0} items")
                    if items:
                        if debug_enabled:
                            print(f"DEBUG TAG: Category '{self.text}' is VALID in filter '{filter_name}'")
                        return False
                    # Also check with case-insensitive matching
                    for category_name in snippet_manager.get_snippets_for_field(field_name, [filter_name]) or {}:
                        if category_name.lower() == self.category_path[0].lower():
                            items = snippet_manager.get_category_items(field_name, category_name, filter_name)
                            if debug_enabled:
                                print(f"DEBUG TAG: Category '{self.text}' (case-insensitive match '{category_name}') in filter '{filter_name}' - found {len(items) if items else 0} items")
                            if items:
                                if debug_enabled:
                                    print(f"DEBUG TAG: Category '{self.text}' is VALID in filter '{filter_name}' (case-insensitive)")
                                return False
                if debug_enabled:
                    print(f"DEBUG TAG: Category '{self.text}' is MISSING - not found in any selected filters")
                return True
            elif self.tag_type == TagType.SUBCATEGORY:
                # Check if subcategory exists in any of the selected filters
                if len(self.category_path) >= 2:
                    for filter_name in selected_filters:
                        items = snippet_manager.get_subcategory_items(
                            field_name, 
                            self.category_path[0], 
                            self.category_path[1], 
                            filter_name
                        )
                        if debug_enabled:
                            print(f"DEBUG TAG: Subcategory '{self.text}' (category: '{self.category_path[0]}') in filter '{filter_name}' - found {len(items) if items else 0} items")
                        if items:
                            if debug_enabled:
                                print(f"DEBUG TAG: Subcategory '{self.text}' is VALID in filter '{filter_name}'")
                            return False
                        # Also check with case-insensitive matching
                        for category_name in snippet_manager.get_snippets_for_field(field_name, [filter_name]) or {}:
                            if category_name.lower() == self.category_path[0].lower():
                                # Check if subcategory exists in this category
                                category_data = snippet_manager.get_snippets_for_field(field_name, [filter_name]).get(category_name, {})
                                if isinstance(category_data, dict):
                                    for subcategory_name in category_data.keys():
                                        if subcategory_name.lower() == self.category_path[1].lower():
                                            items = snippet_manager.get_subcategory_items(
                                                field_name, 
                                                category_name, 
                                                subcategory_name, 
                                                filter_name
                                            )
                                            if debug_enabled:
                                                print(f"DEBUG TAG: Subcategory '{self.text}' (case-insensitive match: category '{category_name}', subcategory '{subcategory_name}') in filter '{filter_name}' - found {len(items) if items else 0} items")
                                            if items:
                                                if debug_enabled:
                                                    print(f"DEBUG TAG: Subcategory '{self.text}' is VALID in filter '{filter_name}' (case-insensitive)")
                                                return False
                if debug_enabled:
                    print(f"DEBUG TAG: Subcategory '{self.text}' is MISSING - not found in any selected filters")
                return True
            elif self.tag_type == TagType.SNIPPET:
                # Check if snippet exists in any of the selected filters
                # For snippet tags, we need to check if the snippet text exists in any category/subcategory
                for filter_name in selected_filters:
                    # Get all snippets for this field and filter
                    field_snippets = snippet_manager.get_snippets_for_field(field_name, [filter_name])
                    if field_snippets:
                        # Search through all categories and subcategories
                        for category_name, category_data in field_snippets.items():
                            if isinstance(category_data, dict):
                                # Check subcategories
                                for subcategory_name, subcategory_items in category_data.items():
                                    if isinstance(subcategory_items, list) and self.text in subcategory_items:
                                        if debug_enabled:
                                            print(f"DEBUG TAG: Snippet '{self.text}' is VALID in filter '{filter_name}' (category: '{category_name}', subcategory: '{subcategory_name}')")
                                        return False
                                # Check if it's a direct category item
                                if isinstance(category_data, list) and self.text in category_data:
                                    if debug_enabled:
                                        print(f"DEBUG TAG: Snippet '{self.text}' is VALID in filter '{filter_name}' (category: '{category_name}')")
                                    return False
                if debug_enabled:
                    print(f"DEBUG TAG: Snippet '{self.text}' is MISSING - not found in any selected filters")
                return True
        except Exception:
            # If there's any error checking, assume it's missing
            return True
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert tag to dictionary for template persistence."""
        result = {
            "text": self.text,
            "type": self.tag_type.value,
            "category_path": self.category_path
        }
        if self.data:
            result["data"] = self.data
        if self.is_missing:
            result["is_missing"] = self.is_missing
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Tag':
        """Create tag from dictionary for template loading."""
        return cls(
            text=data["text"],
            tag_type=TagType(data["type"]),
            category_path=data.get("category_path", []),
            data=data.get("data"),
            is_missing=data.get("is_missing", False)
        )


class TagWidget(QWidget):
    """Visual representation of a single tag with removal button."""
    
    # Signal emitted when tag should be removed
    remove_requested = Signal(object)  # Emits the Tag object
    
    def __init__(self, tag: Tag, parent=None):
        super().__init__(parent)
        self.tag = tag
        self.setObjectName("tagWidget")  # Give it a unique name to exclude from global styling
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the tag UI."""
        self.setFixedHeight(24)  # Small height for tags
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)
        
        # Tag text label
        self.text_label = QLabel(self.tag.text)
        self.text_label.setFont(QFont("Arial", 8))
        self.text_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Remove button (X)
        self.remove_button = QPushButton("×")
        self.remove_button.setFixedSize(16, 16)
        self.remove_button.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.tag))
        
        layout.addWidget(self.text_label)
        layout.addWidget(self.remove_button)
        
        # Set up tooltip
        self._setup_tooltip()
    
    def _apply_styling(self):
        """Apply styling based on tag type using theme colors."""
        # Import theme manager
        from ..utils.theme_manager import theme_manager
        
        # Get current theme colors
        theme_colors = theme_manager.get_theme_colors()
        
        # Color mapping for tag types using theme colors
        # Warm/hot colors for randomized content, cold colors for static content
        colors = {
            TagType.SNIPPET: theme_colors["snippet_bg"],      # Blue - static snippet content
            TagType.USER_TEXT: theme_colors["user_text_bg"],  # Purple - user-created static content
            TagType.CATEGORY: theme_colors["category_bg"],    # Orange - randomized category content
            TagType.SUBCATEGORY: theme_colors["subcategory_bg"], # Yellow - randomized subcategory content
            TagType.MISSING: theme_colors["missing_tag_bg"]   # Red - missing category/subcategory
        }
        
        # Border colors mapping
        border_colors = {
            TagType.SNIPPET: theme_colors["snippet_border"],      # Blue border
            TagType.USER_TEXT: theme_colors["user_text_border"],  # Purple border
            TagType.CATEGORY: theme_colors["category_border"],    # Orange border
            TagType.SUBCATEGORY: theme_colors["subcategory_border"], # Yellow border
            TagType.MISSING: theme_colors["missing_tag_border"]   # Red border
        }
        
        # Text colors mapping
        text_colors = {
            TagType.SNIPPET: theme_colors["snippet_fg"],      # Black/white text
            TagType.USER_TEXT: theme_colors["user_text_fg"],  # Black/white text
            TagType.CATEGORY: theme_colors["category_fg"],    # Black/white text
            TagType.SUBCATEGORY: theme_colors["subcategory_fg"], # Black/white text
            TagType.MISSING: theme_colors["missing_tag_fg"]   # Black/white text
        }
        
        # Handle missing tags - override with missing tag colors
        if self.tag.is_missing:
            bg_color = colors[TagType.MISSING]
            border_color = border_colors[TagType.MISSING]
            text_color = text_colors[TagType.MISSING]
        else:
            bg_color = colors.get(self.tag.tag_type, theme_colors["tag_bg"])
            border_color = border_colors.get(self.tag.tag_type, theme_colors["tag_border"])
            text_color = text_colors.get(self.tag.tag_type, theme_colors["tag_fg"])
        

        

        
        # Apply comprehensive styling with theme colors
        tag_style = f"""
            QWidget#tagWidget {{
                background-color: {bg_color} !important;
                border: 1px solid {border_color} !important;
                border-radius: 8px !important;
                margin: 1px !important;
                color: {text_color} !important;
            }}
            /* Removed hover effect - no highlighting needed */
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
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color slightly for hover effect."""
        # Simple darkening by reducing each RGB component
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 15)
        g = max(0, g - 15)
        b = max(0, b - 15)
        return f"#{r:02x}{g:02x}{b:02x}"


class FlowLayout(QLayout):
    """Layout that arranges widgets in rows, wrapping when necessary."""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing if spacing >= 0 else 5)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
    
    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, 
                QSizePolicy.ControlType.PushButton, 
                Qt.Orientation.Horizontal
            )
            space_y = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, 
                QSizePolicy.ControlType.PushButton, 
                Qt.Orientation.Vertical
            )
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class TagContainer(QWidget):
    """Container for displaying tags with text input capability."""
    
    # Signal emitted when tags change
    tags_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags: List[Tag] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the container UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # Tag display area with flow layout
        self.tag_frame = QFrame()
        self.tag_frame.setFrameStyle(QFrame.Shape.Box)
        self.tag_frame.setLineWidth(1)
        self.tag_frame.setMinimumHeight(30)
        
        self.tag_layout = FlowLayout(self.tag_frame, margin=4, spacing=4)
        
        # Text input for typing
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type and end with , or . to create tags")
        self.text_input.textChanged.connect(self._on_text_changed)
        self.text_input.returnPressed.connect(self._on_return_pressed)
        
        main_layout.addWidget(self.tag_frame)
        main_layout.addWidget(self.text_input)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the container using theme colors."""
        # Import theme manager
        from ..utils.theme_manager import theme_manager
        
        # Get current theme colors
        theme_colors = theme_manager.get_theme_colors()
        
        style = f"""
            QFrame {{
                background-color: {theme_colors["text_bg"]};
                border: 1px solid {theme_colors["tag_border"]};
                border-radius: 4px;
            }}
            QLineEdit {{
                border: 1px solid {theme_colors["tag_border"]};
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                background-color: {theme_colors["text_bg"]};
                color: {theme_colors["text_fg"]};
            }}
            QLineEdit:focus {{
                border: 2px solid {theme_colors["button_bg"]};
            }}
        """
        self.setStyleSheet(style)
    
    def refresh_theme(self):
        """Refresh the styling when theme changes."""
        self._apply_styling()
        # Refresh all tag widgets
        for i in range(self.tag_layout.count()):
            item = self.tag_layout.itemAt(i)
            if item and item.widget():
                tag_widget = item.widget()
                if hasattr(tag_widget, 'refresh_theme'):
                    tag_widget.refresh_theme()
    
    def add_tag(self, tag: Tag):
        """Add a tag to the container."""
        if tag not in self.tags:
            self.tags.append(tag)
            self._refresh_display()
            self.tags_changed.emit()
    
    def remove_tag(self, tag: Tag):
        """Remove a tag from the container."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._refresh_display()
            self.tags_changed.emit()
    
    def clear_tags(self):
        """Remove all tags."""
        self.tags.clear()
        self._refresh_display()
        self.tags_changed.emit()
    
    def get_tags(self) -> List[Tag]:
        """Get all current tags."""
        return self.tags.copy()
    
    def set_tags(self, tags: List[Tag]):
        """Set tags (for loading from templates)."""
        self.tags = tags.copy()
        self._refresh_display()
        self.tags_changed.emit()
    
    def get_display_text(self) -> str:
        """Get text representation of all tags for preview."""
        tag_texts = []
        for tag in self.tags:
            if tag.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY]:
                # For random tags, show placeholder text
                tag_texts.append(f"[RANDOM {tag.text.upper()}]")
            else:
                tag_texts.append(tag.text)
        
        # Add any typed text
        typed_text = self.text_input.text().strip()
        if typed_text:
            tag_texts.append(typed_text)
        
        return ", ".join(tag_texts)
    
    def generate_random_text(self, seed: int, snippet_manager, selected_filters: List[str] = None) -> str:
        """Generate randomized text based on tags and seed."""
        random.seed(seed)
        result_texts = []
        
        for tag in self.tags:
            if tag.tag_type == TagType.CATEGORY:
                # Get random item from category
                if len(tag.category_path) >= 1:
                    # Need to determine field name - get from parent widget if possible
                    field_name = getattr(self, '_field_name', 'subjects')  # Default fallback
                    filters = selected_filters
                    category_items = []
                    for filter_name in filters:
                        items = snippet_manager.get_category_items(field_name, tag.category_path[0], filter_name)
                        category_items.extend(items)
                    if category_items:
                        result_texts.append(random.choice(category_items))
            elif tag.tag_type == TagType.SUBCATEGORY:
                # Get random item from subcategory
                if len(tag.category_path) >= 2:
                    # Need to determine field name - get from parent widget if possible
                    field_name = getattr(self, '_field_name', 'subjects')  # Default fallback
                    filters = selected_filters
                    subcategory_items = []
                    for filter_name in filters:
                        items = snippet_manager.get_subcategory_items(
                            field_name, tag.category_path[0], tag.category_path[1], filter_name
                        )
                        subcategory_items.extend(items)
                    if subcategory_items:
                        result_texts.append(random.choice(subcategory_items))
            else:
                # Static tag or user text
                result_texts.append(tag.text)
        
        # Add any typed text
        typed_text = self.text_input.text().strip()
        if typed_text:
            result_texts.append(typed_text)
        
        return ", ".join(result_texts)
    
    def _refresh_display(self):
        """Refresh the tag display."""
        # Clear existing tag widgets
        while self.tag_layout.count():
            child = self.tag_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add tag widgets
        for tag in self.tags:
            tag_widget = TagWidget(tag)
            tag_widget.remove_requested.connect(self.remove_tag)
            self.tag_layout.addWidget(tag_widget)
        
        self.tag_frame.update()
    
    def _on_text_changed(self, text: str):
        """Handle text input changes for auto-tagging."""
        # Check for auto-tagging triggers (ending with , or .)
        if text.endswith(',') or text.endswith('.'):
            # Extract the text without the separator
            tag_text = text[:-1].strip()
            if tag_text:
                # Create user text tag
                tag = Tag(tag_text, TagType.USER_TEXT)
                self.add_tag(tag)
                self.text_input.clear()
    
    def _on_return_pressed(self):
        """Handle return key press."""
        text = self.text_input.text().strip()
        if text:
            # Create user text tag
            tag = Tag(text, TagType.USER_TEXT)
            self.add_tag(tag)
            self.text_input.clear()
