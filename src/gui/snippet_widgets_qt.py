"""
Snippet widgets for the GUI using PySide6.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QRadioButton, QButtonGroup, QFrame, QDialog, QPushButton,
    QScrollArea, QLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtGui import QFont
from typing import Callable, Optional, List, Dict
from ..utils.snippet_manager import snippet_manager
from ..utils.theme_manager import theme_manager
from ..utils.logger import get_logger


class FlowLayout(QLayout):
    """A layout that arranges widgets in rows, wrapping when necessary."""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing)
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
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
    
    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            space_y = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QRect(x, y, item.sizeHint().width(), item.sizeHint().height())))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class ContentRatingWidget(QWidget):
    """Widget for selecting content rating."""
    
    # Signal emitted when content rating changes
    rating_changed = Signal(str)
    
    def __init__(self, change_callback: Optional[Callable] = None):
        super().__init__()
        
        self.change_callback = change_callback
        self.current_rating = "PG"
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.rating_changed.connect(self.change_callback)
    
    def _create_widgets(self):
        """Create the content rating widgets."""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(5)
        
        # Create label
        label = QLabel("Content Rating:")
        label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        layout.addWidget(label)
        
        # Create radio button layout
        radio_layout = QHBoxLayout()
        radio_layout.setContentsMargins(10, 0, 0, 0)
        radio_layout.setSpacing(20)
        
        # Create button group for exclusive selection
        self.button_group = QButtonGroup(self)
        
        # Create radio buttons
        self.pg_radio = QRadioButton("PG")
        self.pg_radio.setChecked(True)  # Default selection
        self.pg_radio.toggled.connect(lambda checked: self._on_rating_changed("PG") if checked else None)
        
        self.nsfw_radio = QRadioButton("NSFW")
        self.nsfw_radio.toggled.connect(lambda checked: self._on_rating_changed("NSFW") if checked else None)
        
        # Add radio buttons to group and layout
        self.button_group.addButton(self.pg_radio)
        self.button_group.addButton(self.nsfw_radio)
        
        radio_layout.addWidget(self.pg_radio)
        radio_layout.addWidget(self.nsfw_radio)
        radio_layout.addStretch()
        
        # Add radio layout to main layout
        layout.addLayout(radio_layout)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the radio buttons."""
        colors = theme_manager.get_theme_colors()
        radio_style = f"""
            QRadioButton {
                font-size: 11px;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QRadioButton::indicator:checked {
                background-color: {colors.get('button_bg', '#0066cc')};
                border: 2px solid {colors.get('button_bg', '#0066cc')};
                border-radius: 7px;
            }
            QRadioButton::indicator:unchecked {
                background-color: {colors.get('text_bg', '#ffffff')};
                border: 2px solid {colors.get('tag_border', '#ccc')};
                border-radius: 7px;
            }
        """
        
        self.pg_radio.setStyleSheet(radio_style)
        self.nsfw_radio.setStyleSheet(radio_style)
    
    def _on_rating_changed(self, rating: str):
        """Handle rating changes."""
        self.current_rating = rating
        self.rating_changed.emit(rating)
    
    def get_value(self) -> str:
        """Get the current content rating."""
        return self.current_rating
    
    def set_value(self, rating: str):
        """Set the content rating."""
        self.current_rating = rating
        if rating == "PG":
            self.pg_radio.setChecked(True)
        elif rating == "NSFW":
            self.nsfw_radio.setChecked(True)


class SnippetDropdown(QWidget):
    """Hierarchical dropdown for prompt snippets."""
    
    # Signal emitted when a snippet is selected
    snippet_selected = Signal(str)
    
    def __init__(self, field_name: str, on_select: Optional[Callable] = None, content_rating: str = "PG"):
        super().__init__()
        
        self.field_name = field_name
        self.on_select = on_select
        self.content_rating = content_rating
        
        # Get snippets from snippet manager
        self.snippets = snippet_manager.get_snippets_for_field(field_name, content_rating)
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.on_select:
            self.snippet_selected.connect(self.on_select)
    
    def _create_widgets(self):
        """Create the dropdown widget."""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Create combobox
        self.combo_box = QComboBox()
        self.combo_box.addItem("Select snippet...")
        
        # Populate with snippets
        self._populate_snippets()
        
        # Connect selection change
        self.combo_box.currentTextChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.combo_box)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the combobox."""
        colors = theme_manager.get_theme_colors()
        self.combo_box.setStyleSheet(f"""
            QComboBox {{
                padding: 4px 8px;
                border: 1px solid {colors.get('tag_border', '#ccc')};
                border-radius: 3px;
                font-size: 10px;
                min-height: 20px;
                background-color: {colors.get('text_bg', '#ffffff')};
                color: {colors.get('text_fg', '#000000')};
            }}
            QComboBox:focus {{
                border-color: {colors.get('focus_color', '#0066cc')};
            }}
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                selection-background-color: #0066cc;
                outline: none;
            }
        """)
    
    def _populate_snippets(self):
        """Populate the dropdown with snippets."""
        if not self.snippets:
            return
        
        # Clear existing items (except the first placeholder)
        while self.combo_box.count() > 1:
            self.combo_box.removeItem(1)
        
        # Add snippets by category
        for category, items in self.snippets.items():
            if items:
                # Add category separator
                self.combo_box.addItem(f"--- {category.title()} ---")
                
                # Add items in category
                for item in items:
                    display_name = self._format_snippet_name(item)
                    self.combo_box.addItem(display_name)
    
    def _format_snippet_name(self, snippet_name: str) -> str:
        """Format snippet name for display."""
        # Remove underscores and capitalize
        formatted = snippet_name.replace("_", " ").title()
        
        # Handle special cases
        formatted = formatted.replace("Dslr", "DSLR")
        formatted = formatted.replace("Rgb", "RGB")
        formatted = formatted.replace("Hdr", "HDR")
        
        return formatted
    
    def _on_selection_changed(self, text: str):
        """Handle selection changes."""
        # Skip placeholder and category headers
        if text == "Select snippet..." or text.startswith("---"):
            return
        
        # Convert back to original snippet format
        snippet_value = text.lower().replace(" ", "_")
        
        # Emit signal
        self.snippet_selected.emit(snippet_value)
        
        # Reset to placeholder
        self.combo_box.setCurrentIndex(0)
    
    def update_content_rating(self, new_rating: str):
        """Update the content rating and refresh snippets."""
        self.content_rating = new_rating
        self.snippets = snippet_manager.get_snippets_for_field(self.field_name, new_rating)
        self._populate_snippets()
    
    def get_field_name(self) -> str:
        """Get the field name."""
        return self.field_name


class ModelSelectionWidget(QWidget):
    """Widget for selecting target model."""
    
    # Signal emitted when model changes
    model_changed = Signal(str)
    
    def __init__(self, change_callback: Optional[Callable] = None):
        super().__init__()
        
        self.change_callback = change_callback
        self.current_model = theme_manager.get_preference("target_model", "seedream")
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.model_changed.connect(self.change_callback)
    
    def _create_widgets(self):
        """Create the model selection widgets."""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(5)
        
        # Create label
        label = QLabel("Target Diffusion Model:")
        label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        layout.addWidget(label)
        
        # Create combobox
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "Seedream",
            "Google Veo", 
            "Stability AI Flux",
            "Other"
        ])
        
        # Set current model from preferences
        model_map = {
            "seedream": "Seedream",
            "veo": "Google Veo",
            "flux": "Stability AI Flux",
            "other": "Other"
        }
        display_name = model_map.get(self.current_model, "Seedream")
        self.model_combo.setCurrentText(display_name)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        
        layout.addWidget(self.model_combo)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to the combobox."""
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 11px;
            }
            QComboBox:focus {
                border-color: #0066cc;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                selection-background-color: #0066cc;
            }
        """)
    
    def _on_model_changed(self, model_name: str):
        """Handle model changes."""
        # Convert to internal format
        model_map = {
            "Seedream": "seedream",
            "Google Veo": "veo",
            "Stability AI Flux": "flux",
            "Other": "other"
        }
        
        self.current_model = model_map.get(model_name, "seedream")
        # Save preference
        theme_manager.set_preference("target_model", self.current_model)
        self.model_changed.emit(self.current_model)
    
    def get_value(self) -> str:
        """Get the current model."""
        return self.current_model
    
    def set_value(self, model: str):
        """Set the model."""
        # Convert from internal format
        model_map = {
            "seedream": "Seedream",
            "veo": "Google Veo",
            "flux": "Stability AI Flux",
            "other": "Other"
        }
        
        display_name = model_map.get(model, "Seedream")
        self.model_combo.setCurrentText(display_name)
        self.current_model = model


class LLMSelectionWidget(QWidget):
    """Widget for selecting LLM model with dynamic Ollama integration."""
    
    # Signal emitted when LLM changes
    llm_changed = Signal(str)
    
    def __init__(self, change_callback: Optional[Callable] = None):
        super().__init__()
        
        self.change_callback = change_callback
        self.current_llm = theme_manager.get_preference("llm_model", "gemma3:4b")
        self.ollama_available = False
        self.available_models = []
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.llm_changed.connect(self.change_callback)
        
        # Defer Ollama connection check to avoid blocking startup
        from PySide6.QtCore import QTimer
        QTimer.singleShot(200, self._check_ollama_connection)
    
    def _create_widgets(self):
        """Create the LLM selection widgets."""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(5)
        
        # Create label
        self.label = QLabel("LLM Model:")
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        layout.addWidget(self.label)
        
        # Create combobox with default models (will be updated after connection check)
        self.llm_combo = QComboBox()
        self.llm_combo.addItems(["gemma3:4b", "huihui_ai/dolphin3-abliterated:8b", "deepseek-r1:8b", "qwen3:8b"])
        self.llm_combo.setCurrentText(self.current_llm)
        self.llm_combo.currentTextChanged.connect(self._on_llm_changed)
        layout.addWidget(self.llm_combo)
        
        # Create error label (hidden initially)
        self.error_label = QLabel("Ollama connection failed")
        self.error_label.setStyleSheet("color: red; font-size: 11px; padding: 6px;")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Apply styling
        self._apply_styling()
    
    def _check_ollama_connection(self):
        """Check Ollama connection and populate models."""
        try:
            # Import here to avoid circular imports
            from ..core.llm_integration import LLMManager
            
            llm_manager = LLMManager()
            self.ollama_available = llm_manager.is_available()
            
            if self.ollama_available:
                # Get available models
                self.available_models = llm_manager.get_available_models()
                
                if self.available_models:
                    # Show combobox and populate with actual models
                    self.llm_combo.clear()
                    self.llm_combo.addItems(self.available_models)
                    
                    # Set current model if it exists
                    if self.current_llm in self.available_models:
                        self.llm_combo.setCurrentText(self.current_llm)
                    else:
                        self.current_llm = self.available_models[0]
                        self.llm_combo.setCurrentIndex(0)
                    
                    self.llm_combo.show()
                    self.error_label.hide()
                else:
                    self._show_error("No models found in Ollama")
            else:
                self._show_error("Cannot connect to Ollama")
                
        except Exception as e:
            self._show_error(f"Ollama error: {str(e)}")
    
    def _show_error(self, message: str):
        """Show error message instead of combobox."""
        self.ollama_available = False
        self.llm_combo.hide()
        self.error_label.setText(message)
        self.error_label.show()
    
    def _apply_styling(self):
        """Apply styling to the combobox."""
        self.llm_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 11px;
            }
            QComboBox:focus {
                border-color: #0066cc;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                selection-background-color: #0066cc;
            }
        """)
    
    def _on_llm_changed(self, llm_name: str):
        """Handle LLM changes."""
        if self.ollama_available:
            self.current_llm = llm_name
            # Save preference
            theme_manager.set_preference("llm_model", llm_name)
            self.llm_changed.emit(llm_name)
    
    def get_value(self) -> str:
        """Get the current LLM."""
        return self.current_llm
    
    def set_value(self, llm: str):
        """Set the LLM."""
        if self.ollama_available and llm in self.available_models:
            self.llm_combo.setCurrentText(llm)
            self.current_llm = llm
    
    def refresh_connection(self):
        """Refresh Ollama connection and models."""
        self._check_ollama_connection()


class SnippetPopup(QDialog):
    """Popup dialog for snippet selection."""
    
    def __init__(self, parent, field_name: str, selected_filters: List[str], on_select: Callable):
        super().__init__(parent)
        
        # Enable tooltips on this dialog
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        
        self.field_name = field_name
        self.selected_filters = selected_filters
        self.on_select = on_select
        
        # Get logger for debugging
        self.logger = get_logger()
        
        # Get snippets for each selected filter_name separately
        self.snippets = {}
        self.filter_name_snippets = {}  # Track which filter_name each category belongs to
        
        # Process filters in the order they were selected
        sorted_filters = selected_filters.copy() if selected_filters else []
        
        for filter_name in sorted_filters:
            filter_name_snippets = snippet_manager.get_snippets_for_field(field_name, filter_name)
            if filter_name_snippets:
                # Store snippets with filter_name info
                for category, items in filter_name_snippets.items():
                    if category not in self.snippets:
                        # First time seeing this category - assign it to this filter_name
                        self.snippets[category] = items
                        self.filter_name_snippets[category] = filter_name
                    else:
                        # Category already exists - merge items but keep the original filter_name assignment
                        # (This preserves the priority order - PG takes precedence over NSFW/Hentai)
                        if isinstance(items, list):
                            if isinstance(self.snippets[category], list):
                                self.snippets[category].extend(items)
                            else:
                                self.snippets[category] = items
                        elif isinstance(items, dict):
                            if isinstance(self.snippets[category], dict):
                                for subcat, subitems in items.items():
                                    if subcat not in self.snippets[category]:
                                        self.snippets[category][subcat] = subitems
                                    else:
                                        self.snippets[category][subcat].extend(subitems)
                            else:
                                self.snippets[category] = items
        
        # Initialize widget tracking lists for theme updates
        self.category_frames = []
        self.category_labels = []
        self.snippet_buttons = []
        self.sub_labels = []
        self.category_buttons = []
        self.subcategory_buttons = []
        
        self._setup_dialog()
        self._create_widgets()
    
    def _setup_dialog(self):
        """Setup dialog properties."""
        self.setWindowTitle(f"Snippets for {self.field_name.title()}")
        self.setModal(False)  # Allow interaction with main window
        self.resize(600, 650)
        
        # Position to the right of the parent snippet button
        if self.parent():
            # Find the snippet button in the parent widget
            snippet_button = None
            for child in self.parent().findChildren(QPushButton):
                # Look for snippet button by tooltip or by being the last button in the layout
                if (child.toolTip() and "Snippets" in child.toolTip()) or child.text() == "Snippets":
                    snippet_button = child
                    break
            
            if snippet_button:
                # Position to the right of the snippet button
                button_pos = snippet_button.mapToGlobal(snippet_button.rect().topRight())
                self.move(button_pos.x() + 10, button_pos.y())
            else:
                # Fallback to parent center
                parent_pos = self.parent().mapToGlobal(self.parent().rect().center())
                self.move(parent_pos.x() - 200, parent_pos.y() - 300)
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title removed - window title already provides this information
        
        # Scroll area for snippets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        
        # Scroll content widget with flow layout
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(10)
        
        # Build snippet buttons
        self._build_snippet_buttons(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        # Apply styling
        self._apply_styling()
    
    def refresh_theme(self):
        """Refresh the styling when theme changes."""
        try:
            # Import theme manager here to ensure it's available
            from ..utils.theme_manager import theme_manager
            colors = theme_manager.get_theme_colors()
        except Exception as e:
            print(f"Error getting theme colors: {e}")
            return
        
        # Force repaint of all buttons to ensure colors are applied
        for btn in self.snippet_buttons:
            btn.update()
            btn.repaint()
        
        # Update category frames
        for frame in self.category_frames:
            frame.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 5px;
                    background-color: {colors['text_bg']};
                    margin: 2px;
                }}
            """)
        
        # Update category labels (now buttons) - use category colors
        for button in self.category_labels:
            button.setStyleSheet(f"""
                QPushButton {{
                    color: {colors['category_fg']}; 
                    margin-bottom: 5px; 
                    border: 1px solid {colors['category_border']};
                    border-radius: 5px;
                    background-color: {colors['category_bg']};
                    padding: 6px;
                    text-align: center;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['button_bg']};
                    border: 2px solid {colors['button_bg']};
                    color: {colors['button_fg']};
                }}
            """)
        
        # Update snippet buttons - use correct colors based on button type
        for btn in self.snippet_buttons:
            if hasattr(btn, 'button_type'):
                if btn.button_type == 'category':
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {colors['category_bg']};
                            border: 1px solid {colors['category_border']};
                            border-radius: 3px;
                            padding: 6px 12px;
                            text-align: left;
                            margin: 1px 0px;
                            margin-left: 10px;
                            font-size: 12px;
                            color: {colors['category_fg']};
                        }}
                        QPushButton:hover {{
                            background-color: {colors['button_bg']};
                            border: 2px solid {colors['button_bg']};
                            color: {colors['button_fg']};
                        }}
                    """)
                elif btn.button_type == 'subcategory':
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {colors['subcategory_bg']};
                            border: 1px solid {colors['subcategory_border']};
                            border-radius: 3px;
                            padding: 6px 12px;
                            text-align: left;
                            margin: 1px 0px;
                            margin-left: 10px;
                            font-size: 12px;
                            color: {colors['subcategory_fg']};
                        }}
                        QPushButton:hover {{
                            background-color: {colors['button_bg']};
                            border: 2px solid {colors['button_bg']};
                            color: {colors['button_fg']};
                        }}
                    """)
                else:  # snippet
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {colors['snippet_bg']};
                            border: 1px solid {colors['snippet_border']};
                            border-radius: 3px;
                            padding: 6px 12px;
                            text-align: left;
                            margin: 1px 0px;
                            margin-left: 10px;
                            font-size: 12px;
                            color: {colors['snippet_fg']};
                        }}
                        QPushButton:hover {{
                            background-color: {colors['button_bg']};
                            border: 2px solid {colors['button_bg']};
                            color: {colors['button_fg']};
                        }}
                    """)
            else:
                # Fallback for any buttons without type - use snippet colors
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['snippet_bg']};
                        border: 1px solid {colors['snippet_border']};
                        border-radius: 3px;
                        padding: 4px 8px;
                        text-align: left;
                        margin: 1px 0px;
                        color: {colors['snippet_fg']};
                    }}
                    QPushButton:hover {{
                        background-color: {colors['button_bg']};
                        border: 2px solid {colors['button_bg']};
                        color: {colors['button_fg']};
                    }}
                """)
        
        # Update sub labels (now buttons) - use subcategory colors
        for button in self.sub_labels:
            button.setStyleSheet(f"""
                QPushButton {{
                    color: {colors['subcategory_fg']}; 
                    margin-top: 8px; 
                    margin-bottom: 3px; 
                    border: 1px solid {colors['subcategory_border']};
                    border-radius: 4px;
                    background-color: {colors['subcategory_bg']};
                    padding: 4px;
                    text-align: left;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['button_bg']};
                    border: 2px solid {colors['button_bg']};
                    color: {colors['button_fg']};
                }}
            """)
    
    def _build_snippet_buttons(self, layout):
        """Build snippet selection buttons with category blocks."""
        # Log the popup population
        if self.logger:
            self.logger.log_gui_action("Snippet popup opened", f"Field: {self.field_name}, Filters: {self.selected_filters}")
        
        if not self.snippets:
            if self.logger:
                self.logger.log_warning(f"No snippets found for field {self.field_name}")
            no_snippets_label = QLabel("No snippets available for selected filters")
            no_snippets_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_snippets_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(no_snippets_label)
            return
        
        # Create a flow layout widget to hold category frames
        categories_widget = QWidget()
        categories_flow_layout = FlowLayout(categories_widget, margin=5, spacing=10)
        
        for category, items in self.snippets.items():
            # Create a frame for each category
            category_frame = QFrame()
            category_frame.setFrameStyle(QFrame.Shape.Box)
            # Get theme colors
            try:
                colors = theme_manager.get_theme_colors()
            except Exception as e:
                print(f"Error getting theme colors: {e}")
                print("Using fallback colors for snippet popup")
                # Use fallback colors that match the theme
                colors = {
                    "tag_border": "#cccccc",
                    "text_bg": "#ffffff",
                    "text_fg": "#000000",
                    "tag_bg": "#e3f2fd",
                    "tag_fg": "#000000",
                    "snippet_bg": "#e3f2fd",  # Blue to match theme
                    "snippet_fg": "#000000",
                    "snippet_border": "#90caf9",  # Blue border to match theme
                    "category_bg": "#fff3e0",  # Orange to match theme
                    "category_fg": "#000000",
                    "category_border": "#ffb74d",  # Orange border to match theme
                    "subcategory_bg": "#fffde7",  # Yellow to match theme
                    "subcategory_fg": "#000000",
                    "subcategory_border": "#ffd54f",  # Yellow border to match theme
                    "user_text_bg": "#f3e5f5",  # Purple to match theme
                    "user_text_fg": "#000000",
                    "user_text_border": "#ce93d8",  # Purple border to match theme
                    "button_bg": "#0066cc",
                    "button_fg": "#ffffff",
                    "bg": "#f0f0f0",
                    "entry_bg": "#ffffff",
                    "placeholder_fg": "#666666",
                    "menu_bg": "#f0f0f0",
                    "menu_fg": "#000000",
                    "menu_selection_bg": "#0066cc",
                    "menu_selection_fg": "#ffffff",
                    "status_bg": "#f0f0f0",
                    "status_fg": "#000000",
                    "scrollbar_bg": "#e0e0e0",
                    "scrollbar_handle": "#c0c0c0"
                }
            category_frame.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {colors['tag_border']};
                    border-radius: 5px;
                    background-color: {colors['text_bg']};
                    margin: 2px;
                }}
            """)
            category_frame.setMinimumWidth(200)
            category_frame.setMaximumWidth(300)
            
            # Store reference for theme updates
            self.category_frames.append(category_frame)
            
            # Layout for this category frame
            category_layout = QVBoxLayout(category_frame)
            category_layout.setContentsMargins(8, 8, 8, 8)
            category_layout.setSpacing(5)
            
            # Category title as clickable button with filter_name info
            filter_name_name = self.filter_name_snippets.get(category, "Unknown")
            category_button = QPushButton(f"{category.title()} ({filter_name_name})")
            category_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            category_button.button_type = 'category'  # Mark as category button
            category_button.setStyleSheet(f"""
                QPushButton {{
                    color: {colors['category_fg']};
                    margin-bottom: 5px;
                    border: 1px solid {colors['category_border']};
                    border-radius: 5px;
                    background-color: {colors['category_bg']};
                    padding: 6px;
                    text-align: center;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['button_bg']};
                    border: 2px solid {colors['button_bg']};
                    color: {colors['button_fg']};
                }}
            """)
            category_button.clicked.connect(lambda checked, c=category: self._select_category(c))
            category_layout.addWidget(category_button)
            
            # Store reference for theme updates
            self.category_labels.append(category_button)
            self.category_buttons.append(category_button)
            
            if isinstance(items, list):
                # Simple category with list of items
                for item in items:
                    # Handle both string format (old) and object format (new)
                    if isinstance(item, str):
                        # Traditional string format - mark as snippet button
                        btn = QPushButton(item)
                        btn.setMinimumHeight(25)
                        btn.setMaximumHeight(35)
                        btn.button_type = 'snippet'  # Mark as snippet button

                        
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {colors['snippet_bg']};
                                border: 1px solid {colors['snippet_border']};
                                border-radius: 3px;
                                padding: 4px 8px;
                                text-align: left;
                                margin: 1px 0px;
                                color: {colors['snippet_fg']};
                            }}
                            QPushButton:hover {{
                                background-color: {colors['button_bg']};
                                border: 2px solid {colors['button_bg']};
                                color: {colors['button_fg']};
                            }}
                        """)
                        btn.clicked.connect(lambda checked, i=item: self._select_item(i))
                        category_layout.addWidget(btn)
                        self.snippet_buttons.append(btn)  # Track for theme updates
                    elif isinstance(item, dict):
                        # New key-value format
                        display_name = item.get("name", "Unknown")
                        content = item.get("content", "")
                        description = item.get("description", "")
                        
                        btn = QPushButton()
                        btn.setText(display_name)
                        btn.setMinimumHeight(30)
                        btn.setMaximumHeight(40)
                        btn.setMinimumWidth(200)
                        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                        
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {colors['snippet_bg']};
                                border: 1px solid {colors['snippet_border']};
                                border-radius: 3px;
                                padding: 6px 12px;
                                text-align: left;
                                margin: 1px 0px;
                                margin-left: 10px;
                                font-size: 12px;
                                color: {colors['snippet_fg']};
                            }}
                            QPushButton:hover {{
                                background-color: {colors['button_bg']};
                                border: 2px solid {colors['button_bg']};
                                color: {colors['button_fg']};
                            }}
                        """)
                        
                        # Set tooltip with the full content
                        btn.setToolTip(content)
                        btn.setToolTipDuration(30000)
                        btn.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
                        
                        # Mark as snippet button and track for theme updates
                        btn.button_type = 'snippet'
                        
                        # Fix lambda capture issue by creating a closure
                        def create_click_handler(full_item):
                            return lambda checked: self._select_item(full_item)
                        btn.clicked.connect(create_click_handler(item))
                        category_layout.addWidget(btn)
                        self.snippet_buttons.append(btn)  # Track for theme updates
                    
            elif isinstance(items, dict):
                # Nested category structure - show subcategories properly
                for subcategory, subitems in items.items():
                    if isinstance(subitems, list):
                        # Subcategory as clickable button
                        sub_button = QPushButton(subcategory)
                        sub_button.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                        sub_button.button_type = 'subcategory'  # Mark as subcategory button
                        sub_button.setStyleSheet(f"""
                            QPushButton {{
                                color: {colors['subcategory_fg']}; 
                                margin-top: 8px; 
                                margin-bottom: 3px; 
                                border: 1px solid {colors['subcategory_border']};
                                border-radius: 4px;
                                background-color: {colors['subcategory_bg']};
                                padding: 4px;
                                text-align: left;
                                font-weight: bold;
                            }}
                            QPushButton:hover {{
                                background-color: {colors['button_bg']};
                                border: 2px solid {colors['button_bg']};
                                color: {colors['button_fg']};
                            }}
                        """)
                        sub_button.clicked.connect(lambda checked, cat=category, subcat=subcategory: self._select_subcategory(cat, subcat))
                        category_layout.addWidget(sub_button)
                        self.sub_labels.append(sub_button)
                        self.subcategory_buttons.append(sub_button)
                        
                        # Items in this subcategory
                        for item in subitems:
                            # Handle both string format (old) and object format (new)
                            if isinstance(item, str):
                                # Traditional simple string format
                                btn = QPushButton(item)
                                btn.setMinimumHeight(25)
                                btn.setMaximumHeight(35)
                                btn.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: {colors['tag_bg']};
                                        border: 1px solid {colors['tag_border']};
                                        border-radius: 3px;
                                        padding: 4px 8px;
                                        text-align: left;
                                        margin: 1px 0px;
                                        margin-left: 10px;
                                        color: {colors['tag_fg']};
                                    }}
                                    QPushButton:hover {{
                                        background-color: {colors['button_bg']};
                                        border: 2px solid {colors['button_bg']};
                                        color: {colors['button_fg']};
                                    }}
                                """)
                                btn.clicked.connect(lambda checked, i=item: self._select_item(i))
                                category_layout.addWidget(btn)
                            elif isinstance(item, dict):
                                # New key-value format
                                display_name = item.get("name", "Unknown")
                                content = item.get("content", "")
                                description = item.get("description", "")
                                
                                btn = QPushButton()
                                btn.setText(display_name)
                                btn.setMinimumHeight(30)
                                btn.setMaximumHeight(40)
                                btn.setMinimumWidth(200)
                                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                                
                                btn.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: {colors['snippet_bg']};
                                        border: 1px solid {colors['snippet_border']};
                                        border-radius: 3px;
                                        padding: 6px 12px;
                                        text-align: left;
                                        margin: 1px 0px;
                                        margin-left: 10px;
                                        font-size: 12px;
                                        color: {colors['snippet_fg']};
                                    }}
                                    QPushButton:hover {{
                                        background-color: {colors['button_bg']};
                                        border: 2px solid {colors['button_bg']};
                                        color: {colors['button_fg']};
                                    }}
                                """)
                                
                                # Set tooltip with the full content
                                btn.setToolTip(content)
                                btn.setToolTipDuration(30000)
                                btn.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
                                
                                # Fix lambda capture issue by creating a closure
                                def create_click_handler(full_item):
                                    return lambda checked: self._select_item(full_item)
                                btn.clicked.connect(create_click_handler(item))
                                category_layout.addWidget(btn)
            
            # Add stretch to push content to top
            category_layout.addStretch()
            
            # Add this category frame to the flow layout
            categories_flow_layout.addWidget(category_frame)
        
        # Add the categories widget to the main layout
        layout.addWidget(categories_widget)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def _select_item(self, item):
        """Handle item selection."""
        # Handle both string and object formats
        if isinstance(item, str):
            # Traditional string format
            item_name = item
            item_content = item
        elif isinstance(item, dict):
            # New key-value format
            item_name = item.get("name", "Unknown")
            item_content = item.get("content", "")
        else:
            # Fallback
            item_name = str(item)
            item_content = str(item)
        
        # Log the snippet selection
        if self.logger:
            # Get the filter_name for this item if possible
            filter_name = "Unknown"
            for category, items in self.snippets.items():
                if isinstance(items, list):
                    for list_item in items:
                        if (isinstance(list_item, str) and list_item == item_name) or \
                           (isinstance(list_item, dict) and list_item.get("name") == item_name):
                            filter_name = self.filter_name_snippets.get(category, "Unknown")
                            break
                elif isinstance(items, dict):
                    for subcat, subitems in items.items():
                        if isinstance(subitems, list):
                            for list_item in subitems:
                                if (isinstance(list_item, str) and list_item == item_name) or \
                                   (isinstance(list_item, dict) and list_item.get("name") == item_name):
                                    filter_name = self.filter_name_snippets.get(category, "Unknown")
                                    break
            
            self.logger.log_snippet_interaction(self.field_name, "selected", item_name, filter_name)
        
        # For LLM instructions, pass the original item (dict) to preserve structure
        # For regular snippets, call with just the item text
        if hasattr(self.on_select, '__code__') and self.on_select.__code__.co_argcount > 2:
            # New signature that accepts category_path
            if self.field_name == "llm_instructions" and isinstance(item, dict):
                # For LLM instructions, pass the original dictionary
                self.on_select(item, None)
            else:
                # For regular snippets, pass the content
                self.on_select(item_content, None)
        else:
            # Old signature for backwards compatibility
            if self.field_name == "llm_instructions" and isinstance(item, dict):
                # For LLM instructions, pass the original dictionary
                self.on_select(item)
            else:
                # For regular snippets, pass the content
                self.on_select(item_content)
        # Don't close popup - let user select multiple items
    
    def _select_category(self, category: str):
        """Handle category selection."""
        # Pass category path to the callback
        if hasattr(self.on_select, '__code__') and self.on_select.__code__.co_argcount > 2:
            self.on_select(category, [category])
        else:
            # Fallback for old signature
            self.on_select(f"[CATEGORY: {category}]")
        # Don't close popup - let user select multiple items
    
    def _select_subcategory(self, category: str, subcategory: str):
        """Handle subcategory selection."""
        # Pass subcategory path to the callback
        if hasattr(self.on_select, '__code__') and self.on_select.__code__.co_argcount > 2:
            self.on_select(subcategory, [category, subcategory])
        else:
            # Fallback for old signature
            self.on_select(f"[SUBCATEGORY: {category}/{subcategory}]")
        # Don't close popup - let user select multiple items
    

    
    def _apply_styling(self):
        """Apply styling to the dialog."""
        # Only style the close button - other buttons have their own specific styling
        close_button = None
        for button in self.findChildren(QPushButton):
            if button.text() == "Close":
                close_button = button
                break
        
        if close_button:
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
            
            close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {button_bg};
                    color: {button_text};
                    border: 2px solid {button_border};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {button_hover_bg};
                    border-color: {button_hover_border};
                }}
                QPushButton:pressed {{
                    background-color: {button_pressed_bg};
                    border-color: {button_pressed_border};
                }}
            """)
    
    def refresh_theme(self):
        """Refresh the theme styling."""
        self._apply_styling()
        self.refresh_theme_buttons()
    
    def refresh_theme_buttons(self):
        """Refresh the theme styling for all buttons."""
        from ..utils.theme_manager import theme_manager
        colors = theme_manager.get_theme_colors()
        
        # Refresh all tracked buttons
        for button in self.snippet_buttons:
            if hasattr(button, 'button_type'):
                if button.button_type == 'snippet':
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {colors.get('snippet_bg', '#4a90e2')};
                            color: {colors.get('snippet_text', '#ffffff')};
                            border: 1px solid {colors.get('snippet_border', '#357abd')};
                            border-radius: 4px;
                            padding: 4px 8px;
                            font-size: 11px;
                        }}
                        QPushButton:hover {{
                            background-color: {colors.get('snippet_hover_bg', '#357abd')};
                            border-color: {colors.get('snippet_hover_border', '#2e6da4')};
                        }}
                        QPushButton:pressed {{
                            background-color: {colors.get('snippet_pressed_bg', '#2e6da4')};
                            border-color: {colors.get('snippet_pressed_border', '#1e4a6b')};
                        }}
                    """)
        
        # Refresh category and subcategory buttons
        for button in self.category_buttons:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors.get('category_bg', '#ff9500')};
                    color: {colors.get('category_text', '#ffffff')};
                    border: 1px solid {colors.get('category_border', '#e6850e')};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('category_hover_bg', '#e6850e')};
                    border-color: {colors.get('category_hover_border', '#d17a0d')};
                }}
                QPushButton:pressed {{
                    background-color: {colors.get('category_pressed_bg', '#d17a0d')};
                    border-color: {colors.get('category_pressed_border', '#b86b0b')};
                }}
            """)
        
        for button in self.subcategory_buttons:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors.get('subcategory_bg', '#ffcc00')};
                    color: {colors.get('subcategory_text', '#333333')};
                    border: 1px solid {colors.get('subcategory_border', '#e6b800')};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('subcategory_hover_bg', '#e6b800')};
                    border-color: {colors.get('subcategory_hover_border', '#d4a800')};
                }}
                QPushButton:pressed {{
                    background-color: {colors.get('subcategory_pressed_bg', '#d4a800')};
                    border-color: {colors.get('subcategory_pressed_border', '#b89400')};
                }}
            """)
    
    def refresh_snippets(self, selected_filters: List[str]):
        """Refresh snippets based on new filter_name selection."""
        self.selected_filters = selected_filters
        
        # Rebuild snippets with new filter_name selection
        self.snippets = {}
        self.filter_name_snippets = {}
        
        # Process filters in the order they were selected
        sorted_filters = selected_filters.copy() if selected_filters else []
        
        for filter_name in sorted_filters:
            filter_name_snippets = snippet_manager.get_snippets_for_field(self.field_name, filter_name)
            if filter_name_snippets:
                # Store snippets with filter_name info
                for category, items in filter_name_snippets.items():
                    if category not in self.snippets:
                        # First time seeing this category - assign it to this filter_name
                        self.snippets[category] = items
                        self.filter_name_snippets[category] = filter_name
                    else:
                        # Category already exists - merge items but keep the original filter_name assignment
                        # (This preserves the priority order - PG takes precedence over NSFW/Hentai)
                        if isinstance(items, list):
                            if isinstance(self.snippets[category], list):
                                self.snippets[category].extend(items)
                            else:
                                self.snippets[category] = items
                        elif isinstance(items, dict):
                            if isinstance(self.snippets[category], dict):
                                for subcat, subitems in items.items():
                                    if subcat not in self.snippets[category]:
                                        self.snippets[category][subcat] = subitems
                                    else:
                                        self.snippets[category][subcat].extend(subitems)
                            else:
                                self.snippets[category] = items
        
        # Rebuild the UI by clearing and recreating the scroll area content
        self._rebuild_scroll_content()
    
    def _rebuild_scroll_content(self):
        """Rebuild only the scroll area content with updated snippets."""
        # Find the scroll area and its content widget
        scroll_area = None
        for child in self.findChildren(QScrollArea):
            scroll_area = child
            break
        
        if scroll_area and scroll_area.widget():
            # Get the scroll content widget
            scroll_widget = scroll_area.widget()
            
            # Clear the scroll widget's layout
            scroll_layout = scroll_widget.layout()
            if scroll_layout:
                while scroll_layout.count():
                    item = scroll_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                # Rebuild snippet buttons in the scroll area
                self._build_snippet_buttons(scroll_layout)
    
    def _rebuild_widgets(self):
        """Rebuild the widget content with updated snippets."""
        # Clear existing content by removing all items from the main layout
        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Recreate widgets
        self._create_widgets()
    
    def show_popup(self):
        """Show the popup dialog."""
        self.show()
