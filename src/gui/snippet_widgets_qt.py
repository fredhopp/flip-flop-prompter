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
        radio_style = """
            QRadioButton {
                font-size: 11px;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QRadioButton::indicator:checked {
                background-color: #0066cc;
                border: 2px solid #0066cc;
                border-radius: 7px;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
                border: 2px solid #ccc;
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
        self.combo_box.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 10px;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #0066cc;
            }
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
        self.current_model = "seedream"
        
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
        self.model_combo.setCurrentText("Seedream")
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
        self.current_llm = "deepseek-r1:8b"
        self.ollama_available = False
        self.available_models = []
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        if self.change_callback:
            self.llm_changed.connect(self.change_callback)
        
        # Check Ollama connection on startup
        self._check_ollama_connection()
    
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
        
        # Create combobox (will be replaced with error label if needed)
        self.llm_combo = QComboBox()
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
    
    def __init__(self, parent, field_name: str, selected_families: List[str], on_select: Callable):
        super().__init__(parent)
        
        self.field_name = field_name
        self.selected_families = selected_families
        self.on_select = on_select
        
        # Get snippets for all selected families
        self.snippets = {}
        self.family_snippets = {}  # Track which family each snippet comes from
        
        for family in selected_families:
            family_snippets = snippet_manager.get_snippets_for_field(field_name, family)
            if family_snippets:
                # Store snippets with family info
                for category, items in family_snippets.items():
                    if category not in self.snippets:
                        self.snippets[category] = items
                        self.family_snippets[category] = family
                    else:
                        # Merge items from different families
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
                if child.text() == "Snippets":
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
    
    def _build_snippet_buttons(self, layout):
        """Build snippet selection buttons with category blocks."""
        if not self.snippets:
            no_snippets_label = QLabel("No snippets available for selected families")
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
            category_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                    margin: 2px;
                }
            """)
            category_frame.setMinimumWidth(200)
            category_frame.setMaximumWidth(300)
            
            # Layout for this category frame
            category_layout = QVBoxLayout(category_frame)
            category_layout.setContentsMargins(8, 8, 8, 8)
            category_layout.setSpacing(5)
            
            # Category title as clickable button with family info
            family_name = self.family_snippets.get(category, "Unknown")
            category_button = QPushButton(f"{category.title()} ({family_name})")
            category_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            category_button.setStyleSheet("""
                QPushButton {
                    color: #333; 
                    margin-bottom: 5px; 
                    border: 1px solid #FF9800;
                    border-radius: 5px;
                    background-color: #FFF3E0;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #FFE0B2;
                    border: 2px solid #FF9800;
                }
            """)
            category_button.clicked.connect(lambda checked, cat=category: self._select_category(cat))
            category_layout.addWidget(category_button)
            
            if isinstance(items, list):
                # Simple category with list of items
                for item in items:
                    btn = QPushButton(item)
                    btn.setMinimumHeight(25)
                    btn.setMaximumHeight(35)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #E3F2FD;
                            border: 1px solid #90CAF9;
                            border-radius: 3px;
                            padding: 4px 8px;
                            text-align: left;
                            margin: 1px 0px;
                        }
                        QPushButton:hover {
                            background-color: #BBDEFB;
                            border: 2px solid #2196F3;
                        }
                    """)
                    btn.clicked.connect(lambda checked, i=item: self._select_item(i))
                    category_layout.addWidget(btn)
                    
            elif isinstance(items, dict):
                # Nested category structure - show subcategories properly
                for subcategory, subitems in items.items():
                    if isinstance(subitems, list):
                        # Subcategory as clickable button
                        sub_button = QPushButton(subcategory)
                        sub_button.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                        sub_button.setStyleSheet("""
                            QPushButton {
                                color: #555; 
                                margin-top: 8px; 
                                margin-bottom: 3px; 
                                border: 1px solid #FFC107;
                                border-radius: 4px;
                                background-color: #FFFDE7;
                                padding: 4px;
                                text-align: left;
                            }
                            QPushButton:hover {
                                background-color: #FFF9C4;
                                border: 2px solid #FFC107;
                            }
                        """)
                        sub_button.clicked.connect(lambda checked, cat=category, sub=subcategory: self._select_subcategory(cat, sub))
                        category_layout.addWidget(sub_button)
                        
                        # Items in this subcategory
                        for item in subitems:
                            btn = QPushButton(item)
                            btn.setMinimumHeight(25)
                            btn.setMaximumHeight(35)
                            btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #E3F2FD;
                                    border: 1px solid #90CAF9;
                                    border-radius: 3px;
                                    padding: 4px 8px;
                                    text-align: left;
                                    margin: 1px 0px;
                                    margin-left: 10px;
                                }
                                QPushButton:hover {
                                    background-color: #BBDEFB;
                                    border: 2px solid #2196F3;
                                }
                            """)
                            btn.clicked.connect(lambda checked, i=item: self._select_item(i))
                            category_layout.addWidget(btn)
            
            # Add stretch to push content to top
            category_layout.addStretch()
            
            # Add this category frame to the flow layout
            categories_flow_layout.addWidget(category_frame)
        
        # Add the categories widget to the main layout
        layout.addWidget(categories_widget)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def _select_item(self, item: str):
        """Handle item selection."""
        # For regular snippets, call with just the item text
        if hasattr(self.on_select, '__code__') and self.on_select.__code__.co_argcount > 2:
            # New signature that accepts category_path
            self.on_select(item, None)
        else:
            # Old signature for backwards compatibility
            self.on_select(item)
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
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #333;
                    border: 2px solid #ccc;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f8f8f8;
                    border-color: #999;
                }
                QPushButton:pressed {
                    background-color: #e8e8e8;
                    border-color: #666;
                }
            """)
    
    def refresh_snippets(self, selected_families: List[str]):
        """Refresh snippets based on new family selection."""
        self.selected_families = selected_families
        
        # Rebuild snippets with new family selection
        self.snippets = {}
        self.family_snippets = {}
        
        for family in selected_families:
            family_snippets = snippet_manager.get_snippets_for_field(self.field_name, family)
            if family_snippets:
                # Store snippets with family info
                for category, items in family_snippets.items():
                    if category not in self.snippets:
                        self.snippets[category] = items
                        self.family_snippets[category] = family
                    else:
                        # Merge items from different families
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
