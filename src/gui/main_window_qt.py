"""
Main GUI window for the FlipFlopPrompt application using PySide6.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QScrollArea, QSizePolicy, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QFont

from .field_widgets_qt import TextFieldWidget, TextAreaWidget
from .snippet_widgets_qt import ContentRatingWidget, ModelSelectionWidget, LLMSelectionWidget
from .preview_panel_qt import PreviewPanel
from ..core.prompt_engine import PromptEngine
from ..core.data_models import PromptData
from ..utils.snippet_manager import snippet_manager
from ..utils.theme_manager import theme_manager


class MainWindow(QMainWindow):
    """Main application window using PySide6."""
    
    # Custom signals
    content_rating_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.prompt_engine = PromptEngine()
        
        # Debug settings
        self.debug_enabled = False
        
        # User data directories
        self.user_data_dir = theme_manager.user_data_dir
        self.templates_dir = self.user_data_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize UI
        self._setup_window()
        self._create_menu_bar()
        self._create_central_widget()
        self._create_input_fields()
        self._create_model_selection_row()
        self._create_button_frame()
        self._create_preview_panel()
        
        # Initialize components
        self._update_llm_status()
        self._initialize_snippet_dropdowns()
        self._setup_callbacks()  # Set up callbacks after all widgets exist
        
        # Load user preferences
        self._load_preferences()
        
        # Apply modern styling
        self._apply_styling()
    
    def _setup_window(self):
        """Setup the main window properties."""
        self.setWindowTitle("FlipFlopPrompt")
        self.setGeometry(100, 100, 800, 900)
        self.setMinimumSize(600, 700)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Load template
        load_template_action = QAction("Load Template", self)
        load_template_action.triggered.connect(self._load_template)
        file_menu.addAction(load_template_action)
        
        # Save template
        save_template_action = QAction("Save Template", self)
        save_template_action.triggered.connect(self._save_template)
        file_menu.addAction(save_template_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Families menu (replacing content rating)
        families_menu = menubar.addMenu("Families")
        
        # Initialize families (checkboxes)
        self.family_actions = {}
        families = ["PG", "NSFW", "Hentai"]
        
        for family in families:
            action = QAction(family, self)
            action.setCheckable(True)
            if family == "PG":  # Default selection
                action.setChecked(True)
            action.triggered.connect(lambda checked, f=family: self._on_family_changed(f, checked))
            families_menu.addAction(action)
            self.family_actions[family] = action
        
        # Themes menu (top-level)
        themes_menu = menubar.addMenu("Themes")
        
        # Light theme
        light_action = QAction("Light Theme", self)
        light_action.triggered.connect(lambda: self._set_theme("light"))
        themes_menu.addAction(light_action)
        
        # Debug menu
        debug_menu = menubar.addMenu("Debug")
        
        # Debug toggle
        self.debug_action = QAction("Enable Debug Mode", self)
        self.debug_action.setCheckable(True)
        self.debug_action.setChecked(False)
        self.debug_action.triggered.connect(self._toggle_debug_mode)
        debug_menu.addAction(self.debug_action)
        
        debug_menu.addSeparator()
        
        # Open debug folder
        debug_folder_action = QAction("Open Debug Folder", self)
        debug_folder_action.triggered.connect(self._open_debug_folder)
        debug_menu.addAction(debug_folder_action)
    
    def _create_central_widget(self):
        """Create the central widget with scroll area."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create main content widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)
        
        # Set scroll area widget
        scroll_area.setWidget(self.main_widget)
        
        # Layout for central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
    
    def _create_input_fields(self):
        """Create input field widgets."""
        # Style
        self.style_widget = TextFieldWidget(
            "Style:", placeholder="Select art style...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.style_widget)
        
        # Setting (renamed from environment)
        self.setting_widget = TextFieldWidget(
            "Setting:", placeholder="Describe the setting...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.setting_widget)
        
        # Weather
        self.weather_widget = TextFieldWidget(
            "Weather:", placeholder="Describe the weather...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.weather_widget)
        
        # Date and Time
        self.datetime_widget = TextFieldWidget(
            "Date and Time:", placeholder="Select season and time of day...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.datetime_widget)
        
        # Subjects
        self.subjects_widget = TextFieldWidget(
            "Subjects:", placeholder="Describe the subjects...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.subjects_widget)
        
        # Subjects Pose and Action
        self.pose_widget = TextFieldWidget(
            "Subjects Pose and Action:", placeholder="Describe poses and actions...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.pose_widget)
        
        # Camera (expanded choices)
        self.camera_widget = TextFieldWidget(
            "Camera:", placeholder="Select camera type...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.camera_widget)
        
        # Camera Framing and Action
        self.framing_widget = TextFieldWidget(
            "Camera Framing and Action:", placeholder="Describe framing and movement...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.framing_widget)
        
        # Color Grading & Mood
        self.grading_widget = TextFieldWidget(
            "Color Grading & Mood:", placeholder="Describe color grading and mood...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.grading_widget)
        
        # Additional Details
        self.details_widget = TextAreaWidget(
            "Additional Details:", placeholder="Any additional details...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.details_widget)
    
    def _create_model_selection_row(self):
        """Create model selection widgets side by side."""
        # Create horizontal layout for model widgets
        model_row = QWidget()
        model_layout = QHBoxLayout(model_row)
        model_layout.setContentsMargins(0, 5, 0, 5)
        model_layout.setSpacing(20)
        
        # Target Diffusion Model
        self.model_widget = ModelSelectionWidget(
            change_callback=self._on_model_changed
        )
        model_layout.addWidget(self.model_widget)
        
        # LLM Model  
        self.llm_widget = LLMSelectionWidget(
            change_callback=self._on_llm_changed
        )
        model_layout.addWidget(self.llm_widget)
        
        # Add to main layout
        self.main_layout.addWidget(model_row)
    
    def _create_content_rating(self):
        """Create content rating selection widget."""
        # Content rating is now handled by the Families menu
        pass
    
    def _create_button_frame(self):
        """Create button frame with action buttons."""
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.setSpacing(2)  # Small 2px gap between buttons
        
        # Generate Prompt button
        self.generate_button = QPushButton("Generate Final Prompt")
        self.generate_button.clicked.connect(self._generate_prompt)
        button_layout.addWidget(self.generate_button, 1)  # Equal stretch

        # Save Prompt button
        self.save_button = QPushButton("Save Prompt")
        self.save_button.clicked.connect(self._save_prompt)
        button_layout.addWidget(self.save_button, 1)  # Equal stretch

        # Copy to Clipboard button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_button, 1)  # Equal stretch

        # Clear All Fields button (moved to end)
        self.clear_button = QPushButton("Clear All Fields")
        self.clear_button.clicked.connect(self._clear_all_fields)
        button_layout.addWidget(self.clear_button, 1)  # Equal stretch
        
        self.main_layout.addWidget(button_frame)
    
    def _create_preview_panel(self):
        """Create the preview panel."""
        self.preview_panel = PreviewPanel()
        self.main_layout.addWidget(self.preview_panel, 1)  # Give it stretch factor 1 to expand
        
        # Create fixed status bar at bottom
        self.status_label = QLabel("0 words / 0 characters")
        self.status_label.setFont(QFont("Arial", 8))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setStyleSheet("color: #666; padding: 5px; border-top: 1px solid #ddd; background-color: #f8f9fa;")
        self.status_label.setFixedHeight(25)  # Fixed height
        self.main_layout.addWidget(self.status_label)
    
    def _apply_styling(self):
        """Apply light theme styling to the application."""
        # Light theme styles
        
        # Main window style with modern scrollbars
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #333333;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #ffffff;
            }
            QScrollArea {
                border: 1px solid #ddd;
                background-color: #ffffff;
            }
            
            /* Modern Scrollbars */
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
                border: none;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                width: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 12px;
                border-radius: 6px;
                border: none;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:horizontal:pressed {
                background-color: #808080;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                height: 0px;
                width: 0px;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # Button styles
        button_style = """
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: 2px solid #0066cc;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0052a3;
                border-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
                border-color: #003d7a;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #666666;
            }
        """
        
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
    
    # Event handlers
    def _clear_all_fields(self):
        """Clear all input fields."""
        # Clear all input fields
        if hasattr(self, 'style_widget'):
            self.style_widget.clear()
        if hasattr(self, 'setting_widget'):
            self.setting_widget.clear()
        if hasattr(self, 'weather_widget'):
            self.weather_widget.clear()
        if hasattr(self, 'datetime_widget'):
            self.datetime_widget.clear()
        if hasattr(self, 'subjects_widget'):
            self.subjects_widget.clear()
        if hasattr(self, 'pose_widget'):
            self.pose_widget.clear()
        if hasattr(self, 'camera_widget'):
            self.camera_widget.clear()
        if hasattr(self, 'framing_widget'):
            self.framing_widget.clear()
        if hasattr(self, 'grading_widget'):
            self.grading_widget.clear()
        if hasattr(self, 'details_widget'):
            self.details_widget.clear()
        
        # Reset families to default
        for family, action in self.family_actions.items():
            action.setChecked(family == "PG")
        
        # Reset model to default
        if hasattr(self, 'model_widget'):
            self.model_widget.set_value("seedream")
        
        # Reset LLM to default
        if hasattr(self, 'llm_widget'):
            self.llm_widget.set_value("deepseek-r1:8b")
        
        # Clear preview
        self._update_preview()
        
        # Show status message
        self.statusBar().showMessage("All fields cleared", 2000)
    
    def _save_prompt(self):
        """Save the current prompt to a file."""
        # Get current prompt text
        prompt_text = self.preview_panel.get_current_text()
        
        if not prompt_text:
            QMessageBox.warning(self, "No Prompt", "No prompt to save. Please generate a prompt first.")
            return
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Prompt", 
            str(self.user_data_dir / "prompt.txt"),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(prompt_text)
                QMessageBox.information(self, "Success", f"Prompt saved to {file_path}")
                self.statusBar().showMessage(f"Prompt saved to {Path(file_path).name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save prompt: {str(e)}")
    
    def _save_template(self):
        """Save current settings as a template."""
        # Collect current field values
        template_data = {
            "style": self.style_widget.get_value() if hasattr(self, 'style_widget') else "",
            "setting": self.setting_widget.get_value() if hasattr(self, 'setting_widget') else "",
            "weather": self.weather_widget.get_value() if hasattr(self, 'weather_widget') else "",
            "datetime": self.datetime_widget.get_value() if hasattr(self, 'datetime_widget') else "",
            "subjects": self.subjects_widget.get_value() if hasattr(self, 'subjects_widget') else "",
            "pose": self.pose_widget.get_value() if hasattr(self, 'pose_widget') else "",
            "families": self._get_selected_families(),
            "model": self.model_widget.get_value() if hasattr(self, 'model_widget') else "seedream",
            "llm": self.llm_widget.get_value() if hasattr(self, 'llm_widget') else "deepseek-r1:8b",
            "saved_at": datetime.now().isoformat()
        }
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Template", 
            str(self.templates_dir / "template.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Template saved to {file_path}")
                self.statusBar().showMessage(f"Template saved to {Path(file_path).name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save template: {str(e)}")
    
    def _load_template(self):
        """Load a template file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Template", 
            str(self.templates_dir),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Load field values
                if hasattr(self, 'style_widget') and "style" in template_data:
                    self.style_widget.set_value(template_data["style"])
                if hasattr(self, 'setting_widget') and "setting" in template_data:
                    self.setting_widget.set_value(template_data["setting"])
                if hasattr(self, 'weather_widget') and "weather" in template_data:
                    self.weather_widget.set_value(template_data["weather"])
                if hasattr(self, 'datetime_widget') and "datetime" in template_data:
                    self.datetime_widget.set_value(template_data["datetime"])
                if hasattr(self, 'subjects_widget') and "subjects" in template_data:
                    self.subjects_widget.set_value(template_data["subjects"])
                if hasattr(self, 'pose_widget') and "pose" in template_data:
                    self.pose_widget.set_value(template_data["pose"])
                if "families" in template_data:
                    # Reset all families first
                    for family, action in self.family_actions.items():
                        action.setChecked(False)
                    # Set families from template
                    for family in template_data["families"]:
                        if family in self.family_actions:
                            self.family_actions[family].setChecked(True)
                if hasattr(self, 'model_widget') and "model" in template_data:
                    self.model_widget.set_value(template_data["model"])
                if hasattr(self, 'llm_widget') and "llm" in template_data:
                    self.llm_widget.set_value(template_data["llm"])
                
                # Update preview
                self._update_preview()
                
                QMessageBox.information(self, "Success", f"Template loaded from {file_path}")
                self.statusBar().showMessage(f"Template loaded from {Path(file_path).name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load template: {str(e)}")
    
    def _generate_prompt(self):
        """Generate the final prompt using the LLM."""
        # Show processing status
        self.statusBar().showMessage("Generating prompt...", 5000)
        
        try:
            # Create PromptData object from field values
            prompt_data = PromptData(
                style=self.style_widget.get_value() if hasattr(self, 'style_widget') else "",
                setting=self.setting_widget.get_value() if hasattr(self, 'setting_widget') else "",
                weather=self.weather_widget.get_value() if hasattr(self, 'weather_widget') else "",
                date_time=self.datetime_widget.get_value() if hasattr(self, 'datetime_widget') else "",
                subjects=self.subjects_widget.get_value() if hasattr(self, 'subjects_widget') else "",
                pose_action=self.pose_widget.get_value() if hasattr(self, 'pose_widget') else "",
                camera="",  # Not implemented yet
                framing_action="",  # Not implemented yet  
                grading="",  # Not implemented yet
                details=""  # Not implemented yet
            )
            
            # Get model and families (use first selected family for backward compatibility)
            model = self.model_widget.get_value() if hasattr(self, 'model_widget') else "seedream"
            selected_families = self._get_selected_families()
            content_rating = selected_families[0] if selected_families else "PG"
            
            # Generate prompt using the engine
            final_prompt = self.prompt_engine.generate_prompt(model, prompt_data, content_rating, self.debug_enabled)
            
            # Update preview with final prompt
            self.preview_panel.update_preview(final_prompt, is_final=True)
            
            # Update status bar
            self._update_status_bar()
            
            self.statusBar().showMessage("Prompt generated successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate prompt: {str(e)}")
            self.statusBar().showMessage("Failed to generate prompt", 3000)
            import traceback
            traceback.print_exc()  # For debugging
    
    def _set_theme(self, theme_name):
        """Set the application theme."""
        # This is a placeholder - theme system will be implemented later
        self.statusBar().showMessage(f"Theme set to {theme_name}", 2000)
    
    def _toggle_debug_mode(self):
        """Toggle debug mode."""
        self.debug_enabled = self.debug_action.isChecked()
        status = "enabled" if self.debug_enabled else "disabled"
        self.statusBar().showMessage(f"Debug mode {status}", 2000)
    
    def _open_debug_folder(self):
        """Open the debug folder."""
        debug_folder = self.user_data_dir / "debug"
        if debug_folder.exists():
            os.startfile(str(debug_folder))  # Windows-specific
        else:
            QMessageBox.information(self, "Debug Folder", "No debug folder found.")
    
    def _update_preview(self):
        """Update the prompt preview."""
        # Don't update if preview panel doesn't exist yet
        if not hasattr(self, 'preview_panel'):
            return
            
        try:
            # Collect current field values
            field_values = {
                "Style": self.style_widget.get_value() if hasattr(self, 'style_widget') else "",
                "Setting": self.setting_widget.get_value() if hasattr(self, 'setting_widget') else "",
                "Weather": self.weather_widget.get_value() if hasattr(self, 'weather_widget') else "",
                "Date/Time": self.datetime_widget.get_value() if hasattr(self, 'datetime_widget') else "",
                "Subjects": self.subjects_widget.get_value() if hasattr(self, 'subjects_widget') else "",
                "Pose/Action": self.pose_widget.get_value() if hasattr(self, 'pose_widget') else "",
                "Camera": self.camera_widget.get_value() if hasattr(self, 'camera_widget') else "",
                "Framing/Action": self.framing_widget.get_value() if hasattr(self, 'framing_widget') else "",
                "Color/Mood": self.grading_widget.get_value() if hasattr(self, 'grading_widget') else "",
                "Details": self.details_widget.get_value() if hasattr(self, 'details_widget') else "",
            }
            
            # Build preview text - only include fields with values (same logic as Tkinter version)
            preview_lines = []
            for field, value in field_values.items():
                if value.strip():  # Only include non-empty fields
                    preview_lines.append(f"{field}: {value}")
            
            # Generate preview text
            if preview_lines:
                preview_text = "\n".join(preview_lines)
            else:
                preview_text = ""  # Empty preview will show placeholder
            
            # Update preview panel
            self.preview_panel.update_preview(preview_text, is_final=False)
            
            # Update status bar
            self._update_status_bar()
            
        except Exception as e:
            print(f"Error updating preview: {e}")
            # Show empty preview on error if preview panel exists
            if hasattr(self, 'preview_panel'):
                self.preview_panel.update_preview("", is_final=False)
    
    def _update_llm_status(self):
        """Update LLM connection status."""
        # This will be implemented when LLM widgets are converted
        pass
    
    def _initialize_snippet_dropdowns(self):
        """Initialize snippet dropdowns with current content rating."""
        # This will be implemented when snippet widgets are converted
        pass
    
    def _on_content_rating_changed(self, new_rating):
        """Handle content rating changes."""
        # Emit signal for other widgets to update
        self.content_rating_changed.emit(new_rating)
        
        # Update snippet dropdowns
        self._initialize_snippet_dropdowns()
        
        # Update preview
        self._update_preview()
    
    def _on_model_changed(self, model_name):
        """Handle model selection changes."""
        # Update preview panel model info
        self.preview_panel.update_model_info(model_name)
        
        # Update preview
        self._update_preview()
    
    def _on_llm_changed(self, llm_name):
        """Handle LLM selection changes."""
        # Update preview panel LLM info (if preview panel exists)
        if hasattr(self, 'preview_panel'):
            self.preview_panel.update_llm_info(llm_name)
        
        # Update preview
        self._update_preview()
    
    def _on_family_changed(self, family_name, checked):
        """Handle family selection changes."""
        # Update snippet dropdowns with new family selection
        self._update_snippet_families()
        
        # Update preview
        self._update_preview()
        
        # Save preferences
        self._save_preferences()
    
    def _copy_to_clipboard(self):
        """Copy the current prompt to clipboard."""
        prompt_text = self.preview_panel.get_current_text()
        
        if not prompt_text:
            QMessageBox.warning(self, "No Prompt", "No prompt to copy. Please generate a prompt first.")
            return
        
        # Copy to clipboard
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(prompt_text)
        
        QMessageBox.information(self, "Success", "Prompt copied to clipboard!")
        self.statusBar().showMessage("Prompt copied to clipboard", 2000)
    
    def _update_snippet_families(self):
        """Update snippet dropdowns based on selected families."""
        # Get selected families
        selected_families = []
        for family, action in self.family_actions.items():
            if action.isChecked():
                selected_families.append(family)
        
        # Update all snippet widgets
        # This will be implemented when we add the snippet functionality
        pass
    
    def _get_selected_families(self):
        """Get list of currently selected families."""
        selected = []
        for family, action in self.family_actions.items():
            if action.isChecked():
                selected.append(family)
        return selected
    
    def _setup_callbacks(self):
        """Set up all callbacks after widgets are created."""
        # Set up field widget callbacks
        if hasattr(self, 'style_widget'):
            self.style_widget.change_callback = self._update_preview
        if hasattr(self, 'setting_widget'):
            self.setting_widget.change_callback = self._update_preview
        if hasattr(self, 'weather_widget'):
            self.weather_widget.change_callback = self._update_preview
        if hasattr(self, 'datetime_widget'):
            self.datetime_widget.change_callback = self._update_preview
        if hasattr(self, 'subjects_widget'):
            self.subjects_widget.change_callback = self._update_preview
        if hasattr(self, 'pose_widget'):
            self.pose_widget.change_callback = self._update_preview
        if hasattr(self, 'camera_widget'):
            self.camera_widget.change_callback = self._update_preview
        if hasattr(self, 'framing_widget'):
            self.framing_widget.change_callback = self._update_preview
        if hasattr(self, 'grading_widget'):
            self.grading_widget.change_callback = self._update_preview
        if hasattr(self, 'details_widget'):
            self.details_widget.change_callback = self._update_preview
        
        # Initial preview update
        self._update_preview()
    
    def _update_status_bar(self):
        """Update the status bar with word and character count."""
        if hasattr(self, 'preview_panel') and hasattr(self, 'status_label'):
            word_count = self.preview_panel.get_word_count()
            char_count = self.preview_panel.get_char_count()
            self.status_label.setText(f"{word_count} words / {char_count} characters")
    
    def _load_preferences(self):
        """Load saved preferences."""
        try:
            prefs_file = self.user_data_dir / "preferences.json"
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Load family preferences
                if 'families' in prefs:
                    selected_families = prefs['families']
                    for family, action in self.family_actions.items():
                        action.setChecked(family in selected_families)
                
                # Load model preferences
                if 'model' in prefs and hasattr(self, 'model_widget'):
                    self.model_widget.set_value(prefs['model'])
                if 'llm_model' in prefs and hasattr(self, 'llm_widget'):
                    self.llm_widget.set_value(prefs['llm_model'])
                    
        except Exception as e:
            print(f"Warning: Could not load preferences: {e}")
    
    def _save_preferences(self):
        """Save current preferences."""
        try:
            # Get selected families
            selected_families = []
            for family, action in self.family_actions.items():
                if action.isChecked():
                    selected_families.append(family)
            
            prefs = {
                'families': selected_families,
                'theme': 'light'
            }
            
            # Add model preferences if available
            if hasattr(self, 'model_widget'):
                prefs['model'] = self.model_widget.get_value()
            if hasattr(self, 'llm_widget'):
                prefs['llm_model'] = self.llm_widget.get_value()
            
            prefs_file = self.user_data_dir / "preferences.json"
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        # Save preferences on exit
        self._save_preferences()
        event.accept()
