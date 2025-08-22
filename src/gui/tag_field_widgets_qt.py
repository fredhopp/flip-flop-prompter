"""
Tag-enabled field widgets for the FlipFlopPrompt application using PySide6.
These replace the traditional text input widgets with tag-based input systems.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon
from pathlib import Path
from typing import Callable, Optional, List

# Try to import qtawesome, fallback to text if not available
try:
    import qtawesome as qta
    FONTAWESOME_AVAILABLE = True
except ImportError:
    FONTAWESOME_AVAILABLE = False
    print("Warning: qtawesome not available, using text icons")

from .tag_widgets_qt import Tag, TagType
from .inline_tag_input_qt import InlineTagInputWidget
from .snippet_widgets_qt import SnippetPopup
from ..utils.snippet_manager import snippet_manager


class TagFieldWidget(QWidget):
    """Base class for tag-enabled field widgets."""
    
    # Signal emitted when field value changes
    value_changed = Signal()
    
    def __init__(self, label: str, placeholder: str = "", change_callback: Optional[Callable] = None):
        super().__init__()
        
        self.label_text = label
        self.placeholder = placeholder
        self.change_callback = change_callback
        self.field_name = self._get_field_name_from_label(label)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Reduced from 1 to 0 for tighter spacing
        self.layout.setSpacing(0)  # Reduced from 1 to 0 for minimal spacing between title and field
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.value_changed.connect(self.change_callback)
    
    def _create_widgets(self):
        """Create the widget components."""
        # Create label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.layout.addWidget(self.label)
        
        # Create horizontal layout for tag container and snippet button
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)  # Increased from 5 to 10 to prevent scrollbar overlap
        
        # Create inline tag input
        self.tag_input = InlineTagInputWidget(self.placeholder)
        self.tag_input.tags_changed.connect(self._on_tags_changed)
        self.tag_input.value_changed.connect(self._on_tags_changed)
        
        # Set field name for randomization
        self.tag_input._field_name = self.field_name
        
        # Create snippet button with icon only
        self.snippet_button = QPushButton()
        if FONTAWESOME_AVAILABLE:
            self.snippet_button.setIcon(qta.icon('fa5s.list', color='white'))
        self.snippet_button.setFixedSize(35, 35)  # Same size as other action buttons
        self.snippet_button.setToolTip("Snippets - Browse and select predefined content")
        self.snippet_button.clicked.connect(self._show_snippets)
        
        input_layout.addWidget(self.tag_input, 1)  # Give most space to tag input
        input_layout.addWidget(self.snippet_button)
        
        self.layout.addLayout(input_layout)
    
    def _get_field_name_from_label(self, label: str) -> str:
        """Convert label to field name for snippet lookup."""
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
    
    def _show_snippets(self):
        """Show the snippet popup with category/subcategory buttons."""
        # Get selected families from main window
        selected_families = ["PG"]  # Default fallback
        
        # Try to find the main window to get selected families
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, '_get_selected_families'):
            selected_families = main_window._get_selected_families()
        
        # Create and show snippet popup
        popup = SnippetPopup(self, self.field_name, selected_families, self._on_snippet_selected)
        
        # Track the popup in the main window
        if main_window and hasattr(main_window, 'open_snippet_popups'):
            main_window.open_snippet_popups.append(popup)
            # Connect popup close signal to remove from tracking
            popup.finished.connect(lambda: main_window.open_snippet_popups.remove(popup) if popup in main_window.open_snippet_popups else None)
        
        popup.show()
    
    def _find_main_window(self):
        """Find the main window by traversing up the widget hierarchy."""
        current = self
        while current:
            if hasattr(current, '_get_selected_families'):
                return current
            current = current.parent()
        return None
    
    def _on_snippet_selected(self, snippet_text: str, category_path: List[str] = None):
        """Handle snippet selection from popup - toggle if exists."""
        if category_path:
            # This is a category or subcategory selection
            if len(category_path) == 1:
                # Category selection
                tag_type = TagType.CATEGORY
                tag_text = category_path[0]
            else:
                # Subcategory selection
                tag_type = TagType.SUBCATEGORY
                tag_text = category_path[-1]  # Use the subcategory name
            
            new_tag = Tag(tag_text, tag_type, category_path)
        else:
            # Check if this is an LLM instruction with key-value format
            if isinstance(snippet_text, dict):
                # New key-value format
                display_name = snippet_text.get("name", "Unknown")
                content = snippet_text.get("content", "")
                # Store the full instruction content for LLM use
                new_tag = Tag(display_name, TagType.SNIPPET, data=content)
            elif "|" in snippet_text:
                # Legacy name|content format (for backward compatibility)
                parts = snippet_text.split("|", 1)
                display_name = parts[0]
                # Store the full instruction (name|content) for LLM use
                new_tag = Tag(display_name, TagType.SNIPPET, data=snippet_text)
            else:
                # Regular snippet selection
                new_tag = Tag(snippet_text, TagType.SNIPPET)
        
        # Check if tag already exists
        existing_tags = self.tag_input.get_tags()
        for existing_tag in existing_tags:
            if (existing_tag.text == new_tag.text and 
                existing_tag.tag_type == new_tag.tag_type and
                existing_tag.category_path == new_tag.category_path):
                # Tag exists - remove it (toggle off)
                self.tag_input.remove_tag(existing_tag)
                return
        
        # Tag doesn't exist - add it
        self.tag_input.add_tag(new_tag)
    
    def _on_tags_changed(self):
        """Handle tag container changes."""
        self.value_changed.emit()
    
    def get_value(self) -> str:
        """Get the current field value for display."""
        return self.tag_input.get_display_text()
    
    def get_llm_instruction_content(self) -> str:
        """Get the full LLM instruction content from tags."""
        tags = self.tag_input.get_tags()
        for tag in tags:
            if tag.data:
                # Check if it's the new format (content stored directly)
                if not "|" in tag.data:
                    # New format: content is stored directly in tag.data
                    return tag.data
                else:
                    # Legacy format: content part of name|content format
                    return tag.data.split("|", 1)[1]
            elif tag.text and not tag.data:
                # Fallback to tag text for simple tags
                return tag.text
        return ""
    
    def get_randomized_value(self, seed: int) -> str:
        """Get the randomized value based on current seed."""
        # Get selected families from main window
        selected_families = ["PG"]  # Default fallback
        
        # Try to find the main window to get selected families
        main_window = self._find_main_window()
        if main_window and hasattr(main_window, '_get_selected_families'):
            selected_families = main_window._get_selected_families()
        
        return self.tag_input.generate_random_text(seed, snippet_manager, selected_families)
    
    def get_display_value(self) -> str:
        """Get the current display value (non-randomized)."""
        return self.tag_input.get_display_text()
    
    def set_value(self, value: str):
        """Set the field value (for backwards compatibility with plain text)."""
        # For now, just clear tags and add as user text if not empty
        self.tag_input.clear_tags()
        if value.strip():
            # Split by common separators and create tags
            parts = [part.strip() for part in value.replace(',', '|').replace('.', '|').split('|')]
            for part in parts:
                if part:
                    tag = Tag(part, TagType.USER_TEXT)
                    self.tag_input.add_tag(tag)
    
    def clear(self):
        """Clear the field value."""
        self.tag_input.clear_tags()
    
    def get_tags(self) -> List[Tag]:
        """Get all current tags."""
        return self.tag_input.get_tags()
    
    def set_tags(self, tags: List[Tag]):
        """Set tags (for template loading)."""
        self.tag_input.set_tags(tags)
    
    def realize_category_tags(self, seed: int, selected_families: List[str]):
        """Realize category and subcategory tags to actual snippet items."""
        current_tags = self.tag_input.get_tags()
        new_tags = []
        
        for tag in current_tags:
            if tag.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY]:
                # Generate a random snippet item for this category/subcategory
                realized_item = self._generate_realized_item(tag, seed, selected_families)
                if realized_item:
                    # Replace category/subcategory tag with realized snippet
                    new_tags.append(Tag(realized_item, TagType.SNIPPET))
                # Don't add the original category/subcategory tag (it's replaced)
            else:
                # Keep non-category/subcategory tags as they are
                new_tags.append(tag)
        
        # Update the tag input with realized tags
        self.tag_input.set_tags(new_tags)
    
    def _generate_realized_item(self, category_tag: Tag, seed: int, selected_families: List[str]) -> str:
        """Generate a realized snippet item for a category or subcategory tag."""
        import random
        
        # Create a deterministic seed based on field name and tag text
        # This ensures the same tag in the same field always gets the same result
        field_hash = hash(self.field_name)
        tag_hash = hash(category_tag.text)
        deterministic_seed = seed + field_hash + tag_hash
        random.seed(deterministic_seed)
        
        try:
            if category_tag.tag_type == TagType.CATEGORY:
                # Use the SAME logic as preview system: tag.category_path[0]
                if len(category_tag.category_path) >= 1:
                    category_items = []
                    families = selected_families or ["PG"]
                    for family in families:
                        items = snippet_manager.get_category_items(self.field_name, category_tag.category_path[0], family)
                        category_items.extend(items)
                    
                    if category_items:
                        return random.choice(category_items)
                else:
                    return category_tag.text  # Fallback to original text
            
            elif category_tag.tag_type == TagType.SUBCATEGORY:
                # Use the SAME logic as preview system: tag.category_path[0] and tag.category_path[1]
                if len(category_tag.category_path) >= 2:
                    subcategory_items = []
                    families = selected_families or ["PG"]
                    for family in families:
                        items = snippet_manager.get_subcategory_items(
                            self.field_name, 
                            category_tag.category_path[0],  # Use category_path[0] like preview
                            category_tag.category_path[1],  # Use category_path[1] like preview
                            family
                        )
                        subcategory_items.extend(items)
                    
                    if subcategory_items:
                        return random.choice(subcategory_items)
                else:
                    return category_tag.text  # Fallback to original text
            
            else:
                return category_tag.text  # Not a category/subcategory tag
                
        except Exception as e:
            print(f"Error realizing category tag '{category_tag.text}': {e}")
            return category_tag.text  # Fallback to original text


class TagTextFieldWidget(TagFieldWidget):
    """Single-line tag field widget (replaces TextFieldWidget)."""
    pass


class TagTextAreaWidget(TagFieldWidget):
    """Multi-line tag field widget (replaces TextAreaWidget)."""
    
    def __init__(self, label: str, placeholder: str = "", change_callback: Optional[Callable] = None):
        super().__init__(label, placeholder, change_callback)
        
        # After parent initialization, set minimum height for text area appearance
        if hasattr(self, 'tag_input'):
            self.tag_input.setMinimumHeight(50)  # Reduced from 60 to be more compact


class SeedFieldWidget(QWidget):
    """Widget for the seed input field."""
    
    # Signal emitted when seed changes
    value_changed = Signal()
    
    def __init__(self, change_callback: Optional[Callable] = None):
        super().__init__()
        
        self.change_callback = change_callback
        self.current_seed = 0
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 2, 0, 2)
        self.layout.setSpacing(10)
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.value_changed.connect(self.change_callback)
    
    def _create_widgets(self):
        """Create the seed field widgets."""
        # Create label
        self.label = QLabel("Seed:")
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        
        # Create seed input
        self.seed_input = QSpinBox()
        self.seed_input.setMinimum(0)
        self.seed_input.setMaximum(999999)
        self.seed_input.setValue(0)
        self.seed_input.setFixedWidth(100)
        self.seed_input.valueChanged.connect(self._on_seed_changed)
        
        # Create randomize button
        self.randomize_button = QPushButton("🎲")
        self.randomize_button.setObjectName("diceButton")  # Give it a unique name
        self.randomize_button.setFixedSize(30, 30)  # 25% smaller (from 35x35)
        self.randomize_button.clicked.connect(self._randomize_seed)
        self.randomize_button.setToolTip("Roll the dice - Generate random seed")
        
        # Create realize button with custom icon
        self.realize_button = QPushButton()
        self.realize_button.setObjectName("realizeButton")
        self.realize_button.setFixedSize(30, 30)
        self.realize_button.clicked.connect(self._realize_fields)
        self.realize_button.setToolTip("Realize fields - Convert category/subcategory tags to actual items")
        
        # Set custom icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "imagenRealizeRndClean_01.svg"
        if icon_path.exists():
            self.realize_button.setIcon(QIcon(str(icon_path)))
            self.realize_button.setIconSize(QSize(16, 16))
        else:
            # Fallback to text icon if custom icon not found
            self.realize_button.setText("❗")
        
        # Apply styling with theme colors
        self._apply_button_styling()
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.seed_input)
        self.layout.addWidget(self.randomize_button)
        self.layout.addWidget(self.realize_button)
        self.layout.addStretch()  # Push everything to the left
    
    def _on_seed_changed(self, value: int):
        """Handle seed value changes."""
        self.current_seed = value
        self.value_changed.emit()
    
    def _apply_button_styling(self):
        """Apply theme-aware styling to the dice and realize buttons."""
        from ..utils.theme_manager import theme_manager
        colors = theme_manager.get_theme_colors()
        
        # Use UI background colors instead of button colors
        ui_bg = colors.get("bg", "#f0f0f0")
        ui_text_bg = colors.get("text_bg", "#ffffff")
        
        # Create slightly lighter/darker versions for button states
        current_theme = theme_manager.get_current_theme()
        if current_theme == "dark":
            # Dark theme: use slightly lighter background
            button_bg = "#404040"  # Lighter than #2b2b2b
            button_hover_bg = "#505050"  # Even lighter
            button_pressed_bg = "#606060"  # Lightest
            button_text = "#ffffff"
        else:
            # Light theme: use slightly darker background
            button_bg = "#e0e0e0"  # Darker than #f0f0f0
            button_hover_bg = "#d0d0d0"  # Even darker
            button_pressed_bg = "#c0c0c0"  # Darkest
            button_text = "#333333"
        
        # Use subtle borders that match the theme
        button_border = colors.get("tag_border", "#ccc")
        button_hover_border = colors.get("snippet_border", "#999")
        button_pressed_border = colors.get("category_border", "#666")
        
        button_style = f"""
            QPushButton#diceButton {{
                background-color: {button_bg} !important;
                border: 2px solid {button_border} !important;
                border-radius: 6px !important;
                font-size: 18px !important;
                color: {button_text} !important;
                padding: 2px !important;
                min-height: 26px !important;
                max-height: 26px !important;
                min-width: 26px !important;
                max-width: 26px !important;
                font-weight: normal !important;
            }}
            QPushButton#diceButton:hover {{
                background-color: {button_hover_bg} !important;
                border: 2px solid {button_hover_border} !important;
                color: {button_text} !important;
            }}
            QPushButton#diceButton:pressed {{
                background-color: {button_pressed_bg} !important;
                border: 2px solid {button_pressed_border} !important;
                color: {button_text} !important;
            }}
            QPushButton#realizeButton {{
                background-color: {button_bg} !important;
                border: 2px solid {button_border} !important;
                border-radius: 6px !important;
                font-size: 16px !important;
                color: {button_text} !important;
                padding: 2px !important;
                min-height: 26px !important;
                max-height: 26px !important;
                min-width: 26px !important;
                max-width: 26px !important;
                font-weight: normal !important;
            }}
            QPushButton#realizeButton:hover {{
                background-color: {button_hover_bg} !important;
                border: 2px solid {button_hover_border} !important;
                color: {button_text} !important;
            }}
            QPushButton#realizeButton:pressed {{
                background-color: {button_pressed_bg} !important;
                border: 2px solid {button_pressed_border} !important;
                color: {button_text} !important;
            }}
        """
        self.randomize_button.setStyleSheet(button_style)
        self.realize_button.setStyleSheet(button_style)
        
        # Force the buttons to use the new style immediately
        self.randomize_button.setAutoFillBackground(True)
        self.realize_button.setAutoFillBackground(True)
        palette = self.randomize_button.palette()
        palette.setColor(palette.ColorRole.Button, QColor(button_bg))
        palette.setColor(palette.ColorRole.ButtonText, QColor(button_text))
        self.randomize_button.setPalette(palette)
        self.realize_button.setPalette(palette)
    
    def refresh_theme(self):
        """Refresh the theme styling for the buttons."""
        self._apply_button_styling()
    
    def _randomize_seed(self):
        """Generate a random seed."""
        import random
        new_seed = random.randint(0, 999999)
        self.seed_input.setValue(new_seed)
    
    def _realize_fields(self):
        """Realize category/subcategory tags to actual snippet items."""
        # Find the main window to access all field widgets
        main_window = self._find_main_window()
        if not main_window:
            return
        
        # Get current seed for consistent realization
        current_seed = self.get_value()
        
        # Get selected families for snippet filtering
        selected_families = main_window._get_selected_families() if hasattr(main_window, '_get_selected_families') else ["PG"]
        
        # Realize all field widgets
        field_widgets = [
            getattr(main_window, attr, None) for attr in [
                'style_widget', 'setting_widget', 'weather_widget', 'datetime_widget',
                'subjects_widget', 'pose_widget', 'camera_widget', 'framing_widget',
                'grading_widget', 'details_widget'
            ]
        ]
        
        for field_widget in field_widgets:
            if field_widget and hasattr(field_widget, 'realize_category_tags'):
                field_widget.realize_category_tags(current_seed, selected_families)
        
        # Emit change signal to update preview
        self.value_changed.emit()
    
    def _find_main_window(self):
        """Find the main window by traversing up the widget hierarchy."""
        current = self
        while current:
            if hasattr(current, '_get_selected_families'):
                return current
            current = current.parent()
        return None
    
    def get_value(self) -> int:
        """Get the current seed value."""
        return self.current_seed
    
    def set_value(self, value: int):
        """Set the seed value."""
        self.seed_input.setValue(value)
