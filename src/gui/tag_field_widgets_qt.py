"""
Tag-enabled field widgets for the FlipFlopPrompt application using PySide6.
These replace the traditional text input widgets with tag-based input systems.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Callable, Optional, List
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
        self.layout.setContentsMargins(0, 2, 0, 2)
        self.layout.setSpacing(2)
        
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
        input_layout.setSpacing(5)
        
        # Create inline tag input
        self.tag_input = InlineTagInputWidget(self.placeholder)
        self.tag_input.tags_changed.connect(self._on_tags_changed)
        self.tag_input.value_changed.connect(self._on_tags_changed)
        
        # Set field name for randomization
        self.tag_input._field_name = self.field_name
        
        # Create snippet button
        self.snippet_button = QPushButton("Snippets")
        self.snippet_button.setMinimumWidth(90)
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
        selected_families = ["PG"]  # Default, will be updated by main window
        if hasattr(self.parent(), '_get_selected_families'):
            selected_families = self.parent()._get_selected_families()
        
        # Create and show snippet popup
        popup = SnippetPopup(self, self.field_name, selected_families, self._on_snippet_selected)
        popup.show()
    
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
    
    def get_randomized_value(self, seed: int) -> str:
        """Get the randomized value based on current seed."""
        # Get selected families from main window
        selected_families = ["PG"]  # Default fallback
        if hasattr(self.parent(), '_get_selected_families'):
            selected_families = self.parent()._get_selected_families()
        
        return self.tag_input.generate_random_text(seed, snippet_manager, selected_families)
    
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


class TagTextFieldWidget(TagFieldWidget):
    """Single-line tag field widget (replaces TextFieldWidget)."""
    pass


class TagTextAreaWidget(TagFieldWidget):
    """Multi-line tag field widget (replaces TextAreaWidget)."""
    
    def _create_widgets(self):
        """Create the text area widgets with tag support."""
        # Create label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.layout.addWidget(self.label)
        
        # Create horizontal layout for tag container and snippet button
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)
        
        # Create inline tag input with larger minimum height for text area
        self.tag_input = InlineTagInputWidget(self.placeholder)
        self.tag_input.tags_changed.connect(self._on_tags_changed)
        self.tag_input.value_changed.connect(self._on_tags_changed)
        
        # Set field name for randomization
        self.tag_input._field_name = self.field_name
        
        # Set minimum height for multi-line appearance
        self.tag_input.setMinimumHeight(80)
        
        # Create snippet button
        self.snippet_button = QPushButton("Snippets")
        self.snippet_button.setMinimumWidth(90)
        self.snippet_button.clicked.connect(self._show_snippets)
        
        input_layout.addWidget(self.tag_input, 1)
        input_layout.addWidget(self.snippet_button)
        
        self.layout.addLayout(input_layout)


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
        self.randomize_button.setFixedSize(30, 30)
        self.randomize_button.clicked.connect(self._randomize_seed)
        self.randomize_button.setToolTip("Roll the dice - Generate random seed")
        
        # Apply styling with important flags to override defaults
        button_style = """
            QPushButton {
                background-color: #f0f0f0 !important;
                border: 1px solid #ccc !important;
                border-radius: 4px !important;
                font-size: 16px !important;
                color: #333 !important;
            }
            QPushButton:hover {
                background-color: #e0e0e0 !important;
                border: 2px solid #0066cc !important;
            }
            QPushButton:pressed {
                background-color: #d0d0d0 !important;
            }
        """
        self.randomize_button.setStyleSheet(button_style)
        
        # Force style refresh
        self.randomize_button.style().unpolish(self.randomize_button)
        self.randomize_button.style().polish(self.randomize_button)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.seed_input)
        self.layout.addWidget(self.randomize_button)
        self.layout.addStretch()  # Push everything to the left
    
    def _on_seed_changed(self, value: int):
        """Handle seed value changes."""
        self.current_seed = value
        self.value_changed.emit()
    
    def _randomize_seed(self):
        """Generate a random seed."""
        import random
        new_seed = random.randint(0, 999999)
        self.seed_input.setValue(new_seed)
    
    def get_value(self) -> int:
        """Get the current seed value."""
        return self.current_seed
    
    def set_value(self, value: int):
        """Set the seed value."""
        self.seed_input.setValue(value)
