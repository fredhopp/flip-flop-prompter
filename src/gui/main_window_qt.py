"""
Main GUI window for the FlipFlopPrompt application using PySide6.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import os
from enum import Enum
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QScrollArea, QSizePolicy, QPushButton, QProgressBar, QStatusBar,
    QLineEdit, QComboBox, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QFont

from .tag_field_widgets_qt import TagTextFieldWidget, TagTextAreaWidget, SeedFieldWidget
from .tag_widgets_qt import TagType
from .snippet_widgets_qt import ContentRatingWidget, LLMSelectionWidget
from .preview_panel_qt import PreviewPanel
from ..core.data_models import PromptData
from ..utils.theme_manager import theme_manager
from ..utils.logger import get_logger
from ..utils.history_manager import HistoryManager


class NavigationState(Enum):
    CURRENT = "current"
    HISTORY = "history"
    TRANSITIONING = "transitioning"


class MainWindow(QMainWindow):
    """Main application window using PySide6."""
    
    # Custom signals
    content_rating_changed = Signal(str)
    
    def __init__(self, debug_enabled: bool = False):
        super().__init__()
        
        # Initialize components with lazy loading
        self.prompt_engine = None  # Lazy load when needed
        self._prompt_engine_initialized = False
        
        # Debug settings
        self.debug_enabled = debug_enabled
        self.logger = get_logger()
        
        # Cache for 0/X state (current state)
        self._cached_current_state = None
        
        # Flag to prevent recursive restoration
        self._restoring_state = False
        self._jumping_to_current = False
        self._intentionally_navigating = False  # Flag to prevent jump-to-current during intentional navigation
        self._generating_prompt = False  # Flag to prevent navigation updates during generation
        self._just_finished_generation = False  # Flag to handle post-generation navigation updates
        
        # Track blocked widgets during state restoration
        self._blocked_widgets = []
        
        # Track open snippet popups for dynamic updates
        self.open_snippet_popups = []
        
        # Initialize history manager (session-only, no persistence)
        self.history_manager = HistoryManager()
        
        # User data directories
        self.user_data_dir = theme_manager.user_data_dir
        self.templates_dir = self.user_data_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache directory for generation times
        self.cache_dir = self.user_data_dir / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.generation_cache_file = self.cache_dir / "generation_times.json"
        
        # Initialize UI
        self._setup_window()
        self._create_menu_bar()
        self._create_central_widget()
        self._create_input_fields()
        self._create_model_selection_row()
        self._create_button_frame()
        self._create_preview_panel()
        self._create_status_bar()
        
        # Initialize components (lazy load LLM components)
        self._update_llm_status_lazy()
        self._initialize_snippet_dropdowns()
        self._setup_callbacks()  # Set up callbacks after all widgets exist
        
        # Load user preferences
        self._load_preferences()
        
        # Set initial theme checkmark
        current_theme = theme_manager.get_current_theme()
        self._update_theme_checkmarks(current_theme)
        
        # Apply modern styling
        self._apply_styling()
        
        # Ensure navigation controls are properly styled
        if hasattr(self, 'preview_panel'):
            self.preview_panel.refresh_navigation_styling()
        
        # Initialize progress tracking
        self._init_progress_tracking()
        
        # Set navigation state
        self.navigation_state = NavigationState.CURRENT
    
    def _get_prompt_engine(self):
        """Lazy load the prompt engine when first needed."""
        if not self._prompt_engine_initialized:
            from ..core.prompt_engine import PromptEngine
            self.prompt_engine = PromptEngine()
            self._prompt_engine_initialized = True
        return self.prompt_engine
    
    def _get_snippet_manager(self):
        """Lazy load the snippet manager when first needed."""
        from ..utils.snippet_manager import snippet_manager
        return snippet_manager
    
    def _setup_window(self):
        """Setup the main window properties."""
        # Set window properties
        self.setWindowTitle("FlipFlopPrompt - AI Image Generation Prompt Builder")
        self.setMinimumSize(800, 600)
        
        # Load saved window size from preferences
        saved_width = theme_manager.get_preference("window_width", 1000)
        saved_height = theme_manager.get_preference("window_height", 700)
        self.resize(saved_width, saved_height)
    
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
        
        # Filters menu (replacing content rating)
        filters_menu = menubar.addMenu("Filters")
        
        # Initialize filters (checkboxes)
        self.filter_actions = {}
        # Get available filters dynamically from snippet files
        snippet_manager = None
        try:
            from ..utils.snippet_manager import SnippetManager
            snippet_manager = SnippetManager()
            available_filters = snippet_manager.get_available_filters()
            filters = available_filters if available_filters else ["PG"]  # Fallback for empty case
        except Exception:
            filters = ["PG", "NSFW", "Hentai"]  # Ultimate fallback
        
        for filter_name in filters:
            action = QAction(filter_name, self)
            action.setCheckable(True)
            if filter_name == filters[0]:  # Default to first available filter
                action.setChecked(True)
            action.triggered.connect(lambda checked, f=filter_name: self._on_filter_changed(f, checked))
            filters_menu.addAction(action)
            self.filter_actions[filter_name] = action
        
        # Themes menu (top-level)
        themes_menu = menubar.addMenu("Themes")
        
        # Light theme
        self.light_theme_action = QAction("Light Theme", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self._set_theme("light"))
        themes_menu.addAction(self.light_theme_action)
        
        # Dark theme
        self.dark_theme_action = QAction("Dark Theme", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self._set_theme("dark"))
        themes_menu.addAction(self.dark_theme_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        # Debug mode toggle
        self.debug_action = QAction("Debug Mode", self)
        self.debug_action.setCheckable(True)
        self.debug_action.triggered.connect(self._toggle_debug_mode)
        tools_menu.addAction(self.debug_action)
        
        # Open debug folder
        open_debug_action = QAction("Open Debug Folder", self)
        open_debug_action.triggered.connect(self._open_debug_folder)
        tools_menu.addAction(open_debug_action)
        
        # Clear generation cache
        clear_cache_action = QAction("Clear Generation Cache", self)
        clear_cache_action.triggered.connect(self._clear_generation_cache)
        tools_menu.addAction(clear_cache_action)
        
        # Reload snippets
        reload_snippets_action = QAction("Reload Snippets", self)
        reload_snippets_action.triggered.connect(self._reload_snippets)
        tools_menu.addAction(reload_snippets_action)
    
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
        self.main_layout.setSpacing(2)  # Reduced from 5 to 2 for more compact layout
        
        # Set scroll area widget
        scroll_area.setWidget(self.main_widget)
        
        # Layout for central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
    
    def _create_input_fields(self):
        """Create input field widgets."""
        # Style
        self.style_widget = TagTextFieldWidget(
            "Style:", placeholder="Select art style...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.style_widget)
        
        # Setting (renamed from environment)
        self.setting_widget = TagTextFieldWidget(
            "Setting:", placeholder="Describe the setting...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.setting_widget)
        
        # Weather
        self.weather_widget = TagTextFieldWidget(
            "Weather:", placeholder="Describe the weather...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.weather_widget)
        
        # Date and Time
        self.datetime_widget = TagTextFieldWidget(
            "Date and Time:", placeholder="Select season and time of day...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.datetime_widget)
        
        # Subjects
        self.subjects_widget = TagTextFieldWidget(
            "Subjects:", placeholder="Describe the subjects...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.subjects_widget)
        
        # Subjects Pose and Action
        self.pose_widget = TagTextFieldWidget(
            "Subjects Pose and Action:", placeholder="Describe poses and actions...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.pose_widget)
        
        # Camera (expanded choices)
        self.camera_widget = TagTextFieldWidget(
            "Camera:", placeholder="Select camera type...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.camera_widget)
        
        # Camera Framing and Action
        self.framing_widget = TagTextFieldWidget(
            "Camera Framing and Action:", placeholder="Describe framing and movement...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.framing_widget)
        
        # Color Grading & Mood
        self.grading_widget = TagTextFieldWidget(
            "Color Grading & Mood:", placeholder="Describe color grading and mood...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.grading_widget)
        
        # Additional Details
        self.details_widget = TagTextAreaWidget(
            "Additional Details:", placeholder="Any additional details...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.details_widget)
        
        # LLM Instructions
        self.llm_instructions_widget = TagTextAreaWidget(
            "LLM Instructions:", placeholder="Select or enter custom LLM processing instructions...", 
            change_callback=None  # Will be set later
        )
        self.main_layout.addWidget(self.llm_instructions_widget)
    
    def _create_model_selection_row(self):
        """Create seed row (with Clear button), LLM model row, and full-width Generate button."""
        # Seed row: left = seed/randomize/realize block, right = Clear All Fields button
        self.seed_widget = SeedFieldWidget(change_callback=self._on_seed_changed)
        seed_row = QWidget()
        seed_layout = QHBoxLayout(seed_row)
        seed_layout.setContentsMargins(0, 2, 0, 2)
        seed_layout.setSpacing(10)
        seed_layout.addWidget(self.seed_widget, 0)
        seed_layout.addStretch(1)
        
        # Clear All Fields button (right-aligned, size-to-content)
        self.clear_button = QPushButton("Clear All Fields")
        self.clear_button.clicked.connect(self._clear_all_fields)
        self.clear_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        seed_layout.addWidget(self.clear_button, 0, Qt.AlignmentFlag.AlignRight)
        
        self.main_layout.addWidget(seed_row)
        
        # LLM Model row
        model_row = QWidget()
        model_layout = QHBoxLayout(model_row)
        model_layout.setContentsMargins(0, 2, 0, 2)
        model_layout.setSpacing(20)
        self.llm_widget = LLMSelectionWidget(change_callback=self._on_llm_changed)
        model_layout.addWidget(self.llm_widget)
        self.main_layout.addWidget(model_row)
        
        # Batch row: left (50%) generate button, right (50%) batch controls
        batch_row = QWidget()
        batch_row.setObjectName("batchRow")
        batch_layout = QHBoxLayout(batch_row)
        batch_layout.setContentsMargins(0, 4, 0, 4)
        batch_layout.setSpacing(10)

        # Left: Generate button (expands to half width within layout)
        self.generate_button = QPushButton("Generate Final Prompt")
        self.generate_button.clicked.connect(self._generate_prompt)
        self.generate_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        batch_layout.addWidget(self.generate_button, 1)

        # Right: batch controls container
        batch_controls = QFrame()
        batch_controls.setObjectName("batchControls")
        batch_controls_layout = QHBoxLayout(batch_controls)
        batch_controls_layout.setContentsMargins(0, 0, 0, 0)
        # Larger spacing between the Size and Seed groups for clarity
        batch_controls_layout.setSpacing(28)
        batch_controls.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Batch checkbox (fixed width)
        self.batch_checkbox = QCheckBox("Batch")
        self.batch_checkbox.setObjectName("batchCheckBox")
        self.batch_checkbox.setChecked(False)
        self.batch_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        batch_controls_layout.addWidget(self.batch_checkbox)

        # Size group: tight spacing between label and spinbox
        size_group = QWidget()
        size_layout = QHBoxLayout(size_group)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(6)  # small gap between label and control
        size_label = QLabel("Size:")
        size_layout.addWidget(size_label)
        self.batch_size_input = QSpinBox()
        self.batch_size_input.setMinimum(1)
        self.batch_size_input.setMaximum(100)  # Limit to 100 for batch processing
        self.batch_size_input.setValue(5)
        self.batch_size_input.setFixedWidth(80)
        # Ensure arrows visible
        try:
            from PySide6.QtWidgets import QAbstractSpinBox
            self.batch_size_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        except Exception:
            pass
        self.batch_size_input.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        size_layout.addWidget(self.batch_size_input)
        batch_controls_layout.addWidget(size_group)

        # Seed group: tight spacing between label and combobox
        seed_group = QWidget()
        seed_layout = QHBoxLayout(seed_group)
        seed_layout.setContentsMargins(0, 0, 0, 0)
        seed_layout.setSpacing(6)  # small gap between label and control
        seed_label = QLabel("Seed:")
        seed_layout.addWidget(seed_label)
        self.seed_mode_combo = QComboBox()
        self.seed_mode_combo.addItems(["fixed", "increment", "decrement", "randomize"])
        self.seed_mode_combo.setCurrentText("increment")
        self.seed_mode_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        seed_layout.addWidget(self.seed_mode_combo)
        batch_controls_layout.addWidget(seed_group)

        # Make right side occupy equal space
        batch_layout.addWidget(batch_controls, 1)

        # Enable/disable size and seed controls when Batch is checked
        self.batch_checkbox.toggled.connect(self._on_batch_toggled)
        self._on_batch_toggled(self.batch_checkbox.isChecked())

        # Add batch row to main layout
        self.main_layout.addWidget(batch_row)
        # Keep a reference for styling updates
        self.batch_controls = batch_controls

        # Style batch controls according to theme and active state
        self._apply_batch_styling()

    def _on_batch_toggled(self, checked: bool):
        """Enable/disable Size and Seed controls when Batch is checked."""
        if self.debug_enabled:
            print(f"DEBUG BATCH: _on_batch_toggled() called with checked={checked}")
        
        # When Batch is checked, controls should be active; otherwise inactive
        if hasattr(self, 'batch_size_input'):
            self.batch_size_input.setDisabled(not checked)
            if self.debug_enabled:
                print(f"DEBUG BATCH: batch_size_input disabled: {not checked}")
        if hasattr(self, 'seed_mode_combo'):
            self.seed_mode_combo.setDisabled(not checked)
            if self.debug_enabled:
                print(f"DEBUG BATCH: seed_mode_combo disabled: {not checked}")
        # Update styling
        self._apply_batch_styling()

    def _apply_batch_styling(self):
        """Apply visual styling for batch controls based on checkbox state and theme."""
        try:
            colors = theme_manager.get_theme_colors()
        except Exception:
            colors = {
                "batch_active_outline": "#0066cc",
                "batch_inactive_bg": "#f2f2f2",
                "batch_dim_fg": "#888888",
            }
        active = self.batch_checkbox.isChecked() if hasattr(self, 'batch_checkbox') else False
        # Determine frame background used for inner controls
        frame_bg = colors.get('text_bg', '#ffffff') if active else colors.get('batch_inactive_bg', '#f2f2f2')
        # Row background and outline + checkbox indicator color
        if hasattr(self, 'batch_controls') and self.batch_controls is not None:
            if active:
                self.batch_controls.setStyleSheet(
                    f"""
                    #batchControls {{
                        background-color: {colors.get('text_bg', '#ffffff')};
                        border: 2px solid {colors.get('batch_active_outline','#0066cc')};
                        border-radius: 8px;
                        padding: 6px;
                    }}
                    #batchControls QCheckBox#batchCheckBox,
                    #batchControls QComboBox {{
                        background-color: {frame_bg};
                    }}
                    #batchControls QLabel {{
                        background-color: {frame_bg};
                    }}
                    QCheckBox#batchCheckBox::indicator {{
                        width: 14px; height: 14px; border: 1px solid {colors.get('batch_active_outline','#0066cc')}; border-radius: 3px; background: transparent;
                    }}
                    QCheckBox#batchCheckBox::indicator:checked {{
                        background-color: {colors.get('batch_active_outline','#0066cc')};
                        border: 1px solid {colors.get('batch_active_outline','#0066cc')};
                    }}
                    """
                )
            else:
                self.batch_controls.setStyleSheet(
                    f"""
                    #batchControls {{
                        background-color: {colors.get('batch_inactive_bg','#f2f2f2')};
                        border: 1px solid {colors.get('tag_border','#cccccc')};
                        border-radius: 8px;
                        padding: 6px;
                    }}
                    #batchControls QCheckBox#batchCheckBox,
                    #batchControls QComboBox {{
                        background-color: {frame_bg};
                    }}
                    #batchControls QLabel {{
                        background-color: {frame_bg};
                    }}
                    QCheckBox#batchCheckBox::indicator {{
                        width: 14px; height: 14px; border: 1px solid {colors.get('tag_border','#cccccc')}; border-radius: 3px; background: {colors.get('batch_inactive_bg','#f2f2f2')};
                    }}
                    QCheckBox#batchCheckBox::indicator:checked {{
                        background-color: {colors.get('batch_active_outline','#0066cc')};
                        border: 1px solid {colors.get('batch_active_outline','#0066cc')};
                    }}
                    """
                )
        # Dim labels and controls when inactive
        dim_fg = colors.get('batch_dim_fg', '#888888')
        normal_fg = colors.get('text_fg', '#000000')
        if hasattr(self, 'seed_mode_combo'):
            # Keep native arrow; set explicit bg to frame color so no halo
            self.seed_mode_combo.setStyleSheet(
                f"""
                QComboBox {{
                    color: {dim_fg if not active else normal_fg};
                    background-color: {frame_bg};
                    border: 1px solid {colors.get('tag_border','#cccccc')};
                    border-radius: 4px;
                    padding: 2px 6px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {frame_bg};
                    border: 1px solid {colors.get('tag_border','#cccccc')};
                    selection-background-color: {colors.get('batch_active_outline','#0066cc')};
                    selection-color: {colors.get('text_bg','#ffffff')};
                }}
                """
            )
        if hasattr(self, 'batch_size_input'):
            # Remove all stylesheets so native arrows render correctly
            try:
                self.batch_size_input.setStyleSheet("")
            except Exception:
                pass
            # Align palette roles so native-drawn parts match the frame background
            try:
                from PySide6.QtGui import QPalette, QColor
                pal = self.batch_size_input.palette()
                qcol = QColor(frame_bg)
                for role in (QPalette.Base, QPalette.Button, QPalette.Window):
                    pal.setColor(role, qcol)
                # Text colors for active/inactive
                pal.setColor(QPalette.Text, QColor(normal_fg if active else dim_fg))
                pal.setColor(QPalette.Disabled, QPalette.Text, QColor(dim_fg))
                self.batch_size_input.setPalette(pal)
            except Exception:
                pass
    
    def _create_content_rating(self):
        """Create content rating selection widget."""
        # Content rating is now handled by the Filters menu
        pass
    
    def _create_button_frame(self):
        """Deprecated: Buttons are placed in seed/model rows now."""
        return
    
    def _create_preview_panel(self):
        """Create the preview panel."""
        self.preview_panel = PreviewPanel()
        
        # Connect the new action button signals
        self.preview_panel.copy_requested.connect(self._copy_to_clipboard)
        self.preview_panel.save_requested.connect(self._save_prompt)
        self.preview_panel.save_all_requested.connect(self._save_all_prompts)  # New method to implement
        
        self.main_layout.addWidget(self.preview_panel)
    
    def _create_status_bar(self):
        """Create the status bar with progress functionality."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_label.setMinimumWidth(300)
        
        # Add widget to status bar
        self.status_bar.addWidget(self.status_label, 1)
    
    def _init_progress_tracking(self):
        """Initialize progress tracking and caching."""
        # Create cache directory
        self.cache_dir = self.user_data_dir / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache file for generation times
        self.generation_cache_file = self.cache_dir / "generation_times.json"
        self.generation_times = self._load_generation_cache()
        
        # Progress tracking
        self.generation_start_time = None
        self.estimated_duration = None
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
    
    def _load_generation_cache(self):
        """Load cached generation times."""
        try:
            if self.generation_cache_file.exists():
                with open(self.generation_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load generation cache: {e}")
        
        return {}
    
    def _save_generation_cache(self):
        """Save generation times to cache."""
        try:
            with open(self.generation_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.generation_times, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save generation cache: {e}")
    
    def _get_cached_generation_time(self, llm_model, target_model):
        """Get cached generation time for model combination."""
        key = f"{llm_model}_{target_model}"
        times = self.generation_times.get(key, [])
        
        if isinstance(times, list) and times:
            # Return average of recent times
            return sum(times) / len(times)
        elif isinstance(times, (int, float)):
            # Convert old single value format
            return times
        else:
            # Default 5 seconds
            return 5.0
    
    def _update_cached_generation_time(self, llm_model, target_model, duration):
        """Update cached generation time."""
        key = f"{llm_model}_{target_model}"
        times = self.generation_times.get(key, [])
        
        if isinstance(times, list):
            # Add new time to list
            times.append(duration)
            # Keep only last 10 times for statistics
            if len(times) > 10:
                times = times[-10:]
        else:
            # Convert old single value to list
            times = [times, duration] if isinstance(times, (int, float)) else [duration]
        
        self.generation_times[key] = times
        self._save_generation_cache()
    
    def _start_progress_tracking(self, llm_model, target_model):
        """Start progress tracking for generation."""
        self.generation_start_time = datetime.now()
        self.estimated_duration = self._get_cached_generation_time(llm_model, target_model)
        
        # Show expected time before starting
        if self.estimated_duration > 0:
            self.status_label.setText(f"Starting generation with {llm_model} (expected: {self.estimated_duration:.1f}s)...")
        else:
            self.status_label.setText(f"Starting generation with {llm_model}...")
        
        # Start progress updates after a short delay
        QTimer.singleShot(500, lambda: self._start_progress_updates())
    
    def _start_progress_updates(self):
        """Start the progress update timer."""
        self.progress_timer.start(100)  # Update every 100ms
    
    def _update_progress(self):
        """Update progress bar based on elapsed time."""
        if self.generation_start_time and self.estimated_duration:
            elapsed = (datetime.now() - self.generation_start_time).total_seconds()
            progress = min(int((elapsed / self.estimated_duration) * 100), 99)  # Cap at 99%
            
            # Update status with terminal-style progress
            llm_model = self.llm_widget.get_value() if hasattr(self, 'llm_widget') else "unknown"
            self.status_label.setText(f"Generating with {llm_model}... {elapsed:.1f}s/{self.estimated_duration:.1f}s [{progress}%]")
    
    def _stop_progress_tracking(self, duration=None):
        """Stop progress tracking."""
        self.progress_timer.stop()
        self.generation_start_time = None
        
        if duration:
            # Update cache with actual duration
            if hasattr(self, 'llm_widget'):
                llm_model = self.llm_widget.get_value()
                target_model = "seedream"  # Default model since target model is handled by LLM instructions
                self._update_cached_generation_time(llm_model, target_model, duration)
            
            # Show completion message with statistics
            self._show_generation_stats(llm_model, target_model, duration)
        else:
            self.status_label.setText("Ready")
    
    def _show_generation_stats(self, llm_model, target_model, duration):
        """Show generation statistics in status bar."""
        key = f"{llm_model}_{target_model}"
        times = self.generation_times.get(key, [])
        
        if isinstance(times, list):
            # Add new time to list
            times.append(duration)
            # Keep only last 10 times for statistics
            if len(times) > 10:
                times = times[-10:]
            self.generation_times[key] = times
        else:
            # Convert old single value to list
            times = [times, duration]
            self.generation_times[key] = times
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Show statistics
        self.status_label.setText(f"Generated in {duration:.2f}s (avg: {avg_time:.2f}s, min: {min_time:.2f}s, max: {max_time:.2f}s)")
        
        # Save updated cache
        self._save_generation_cache()
    
    def _show_status_message(self, message, timeout=3000):
        """Show a status message."""
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
    
    def _show_error_message(self, message):
        """Show an error message in status bar."""
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: red;")
        QTimer.singleShot(5000, lambda: self._clear_error_style())
    
    def _clear_error_style(self):
        """Clear error styling from status label."""
        self.status_label.setStyleSheet("")
        self.status_label.setText("Ready")
    
    def _apply_styling(self):
        """Apply theme-based styling to the application."""
        # Get current theme colors
        colors = theme_manager.get_theme_colors()
        
        # Build stylesheet with theme colors
        stylesheet = f"""
            QMainWindow {{
                background-color: {colors['bg']};
                color: {colors['text_fg']};
            }}
            QWidget {{
                background-color: {colors['bg']};
                color: {colors['text_fg']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors['tag_border']};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {colors['text_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: {colors['text_bg']};
            }}
            QScrollArea {{
                border: 1px solid {colors['tag_border']};
                background-color: {colors['text_bg']};
            }}
            
            /* Modern Scrollbars */
            QScrollBar:vertical {{
                background-color: {colors['scrollbar_bg']};
                width: 12px;
                border-radius: 6px;
                border: none;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['scrollbar_handle']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['button_bg']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: {colors['button_bg']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                width: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            QScrollBar:horizontal {{
                background-color: {colors['scrollbar_bg']};
                height: 12px;
                border-radius: 6px;
                border: none;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {colors['scrollbar_handle']};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {colors['button_bg']};
            }}
            QScrollBar::handle:horizontal:pressed {{
                background-color: {colors['button_bg']};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                height: 0px;
                width: 0px;
            }}
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background: none;
            }}
            
            /* Menu styling */
            QMenuBar {{
                background-color: {colors['menu_bg']};
                color: {colors['menu_fg']};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background-color: {colors['menu_selection_bg']};
                color: {colors['menu_selection_fg']};
            }}
            QMenu {{
                background-color: {colors['menu_bg']};
                color: {colors['menu_fg']};
                border: 1px solid {colors['tag_border']};
            }}
            QMenu::item {{
                padding: 4px 8px;
            }}
            QMenu::item:selected {{
                background-color: {colors['menu_selection_bg']};
                color: {colors['menu_selection_fg']};
            }}
            
            /* Status bar styling */
            QStatusBar {{
                background-color: {colors['status_bg']};
                color: {colors['status_fg']};
            }}
        """
        
        # Apply the main stylesheet
        self.setStyleSheet(stylesheet)
        
        # Apply button styling
        for button in self.findChildren(QPushButton):
            # Skip dice button, realize button, and buttons inside tag widgets
            parent = button.parent()
            if (button.objectName() not in ["diceButton", "realizeButton"] and 
                not (parent and parent.objectName() in ["tagWidget", "InlineTagWidget"])):
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors['button_bg']};
                        color: {colors['button_fg']};
                        border: 2px solid {colors['button_bg']};
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-height: 20px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['button_bg']};
                        border-color: {colors['button_bg']};
                        opacity: 0.8;
                    }}
                    QPushButton:pressed {{
                        background-color: {colors['button_bg']};
                        border-color: {colors['button_bg']};
                        opacity: 0.6;
                    }}
                    QPushButton:disabled {{
                        background-color: {colors['placeholder_fg']};
                        border-color: {colors['placeholder_fg']};
                        color: {colors['text_bg']};
                    }}
                """)
    
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
        if hasattr(self, 'llm_instructions_widget'):
            self.llm_instructions_widget.clear()
        
        # Reset filters to default
        # Reset to first available filter (or none if no filters available)
        first_filter = list(self.filter_actions.keys())[0] if self.filter_actions else None
        for filter_name, action in self.filter_actions.items():
            action.setChecked(filter_name == first_filter)
        
        # Reset model to default
        if hasattr(self, 'model_widget'):
            self.model_widget.set_value("seedream")
        
        # Reset LLM to default
        if hasattr(self, 'llm_widget'):
            self.llm_widget.set_value("deepseek-r1:8b")
        
        # Clear preview
        self._update_preview()
        
        # Show status message
        self._show_status_message("All fields cleared")
    
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
                self._show_status_message(f"Prompt saved to {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save prompt: {str(e)}")
    
    def _save_template(self):
        """Save current settings as a template with tag support."""
        # Collect current field tags and values
        template_data = {
            "format_version": "2.0",  # New format with tag support
            "style_tags": [tag.to_dict() for tag in self.style_widget.get_tags()] if hasattr(self, 'style_widget') else [],
            "setting_tags": [tag.to_dict() for tag in self.setting_widget.get_tags()] if hasattr(self, 'setting_widget') else [],
            "weather_tags": [tag.to_dict() for tag in self.weather_widget.get_tags()] if hasattr(self, 'weather_widget') else [],
            "datetime_tags": [tag.to_dict() for tag in self.datetime_widget.get_tags()] if hasattr(self, 'datetime_widget') else [],
            "subjects_tags": [tag.to_dict() for tag in self.subjects_widget.get_tags()] if hasattr(self, 'subjects_widget') else [],
            "pose_tags": [tag.to_dict() for tag in self.pose_widget.get_tags()] if hasattr(self, 'pose_widget') else [],
            "camera_tags": [tag.to_dict() for tag in self.camera_widget.get_tags()] if hasattr(self, 'camera_widget') else [],
            "framing_tags": [tag.to_dict() for tag in self.framing_widget.get_tags()] if hasattr(self, 'framing_widget') else [],
            "grading_tags": [tag.to_dict() for tag in self.grading_widget.get_tags()] if hasattr(self, 'grading_widget') else [],
            "details_tags": [tag.to_dict() for tag in self.details_widget.get_tags()] if hasattr(self, 'details_widget') else [],
            "llm_instructions_tags": [tag.to_dict() for tag in self.llm_instructions_widget.get_tags()] if hasattr(self, 'llm_instructions_widget') else [],
            "seed": self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0,
            "filters": self._get_selected_filters(),
            "model": self.model_widget.get_value() if hasattr(self, 'model_widget') else "seedream",
            "llm": self.llm_widget.get_value() if hasattr(self, 'llm_widget') else "deepseek-r1:8b",
            "debug_enabled": self.debug_enabled,
            "saved_at": datetime.now().isoformat()
        }
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Template", 
            str(self.templates_dir / f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Template saved to {file_path}")
                self._show_status_message(f"Template saved to {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save template: {str(e)}")
    
    def _load_template(self):
        """Load a template file with backward compatibility."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Template", 
            str(self.templates_dir),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Import Tag class for loading
                from .tag_widgets_qt import Tag
                
                # Check format version
                format_version = template_data.get("format_version", "1.0")
                
                if format_version == "2.0":
                    # New tag-based format
                    if hasattr(self, 'style_widget') and "style_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["style_tags"], "style")
                        self.style_widget.set_tags(tags)
                    if hasattr(self, 'setting_widget') and "setting_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["setting_tags"], "setting")
                        self.setting_widget.set_tags(tags)
                    if hasattr(self, 'weather_widget') and "weather_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["weather_tags"], "weather")
                        self.weather_widget.set_tags(tags)
                    if hasattr(self, 'datetime_widget') and "datetime_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["datetime_tags"], "datetime")
                        self.datetime_widget.set_tags(tags)
                    if hasattr(self, 'subjects_widget') and "subjects_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["subjects_tags"], "subjects")
                        self.subjects_widget.set_tags(tags)
                    if hasattr(self, 'pose_widget') and "pose_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["pose_tags"], "pose")
                        self.pose_widget.set_tags(tags)
                    if hasattr(self, 'camera_widget') and "camera_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["camera_tags"], "camera")
                        self.camera_widget.set_tags(tags)
                    if hasattr(self, 'framing_widget') and "framing_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["framing_tags"], "framing")
                        self.framing_widget.set_tags(tags)
                    if hasattr(self, 'grading_widget') and "grading_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["grading_tags"], "grading")
                        self.grading_widget.set_tags(tags)
                    if hasattr(self, 'details_widget') and "details_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["details_tags"], "details")
                        self.details_widget.set_tags(tags)
                    if hasattr(self, 'llm_instructions_widget') and "llm_instructions_tags" in template_data:
                        tags = self._load_and_check_tags(template_data["llm_instructions_tags"], "llm_instructions")
                        self.llm_instructions_widget.set_tags(tags)
                    if hasattr(self, 'seed_widget') and "seed" in template_data:
                        self.seed_widget.set_value(template_data["seed"])
                else:
                    # Legacy format - convert to tags
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
                
                # Common settings (both formats)
                # Handle both "filters" (new) and "families" (old) for backward compatibility
                filters_data = template_data.get("filters", template_data.get("families", []))
                if filters_data:
                    # Reset all filters first
                    for filter_name, action in self.filter_actions.items():
                        action.setChecked(False)
                    # Set filters from template
                    for filter_name in filters_data:
                        if filter_name in self.filter_actions:
                            self.filter_actions[filter_name].setChecked(True)
                if hasattr(self, 'model_widget') and "model" in template_data:
                    self.model_widget.set_value(template_data["model"])
                if hasattr(self, 'llm_widget') and "llm" in template_data:
                    self.llm_widget.set_value(template_data["llm"])
                
                # Load debug mode setting
                if "debug_enabled" in template_data:
                    self.debug_enabled = template_data["debug_enabled"]
                    if hasattr(self, 'debug_action'):
                        self.debug_action.setChecked(self.debug_enabled)
                
                # Update preview
                self._update_preview()
                
                # Refresh existing tags to update visual state after template loading
                self._refresh_existing_tags()
                
                QMessageBox.information(self, "Success", f"Template loaded from {file_path}")
                self._show_status_message(f"Template loaded from {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load template: {str(e)}")
    
    def _load_and_check_tags(self, tag_data_list, field_name: str):
        """Load tags from template data and check for missing categories/subcategories."""
        from .tag_widgets_qt import Tag
        
        # Map UI field names to actual JSON field names for validation
        field_mappings = {
            "pose": "subjects_pose_and_action",
            "grading": "color_grading_&_mood", 
            "datetime": "date_time",
            "framing": "camera_framing_and_action",
            "details": "additional_details"
        }
        
        # Use mapped field name for validation, fallback to original if no mapping
        validation_field_name = field_mappings.get(field_name, field_name)
        
        tags = []
        for tag_data in tag_data_list:
            tag = Tag.from_dict(tag_data)
            
            # Check if this tag is missing (for category/subcategory tags)
            if tag.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY]:
                if tag.check_if_missing(validation_field_name):
                    tag.is_missing = True
            
            tags.append(tag)
        
        return tags
    
    def _generate_prompt(self):
        """Generate the final prompt using the LLM."""
        # Add verbose debug logging for batch processing
        if self.debug_enabled:
            print(f"DEBUG BATCH: _generate_prompt() called")
            print(f"DEBUG BATCH: batch_checkbox exists: {hasattr(self, 'batch_checkbox')}")
            if hasattr(self, 'batch_checkbox'):
                print(f"DEBUG BATCH: batch_checkbox checked: {self.batch_checkbox.isChecked()}")
                print(f"DEBUG BATCH: batch_checkbox object: {self.batch_checkbox}")
                print(f"DEBUG BATCH: batch_checkbox state: {self.batch_checkbox.checkState()}")
                print(f"DEBUG BATCH: batch_size_input value: {self.batch_size_input.value() if hasattr(self, 'batch_size_input') else 'N/A'}")
                print(f"DEBUG BATCH: seed_mode_combo value: {self.seed_mode_combo.currentText() if hasattr(self, 'seed_mode_combo') else 'N/A'}")
        
        # Unified approach: always call _generate_batch_prompts()
        # Single submission is treated as batch of 1 with "fixed" seed mode
        if self.debug_enabled:
            print(f"DEBUG BATCH: Calling _generate_batch_prompts() (unified approach)")
        self._generate_batch_prompts()



    def _generate_batch_prompts(self):
        """Generate multiple prompts in batch using different seeds - unified approach for single and batch."""
        if self.debug_enabled:
            print(f"DEBUG BATCH: _generate_batch_prompts() called")
        
        # Initialize variables outside try block to avoid UnboundLocalError
        llm_model = "gemma3:4b"  # Default fallback
        model = "seedream"  # Default model
        # Get first available filter as fallback 
        first_filter = list(self.filter_actions.keys())[0] if self.filter_actions else None
        content_rating = first_filter if first_filter else "PG"  # Ultimate fallback
        
        # INFINITE LOOP PROTECTION: Set processing flag (NO navigation)
        self._generating_prompt = True
        
        if self.debug_enabled:
            print(f"DEBUG BATCH: Staying on current position during generation")
        
        try:
            # Log the generation attempt
            if self.logger:
                self.logger.log_gui_action("Generate prompts", "Starting prompt generation")
            
            # UNIFIED APPROACH: Determine if this is single or batch
            batch_enabled = hasattr(self, 'batch_checkbox') and self.batch_checkbox.isChecked()
            
            if batch_enabled:
                # Actual batch processing
                batch_size = self.batch_size_input.value() if hasattr(self, 'batch_size_input') else 5
                seed_mode = self.seed_mode_combo.currentText() if hasattr(self, 'seed_mode_combo') else "increment"
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Batch mode - size: {batch_size}, mode: {seed_mode}")
            else:
                # Single submission treated as batch of 1 with "fixed" seed mode
                batch_size = 1
                seed_mode = "fixed"  # Always use current seed unchanged for single submission
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Single mode (batch of 1) - size: {batch_size}, mode: {seed_mode}")
            
            base_seed = self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0
            
            if self.debug_enabled:
                print(f"DEBUG BATCH: Batch parameters - size: {batch_size}, mode: {seed_mode}, base_seed: {base_seed}")
            
            # Validate that LLM instructions are selected
            llm_instructions = self.llm_instructions_widget.get_llm_instruction_content() if hasattr(self, 'llm_instructions_widget') else ""
            if not llm_instructions.strip():
                QMessageBox.warning(self, "LLM Instructions Required", 
                    "Please select an LLM instruction from the 'LLM Instructions' field before generating batch prompts.\n\n"
                    "This ensures the LLM knows how to process your prompt data correctly.")
                self._show_error_message("LLM instructions required")
                return
            
            # Get LLM model and filters
            llm_model = self.llm_widget.get_value() if hasattr(self, 'llm_widget') else "gemma3:4b"
            selected_filters = self._get_selected_filters()
            content_rating = selected_filters[0] if selected_filters else first_filter
            
            if self.debug_enabled:
                print(f"DEBUG BATCH: Using LLM model: {llm_model}")
                print(f"DEBUG BATCH: Using content rating: {content_rating}")
                print(f"DEBUG BATCH: Starting batch generation loop for {batch_size} prompts")
            
            # Start progress tracking for batch
            self._start_progress_tracking(llm_model, "seedream")
            
            # Record start time
            start_time = datetime.now()
            
            # Generate batch prompts sequentially
            for i in range(batch_size):
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Starting iteration {i+1}/{batch_size}")
                
                # Calculate seed for this iteration
                if seed_mode == "fixed":
                    current_seed = base_seed
                elif seed_mode == "increment":
                    current_seed = base_seed + i
                elif seed_mode == "decrement":
                    current_seed = max(0, base_seed - i)  # Clamp to 0 minimum
                elif seed_mode == "randomize":
                    import random
                    random.seed(base_seed + i)  # Use base_seed + i as seed for reproducible randomness
                    current_seed = random.randint(0, 999999)
                else:
                    current_seed = base_seed + i  # Default to increment
                
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Iteration {i+1} - calculated seed: {current_seed}")
                
                # Update status for this iteration
                self._show_status_message(f"Generating {i+1}/{batch_size} prompts (seed: {current_seed})...")
                
                # Create PromptData object with current seed
                prompt_data = PromptData(
                    style=self.style_widget.get_randomized_value(current_seed) if hasattr(self, 'style_widget') else "",
                    setting=self.setting_widget.get_randomized_value(current_seed) if hasattr(self, 'setting_widget') else "",
                    weather=self.weather_widget.get_randomized_value(current_seed) if hasattr(self, 'weather_widget') else "",
                    date_time=self.datetime_widget.get_randomized_value(current_seed) if hasattr(self, 'datetime_widget') else "",
                    subjects=self.subjects_widget.get_randomized_value(current_seed) if hasattr(self, 'subjects_widget') else "",
                    pose_action=self.pose_widget.get_randomized_value(current_seed) if hasattr(self, 'pose_widget') else "",
                    camera=self.camera_widget.get_randomized_value(current_seed) if hasattr(self, 'camera_widget') else "",
                    framing_action=self.framing_widget.get_randomized_value(current_seed) if hasattr(self, 'framing_widget') else "",
                    grading=self.grading_widget.get_randomized_value(current_seed) if hasattr(self, 'grading_widget') else "",
                    details=self.details_widget.get_randomized_value(current_seed) if hasattr(self, 'details_widget') else "",
                    llm_instructions=llm_instructions
                )
                
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Iteration {i+1} - calling prompt engine.generate_prompt()")
                
                # Generate prompt using the engine
                final_prompt = self._get_prompt_engine().generate_prompt(model, prompt_data, content_rating, self.debug_enabled)
                
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Iteration {i+1} - received final prompt (length: {len(final_prompt)})")
                    print(f"DEBUG BATCH: Iteration {i+1} - final prompt: '{final_prompt[:200]}{'...' if len(final_prompt) > 200 else ''}'")
                
                # Generate summary text for this iteration using the current seed (before saving to history)
                summary_text = self._generate_preview_text_with_seed(current_seed)
                
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Iteration {i+1} - summary: '{summary_text}'")
                
                # Save to history with final prompt (each gets individual history entry)
                self._save_to_history(final_prompt, summary_text, current_seed)
                
                # Get current history state after saving
                current_pos, total_count = self.history_manager.get_navigation_info()
                
                if self.debug_enabled:
                    print(f"DEBUG BATCH: Iteration {i+1} - saved to history (state: {current_pos}/{total_count})")
                
                # Update progress
                progress = (i + 1) / batch_size * 100
                self.status_label.setText(f"Batch progress: {progress:.0f}% ({i+1}/{batch_size})")
            
            # Calculate total generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
            if self.debug_enabled:
                print(f"DEBUG BATCH: Generation completed - {batch_size} prompts in {generation_time:.2f}s")
            
            # Log successful generation
            if self.logger:
                self.logger.log_gui_action("Generate prompts", f"Success - {generation_time:.2f}s - {batch_size} prompts - Model: {llm_model}")
            
            # Stop progress tracking
            self._stop_progress_tracking(generation_time)
            
            # INFINITE LOOP PROTECTION: Clear processing flag and set post-generation flag
            self._generating_prompt = False
            self._just_finished_generation = True
            
            # Update navigation controls (history count) without triggering full restoration
            self._update_history_navigation()
            
            # Clear post-generation flag
            self._just_finished_generation = False
            
            # Update status bar
            self._update_status_bar()
            
            # Show success message
            if batch_size == 1:
                self._show_status_message(f"Prompt generated successfully in {generation_time:.2f}s")
            else:
                self._show_status_message(f"Batch generation completed: {batch_size} prompts in {generation_time:.2f}s")
            
        except Exception as e:
            # Stop progress tracking on error
            self._stop_progress_tracking()
            
            # INFINITE LOOP PROTECTION: Clear processing flag on error
            self._generating_prompt = False
            self._just_finished_generation = False
            
            if self.debug_enabled:
                print(f"DEBUG BATCH: Error in generation: {str(e)}")
            
            # Log the error
            if self.logger:
                self.logger.log_error(f"Failed to generate prompts: {str(e)}", "Generate prompts")
            
            QMessageBox.critical(self, "Error", f"Failed to generate prompts: {str(e)}")
            self._show_error_message(f"Failed to generate prompts: {str(e)}")
            import traceback
            traceback.print_exc()  # For debugging
    
    def _set_theme(self, theme_name):
        """Set the application theme."""
        try:
            # Set theme in theme manager
            theme_manager.set_current_theme(theme_name)
            
            # Update theme action checkmarks
            self._update_theme_checkmarks(theme_name)
            
            # Apply the new theme
            self._apply_styling()
            
            # Refresh preview panel
            if hasattr(self, 'preview_panel'):
                self.preview_panel._apply_styling()
                self.preview_panel.refresh_navigation_styling()
            
            # Refresh any open snippet popups
            self._refresh_snippet_popups()
            
            # Refresh all tag containers
            self._refresh_tag_containers()
            
            # Refresh batch controls styling to new theme
            if hasattr(self, '_apply_batch_styling'):
                self._apply_batch_styling()
            
            # Log the theme change
            if self.logger:
                self.logger.log_gui_action("Theme changed", f"Set to {theme_name}")
            
            self._show_status_message(f"Theme set to {theme_name}")
        except Exception as e:
            self._show_error_message(f"Failed to set theme: {str(e)}")
    
    def _update_theme_checkmarks(self, theme_name):
        """Update the checkmarks for theme menu items."""
        # Uncheck all theme actions
        self.light_theme_action.setChecked(False)
        self.dark_theme_action.setChecked(False)
        
        # Check the current theme action
        if theme_name == "light":
            self.light_theme_action.setChecked(True)
        elif theme_name == "dark":
            self.dark_theme_action.setChecked(True)
    

    
    def _refresh_tag_containers(self):
        """Refresh all tag containers when theme changes."""
        tag_widgets = [
            self.style_widget, self.setting_widget, self.weather_widget,
            self.datetime_widget, self.subjects_widget, self.pose_widget,
            self.camera_widget, self.framing_widget, self.grading_widget,
            self.details_widget, self.llm_instructions_widget
        ]
        
        for widget in tag_widgets:
            if hasattr(widget, 'tag_input') and hasattr(widget.tag_input, 'refresh_theme'):
                widget.tag_input.refresh_theme()
        
        # Refresh seed widget buttons
        if hasattr(self, 'seed_widget') and hasattr(self.seed_widget, 'refresh_theme'):
            self.seed_widget.refresh_theme()
    
    def _toggle_debug_mode(self):
        """Toggle debug mode."""
        self.debug_enabled = self.debug_action.isChecked()
        status = "enabled" if self.debug_enabled else "disabled"
        self._show_status_message(f"Debug mode {status}")
    
    def _open_debug_folder(self):
        """Open the debug folder."""
        debug_folder = self.user_data_dir / "debug"
        if debug_folder.exists():
            os.startfile(str(debug_folder))  # Windows-specific
        else:
            QMessageBox.information(self, "Debug Folder", "No debug folder found.")
    
    def _clear_generation_cache(self):
        """Clear the generation cache."""
        try:
            # Clear the cache dictionary
            self.generation_times = {}
            
            # Remove the cache file
            if self.generation_cache_file.exists():
                self.generation_cache_file.unlink()
            
            self._show_status_message("Generation cache cleared")
        except Exception as e:
            self._show_error_message(f"Failed to clear cache: {str(e)}")
    
    def _reload_snippets(self):
        """Reload snippets from files."""
        try:
            # Import snippet manager
            from ..utils.snippet_manager import snippet_manager
            
            # Reload snippets
            snippet_manager.reload_snippets()
            
            # Refresh all snippet popups if they're open
            self._refresh_snippet_popups()
            
            # Refresh existing tags to check if they're still missing
            self._refresh_existing_tags()
            
            # Recreate filter menus completely instead of trying to refresh them
            self._recreate_filter_menus()
            
            self._show_status_message("Snippets reloaded successfully.")
        except Exception as e:
            self._show_error_message(f"Failed to reload snippets: {str(e)}")
    
    def _refresh_existing_tags(self):
        """Refresh existing tags to check if they're still missing after snippet reload."""
        try:
            print(f"DEBUG REFRESH: Starting _refresh_existing_tags()")
            selected_filters = self._get_selected_filters()
            print(f"DEBUG REFRESH: Current filters: {selected_filters}")
            
            # Get all tag field widgets
            tag_widgets = [
                self.style_widget, self.setting_widget, self.weather_widget,
                self.datetime_widget, self.subjects_widget, self.pose_widget,
                self.camera_widget, self.framing_widget, self.grading_widget,
                self.details_widget
            ]
            
            print(f"DEBUG REFRESH: Found {len(tag_widgets)} tag widgets")
            
            refresh_count = 0
            for i, widget in enumerate(tag_widgets):
                if widget is None:
                    print(f"DEBUG REFRESH: Widget {i} is None")
                    continue
                print(f"DEBUG REFRESH: Checking widget {i} - {type(widget).__name__} - has refresh_tags: {hasattr(widget, 'refresh_tags')}")
                if hasattr(widget, 'refresh_tags'):
                    print(f"DEBUG REFRESH: Refreshing widget {i} - {type(widget).__name__}")
                    widget.refresh_tags()
                    refresh_count += 1
                else:
                    print(f"DEBUG REFRESH: Widget {i} - {type(widget).__name__} does NOT have refresh_tags method")
            
            print(f"DEBUG REFRESH: Refreshed {refresh_count} tag widgets")
                    
        except Exception as e:
            import traceback
            print(f"Error refreshing existing tags: {e}")
            print(f"DEBUG REFRESH: Exception traceback:")
            traceback.print_exc()
    
    def _refresh_snippet_popups(self):
        """Refresh any open snippet popups."""
        # Find and refresh any open snippet popups
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'refresh_snippets') and callable(widget.refresh_snippets):
                try:
                    # Get current selected filters for this popup
                    if hasattr(widget, 'selected_filters'):
                        widget.refresh_snippets(widget.selected_filters)
                except Exception as e:
                    print(f"Error refreshing snippet popup: {e}")
            elif hasattr(widget, 'refresh_theme') and callable(widget.refresh_theme):
                try:
                    widget.refresh_theme()
                except Exception as e:
                    print(f"Error refreshing popup theme: {e}")
    
    def _recreate_filter_menus(self):
        """Completely recreate the filter menus with updated available filters."""
        try:
            from ..utils.snippet_manager import snippet_manager
            
            # Get updated available filters
            available_filters = snippet_manager.get_available_filters()
            filters = available_filters if available_filters else ["PG"]  # Fallback for empty case
            
            # Find the Filters menu
            menubar = self.menuBar()
            if not menubar:
                print("Warning: No menubar found")
                return
                
            # Find and remove the existing Filters menu
            filters_action = None
            filters_index = -1
            for i, action in enumerate(menubar.actions()):
                if action.text() == "Filters":
                    filters_action = action
                    filters_index = i
                    break
            
            if filters_action:
                menubar.removeAction(filters_action)
            
            # Create a new Filters menu
            filters_menu = QMenu("Filters", self)
            
            # Clear the filter actions dictionary
            self.filter_actions.clear()
            
            # Add filter actions
            for filter_name in filters:
                try:
                    action = QAction(filter_name, self)
                    action.setCheckable(True)
                    if filter_name == filters[0]:  # Default to first available filter
                        action.setChecked(True)
                    action.triggered.connect(lambda checked, f=filter_name: self._on_filter_changed(f, checked))
                    filters_menu.addAction(action)
                    self.filter_actions[filter_name] = action
                except Exception as e:
                    print(f"Error adding filter action {filter_name}: {e}")
            
            # Add the new menu to the menubar at the original position
            if filters_index >= 0:
                # Insert at the original position
                menubar.insertMenu(menubar.actions()[filters_index], filters_menu)
            else:
                # Fallback: add to the end
                menubar.addMenu(filters_menu)
                    
        except Exception as e:
            print(f"Error recreating filter menus: {e}")
    
    def _refresh_filter_menus(self):
        """Refresh the filter menus with updated available filters."""
        try:
            from ..utils.snippet_manager import snippet_manager
            
            # Get updated available filters
            available_filters = snippet_manager.get_available_filters()
            filters = available_filters if available_filters else ["PG"]  # Fallback for empty case
            
            # Find the Filters menu - be more defensive about menu access
            menubar = self.menuBar()
            if not menubar:
                print("Warning: No menubar found")
                return
                
            filters_menu = None
            for action in menubar.actions():
                if action.text() == "Filters":
                    filters_menu = action.menu()
                    break
            
            if not filters_menu:
                print("Warning: Filters menu not found")
                return
                
            # Check if menu is still valid
            if not filters_menu.isWidgetType():
                print("Warning: Filters menu is not a valid widget")
                return
            
            # Clear existing filter actions
            try:
                filters_menu.clear()
                self.filter_actions.clear()
            except Exception as e:
                print(f"Error clearing filter menu: {e}")
                return
                
            # Add updated filter actions
            for filter_name in filters:
                try:
                    action = QAction(filter_name, self)
                    action.setCheckable(True)
                    if filter_name == filters[0]:  # Default to first available filter
                        action.setChecked(True)
                    action.triggered.connect(lambda checked, f=filter_name: self._on_filter_changed(f, checked))
                    filters_menu.addAction(action)
                    self.filter_actions[filter_name] = action
                except Exception as e:
                    print(f"Error adding filter action {filter_name}: {e}")
                    
        except Exception as e:
            print(f"Error refreshing filter menus: {e}")
    
    def _generate_preview_text_with_seed(self, seed: int) -> str:
        """Generate preview text from current field values using a specific seed."""
        try:
            # Collect randomized field values using the provided seed
            field_values = {
                "Style": self.style_widget.get_randomized_value(seed) if hasattr(self, 'style_widget') else "",
                "Setting": self.setting_widget.get_randomized_value(seed) if hasattr(self, 'setting_widget') else "",
                "Weather": self.weather_widget.get_randomized_value(seed) if hasattr(self, 'weather_widget') else "",
                "Date/Time": self.datetime_widget.get_randomized_value(seed) if hasattr(self, 'datetime_widget') else "",
                "Subjects": self.subjects_widget.get_randomized_value(seed) if hasattr(self, 'subjects_widget') else "",
                "Pose/Action": self.pose_widget.get_randomized_value(seed) if hasattr(self, 'pose_widget') else "",
                "Camera": self.camera_widget.get_randomized_value(seed) if hasattr(self, 'camera_widget') else "",
                "Framing/Action": self.framing_widget.get_randomized_value(seed) if hasattr(self, 'framing_widget') else "",
                "Color/Mood": self.grading_widget.get_randomized_value(seed) if hasattr(self, 'grading_widget') else "",
                "Details": self.details_widget.get_randomized_value(seed) if hasattr(self, 'details_widget') else "",
            }
            
            # Build preview text - only include fields with values
            preview_lines = []
            for field, value in field_values.items():
                if value.strip():  # Only include non-empty fields
                    preview_lines.append(f"{field}: {value}")
            
            # Generate preview text
            if preview_lines:
                return "\n".join(preview_lines)
            else:
                return ""  # Empty preview will show placeholder
                
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error generating preview text with seed {seed}: {e}")
            return ""

    def _generate_preview_text(self) -> str:
        """Generate preview text from current field values."""
        try:
            # Get current seed for randomization
            seed = self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0
            
            # Use the seed-specific method
            return self._generate_preview_text_with_seed(seed)
                
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error generating preview text: {e}")
            return ""

    def _update_preview(self, preserve_tab: bool = False, force_update: bool = False):
        """Update the prompt preview with smart caching logic."""
        # Don't update if preview panel doesn't exist yet
        if not hasattr(self, 'preview_panel'):
            return
        
        # Don't update if we're transitioning (prevents cascading)
        if self.navigation_state == NavigationState.TRANSITIONING and not force_update:
            if self.debug_enabled:
                print("DEBUG NAV: Preview update skipped - transitioning")
            return
        
        # SIMPLE FLAG-BASED LOGIC: Handle field changes based on current position
        if not force_update and not (hasattr(self, '_restoring_state') and self._restoring_state) and not (hasattr(self, '_intentionally_navigating') and self._intentionally_navigating):
            current_pos, total_count = self.history_manager.get_navigation_info()
            
            if current_pos > 0:  # User is on history (1/X, 2/X, 3/X, etc.)
                # User modified fields while viewing history - cache current state as new 0/X and jump
                if self.debug_enabled:
                    print(f"DEBUG NAV: User modified fields on history position {current_pos}/{total_count} - caching as new 0/X")
                
                # Set restoring flag to prevent cascading during the entire operation
                self._restoring_state = True
                
                try:
                    # Cache the current field state as the new 0/X
                    self._cache_current_state()
                    
                    # Jump to position 0 (current state) FIRST
                    self.history_manager.jump_to_position(0)
                    
                    # Restore the cached current state (signals are blocked, no cascading)
                    self._restore_cached_current_state()
                    
                    # Update navigation to show current state
                    self._update_history_navigation()
                    
                    # Switch to summary tab to show the editable current state
                    if hasattr(self, 'preview_panel'):
                        self.preview_panel.tab_widget.setCurrentIndex(0)  # Summary tab
                        
                    if self.debug_enabled:
                        print("DEBUG NAV: Completed smart jump to current state")
                finally:
                    # Clear flag immediately (no timer needed)
                    self._restoring_state = False
                
                return  # Exit early - preview will be updated after jump
            elif current_pos == 0:  # User is on 0/X (current state)
                # User modified fields on current state - update the cache
                if self.debug_enabled:
                    print("DEBUG NAV: User modified fields on 0/X - updating cache")
                self._cache_current_state()
        
        try:
            # Generate preview text
            preview_text = self._generate_preview_text()
            
            if self.debug_enabled:
                print(f"DEBUG NAV: Generated preview text: '{preview_text}'")
            
            # Update preview panel - only if there's actual content
            if preview_text.strip():
                self.preview_panel.update_preview(preview_text, is_final=False, preserve_tab=preserve_tab)
            
            # Update status bar
            self._update_status_bar()
            
        except Exception as e:
            print(f"Error updating preview: {e}")
            if hasattr(self, 'preview_panel'):
                self.preview_panel.update_preview("", is_final=False, preserve_tab=preserve_tab)
    
    def _update_llm_status_lazy(self):
        """Lazy update LLM status to avoid blocking startup."""
        # Schedule LLM status update for after window is shown
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._update_llm_status)
    
    def _update_llm_status(self):
        """Update LLM status (now called lazily after startup)."""
        # This will be called after the window is shown
        if hasattr(self, 'llm_widget'):
            # Trigger LLM connection check in background
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self.llm_widget._check_ollama_connection)
    
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
    

    
    def _on_llm_changed(self, llm_name):
        """Handle LLM selection changes."""
        # Update preview panel LLM info (if preview panel exists)
        if hasattr(self, 'preview_panel'):
            self.preview_panel.update_llm_info(llm_name)
        
        # Update preview
        self._update_preview()
    
    def _get_selected_filters(self):
        """Get list of currently selected filters."""
        selected = []
        for filter_name, action in self.filter_actions.items():
            if action.isChecked():
                selected.append(filter_name)
        return selected  # Return empty list if none selected - no default fallback
    
    def _on_seed_changed(self):
        """Handle seed value changes."""
        # Update preview with new randomization
        self._update_preview()
        
        # Save seed in preferences if needed
        self._save_preferences()
    
    def _on_filter_changed(self, filter_name, checked):
        """Handle filter selection changes."""
        # Log the filter change
        if self.logger:
            self.logger.log_gui_action(f"Filter changed", f"{filter_name}: {'checked' if checked else 'unchecked'}")
        
        print(f"DEBUG FILTER: Filter {filter_name} {'checked' if checked else 'unchecked'}")
        selected_filters = self._get_selected_filters()
        print(f"DEBUG FILTER: Current selected filters: {selected_filters}")
        
        # Update snippet dropdowns with new filter selection
        self._update_snippet_filters()
        
        # Refresh all open snippet popups
        self._refresh_open_snippet_popups()
        
        # Refresh existing tags to check if they're still missing with new filter selection
        print(f"DEBUG FILTER: Calling _refresh_existing_tags()")
        self._refresh_existing_tags()
        
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
        self._show_status_message("Prompt copied to clipboard")
    
    def _update_snippet_filters(self):
        """Update snippet dropdowns based on selected filters."""
        # Get selected filters
        selected_filters = self._get_selected_filters()
        
        # Update all snippet widgets - this will refresh when snippet popups are opened
        # The snippet popups will call _get_selected_filters() when they open
        pass
    
    def _refresh_open_snippet_popups(self):
        """Refresh all currently open snippet popups."""
        selected_filters = self._get_selected_filters()
        
        # Remove closed popups from the list
        self.open_snippet_popups = [popup for popup in self.open_snippet_popups if popup.isVisible()]
        
        # Refresh each open popup
        for popup in self.open_snippet_popups:
            popup.refresh_snippets(selected_filters)
    
    def _setup_callbacks(self):
        """Set up all callbacks after widgets are created."""
        # Initialize field_widgets dictionary for caching
        self.field_widgets = {}
        field_names = ['style', 'setting', 'weather', 'datetime', 'subjects', 'pose', 'camera', 'framing', 'grading', 'details', 'llm_instructions', 'seed']
        
        for field_name in field_names:
            widget_attr = f'{field_name}_widget'
            if hasattr(self, widget_attr):
                self.field_widgets[field_name] = getattr(self, widget_attr)
        
        # Set up debounced preview update timer (Qt best practice)
        self._preview_update_timer = QTimer()
        self._preview_update_timer.setSingleShot(True)
        self._preview_update_timer.timeout.connect(self._update_preview)
        
        # Connect field changes to debounced update (prevents signal cascading)
        if hasattr(self, 'style_widget'):
            self.style_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'setting_widget'):
            self.setting_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'weather_widget'):
            self.weather_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'datetime_widget'):
            self.datetime_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'subjects_widget'):
            self.subjects_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'pose_widget'):
            self.pose_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'camera_widget'):
            self.camera_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'framing_widget'):
            self.framing_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'grading_widget'):
            self.grading_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'details_widget'):
            self.details_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'llm_instructions_widget'):
            self.llm_instructions_widget.value_changed.connect(self._schedule_preview_update)
        if hasattr(self, 'seed_widget'):
            self.seed_widget.value_changed.connect(self._schedule_preview_update)
        
        # Connect preview panel history signals
        if hasattr(self, 'preview_panel'):
            self.preview_panel.history_back_requested.connect(self._navigate_history_back)
            self.preview_panel.history_forward_requested.connect(self._navigate_history_forward)
            self.preview_panel.history_delete_requested.connect(self._delete_history_entry)
            self.preview_panel.history_clear_requested.connect(self._clear_history)
            self.preview_panel.load_preview_requested.connect(self._load_preview_into_fields)
            self.preview_panel.history_jump_requested.connect(self._jump_to_history_position)
        
        # Initial preview update - delay to ensure window is ready
        QTimer.singleShot(100, self._update_preview)
    
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
                
                # Load filter preferences (handle both "filters" and "families" for backward compatibility)
                selected_filters = prefs.get('filters', prefs.get('families', []))
                if selected_filters:
                    for filter_name, action in self.filter_actions.items():
                        action.setChecked(filter_name in selected_filters)
                
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
            # Get selected filters
            selected_filters = []
            for filter_name, action in self.filter_actions.items():
                if action.isChecked():
                    selected_filters.append(filter_name)
            
            prefs = {
                'filters': selected_filters,
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
        # Save window size to preferences
        theme_manager.set_preference("window_width", self.width())
        theme_manager.set_preference("window_height", self.height())
        
        # Save preferences
        theme_manager.save_preferences(theme_manager.preferences)
        
        event.accept()
    
    def _navigate_history_back(self):
        """Navigate to previous history entry."""
        print(f"DEBUG NAV: User clicked BACK button")
        self._intentionally_navigating = True
        try:
            if self.history_manager.navigate_back():
                self._update_history_navigation()
        finally:
            # Clear flag immediately (no timer needed)
            self._intentionally_navigating = False
    
    def _navigate_history_forward(self):
        """Navigate to next history entry."""
        print(f"DEBUG NAV: User clicked FORWARD button")
        self._intentionally_navigating = True
        try:
            if self.history_manager.navigate_forward():
                self._update_history_navigation()
        finally:
            # Clear flag immediately (no timer needed)
            self._intentionally_navigating = False
    
    def _delete_history_entry(self):
        """Delete current history entry."""
        self._intentionally_navigating = True
        try:
            if self.history_manager.delete_current_entry():
                self._update_history_navigation()
        finally:
            # Clear flag immediately (no timer needed)
            self._intentionally_navigating = False
    
    def _clear_history(self):
        """Clear all history entries."""
        self._intentionally_navigating = True
        try:
            self.history_manager.clear_history()
            self._update_history_navigation()
        finally:
            # Clear flag immediately (no timer needed)
            self._intentionally_navigating = False
    
    def _jump_to_history_position(self, position: int):
        """Jump to specific history position."""
        print(f"DEBUG NAV: User manually entered position {position}")
        self._intentionally_navigating = True
        try:
            if self.history_manager.jump_to_position(position):
                self._update_history_navigation()
        finally:
            # Clear flag immediately (no timer needed)
            self._intentionally_navigating = False
    
    def _should_jump_to_current_state(self) -> bool:
        """Check if we should jump back to current state (0/X) when field changes."""
        # Don't jump if we're intentionally navigating to history entries
        if hasattr(self, '_intentionally_navigating') and self._intentionally_navigating:
            if self.debug_enabled:
                print("DEBUG NAV: Skipping jump to current - intentionally navigating")
            return False
        
        # Only jump if we're in history mode (not on 0/X)
        current_pos, total_count = self.history_manager.get_navigation_info()
        should_jump = current_pos > 0  # 0 = current state, 1+ = history entries
        
        if self.debug_enabled:
            print(f"DEBUG NAV: _should_jump_to_current_state: current_pos={current_pos}, total_count={total_count}, should_jump={should_jump}")
        
        return should_jump
    
    def _block_all_field_signals(self):
        """Block signals from all field widgets to prevent cascading updates."""
        self._blocked_widgets = []
        for field_key, widget in self.field_widgets.items():
            if hasattr(widget, 'blockSignals'):
                widget.blockSignals(True)
                self._blocked_widgets.append(widget)
        if self.debug_enabled:
            print(f"DEBUG NAV: Blocked signals for {len(self._blocked_widgets)} widgets")
    
    def _unblock_all_field_signals(self):
        """Unblock signals from all field widgets."""
        for widget in self._blocked_widgets:
            if hasattr(widget, 'blockSignals'):
                widget.blockSignals(False)
        self._blocked_widgets = []
        if self.debug_enabled:
            print("DEBUG NAV: Unblocked all field widget signals")
    
    def _cache_current_state(self):
        """Cache the current field state as 0/X state."""
        if self.debug_enabled:
            print("DEBUG NAV: Caching current state")
        
        # Get current field state
        field_data = {}
        for field_key, widget in self.field_widgets.items():
            if hasattr(widget, 'get_tags'):
                field_data[field_key] = widget.get_tags()
            elif hasattr(widget, 'toPlainText'):
                field_data[field_key] = widget.toPlainText()
        
        self._cached_current_state = field_data
        
        if self.debug_enabled:
            print(f"DEBUG NAV: Cached {len(field_data)} fields")
    
    def _restore_cached_current_state(self):
        """Restore the cached 0/X state to the fields."""
        if not self._cached_current_state or self._restoring_state:
            if self.debug_enabled:
                if not self._cached_current_state:
                    print("DEBUG NAV: No cached current state to restore")
                else:
                    print("DEBUG NAV: Already restoring state, skipping")
            return
        
        if self.debug_enabled:
            print("DEBUG NAV: Restoring cached current state")
        
        # Set flag to prevent recursive calls
        self._restoring_state = True
        
        # Block ALL field widget signals during restoration
        self._block_all_field_signals()
        
        try:
            for field_key, field_data in self._cached_current_state.items():
                if field_key in self.field_widgets:
                    widget = self.field_widgets[field_key]
                    
                    if hasattr(widget, 'set_tags') and isinstance(field_data, list):
                        widget.set_tags(field_data)
                    elif hasattr(widget, 'setPlainText') and isinstance(field_data, str):
                        widget.setPlainText(field_data)
                    
                    if self.debug_enabled:
                        print(f"DEBUG NAV: Restored field {field_key}: {type(field_data)}")
        finally:
            # Unblock signals
            self._unblock_all_field_signals()
            
            # Clear flag immediately (no timer needed)
            self._restoring_state = False
    
    def _jump_to_current_state(self):
        """Jump back to current state (0/X) and load the cached state."""
        # Prevent recursive calls
        if hasattr(self, '_jumping_to_current') and self._jumping_to_current:
            if self.debug_enabled:
                print("DEBUG NAV: Already jumping to current state, skipping")
            return
        
        # Set flag to prevent recursive calls
        self._jumping_to_current = True
        
        try:
            if self.debug_enabled:
                print("DEBUG NAV: Starting jump to current state")
            
            # Jump to position 0 (current state) FIRST
            self.history_manager.jump_to_position(0)
            
            # Load the cached current state (don't cache, just restore)
            self._restore_cached_current_state()
            
            # Update navigation to show current state (this will call _show_current_state)
            self._update_history_navigation()
            
            # Switch to summary tab to show the editable current state
            if hasattr(self, 'preview_panel'):
                self.preview_panel.tab_widget.setCurrentIndex(0)  # Summary tab
                
            if self.debug_enabled:
                print("DEBUG NAV: Completed jump to current state")
        finally:
            # Clear flag immediately (no timer needed)
            self._jumping_to_current = False
    
    def _load_history_entry_into_current_state(self, entry):
        """Load a history entry into the current state (0/X) for editing."""
        # Preserve current tab selection
        current_tab = self.preview_panel.tab_widget.currentIndex() if hasattr(self, 'preview_panel') else 0
        
        # Set flag to prevent recursive calls during restoration
        self._restoring_state = True
        
        # Block ALL field widget signals during restoration
        self._block_all_field_signals()
        
        try:
            # Restore field data
            if self.debug_enabled:
                print(f"DEBUG NAV: Starting field restoration for {len(entry.field_data)} fields")
            for field_name, field_data in entry.field_data.items():
                if self.debug_enabled:
                    print(f"DEBUG NAV: Processing field {field_name}: {type(field_data)}")
                if hasattr(self, f'{field_name}_widget'):
                    widget = getattr(self, f'{field_name}_widget')
                    if self.debug_enabled:
                        print(f"DEBUG NAV: Found widget for {field_name}")
                    
                    if isinstance(field_data, dict) and field_data.get('type') == 'tags':
                        # Restore tags
                        from ..gui.tag_widgets_qt import Tag, TagType
                        tags = [Tag.from_dict(tag_data) for tag_data in field_data['tags']]
                        if self.debug_enabled:
                            print(f"DEBUG NAV: Restoring {len(tags)} tags for field {field_name}: {[tag.text for tag in tags]}")
                        widget.set_tags(tags)
                    elif isinstance(field_data, dict) and field_data.get('type') == 'text':
                        # Restore plain text
                        if self.debug_enabled:
                            print(f"DEBUG NAV: Restoring text for field {field_name}: '{field_data['value']}'")
                        widget.set_value(field_data['value'])
                    else:
                        # Legacy format - treat as plain text
                        if self.debug_enabled:
                            print(f"DEBUG NAV: Restoring legacy text for field {field_name}: '{field_data}'")
                        widget.set_value(str(field_data))
            
            # Restore filters
            for filter_name in entry.filters:
                if filter_name in self.filter_actions:
                    self.filter_actions[filter_name].setChecked(True)
            
            # Restore seed
            if hasattr(self, 'seed_widget'):
                self.seed_widget.set_value(entry.seed)
            
            # Restore LLM model
            if hasattr(self, 'llm_widget'):
                self.llm_widget.set_value(entry.llm_model)
            
        finally:
            # Unblock signals
            self._unblock_all_field_signals()
            
            # Clear flag immediately (no timer needed)
            self._restoring_state = False
            
            # Update preview to show the loaded state (force update to avoid recursion)
            self._update_preview(preserve_tab=True, force_update=True)
            
            # Restore the original tab selection
            if hasattr(self, 'preview_panel'):
                self.preview_panel.tab_widget.setCurrentIndex(current_tab)
            
            # Set current state styling with total count
            current_pos, total_count = self.history_manager.get_navigation_info()
            self.preview_panel.set_history_state(False, total_count)
    
    def _load_preview_into_fields(self):
        """Load the current preview content into the input fields."""
        # Get the current preview text (from the active tab)
        current_tab = self.preview_panel.tab_widget.currentIndex()
        
        if current_tab == 0:  # Summary tab
            preview_text = self.preview_panel.summary_text.toPlainText()
        else:  # Final Prompt tab
            preview_text = self.preview_panel.final_text.toPlainText()
        
        print(f"DEBUG LOAD: Preview text from tab {current_tab}:")
        print(f"DEBUG LOAD: {preview_text}")
        
        if not preview_text.strip():
            return
        
        # Parse the preview text and extract field values
        # The format is typically "Field: value" on separate lines
        field_values = {}
        lines = preview_text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                field_name, value = line.split(':', 1)
                field_name = field_name.strip()
                value = value.strip()
                if value:  # Only add non-empty values
                    field_values[field_name] = value
                    print(f"DEBUG LOAD: Parsed field '{field_name}' = '{value}'")
        
        print(f"DEBUG LOAD: All parsed fields: {field_values}")
        
        # Get snippet manager for matching existing snippets
        from ..utils.snippet_manager import snippet_manager
        
        # Map field names to widget names and their corresponding snippet field names
        field_mapping = {
            'Style': ('style', 'style'),
            'Setting': ('setting', 'setting'), 
            'Weather': ('weather', 'weather'),
            'Date/Time': ('datetime', 'datetime'),
            'Subjects': ('subjects', 'subjects'),
            'Pose/Action': ('pose', 'subjects_pose_and_action'),  # Widget: pose, Snippet field: subjects_pose_and_action
            'Camera': ('camera', 'camera'),
            'Camera Framing and Action': ('framing', 'camera_framing_and_action'),  # Widget: framing, Snippet field: camera_framing_and_action
            'Color Grading & Mood': ('grading', 'color_grading_&_mood'),  # Widget: grading, Snippet field: color_grading_&_mood
            'Details': ('details', 'details')
        }
        
        # Block signals during loading to prevent cascading updates
        blocked_widgets = []
        for display_name, (widget_name, snippet_field_name) in field_mapping.items():
            if display_name in field_values and hasattr(self, f'{widget_name}_widget'):
                widget = getattr(self, f'{widget_name}_widget')
                if hasattr(widget, 'blockSignals'):
                    widget.blockSignals(True)
                    blocked_widgets.append(widget)
        
        try:
            for display_name, (widget_name, snippet_field_name) in field_mapping.items():
                if display_name in field_values and hasattr(self, f'{widget_name}_widget'):
                    widget = getattr(self, f'{widget_name}_widget')
                    value = field_values[display_name]
                    
                    if hasattr(widget, 'set_tags'):
                        from ..gui.tag_widgets_qt import Tag, TagType
                        
                        # Split comma-separated values into individual tags
                        individual_values = [v.strip() for v in value.split(',') if v.strip()]
                        tags = []
                        
                        for individual_value in individual_values:
                            # Try to find matching snippet using the correct snippet field name
                            matching_result = self._find_matching_snippet(snippet_field_name, individual_value, snippet_manager)
                            
                            if matching_result[0] is not None:
                                snippet_data, category_path, is_category = matching_result
                                print(f"DEBUG LOAD: MATCH FOUND for '{individual_value}': is_category={is_category}, category_path={category_path}, snippet_data={snippet_data}")
                                
                                if is_category:
                                    # Create category tag
                                    if len(category_path) == 1:
                                        tag = Tag(individual_value, TagType.CATEGORY, category_path=category_path)
                                        print(f"DEBUG LOAD: Created CATEGORY tag: {individual_value}")
                                    else:
                                        tag = Tag(individual_value, TagType.SUBCATEGORY, category_path=category_path)
                                        print(f"DEBUG LOAD: Created SUBCATEGORY tag: {individual_value}")
                                else:
                                    # Create snippet tag with proper data
                                    if isinstance(snippet_data, dict):
                                        # Handle instruction format with content
                                        snippet_display_name = snippet_data.get("name", individual_value)
                                        content = snippet_data.get("content", "")
                                        tag = Tag(snippet_display_name, TagType.SNIPPET, data=content)
                                        print(f"DEBUG LOAD: Created SNIPPET tag (dict): {snippet_display_name}")
                                    else:
                                        # Handle simple string snippets
                                        tag = Tag(individual_value, TagType.SNIPPET, data=snippet_data)
                                        print(f"DEBUG LOAD: Created SNIPPET tag (string): {individual_value}")
                                tags.append(tag)
                            else:
                                # Create user text tag if no snippet found
                                tag = Tag(individual_value, TagType.USER_TEXT)
                                print(f"DEBUG LOAD: NO MATCH - Created USER_TEXT tag: {individual_value}")
                                tags.append(tag)
                        
                        # Set the tags
                        widget.set_tags(tags)
                    else:
                        widget.set_value(value)
        
        finally:
            # Unblock signals
            for widget in blocked_widgets:
                widget.blockSignals(False)
            
            # Update preview to reflect the loaded values
            self._update_preview()
    
    def _find_matching_snippet(self, field_name: str, value: str, snippet_manager) -> tuple:
        """
        Find a matching snippet and return (snippet_data, category_path, is_category).
        Returns (None, None, False) if no match found.
        """
        try:

            filters = snippet_manager.get_available_filters()
            for filter_name in filters:
                snippets_data = snippet_manager.get_snippets_for_field(field_name, filter_name)
                if snippets_data:
                    # Search through categories
                    for category_name, category_data in snippets_data.items():
                        if isinstance(category_data, list):
                            # Simple list of snippets
                            for snippet in category_data:
                                if isinstance(snippet, str):
                                    if snippet.lower() == value.lower():
                                        return snippet, [category_name], False
                                elif isinstance(snippet, dict):
                                    snippet_name = snippet.get("name", "")
                                    if snippet_name and snippet_name.lower() == value.lower():
                                        return snippet, [category_name], False
                        elif isinstance(category_data, dict):
                            # Nested category structure
                            for subcategory_name, subcategory_items in category_data.items():
                                if isinstance(subcategory_items, list):
                                    # List of items in subcategory
                                    for item in subcategory_items:
                                        if isinstance(item, str):
                                            if item.lower() == value.lower():
                                                return item, [category_name, subcategory_name], False
                                        elif isinstance(item, dict):
                                            item_name = item.get("name", "")
                                            if item_name and item_name.lower() == value.lower():
                                                return item, [category_name, subcategory_name], False
                                elif isinstance(subcategory_items, dict):
                                    # Instruction format with content/description
                                    for instruction_name, instruction_data in subcategory_items.items():
                                        if isinstance(instruction_data, dict):
                                            instruction_display = instruction_data.get("name", instruction_name)
                                            if instruction_display and instruction_display.lower() == value.lower():
                                                return instruction_data, [category_name, subcategory_name], False
                    
                    # If no exact match, check if it's a category name
                    for category_name, category_data in snippets_data.items():
                        if category_name.lower() == value.lower():
                            return category_name, [category_name], True
                        if isinstance(category_data, dict):
                            for subcategory_name in category_data.keys():
                                if subcategory_name.lower() == value.lower():
                                    return subcategory_name, [category_name, subcategory_name], True
            return None, None, False
        except Exception as e:
            print(f"Error finding matching snippet: {e}")
            return None, None, False
    
    def _restore_from_history_entry(self):
        """Restore fields from current history entry."""
        entry = self.history_manager.get_current_entry()
        if entry:
            if self.debug_enabled:
                print(f"DEBUG NAV: Restoring history entry - seed={entry.seed}, filters={entry.filters}, llm_model={entry.llm_model}")
                print(f"DEBUG NAV: History entry field data: {list(entry.field_data.keys())}")
                print(f"DEBUG NAV: History entry final prompt: '{entry.final_prompt[:100] if entry.final_prompt else 'None'}{'...' if entry.final_prompt and len(entry.final_prompt) > 100 else ''}'")
                print(f"DEBUG NAV: History entry summary: '{entry.summary_text}'")
                print(f"DEBUG NAV: _intentionally_navigating flag is: {self._intentionally_navigating}")
            
            # Preserve current tab selection
            current_tab = self.preview_panel.tab_widget.currentIndex() if hasattr(self, 'preview_panel') else 0
            
            # Set flag to prevent recursive calls during restoration
            self._restoring_state = True
            
            # Block ALL field widget signals during restoration
            self._block_all_field_signals()
            
            try:
                # Restore field data
                for field_name, field_data in entry.field_data.items():
                    if hasattr(self, f'{field_name}_widget'):
                        widget = getattr(self, f'{field_name}_widget')
                        
                        if isinstance(field_data, dict) and field_data.get('type') == 'tags':
                            # Restore tags
                            from ..gui.tag_widgets_qt import Tag, TagType
                            tags = [Tag.from_dict(tag_data) for tag_data in field_data['tags']]
                            widget.set_tags(tags)
                        elif isinstance(field_data, dict) and field_data.get('type') == 'text':
                            # Restore plain text
                            widget.set_value(field_data['value'])
                        else:
                            # Legacy format - treat as plain text
                            widget.set_value(str(field_data))
                
                # Restore families
                for filter_name in entry.filters:
                    if filter_name in self.filter_actions:
                        self.filter_actions[filter_name].setChecked(True)
                
                # Restore seed
                if hasattr(self, 'seed_widget'):
                    self.seed_widget.set_value(entry.seed)
                
                # Restore LLM model
                if hasattr(self, 'llm_widget'):
                    self.llm_widget.set_value(entry.llm_model)
                
            finally:
                # Unblock signals
                self._unblock_all_field_signals()
                
                # Clear flag immediately (no timer needed)
                self._restoring_state = False
                
                # Update preview once at the end (preserve tab selection during history restoration)
                self._update_preview(preserve_tab=True, force_update=True)
                
                # Restore the final prompt if it exists
                if entry.final_prompt:
                    if self.debug_enabled:
                        print(f"DEBUG NAV: Setting final prompt text: '{entry.final_prompt[:100]}{'...' if len(entry.final_prompt) > 100 else ''}'") 
                    self.preview_panel.final_text.setPlainText(entry.final_prompt)
                    # Set regular font for generated content
                    font = self.preview_panel.final_text.font()
                    font.setItalic(False)
                    self.preview_panel.final_text.setFont(font)
                
                # Force a preview update to ensure summary reflects the restored fields
                # This is needed because the fields might not have been fully restored when _update_preview was called
                QTimer.singleShot(100, lambda: self._update_preview(preserve_tab=True, force_update=True))
                
                # Restore the original tab selection
                if hasattr(self, 'preview_panel'):
                    self.preview_panel.tab_widget.setCurrentIndex(current_tab)
                
                # History state styling is already set above
    
    def _update_history_navigation(self):
        """Update navigation controls state."""
        if hasattr(self, 'preview_panel'):
            can_go_back = self.history_manager.can_go_back()
            can_go_forward = self.history_manager.can_go_forward()
            current_pos, total_count = self.history_manager.get_navigation_info()
            has_history = self.history_manager.has_history()
            
            print(f"DEBUG NAV: Navigation update - current_pos={current_pos}, total_count={total_count}, is_current_state={current_pos == 0}")
            
            # Check if we're in current state (0) or history state (1+)
            is_current_state = current_pos == 0
            
            # POST-GENERATION HANDLING: Only update navigation controls, don't restore state
            if self._just_finished_generation:
                if self.debug_enabled:
                    print(f"DEBUG NAV: Post-generation update - only updating navigation controls")
                self.preview_panel.update_navigation_controls(
                    can_go_back, can_go_forward, current_pos, total_count, has_history, is_current_state
                )
                return
            
            # Set styling immediately based on state to prevent flashing
            if is_current_state:
                print(f"DEBUG NAV: Showing CURRENT state (0/{total_count})")
                # Set current state styling first to prevent flash
                self.preview_panel.set_history_state(False, total_count)
                self._show_current_state()
            else:
                print(f"DEBUG NAV: Showing HISTORY state ({current_pos}/{total_count})")
                # Set history state styling first to prevent flash
                self.preview_panel.set_history_state(True, total_count)
                # We're in history state, restore from history entry
                self._restore_from_history_entry()
            
            self.preview_panel.update_navigation_controls(
                can_go_back, can_go_forward, current_pos, total_count, has_history, is_current_state
            )
    
    def _show_current_state(self):
        """Show the current state of the fields (not from history)."""
        # If we have a cached current state, restore it first
        if self._cached_current_state:
            if self.debug_enabled:
                print("DEBUG NAV: Restoring cached current state in _show_current_state")
            self._restore_cached_current_state()
        
        # Generate preview text
        preview_text = self._generate_preview_text()
        
        print(f"DEBUG NAV: Current state preview text: '{preview_text}'")
        
        # Update preview panel with current state (only if we have content)
        if preview_text.strip():
            self.preview_panel.update_preview(preview_text, is_final=False, preserve_tab=True)
    
    def _save_to_history(self, final_prompt: str = "", summary_text: str = "", seed: Optional[int] = None):
        """Save current state to history."""
        # Get current field data
        field_data = {}
        field_widgets = [
            'style', 'setting', 'weather', 'datetime', 'subjects', 
            'pose', 'camera', 'framing', 'grading', 'details', 'llm_instructions'
        ]
        
        for field in field_widgets:
            if hasattr(self, f'{field}_widget'):
                widget = getattr(self, f'{field}_widget')
                # Save the actual tags for proper restoration
                if hasattr(widget, 'get_tags'):
                    field_data[field] = {
                        'type': 'tags',
                        'tags': [tag.to_dict() for tag in widget.get_tags()]
                    }
                else:
                    field_data[field] = {
                        'type': 'text',
                        'value': widget.get_value()
                    }
        
        # Get selected filters
        selected_filters = []
        for filter_name, action in self.filter_actions.items():
            if action.isChecked():
                selected_filters.append(filter_name)
        
        # Get seed - use provided seed or current UI seed
        if seed is None:
            seed = self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0
        
        # Get LLM model
        llm_model = self.llm_widget.get_value() if hasattr(self, 'llm_widget') else "deepseek-coder:6.7b"
        
        # Use provided summary text or generate if not provided
        if not summary_text:
            summary_text = self._generate_preview_text()
        
        # Add to history
        self.history_manager.add_entry(
            field_data=field_data,
            seed=seed,
            filters=selected_filters,
            llm_model=llm_model,
            target_model="seedream",  # Hardcoded as per current implementation
            final_prompt=final_prompt,
            summary_text=summary_text
        )
        
        # Update navigation controls - but skip during generation to prevent infinite loops
        if not getattr(self, '_generating_prompt', False):
            self._update_history_navigation()
        elif self.debug_enabled:
            print(f"DEBUG BATCH: Skipping navigation update during generation")
    
    def _schedule_preview_update(self):
        """Schedule a debounced preview update (Qt best practice to prevent signal cascading)."""
        # Only schedule if not currently restoring state
        if not (hasattr(self, '_restoring_state') and self._restoring_state):
            if hasattr(self, '_preview_update_timer'):
                self._preview_update_timer.start(100)  # 100ms debounce

    def _save_all_prompts(self):
        """Save all prompts (placeholder for future implementation)."""
        # TODO: Implement save all prompts functionality
        print("Save all prompts functionality not yet implemented")

