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
import subprocess
import threading
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QScrollArea, QSizePolicy, QPushButton, QProgressBar, QStatusBar,
    QLineEdit, QComboBox, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QEvent
from PySide6.QtGui import QAction, QFont

from .tag_field_widgets_qt import TagTextFieldWidget, TagTextAreaWidget, SeedFieldWidget
from .tag_widgets_qt import TagType
from .snippet_widgets_qt import ContentRatingWidget, LLMSelectionWidget
from .preview_panel_qt import PreviewPanel
from ..core.data_models import PromptData, PromptState
from ..utils.theme_manager import theme_manager
from ..utils.logger import get_logger
from ..utils.history_manager import HistoryManager
from ..utils.logger import debug, info, warning, error, LogArea


class NavigationState(Enum):
    CURRENT = "current"
    HISTORY = "history"
    TRANSITIONING = "transitioning"


class MainWindow(QMainWindow):
    """Main application window using PySide6."""
    
    # Custom signals
    content_rating_changed = Signal(str)
    # Emitted when UI is ready after initial show
    ui_ready = Signal()
    
    def __init__(self, debug_enabled: bool = False):
        super().__init__()
        
        # Track total startup time until UI responsiveness
        self._startup_start_time = time.time()
        
        # Track Ollama process to prevent multiple instances
        self._ollama_process = None
        self._ollama_process_lock = threading.Lock()
        
        init_start = time.time()
        
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
        history_start = time.time()
        self.history_manager = HistoryManager()
        history_time = time.time() - history_start
        if self.debug_enabled:
            info(f"STARTUP: HistoryManager initialization took {history_time:.3f}s", LogArea.GENERAL)
        
        # User data directories
        dir_start = time.time()
        self.user_data_dir = theme_manager.user_data_dir
        self.templates_dir = self.user_data_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache directory for generation times
        self.cache_dir = self.user_data_dir / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.generation_cache_file = self.cache_dir / "generation_times.json"
        dir_time = time.time() - dir_start
        if self.debug_enabled:
            info(f"STARTUP: Directory setup took {dir_time:.3f}s", LogArea.GENERAL)
        
        # Initialize UI
        ui_start = time.time()
        self._setup_window()
        setup_window_time = time.time() - ui_start
        if self.debug_enabled:
            info(f"STARTUP: _setup_window took {setup_window_time:.3f}s", LogArea.GENERAL)
        
        menu_start = time.time()
        self._create_menu_bar()
        menu_time = time.time() - menu_start
        if self.debug_enabled:
            info(f"STARTUP: _create_menu_bar took {menu_time:.3f}s", LogArea.GENERAL)
        
        central_start = time.time()
        self._create_central_widget()
        central_time = time.time() - central_start
        if self.debug_enabled:
            info(f"STARTUP: _create_central_widget took {central_time:.3f}s", LogArea.GENERAL)
        
        fields_start = time.time()
        self._create_input_fields()
        fields_time = time.time() - fields_start
        if self.debug_enabled:
            info(f"STARTUP: _create_input_fields took {fields_time:.3f}s", LogArea.GENERAL)
        
        model_start = time.time()
        self._create_model_selection_row()
        model_time = time.time() - model_start
        if self.debug_enabled:
            info(f"STARTUP: _create_model_selection_row took {model_time:.3f}s", LogArea.GENERAL)
        
        button_start = time.time()
        self._create_button_frame()
        button_time = time.time() - button_start
        if self.debug_enabled:
            info(f"STARTUP: _create_button_frame took {button_time:.3f}s", LogArea.GENERAL)
        
        preview_start = time.time()
        self._create_preview_panel()
        preview_time = time.time() - preview_start
        if self.debug_enabled:
            info(f"STARTUP: _create_preview_panel took {preview_time:.3f}s", LogArea.GENERAL)
        
        status_start = time.time()
        self._create_status_bar()
        status_time = time.time() - status_start
        if self.debug_enabled:
            info(f"STARTUP: _create_status_bar took {status_time:.3f}s", LogArea.GENERAL)
        
        ui_total_time = time.time() - ui_start
        if self.debug_enabled:
            info(f"STARTUP: Total UI creation took {ui_total_time:.3f}s", LogArea.GENERAL)
        
        # Initialize components (lazy load LLM components)
        components_start = time.time()
        self._update_llm_status_lazy()
        llm_time = time.time() - components_start
        if self.debug_enabled:
            info(f"STARTUP: _update_llm_status_lazy took {llm_time:.3f}s", LogArea.GENERAL)
        
        snippet_start = time.time()
        self._initialize_snippet_dropdowns()
        snippet_time = time.time() - snippet_start
        if self.debug_enabled:
            info(f"STARTUP: _initialize_snippet_dropdowns took {snippet_time:.3f}s", LogArea.GENERAL)
        
        callbacks_start = time.time()
        self._setup_callbacks()  # Set up callbacks after all widgets exist
        callbacks_time = time.time() - callbacks_start
        if self.debug_enabled:
            info(f"STARTUP: _setup_callbacks took {callbacks_time:.3f}s", LogArea.GENERAL)
        
        components_total_time = time.time() - components_start
        if self.debug_enabled:
            info(f"STARTUP: Total components initialization took {components_total_time:.3f}s", LogArea.GENERAL)
        
        # Load user preferences
        prefs_start = time.time()
        self._load_preferences()
        prefs_time = time.time() - prefs_start
        if self.debug_enabled:
            info(f"STARTUP: _load_preferences took {prefs_time:.3f}s", LogArea.GENERAL)
        
        # Auto-start Ollama if preference is set
        ollama_start = time.time()
        if hasattr(self, 'auto_start_ollama_action') and self.auto_start_ollama_action.isChecked():
            info(f"STARTUP: Auto-start Ollama preference is enabled, checking current processes...", LogArea.GENERAL)
            self._get_ollama_process_info()  # Log current state before auto-start
            self._auto_start_ollama()
        ollama_time = time.time() - ollama_start
        if self.debug_enabled:
            info(f"STARTUP: Ollama auto-start check took {ollama_time:.3f}s", LogArea.GENERAL)
        
        # Set initial theme checkmark
        theme_start = time.time()
        current_theme = theme_manager.get_current_theme()
        self._update_theme_checkmarks(current_theme)
        theme_time = time.time() - theme_start
        if self.debug_enabled:
            info(f"STARTUP: Theme setup took {theme_time:.3f}s", LogArea.GENERAL)
        
        # Apply modern styling
        styling_start = time.time()
        self._apply_styling()
        styling_time = time.time() - styling_start
        if self.debug_enabled:
            info(f"STARTUP: _apply_styling took {styling_time:.3f}s", LogArea.GENERAL)
        
        # Ensure navigation controls are properly styled
        nav_start = time.time()
        if hasattr(self, 'preview_panel'):
            self.preview_panel.refresh_navigation_styling()
        nav_time = time.time() - nav_start
        if self.debug_enabled:
            info(f"STARTUP: Navigation styling took {nav_time:.3f}s", LogArea.GENERAL)
        
        # Initialize progress tracking
        progress_start = time.time()
        self._init_progress_tracking()
        progress_time = time.time() - progress_start
        if self.debug_enabled:
            info(f"STARTUP: Progress tracking init took {progress_time:.3f}s", LogArea.GENERAL)
        
        # Set navigation state
        self.navigation_state = NavigationState.CURRENT
        
        # Debug counters for cycle detection
        self._dbg_prev_sched_count = 0
        self._dbg_prev_update_count = 0
        self._dbg_last_reset_time = time.monotonic()
        self._dbg_cycle_threshold = 100  # calls per 2 seconds

        # Popup/UI suppression during restores/jumps
        self._suppress_popups = False

        # Install global event filter to log QMessageBox storms
        event_start = time.time()
        try:
            app = QApplication.instance()
            if app:
                app.installEventFilter(self)
                self._dbg_popup_count = 0
                self._dbg_popup_last_reset = time.monotonic()
        except Exception:
            pass
        event_time = time.time() - event_start
        if self.debug_enabled:
            info(f"STARTUP: Event filter setup took {event_time:.3f}s", LogArea.GENERAL)

        total_init_time = time.time() - init_start
        if self.debug_enabled:
            info(f"STARTUP: Total MainWindow initialization took {total_init_time:.3f}s", LogArea.GENERAL)
            info(f"STARTUP: MainWindow breakdown - History: {history_time:.3f}s, Dirs: {dir_time:.3f}s, UI: {ui_total_time:.3f}s, Components: {components_total_time:.3f}s, Prefs: {prefs_time:.3f}s, Ollama: {ollama_time:.3f}s, Theme: {theme_time:.3f}s, Styling: {styling_time:.3f}s", LogArea.GENERAL)
        
        # Fire ui_ready after a short delay to allow widgets/services to settle
        QTimer.singleShot(300, self._emit_ui_ready)
    
    def eventFilter(self, obj, event):
        # Log and optionally rate-limit QMessageBox show/hide to detect cycles
        try:
            if isinstance(obj, QMessageBox):
                if event.type() in (QEvent.Show, QEvent.Hide):
                    now = time.monotonic()
                    if now - self._dbg_popup_last_reset > 2.0:
                        self._dbg_popup_count = 0
                        self._dbg_popup_last_reset = now
                    self._dbg_popup_count += 1
                    if self.debug_enabled:
                        debug(r"QMessageBox event: {event.type().name if hasattr(event.type(), 'name') else int(event.type())} count={self._dbg_popup_count}", LogArea.LOAD)
                    # If popups are storming, block further shows briefly
                    if event.type() == QEvent.Show and self._dbg_popup_count > 10:
                        if self.debug_enabled:
                            error(r"Popup storm detected; suppressing this QMessageBox show", LogArea.LOAD)
                        return True  # Filter out this event
                    # Suppress popups during restore/jump windows
                    if event.type() == QEvent.Show and getattr(self, '_suppress_popups', False):
                        if self.debug_enabled:
                            debug(r"Suppressing popup during restore/jump window", LogArea.LOAD)
                        return True
            # Log paint/update storms
            if event.type() in (QEvent.UpdateRequest, QEvent.Paint):
                now = time.monotonic()
                if not hasattr(self, '_dbg_paint_last_reset') or now - getattr(self, '_dbg_paint_last_reset', 0) > 2.0:
                    self._dbg_paint_count = 0
                    self._dbg_paint_last_reset = now
                self._dbg_paint_count += 1
                if self._dbg_paint_count % 200 == 0 and self.debug_enabled:
                    debug(r"High frequency UI updates: {self._dbg_paint_count} in last window", LogArea.NAVIGATION)
        except Exception:
            pass
        return super().eventFilter(obj, event)
        
        # Fire ui_ready after a short delay to allow widgets/services to settle
        QTimer.singleShot(300, self._emit_ui_ready)

    def _emit_ui_ready(self):
        if self.debug_enabled:
            info(r"DEBUG NAV: Emitting ui_ready", LogArea.GENERAL)
        
        # Create initial cache of the default state as 0/X
        if self.debug_enabled:
            info(r"DEBUG NAV: Creating initial cache after UI ready", LogArea.GENERAL)
        self._cache_current_state()
        
        self.ui_ready.emit()
    
    def _get_prompt_engine(self):
        """Lazy load the prompt engine when first needed."""
        if not self._prompt_engine_initialized:
            from ..core.prompt_engine import PromptEngine
            # Pass the process tracker to ensure Ollama process tracking
            self.prompt_engine = PromptEngine(process_tracker=self._is_ollama_running)
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
        
        # Add separator
        tools_menu.addSeparator()
        
        # Ollama management
        ollama_menu = tools_menu.addMenu("Ollama")
        
        # Start Ollama
        self.start_ollama_action = QAction("Start Ollama", self)
        self.start_ollama_action.triggered.connect(self._start_ollama)
        ollama_menu.addAction(self.start_ollama_action)
        
        # Kill Ollama
        self.kill_ollama_action = QAction("Kill Ollama", self)
        self.kill_ollama_action.triggered.connect(self._kill_ollama)
        ollama_menu.addAction(self.kill_ollama_action)
        
        # Refresh models
        refresh_models_action = QAction("Refresh Models", self)
        refresh_models_action.triggered.connect(self._refresh_llm_models)
        ollama_menu.addAction(refresh_models_action)
        
        # Debug: Show process info
        debug_process_action = QAction("Debug: Show Process Info", self)
        debug_process_action.triggered.connect(self._get_ollama_process_info)
        ollama_menu.addAction(debug_process_action)
        
        # Add separator
        ollama_menu.addSeparator()
        
        # Ollama preferences
        self.auto_start_ollama_action = QAction("Start Ollama on Startup", self)
        self.auto_start_ollama_action.setCheckable(True)
        self.auto_start_ollama_action.triggered.connect(self._toggle_auto_start_ollama)
        ollama_menu.addAction(self.auto_start_ollama_action)
        
        self.kill_ollama_on_exit_action = QAction("Kill Ollama on Exit", self)
        self.kill_ollama_on_exit_action.setCheckable(True)
        self.kill_ollama_on_exit_action.triggered.connect(self._toggle_kill_ollama_on_exit)
        ollama_menu.addAction(self.kill_ollama_on_exit_action)
    
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
        self.batch_size_input.setValue(3)
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
        debug(f"_on_batch_toggled() called with checked={checked}", LogArea.BATCH)
        
        # When Batch is checked, controls should be active; otherwise inactive
        if hasattr(self, 'batch_size_input'):
            self.batch_size_input.setDisabled(not checked)
            debug(f"batch_size_input disabled: {not checked}", LogArea.BATCH)
        if hasattr(self, 'seed_mode_combo'):
            self.seed_mode_combo.setDisabled(not checked)
            debug(f"seed_mode_combo disabled: {not checked}", LogArea.BATCH)
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
        
        # Connect the realize signal
        self.preview_panel.realize_requested.connect(self._realize_summary)
        
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
            warning(f"Could not load generation cache: {e}", LogArea.GENERAL)
        
        return {}
    
    def _save_generation_cache(self):
        """Save generation times to cache."""
        try:
            with open(self.generation_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.generation_times, f, indent=2, ensure_ascii=False)
        except Exception as e:
            warning(f"Could not save generation cache: {e}", LogArea.GENERAL)
    
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
        self._schedule_preview_update()
        
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
        """Save current settings as a template using PromptState."""
        try:
            # Capture current state as PromptState
            prompt_state = self.capture_current_state()
            
            # Create template data with PromptState
            template_data = {
                "format_version": "3.0",  # New PromptState-based format
                "prompt_state": prompt_state.to_dict(),
                "debug_enabled": self.debug_enabled,
                "saved_at": datetime.now().isoformat(),
                "description": "Template saved using PromptState format"
            }
            
            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Template", 
                str(self.templates_dir / f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Template saved to {file_path}")
                self._show_status_message(f"Template saved to {Path(file_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save template: {str(e)}")
    
    def _load_template(self, file_path: str = None, show_messages: bool = True):
        """Load a template file with backward compatibility and PromptState support.
        If file_path is provided, loads that file directly; otherwise opens a file dialog.
        """
        # Re-entry guard
        if hasattr(self, '_loading_template') and self._loading_template:
            if self.debug_enabled:
                info(r"[LOAD] Template load requested while already loading - skipping", LogArea.LOAD)
            return
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Template", 
                str(self.templates_dir),
                "JSON Files (*.json);;All Files (*)"
            )
        
        if file_path:
            # Set flag to prevent preview updates during template loading
            self._loading_template = True
            # Add a short post-load suppression window to let signals settle
            self._suppress_preview_updates = True
            
            # Stop any pending preview timer and disable UI updates to avoid flicker/cycling
            try:
                if hasattr(self, '_preview_update_timer'):
                    self._preview_update_timer.stop()
            except Exception:
                pass
            try:
                self._updates_enabled_before_load = self.updatesEnabled()
            except Exception:
                self._updates_enabled_before_load = True
            self.setUpdatesEnabled(False)
            
            try:
                if self.debug_enabled:
                    info(f"Loading template from: {file_path}", LogArea.LOAD)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                if self.debug_enabled:
                    debug(f"Template data keys: {list(template_data.keys())}", LogArea.LOAD)
                
                # Track issues for single popup
                issues = []
                
                # Check format version
                format_version = template_data.get("format_version", "1.0")
                
                if self.debug_enabled:
                    info(f"Template format version: {format_version}", LogArea.LOAD)
                
                if format_version == "3.0":
                    # New PromptState-based format
                    if self.debug_enabled:
                        info("Processing v3.0 PromptState-based template", LogArea.LOAD)
                    
                    if "prompt_state" in template_data:
                        if self.debug_enabled:
                            debug(f"PromptState data keys: {list(template_data['prompt_state'].keys())}", LogArea.LOAD)
                        
                        prompt_state = PromptState.from_dict(template_data["prompt_state"])
                        
                        if self.debug_enabled:
                            info(f"Created PromptState with {len(prompt_state.field_values)} fields and {len(prompt_state.field_tags)} tag sets", LogArea.LOAD)
                        
                        self.restore_from_prompt_state(prompt_state)
                        
                        # Validate LLM model if present
                        if prompt_state.llm_model and hasattr(self, 'llm_widget'):
                            if not self.llm_widget.validate_and_set_model(prompt_state.llm_model):
                                issues.append(f"LLM model '{prompt_state.llm_model}' not found - using '{self.llm_widget.get_value()}' instead")
                    else:
                        issues.append("Template missing prompt_state data")
                        
                elif format_version == "2.0":
                    # Legacy tag-based format - convert to PromptState
                    if self.debug_enabled:
                        info("Processing v2.0 tag-based template", LogArea.LOAD)
                    
                    prompt_state = self._convert_legacy_template_to_prompt_state(template_data)
                    self.restore_from_prompt_state(prompt_state)
                    
                    # Validate LLM model
                    if prompt_state.llm_model and hasattr(self, 'llm_widget'):
                        if not self.llm_widget.validate_and_set_model(prompt_state.llm_model):
                            issues.append(f"LLM model '{prompt_state.llm_model}' not found - using '{self.llm_widget.get_value()}' instead")
                            
                else:
                    # Legacy format - convert to PromptState
                    if self.debug_enabled:
                        info("Processing v1.0 legacy template", LogArea.LOAD)
                    
                    prompt_state = self._convert_legacy_template_to_prompt_state(template_data)
                    self.restore_from_prompt_state(prompt_state)
                
                # Load debug mode setting
                if "debug_enabled" in template_data:
                    self.debug_enabled = template_data["debug_enabled"]
                    if hasattr(self, 'debug_action'):
                        self.debug_action.setChecked(self.debug_enabled)
                
                # Update preview (will be triggered automatically when signals are unblocked)
                # No need to call _update_preview() here - it will be triggered by field changes
                
                # Refresh existing tags to update visual state after template loading
                self._refresh_existing_tags()
                
                # Create initial cache of the loaded state as 0/X
                if self.debug_enabled:
                    info(r"DEBUG NAV: Creating initial cache after template load", LogArea.GENERAL)
                self._cache_current_state()
                
                if self.debug_enabled:
                    info(f"Template loading completed successfully", LogArea.LOAD)
                
                # Log any issues and update status bar instead of showing modal popups
                if issues:
                    info(r"Template loaded with issues: {issues}", LogArea.LOAD)
                    self._show_status_message(f"Template loaded with {len(issues)} issue(s)")
                else:
                    self._show_status_message(f"Template loaded from {Path(file_path).name}")
                
                self._show_status_message(f"Template loaded from {Path(file_path).name}")
                
            except Exception as e:
                error(f"Failed to load template: {str(e)}", LogArea.ERROR)
                if self.debug_enabled:
                    import traceback
                    debug(f"Template loading traceback: {traceback.format_exc()}", LogArea.ERROR)
                # Avoid modal popup on error; log and status-bar only
                self._show_status_message("Failed to load template - see log")
            finally:
                # Clear the template loading flag
                self._loading_template = False
                # Clear suppression shortly after to avoid cascades
                from PySide6.QtCore import QTimer
                QTimer.singleShot(250, lambda: setattr(self, '_suppress_preview_updates', False))
                # No modal popups; rely on status bar and logs only
                # Re-enable UI updates
                try:
                    self.setUpdatesEnabled(self._updates_enabled_before_load)
                    self.update()
                except Exception:
                    pass
    
    def _convert_legacy_template_to_prompt_state(self, template_data):
        """Convert legacy template format to PromptState."""
        from .tag_widgets_qt import Tag, TagType
        
        if self.debug_enabled:
            info("Converting legacy template to PromptState", LogArea.LOAD)
        
        # Initialize field values and tags
        field_values = {}
        field_tags = {}
        
        # Map template field names to widget field names
        field_mappings = {
            "style": "style",
            "setting": "setting", 
            "weather": "weather",
            "datetime": "datetime",
            "subjects": "subjects",
            "pose": "pose",
            "camera": "camera",
            "framing": "framing",
            "grading": "grading",
            "details": "details",
            "llm_instructions": "llm_instructions"
        }
        
        # Handle tag-based format (v2.0)
        if "format_version" in template_data and template_data["format_version"] == "2.0":
            if self.debug_enabled:
                info("Processing v2.0 tag-based format", LogArea.LOAD)
            
            for template_field, widget_field in field_mappings.items():
                tag_key = f"{template_field}_tags"
                if tag_key in template_data:
                    if self.debug_enabled:
                        debug(f"Processing {template_field} tags: {len(template_data[tag_key])} tags", LogArea.LOAD)
                    
                    # Convert tag data to Tag objects
                    tags = []
                    for tag_data in template_data[tag_key]:
                        try:
                            tag = Tag.from_dict(tag_data)
                            tags.append(tag)
                        except Exception as e:
                            if self.debug_enabled:
                                error(f"Failed to convert tag data {tag_data}: {str(e)}", LogArea.ERROR)
                            # Skip this tag and continue
                            continue
                    
                    field_tags[widget_field] = tags
                    
                    # Also set field values from tags
                    field_values[widget_field] = ", ".join([tag.text for tag in tags])
        
        # Handle legacy format (v1.0)
        else:
            if self.debug_enabled:
                info("Processing v1.0 legacy format", LogArea.LOAD)
            
            for template_field, widget_field in field_mappings.items():
                if template_field in template_data:
                    value = template_data[template_field]
                    field_values[widget_field] = value
                    
                    # Convert simple text to user text tags
                    if value.strip():
                        tags = [Tag(value.strip(), TagType.USER_TEXT)]
                        field_tags[widget_field] = tags
        
        # Get metadata
        seed = template_data.get("seed", 0)
        filters = template_data.get("filters", template_data.get("families", []))
        llm_model = template_data.get("llm", template_data.get("llm_model", ""))
        target_model = template_data.get("model", "seedream")
        
        if self.debug_enabled:
            info(f"Template metadata - seed: {seed}, filters: {filters}, llm_model: {llm_model}", LogArea.LOAD)
        
        # Create PromptState
        prompt_state = PromptState(
            field_values=field_values,
            field_tags=field_tags,
            seed=seed,
            filters=filters,
            llm_model=llm_model,
            target_model=target_model,
            summary_text="",
            final_prompt=""
        )
        
        if self.debug_enabled:
            info(f"Created PromptState with {len(field_values)} fields and {len(field_tags)} tag sets", LogArea.LOAD)
        
        return prompt_state
    
    def _load_and_check_tags(self, tag_data_list, field_name: str):
        """Load tags from template data and check for missing categories/subcategories."""
        from .tag_widgets_qt import Tag, TagType
        
        if self.debug_enabled:
            debug(f"Loading and checking tags for field '{field_name}' with {len(tag_data_list)} tags", LogArea.LOAD)
        
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
        
        if self.debug_enabled:
            debug(f"Using validation field name: '{validation_field_name}'", LogArea.LOAD)
        
        tags = []
        for i, tag_data in enumerate(tag_data_list):
            try:
                tag = Tag.from_dict(tag_data)
                
                # Check if this tag is missing (for category/subcategory tags)
                if tag.tag_type in [TagType.CATEGORY, TagType.SUBCATEGORY]:
                    if tag.check_if_missing(validation_field_name):
                        tag.is_missing = True
                        if self.debug_enabled:
                            debug(f"Tag {i+1} '{tag.text}' is missing for field '{validation_field_name}'", LogArea.LOAD)
                
                tags.append(tag)
                
            except Exception as e:
                if self.debug_enabled:
                    error(f"Failed to load tag {i+1} data {tag_data}: {str(e)}", LogArea.ERROR)
                # Skip this tag and continue
                continue
        
        if self.debug_enabled:
            debug(f"Successfully loaded {len(tags)} tags for field '{field_name}'", LogArea.LOAD)
        
        return tags
    
    def _generate_prompt(self):
        """Generate the final prompt using the LLM."""
        # Add verbose debug logging for batch processing
        if self.debug_enabled:
            debug(r"_generate_prompt() called", LogArea.BATCH)
            debug(r"batch_checkbox exists: {hasattr(self, 'batch_checkbox')}", LogArea.BATCH)
            if hasattr(self, 'batch_checkbox'):
                debug(r"batch_checkbox checked: {self.batch_checkbox.isChecked()}", LogArea.BATCH)
                debug(r"batch_checkbox object: {self.batch_checkbox}", LogArea.BATCH)
                debug(r"batch_checkbox state: {self.batch_checkbox.checkState()}", LogArea.BATCH)
                debug(r"batch_size_input value: {self.batch_size_input.value() if hasattr(self, 'batch_size_input') else 'N/A'}", LogArea.BATCH)
                debug(r"seed_mode_combo value: {self.seed_mode_combo.currentText() if hasattr(self, 'seed_mode_combo') else 'N/A'}", LogArea.BATCH)
        
        # Log process state before generation
        info("=== Before Prompt Generation ===", LogArea.OLLAMA)
        self._get_ollama_process_info()
        
        # Unified approach: always call _generate_batch_prompts()
        # Single submission is treated as batch of 1 with "fixed" seed mode
        if self.debug_enabled:
            debug(r"Calling _generate_batch_prompts() (unified approach)", LogArea.BATCH)
        self._generate_batch_prompts()
        
        # Log process state after generation
        info("=== After Prompt Generation ===", LogArea.OLLAMA)
        self._get_ollama_process_info()

    def _generate_batch_prompts(self):
        """Generate multiple prompts in batch using different seeds - unified approach for single and batch."""
        if self.debug_enabled:
            debug(r"_generate_batch_prompts() called", LogArea.BATCH)
        
        # Initialize variables outside try block to avoid UnboundLocalError
        llm_model = None  # No default fallback - let the widget handle it
        model = "seedream"  # Default model
        # Get first available filter as fallback 
        first_filter = list(self.filter_actions.keys())[0] if self.filter_actions else None
        content_rating = first_filter if first_filter else "PG"  # Ultimate fallback
        
        # INFINITE LOOP PROTECTION: Set processing flag (NO navigation)
        self._generating_prompt = True
        
        if self.debug_enabled:
            debug(r"Staying on current position during generation", LogArea.BATCH)
        
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
                    debug(r"Batch mode - size: {batch_size}, mode: {seed_mode}", LogArea.BATCH)
            else:
                # Single submission treated as batch of 1 with "fixed" seed mode
                batch_size = 1
                seed_mode = "fixed"  # Always use current seed unchanged for single submission
                if self.debug_enabled:
                    debug(r"Single mode (batch of 1) - size: {batch_size}, mode: {seed_mode}", LogArea.BATCH)
            
            base_seed = self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0
            
            if self.debug_enabled:
                debug(r"Batch parameters - size: {batch_size}, mode: {seed_mode}, base_seed: {base_seed}", LogArea.BATCH)
            
            # Validate that LLM instructions are selected
            llm_instructions = self.llm_instructions_widget.get_llm_instruction_content() if hasattr(self, 'llm_instructions_widget') else ""
            if not llm_instructions.strip():
                QMessageBox.warning(self, "LLM Instructions Required", 
                    "Please select an LLM instruction from the 'LLM Instructions' field before generating batch prompts.\n\n"
                    "This ensures the LLM knows how to process your prompt data correctly.")
                self._show_error_message("LLM instructions required")
                return
            
            # Get LLM model and filters
            llm_model = self.llm_widget.get_value() if hasattr(self, 'llm_widget') else None
            selected_filters = self._get_selected_filters()
            content_rating = selected_filters[0] if selected_filters else first_filter
            
            if self.debug_enabled:
                debug(r"Using LLM model: {llm_model}", LogArea.BATCH)
                debug(r"Using content rating: {content_rating}", LogArea.BATCH)
                debug(r"Starting batch generation loop for {batch_size} prompts", LogArea.BATCH)
                debug(r"Batch mode enabled - using concurrent processing with up to 3 workers", LogArea.BATCH)
            
            # Validate LLM model is available
            if not llm_model:
                QMessageBox.warning(self, "LLM Model Required", 
                    "Please select an LLM model from the 'LLM Model' field before generating prompts.\n\n"
                    "This is required for AI-powered prompt refinement.")
                self._show_error_message("LLM model required")
                return
            
            # Start progress tracking for batch
            self._start_progress_tracking(llm_model, "seedream")
            
            # Record start time
            start_time = datetime.now()
            
            # Generate batch prompts with concurrent requests for better performance
            import concurrent.futures
            import threading
            
            # Create a thread pool for concurrent API calls
            max_workers = min(batch_size, 3)  # Limit concurrent requests to prevent overwhelming Ollama
            if self.debug_enabled:
                debug(r"Using concurrent processing with {max_workers} workers", LogArea.BATCH)
            
            def generate_single_prompt(iteration_data):
                """Generate a single prompt for concurrent processing."""
                i, current_seed, prompt_data = iteration_data
                
                if self.debug_enabled:
                    debug(r"Concurrent iteration {i+1} - calling prompt engine.generate_prompt() with model: {llm_model}", LogArea.BATCH)
                
                try:
                    # Generate prompt using the engine - pass the LLM model explicitly
                    final_prompt = self._get_prompt_engine().generate_prompt(model, prompt_data, content_rating, self.debug_enabled, llm_model)
                    
                    if self.debug_enabled:
                        debug(r"Concurrent iteration {i+1} - received final prompt (length: {len(final_prompt)})", LogArea.BATCH)
                    
                    return i, final_prompt, current_seed, None
                except Exception as e:
                    if self.debug_enabled:
                        debug(r"Concurrent iteration {i+1} - error: {str(e)}", LogArea.BATCH)
                    return i, None, current_seed, str(e)
            
            # Prepare all prompt data for concurrent processing
            iteration_data_list = []
            for i in range(batch_size):
                if self.debug_enabled:
                    debug(r"Starting iteration {i+1}/{batch_size}", LogArea.BATCH)
                
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
                    debug(r"Iteration {i+1} - calculated seed: {current_seed}", LogArea.BATCH)
                
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
                
                # Add to iteration data list for concurrent processing
                iteration_data_list.append((i, current_seed, prompt_data))
            
            # Process all prompts concurrently
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_iteration = {executor.submit(generate_single_prompt, data): data[0] for data in iteration_data_list}
                
                # Collect results as they complete
                completed_count = 0
                for future in concurrent.futures.as_completed(future_to_iteration):
                    iteration_num = future_to_iteration[future]
                    try:
                        i, final_prompt, current_seed, error = future.result()
                        results.append((i, final_prompt, current_seed, error))
                        
                        completed_count += 1
                        progress = completed_count / batch_size * 100
                        self.status_label.setText(f"Batch progress: {progress:.0f}% ({completed_count}/{batch_size})")
                        self._show_status_message(f"Generated {completed_count}/{batch_size} prompts...")
                        
                        if error:
                            if self.debug_enabled:
                                debug(r"Iteration {i+1} - failed with error: {error}", LogArea.BATCH)
                        else:
                            if self.debug_enabled:
                                debug(r"Iteration {i+1} - final prompt: '{final_prompt[:200]}{'...' if len(final_prompt) > 200 else ''}'", LogArea.BATCH)
                            
                            # Save to history with final prompt (each gets individual history entry)
                            self._save_to_history(final_prompt, "", current_seed)
                            
                    except Exception as e:
                        if self.debug_enabled:
                            debug(r"Iteration {iteration_num+1} - unexpected error: {str(e)}", LogArea.BATCH)
                        results.append((iteration_num, None, None, str(e)))
            
            # Sort results by iteration number to maintain order
            results.sort(key=lambda x: x[0])
            
            # Check for any errors
            errors = [r for r in results if r[3] is not None]
            if errors:
                error_messages = [f"Iteration {r[0]+1}: {r[3]}" for r in errors]
                error_summary = "; ".join(error_messages)
                if self.debug_enabled:
                    debug(r"Batch completed with errors: {error_summary}", LogArea.BATCH)
            
            # Calculate total generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
            if self.debug_enabled:
                debug(r"Generation completed - {batch_size} prompts in {generation_time:.2f}s", LogArea.BATCH)
            
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
                self._show_status_message(f"Batch generation completed: {batch_size} prompts in {generation_time:.2f}s (concurrent processing)")
            
        except Exception as e:
            # Stop progress tracking on error
            self._stop_progress_tracking()
            
            # INFINITE LOOP PROTECTION: Clear processing flag on error
            self._generating_prompt = False
            self._just_finished_generation = False
            
            if self.debug_enabled:
                debug(r"Error in generation: {str(e)}", LogArea.BATCH)
            
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
            # Skip during template loading to avoid cascades
            if hasattr(self, '_loading_template') and self._loading_template:
                if self.debug_enabled:
                    debug(r"Skipping _refresh_existing_tags during template loading", LogArea.REFRESH)
                return
            debug(r"Starting _refresh_existing_tags()", LogArea.REFRESH)
            selected_filters = self._get_selected_filters()
            debug(r"Current filters: {selected_filters}", LogArea.REFRESH)
            
            # Get all tag field widgets
            tag_widgets = [
                self.style_widget, self.setting_widget, self.weather_widget,
                self.datetime_widget, self.subjects_widget, self.pose_widget,
                self.camera_widget, self.framing_widget, self.grading_widget,
                self.details_widget
            ]
            
            debug(r"Found {len(tag_widgets)} tag widgets", LogArea.REFRESH)
            
            refresh_count = 0
            for i, widget in enumerate(tag_widgets):
                if widget is None:
                    debug(r"Widget {i} is None", LogArea.REFRESH)
                    continue
                debug(r"Checking widget {i} - {type(widget).__name__} - has refresh_tags: {hasattr(widget, 'refresh_tags')}", LogArea.REFRESH)
                if hasattr(widget, 'refresh_tags'):
                    debug(r"Refreshing widget {i} - {type(widget).__name__}", LogArea.REFRESH)
                    widget.refresh_tags()
                    refresh_count += 1
                else:
                    debug(r"Widget {i} - {type(widget).__name__} does NOT have refresh_tags method", LogArea.REFRESH)
            
            debug(r"Refreshed {refresh_count} tag widgets", LogArea.REFRESH)
                    
        except Exception as e:
            import traceback
            error(r"refreshing existing tags: {e}", LogArea.ERROR)
            debug(r"Exception traceback:", LogArea.REFRESH)
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
                    error(r"refreshing snippet popup: {e}", LogArea.ERROR)
            elif hasattr(widget, 'refresh_theme') and callable(widget.refresh_theme):
                try:
                    widget.refresh_theme()
                except Exception as e:
                    error(r"refreshing popup theme: {e}", LogArea.ERROR)
    
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
                warning(r"No menubar found", LogArea.GENERAL)
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
                    error(r"adding filter action {filter_name}: {e}", LogArea.ERROR)
            
            # Add the new menu to the menubar at the original position
            if filters_index >= 0:
                # Insert at the original position
                menubar.insertMenu(menubar.actions()[filters_index], filters_menu)
            else:
                # Fallback: add to the end
                menubar.addMenu(filters_menu)
                    
        except Exception as e:
            error(r"recreating filter menus: {e}", LogArea.ERROR)
    
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
                warning(r"No menubar found", LogArea.GENERAL)
                return
                
            filters_menu = None
            for action in menubar.actions():
                if action.text() == "Filters":
                    filters_menu = action.menu()
                    break
            
            if not filters_menu:
                warning(r"Filters menu not found", LogArea.GENERAL)
                return
                
            # Check if menu is still valid
            if not filters_menu.isWidgetType():
                warning(r"Filters menu is not a valid widget", LogArea.GENERAL)
                return
            
            # Clear existing filter actions
            try:
                filters_menu.clear()
                self.filter_actions.clear()
            except Exception as e:
                error(r"clearing filter menu: {e}", LogArea.ERROR)
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
                    error(r"adding filter action {filter_name}: {e}", LogArea.ERROR)
                    
        except Exception as e:
            error(r"refreshing filter menus: {e}", LogArea.ERROR)
    
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
        """Live preview disabled; maintain cache and navigation only."""
        if not hasattr(self, 'preview_panel'):
            return
        # Handle history edits: keep smart jump/cache behavior, skip text generation
        # Skip smart jump logic if this is a forced update or if we're in the middle of state restoration
        if self.debug_enabled:
            debug(r"_update_preview called with force_update={force_update}, _restoring_state={getattr(self, '_restoring_state', False)}, _intentionally_navigating={getattr(self, '_intentionally_navigating', False)}", LogArea.NAVIGATION)
        
        if not force_update and not (hasattr(self, '_restoring_state') and self._restoring_state) and not (hasattr(self, '_intentionally_navigating') and self._intentionally_navigating):
            current_pos, total_count = self.history_manager.get_navigation_info()
            if self.debug_enabled:
                info(r"DEBUG NAV: _update_preview at position {current_pos}/{total_count}", LogArea.GENERAL)
                # Add stack trace to see what's calling _update_preview
                import traceback
                stack_trace = traceback.format_stack()
                if len(stack_trace) > 2:
                    caller = stack_trace[-3].strip()  # Get the caller of the caller
                    info(r"DEBUG NAV: _update_preview called from: {caller}", LogArea.GENERAL)
            
            if current_pos > 0:
                if self.debug_enabled:
                    debug(r"User modified fields on history position {current_pos}/{total_count} - caching as new 0/X", LogArea.NAVIGATION)
                self._restoring_state = True
                try:
                    self._cache_current_state()
                    self.history_manager.jump_to_position(0)
                    self._restore_cached_current_state()
                    self._update_history_navigation()
                    if self.debug_enabled:
                        info(r"DEBUG NAV: Completed smart jump to current state", LogArea.NAVIGATION)
                finally:
                    self._restoring_state = False
                return
            elif current_pos == 0:
                if self.debug_enabled:
                    info(r"DEBUG NAV: User modified fields on 0/X - updating cache", LogArea.GENERAL)
                self._cache_current_state()
        
        # Update summary text with raw prompt preview (non-realized)
        try:
            prompt_data = self._get_current_prompt_data()
            raw_preview = self._get_prompt_engine().get_prompt_preview(prompt_data)
            self.preview_panel.set_summary_text(raw_preview)
        except Exception as e:
            debug(f"Failed to update summary preview: {e}", LogArea.GENERAL)
        
        # Do not generate or update final prompt text here
        if self.debug_enabled:
            debug(r"_update_preview updated summary, skipped final prompt generation", LogArea.NAVIGATION)
    
    def _update_llm_status_lazy(self):
        """Lazy update LLM status to avoid blocking startup."""
        # Schedule LLM status update for after window is shown with a longer delay
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self._update_llm_status)  # Increased delay to 2 seconds
    
    def _update_llm_status(self):
        """Update LLM status (now called lazily after startup)."""
        llm_start = time.time()
        # This will be called after the window is shown
        if hasattr(self, 'llm_widget'):
            # Trigger LLM connection check in background
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self.llm_widget._check_ollama_connection)
        
        llm_time = time.time() - llm_start
        if self.debug_enabled:
            info(f"STARTUP: _update_llm_status took {llm_time:.3f}s", LogArea.GENERAL)
    
    def _check_ui_responsiveness(self):
        """Check when UI becomes responsive after all initialization."""
        if hasattr(self, '_startup_start_time'):
            total_time = time.time() - self._startup_start_time
            if self.debug_enabled:
                info(f"STARTUP: UI responsiveness check at {total_time:.3f}s", LogArea.GENERAL)
                info(f"STARTUP: Window is now responsive and usable", LogArea.GENERAL)
    
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
        
        # Update preview (debounced)
        self._schedule_preview_update()
    

    
    def _on_llm_changed(self, llm_name):
        """Handle LLM selection changes."""
        if (hasattr(self, '_restoring_state') and self._restoring_state) or (hasattr(self, '_loading_template') and self._loading_template):
            return
        # Update preview panel LLM info (if preview panel exists)
        if hasattr(self, 'preview_panel'):
            self.preview_panel.update_llm_info(llm_name)
        
        # Update preview (debounced)
        self._schedule_preview_update()
    
    def _get_selected_filters(self):
        """Get list of currently selected filters."""
        selected = []
        for filter_name, action in self.filter_actions.items():
            if action.isChecked():
                selected.append(filter_name)
        return selected  # Return empty list if none selected - no default fallback
    
    def _set_selected_filters(self, filters):
        """Set the selected filters."""
        # Block QAction signals while we change checks
        for _, action in self.filter_actions.items():
            if hasattr(action, 'blockSignals'):
                action.blockSignals(True)
        try:
            # Reset all filters first
            for filter_name, action in self.filter_actions.items():
                action.setChecked(False)
            # Set filters from list
            for filter_name in filters:
                if filter_name in self.filter_actions:
                    self.filter_actions[filter_name].setChecked(True)
        finally:
            for _, action in self.filter_actions.items():
                if hasattr(action, 'blockSignals'):
                    action.blockSignals(False)
    
    def _on_seed_changed(self):
        """Handle seed value changes."""
        if (hasattr(self, '_restoring_state') and self._restoring_state) or (hasattr(self, '_loading_template') and self._loading_template):
            return
        # Update preview with new randomization
        self._schedule_preview_update()
        
        # Save seed in preferences if needed
        self._save_preferences()
    
    def _on_filter_changed(self, filter_name, checked):
        """Handle filter selection changes."""
        if (hasattr(self, '_restoring_state') and self._restoring_state) or (hasattr(self, '_loading_template') and self._loading_template):
            return
        # Log the filter change
        if self.logger:
            self.logger.log_gui_action(f"Filter changed", f"{filter_name}: {'checked' if checked else 'unchecked'}")
        
        debug(r"Filter {filter_name} {'checked' if checked else 'unchecked'}", LogArea.FILTERS)
        selected_filters = self._get_selected_filters()
        debug(r"Current selected filters: {selected_filters}", LogArea.FILTERS)
        
        # Update snippet dropdowns with new filter selection
        self._update_snippet_filters()
        
        # Refresh all open snippet popups
        self._refresh_open_snippet_popups()
        
        # Refresh existing tags to check if they're still missing with new filter selection
        debug(r"Calling _refresh_existing_tags()", LogArea.FILTERS)
        self._refresh_existing_tags()
        
        # Update preview (debounced)
        self._schedule_preview_update()
        
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
        callbacks_start = time.time()
        
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
        
        callbacks_time = time.time() - callbacks_start
        if self.debug_enabled:
            info(f"STARTUP: _setup_callbacks took {callbacks_time:.3f}s", LogArea.GENERAL)
    
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
                
                # Load Ollama preferences with proper initialization
                if hasattr(self, 'auto_start_ollama_action'):
                    auto_start_value = prefs.get('auto_start_ollama', False)
                    self.auto_start_ollama_action.setChecked(auto_start_value)
                    debug(f"Loaded auto_start_ollama preference: {auto_start_value}", LogArea.GENERAL)
                
                if hasattr(self, 'kill_ollama_on_exit_action'):
                    kill_on_exit_value = prefs.get('kill_ollama_on_exit', True)
                    self.kill_ollama_on_exit_action.setChecked(kill_on_exit_value)
                    debug(f"Loaded kill_ollama_on_exit preference: {kill_on_exit_value}", LogArea.GENERAL)
            else:
                # First time running - set default values and save them
                debug("No preferences file found, setting default values", LogArea.GENERAL)
                if hasattr(self, 'auto_start_ollama_action'):
                    self.auto_start_ollama_action.setChecked(False)
                if hasattr(self, 'kill_ollama_on_exit_action'):
                    self.kill_ollama_on_exit_action.setChecked(True)
                # Save default preferences
                self._save_preferences()
                    
        except Exception as e:
            warning(r"Could not load preferences: {e}", LogArea.GENERAL)
    
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
            
            # Add Ollama preferences if available
            if hasattr(self, 'auto_start_ollama_action'):
                prefs['auto_start_ollama'] = self.auto_start_ollama_action.isChecked()
            if hasattr(self, 'kill_ollama_on_exit_action'):
                prefs['kill_ollama_on_exit'] = self.kill_ollama_on_exit_action.isChecked()
            
            prefs_file = self.user_data_dir / "preferences.json"
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            warning(r"Could not save preferences: {e}", LogArea.GENERAL)

    def _toggle_auto_start_ollama(self):
        """Toggle auto-start Ollama on startup preference."""
        if hasattr(self, 'auto_start_ollama_action'):
            debug(f"Auto-start Ollama preference changed to: {self.auto_start_ollama_action.isChecked()}", LogArea.GENERAL)
            self._save_preferences()
    
    def _toggle_kill_ollama_on_exit(self):
        """Toggle kill Ollama on exit preference."""
        if hasattr(self, 'kill_ollama_on_exit_action'):
            debug(f"Kill Ollama on exit preference changed to: {self.kill_ollama_on_exit_action.isChecked()}", LogArea.GENERAL)
            self._save_preferences()
    
    def _auto_start_ollama(self):
        """Auto-start Ollama on application startup if preference is set."""
        ollama_start = time.time()
        try:
            # Check if Ollama is already running
            if self._is_ollama_running():
                info(r"DEBUG OLLAMA: Ollama is already running, skipping auto-start", LogArea.GENERAL)
                ollama_time = time.time() - ollama_start
                if self.debug_enabled:
                    info(f"STARTUP: Ollama auto-start (already running) took {ollama_time:.3f}s", LogArea.GENERAL)
                return
            
            info(r"DEBUG OLLAMA: Auto-starting Ollama...", LogArea.GENERAL)
            
            # Start Ollama in background
            def start_ollama():
                try:
                    with self._ollama_process_lock:
                        # Double-check that we don't already have a process
                        if self._ollama_process is not None and self._ollama_process.returncode is None:
                            info(f"DEBUG OLLAMA: Another thread already started Ollama (PID: {self._ollama_process.pid})", LogArea.GENERAL)
                            return
                        
                        # Use subprocess.Popen to start Ollama in background
                        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        info(f"DEBUG OLLAMA: Starting Ollama with creationflags={creation_flags}", LogArea.GENERAL)
                        process = subprocess.Popen(
                            ['ollama', 'serve'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=creation_flags
                        )
                        self._ollama_process = process
                        info(f"DEBUG OLLAMA: Ollama started with PID: {process.pid}", LogArea.GENERAL)
                except Exception as e:
                    error(r"DEBUG OLLAMA: Failed to start Ollama: {e}", LogArea.GENERAL)
            
            # Start Ollama in a separate thread to avoid blocking
            ollama_thread = threading.Thread(target=start_ollama, daemon=True)
            ollama_thread.start()
            
            # Return immediately - don't wait for Ollama to start
            ollama_time = time.time() - ollama_start
            if self.debug_enabled:
                info(f"STARTUP: Ollama auto-start initiated in {ollama_time:.3f}s (non-blocking)", LogArea.GENERAL)
                
        except Exception as e:
            error(r"DEBUG OLLAMA: Error in auto-start: {e}", LogArea.GENERAL)
            ollama_time = time.time() - ollama_start
            if self.debug_enabled:
                info(f"STARTUP: Ollama auto-start (with error) took {ollama_time:.3f}s", LogArea.GENERAL)
    
    def _start_ollama(self):
        """Start Ollama server in background."""
        try:
            # Check if Ollama is already running
            if self._is_ollama_running():
                QMessageBox.information(self, "Ollama", "Ollama is already running.")
                return
            
            # Start Ollama in background
            def start_ollama_thread():
                try:
                    with self._ollama_process_lock:
                        # Double-check that we don't already have a process
                        if self._ollama_process is not None and self._ollama_process.returncode is None:
                            info(f"DEBUG OLLAMA: Another thread already started Ollama (PID: {self._ollama_process.pid})", LogArea.GENERAL)
                            QTimer.singleShot(0, lambda: QMessageBox.information(self, "Ollama", "Ollama is already running."))
                            return
                        
                        # Hide console window on Windows
                        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        info(f"STARTUP: Starting Ollama with creationflags={creation_flags}", LogArea.GENERAL)
                        process = subprocess.Popen(["ollama", "serve"], 
                                                 stdout=subprocess.DEVNULL, 
                                                 stderr=subprocess.DEVNULL,
                                                 creationflags=creation_flags)
                        self._ollama_process = process
                        info(f"STARTUP: Ollama process started with PID={process.pid}", LogArea.GENERAL)
                        time.sleep(2)  # Wait for startup
                        
                        # Update UI on main thread
                        QTimer.singleShot(0, self._on_ollama_started)
                except Exception as e:
                    QTimer.singleShot(0, lambda: self._on_ollama_error(f"Failed to start Ollama: {str(e)}"))
            
            # Start in background thread
            thread = threading.Thread(target=start_ollama_thread, daemon=True)
            thread.start()
            
            # Show status
            self.statusBar().showMessage("Starting Ollama...")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start Ollama: {str(e)}")

    def _kill_ollama(self):
        """Kill Ollama server."""
        try:
            # Kill Ollama processes
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                          capture_output=True, text=True)
            
            # Clear our tracked process reference
            with self._ollama_process_lock:
                if self._ollama_process is not None:
                    info(f"DEBUG OLLAMA: Cleared tracked Ollama process reference (PID: {self._ollama_process.pid})", LogArea.GENERAL)
                    self._ollama_process = None
            
            # Update UI
            self._on_ollama_killed()
            self.statusBar().showMessage("Ollama killed.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to kill Ollama: {str(e)}")

    def _refresh_llm_models(self):
        """Refresh the LLM model list."""
        if hasattr(self, 'llm_widget'):
            debug(r"User requested model refresh", LogArea.OLLAMA)
            self.llm_widget.refresh_connection()
            self.statusBar().showMessage("Models refreshed.")

    def _is_ollama_running(self):
        """Check if Ollama is running."""
        try:
            # First check if we have a tracked process that's still alive
            with self._ollama_process_lock:
                if self._ollama_process is not None:
                    # Check if our tracked process is still running
                    # Use returncode instead of poll() to avoid consuming the exit status
                    if self._ollama_process.returncode is None:
                        info(f"DEBUG OLLAMA: Found tracked Ollama process (PID: {self._ollama_process.pid})", LogArea.GENERAL)
                        return True
                    else:
                        # Process has terminated, clear our reference
                        info(f"DEBUG OLLAMA: Tracked Ollama process has terminated (PID: {self._ollama_process.pid})", LogArea.GENERAL)
                        self._ollama_process = None
            
            # Fallback: check for any ollama.exe processes
            result = subprocess.run("tasklist //FI \"IMAGENAME eq ollama.exe\"", 
                                  capture_output=True, text=True, shell=True)
            if "ollama.exe" in result.stdout:
                info(f"DEBUG OLLAMA: Found untracked Ollama process via tasklist", LogArea.GENERAL)
                return True
            
            return False
        except Exception as e:
            error(f"DEBUG OLLAMA: Error checking if Ollama is running: {e}", LogArea.GENERAL)
            return False

    def _on_ollama_started(self):
        """Called when Ollama starts successfully."""
        self.statusBar().showMessage("Ollama started successfully.")
        
        # Refresh LLM models with a slight delay to ensure Ollama is fully ready
        if hasattr(self, 'llm_widget'):
            debug(r"Ollama started, refreshing models...", LogArea.OLLAMA)
            # Use QTimer to ensure this runs on the main thread and with a slight delay
            QTimer.singleShot(1000, lambda: self._refresh_models_after_ollama_start())
        
        QMessageBox.information(self, "Ollama", "Ollama started successfully!")
    
    def _refresh_models_after_ollama_start(self):
        """Refresh models after Ollama has started."""
        if hasattr(self, 'llm_widget'):
            debug(r"Refreshing models after Ollama start...", LogArea.OLLAMA)
            self.llm_widget.refresh_connection()
            self.statusBar().showMessage("Models refreshed after Ollama start.")

    def _on_ollama_killed(self):
        """Called when Ollama is killed."""
        # Update LLM widget to show disconnected state
        if hasattr(self, 'llm_widget'):
            self.llm_widget._show_error("Ollama not running")

    def _on_ollama_error(self, error_msg):
        """Called when Ollama operation fails."""
        self.statusBar().showMessage("Ollama error.")
        QMessageBox.critical(self, "Ollama Error", error_msg)

    def closeEvent(self, event):
        """Handle window close event."""
        # Unload Ollama model to free up VRAM
        try:
            if hasattr(self, 'llm_widget'):
                current_model = self.llm_widget.get_value()
                debug(r"Unloading model '{current_model}' on application close", LogArea.OLLAMA)
                
                # Get prompt engine and unload model
                prompt_engine = self._get_prompt_engine()
                if prompt_engine:
                    success = prompt_engine.unload_llm_model(current_model)
                    if success:
                        debug(r"Successfully unloaded model '{current_model}'", LogArea.OLLAMA)
                    else:
                        debug(r"Failed to unload model '{current_model}'", LogArea.OLLAMA)
                else:
                    info(r"DEBUG OLLAMA: No prompt engine available for model unloading", LogArea.GENERAL)
        except Exception as e:
            debug(r"Error during model unloading: {str(e)}", LogArea.OLLAMA)
        
        # Kill Ollama on exit if user preference is set
        if hasattr(self, 'kill_ollama_on_exit_action') and self.kill_ollama_on_exit_action.isChecked():
            try:
                self._kill_ollama()
            except Exception as e:
                debug(r"Error killing Ollama on exit: {str(e)}", LogArea.OLLAMA)
        
        # Save window size to preferences
        theme_manager.set_preference("window_width", self.width())
        theme_manager.set_preference("window_height", self.height())
        
        # Save preferences
        theme_manager.save_preferences(theme_manager.preferences)
        
        event.accept()
    
    def _navigate_history_back(self):
        """Navigate to previous history entry."""
        debug(r"User clicked BACK button", LogArea.NAVIGATION)
        self._intentionally_navigating = True
        try:
            if self.history_manager.navigate_back():
                self._update_history_navigation()
        finally:
            # Clear flag immediately (no timer needed)
            self._intentionally_navigating = False
    
    def _navigate_history_forward(self):
        """Navigate to next history entry."""
        debug(r"User clicked FORWARD button", LogArea.NAVIGATION)
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
        debug(r"User manually entered position {position}", LogArea.NAVIGATION)
        self._intentionally_navigating = True
        try:
            if self.history_manager.jump_to_position(position):
                self._update_history_navigation()
        finally:
            # Clear flag after a delay to cover any delayed preview updates
            # This prevents the bug where navigating to history state 1/1 would reset to 0/1
            # because _restore_from_history_entry() schedules a delayed _update_preview() call
            # that would execute after _intentionally_navigating was already cleared
            from PySide6.QtCore import QTimer
            QTimer.singleShot(200, lambda: setattr(self, '_intentionally_navigating', False))
    
    def _should_jump_to_current_state(self) -> bool:
        """Check if we should jump back to current state (0/X) when field changes."""
        # Don't jump if we're intentionally navigating to history entries
        if hasattr(self, '_intentionally_navigating') and self._intentionally_navigating:
            if self.debug_enabled:
                info(r"DEBUG NAV: Skipping jump to current - intentionally navigating", LogArea.GENERAL)
            return False
        
        # Only jump if we're in history mode (not on 0/X)
        current_pos, total_count = self.history_manager.get_navigation_info()
        should_jump = current_pos > 0  # 0 = current state, 1+ = history entries
        
        if self.debug_enabled:
            debug(r"_should_jump_to_current_state: current_pos={current_pos}, total_count={total_count}, should_jump={should_jump}", LogArea.NAVIGATION)
        
        return should_jump
    
    def _block_all_field_signals(self):
        """Block signals from all field widgets to prevent cascading updates."""
        self._blocked_widgets = []
        for field_key, widget in self.field_widgets.items():
            if hasattr(widget, 'blockSignals'):
                widget.blockSignals(True)
                self._blocked_widgets.append(widget)
        if self.debug_enabled:
            debug(r"Blocked signals for {len(self._blocked_widgets)} widgets", LogArea.NAVIGATION)
    
    def _unblock_all_field_signals(self):
        """Unblock signals from all field widgets."""
        for widget in self._blocked_widgets:
            if hasattr(widget, 'blockSignals'):
                widget.blockSignals(False)
        self._blocked_widgets = []
        if self.debug_enabled:
            info(r"DEBUG NAV: Unblocked all field widget signals", LogArea.GENERAL)
    
    def _cache_current_state(self):
        """Cache the current field state as 0/X state."""
        if self.debug_enabled:
            info(r"DEBUG NAV: Caching current state", LogArea.GENERAL)
            # Add more detailed logging about what we're caching
            current_pos, total_count = self.history_manager.get_navigation_info()
            info(r"DEBUG NAV: Caching at position {current_pos}/{total_count}", LogArea.GENERAL)
        
        # Capture current state as PromptState
        self._cached_current_state = self.capture_current_state()
        
        if self.debug_enabled:
            debug(r"Cached PromptState with {len(self._cached_current_state.field_values)} fields", LogArea.NAVIGATION)
            # Log some key field values to verify what's being cached
            for field_name, value in list(self._cached_current_state.field_values.items())[:3]:  # First 3 fields
                info(r"DEBUG NAV: Cached field '{field_name}' = '{value[:50]}{'...' if len(value) > 50 else ''}'", LogArea.GENERAL)
    
    def _restore_cached_current_state(self):
        """Restore the cached current state (0/X position)."""
        if not self._cached_current_state:
            if self.debug_enabled:
                info(r"DEBUG NAV: No cached current state to restore", LogArea.GENERAL)
            return
        
        if self.debug_enabled:
            info(r"DEBUG NAV: Restoring cached current state", LogArea.GENERAL)
            # Add more detailed logging about what we're restoring
            current_pos, total_count = self.history_manager.get_navigation_info()
            info(r"DEBUG NAV: Restoring at position {current_pos}/{total_count}", LogArea.GENERAL)
            # Log some key field values to verify what's being restored
            for field_name, value in list(self._cached_current_state.field_values.items())[:3]:  # First 3 fields
                info(r"DEBUG NAV: Restoring field '{field_name}' = '{value[:50]}{'...' if len(value) > 50 else ''}'", LogArea.GENERAL)
        
        # Use the PromptState restoration method - don't restore final prompt for current state
        self.restore_from_prompt_state(self._cached_current_state, restore_final_prompt=False)
        
        # Ensure placeholder text is shown for current state (0/X)
        if hasattr(self, 'preview_panel'):
            current_pos, total_count = self.history_manager.get_navigation_info()
            self.preview_panel.set_history_state(False, total_count)
            # Explicitly set placeholder text for 0/X state
            self.preview_panel.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
        
        # Ensure placeholder text is shown for current state (0/X)
        if hasattr(self, 'preview_panel'):
            current_pos, total_count = self.history_manager.get_navigation_info()
            self.preview_panel.set_history_state(False, total_count)
            # Explicitly set placeholder text for 0/X state
            self.preview_panel.final_text.setPlainText("Generate a final prompt to see the LLM-refined version here...")
    
    def _jump_to_current_state(self):
        """Jump back to current state (0/X) and load the cached state."""
        # Prevent recursive calls
        if hasattr(self, '_jumping_to_current') and self._jumping_to_current:
            if self.debug_enabled:
                info(r"DEBUG NAV: Already jumping to current state, skipping", LogArea.GENERAL)
            return
        
        # Set flag to prevent recursive calls
        self._jumping_to_current = True
        # Suppress popups briefly during jump/restore
        self._suppress_popups = True
        
        try:
            if self.debug_enabled:
                info(r"DEBUG NAV: Starting jump to current state", LogArea.GENERAL)
            
            # Jump to position 0 (current state) FIRST
            self.history_manager.jump_to_position(0)
            
            # Load the cached current state (don't cache, just restore)
            self._restore_cached_current_state()
            
            # Update navigation to show current state (this will call _show_current_state)
            self._update_history_navigation()
            
            # No tabs anymore
                
            if self.debug_enabled:
                info(r"DEBUG NAV: Completed jump to current state", LogArea.GENERAL)
        finally:
            # Clear flag immediately (no timer needed)
            self._jumping_to_current = False
            from PySide6.QtCore import QTimer
            QTimer.singleShot(300, lambda: setattr(self, '_suppress_popups', False))
    

    
    def _load_preview_into_fields(self):
        """Load the current preview content into the input fields."""
        # Get the current preview text (from the active tab)
        # Single final prompt text now
        preview_text = self.preview_panel.final_text.toPlainText()
        
        debug(r"Preview text from tab {current_tab}:", LogArea.LOAD)
        debug(r"{preview_text}", LogArea.LOAD)
        
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
                    debug(r"Parsed field '{field_name}' = '{value}'", LogArea.LOAD)
        
        debug(r"All parsed fields: {field_values}", LogArea.LOAD)
        
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
                                debug(r"MATCH FOUND for '{individual_value}': is_category={is_category}, category_path={category_path}, snippet_data={snippet_data}", LogArea.LOAD)
                                
                                if is_category:
                                    # Create category tag
                                    if len(category_path) == 1:
                                        tag = Tag(individual_value, TagType.CATEGORY, category_path=category_path)
                                        debug(r"Created CATEGORY tag: {individual_value}", LogArea.LOAD)
                                    else:
                                        tag = Tag(individual_value, TagType.SUBCATEGORY, category_path=category_path)
                                        debug(r"Created SUBCATEGORY tag: {individual_value}", LogArea.LOAD)
                                else:
                                    # Create snippet tag with proper data
                                    if isinstance(snippet_data, dict):
                                        # Handle instruction format with content
                                        snippet_display_name = snippet_data.get("name", individual_value)
                                        content = snippet_data.get("content", "")
                                        tag = Tag(snippet_display_name, TagType.SNIPPET, data=content)
                                        debug(r"Created SNIPPET tag (dict): {snippet_display_name}", LogArea.LOAD)
                                    else:
                                        # Handle simple string snippets
                                        tag = Tag(individual_value, TagType.SNIPPET, data=snippet_data)
                                        debug(r"Created SNIPPET tag (string): {individual_value}", LogArea.LOAD)
                                tags.append(tag)
                            else:
                                # Create user text tag if no snippet found
                                tag = Tag(individual_value, TagType.USER_TEXT)
                                debug(r"NO MATCH - Created USER_TEXT tag: {individual_value}", LogArea.LOAD)
                                tags.append(tag)
                        
                        # Set the tags
                        widget.set_tags(tags)
                    else:
                        widget.set_value(value)
        
        finally:
            # Unblock signals
            for widget in blocked_widgets:
                widget.blockSignals(False)
            
            # Schedule preview update to reflect the loaded values (respect guards)
            self._schedule_preview_update()
    
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
            error(r"finding matching snippet: {e}", LogArea.ERROR)
            return None, None, False
    
    def _restore_from_history_entry(self):
        """Restore fields from current history entry using PromptState."""
        entry = self.history_manager.get_current_entry()
        if entry:
            if self.debug_enabled:
                debug(r"Restoring history entry - seed={entry.seed}, filters={entry.filters}, llm_model={entry.llm_model}", LogArea.NAVIGATION)
                debug(r"History entry field values: {list(entry.field_values.keys())}", LogArea.NAVIGATION)
                debug(r"History entry field tags: {list(entry.field_tags.keys())}", LogArea.NAVIGATION)
                debug(r"History entry final prompt: '{entry.final_prompt[:100] if entry.final_prompt else 'None'}{'...' if entry.final_prompt and len(entry.final_prompt) > 100 else ''}'", LogArea.NAVIGATION)
                # Summary removed
                debug(r"_intentionally_navigating flag is: {self._intentionally_navigating}", LogArea.NAVIGATION)
            
            # Use the new PromptState restoration method - restore final prompt for history states
            self.restore_from_prompt_state(entry, restore_final_prompt=True)
            
            # Force a preview update to ensure summary reflects the restored fields
            # Skip if a template is currently loading
            QTimer.singleShot(
                100,
                lambda: (None if (hasattr(self, '_loading_template') and self._loading_template)
                         else self._update_preview(preserve_tab=True, force_update=True))
            )
            if self.debug_enabled:
                debug(r"Scheduled delayed _update_preview call with force_update=True", LogArea.NAVIGATION)
    
    def _update_history_navigation(self):
        """Update navigation controls state."""
        # PREVENT INFINITE RECURSION: Skip if we're currently restoring state
        if hasattr(self, '_restoring_state') and self._restoring_state:
            if self.debug_enabled:
                debug(r"Skipping navigation update during state restoration", LogArea.NAVIGATION)
            return
        # Skip while preview is updating
        if hasattr(self, '_updating_preview') and self._updating_preview:
            if self.debug_enabled:
                debug(r"Skipping navigation update during preview update", LogArea.NAVIGATION)
            return
        
        if hasattr(self, 'preview_panel'):
            can_go_back = self.history_manager.can_go_back()
            can_go_forward = self.history_manager.can_go_forward()
            current_pos, total_count = self.history_manager.get_navigation_info()
            has_history = self.history_manager.has_history()
            
            debug(r"Navigation update - current_pos={current_pos}, total_count={total_count}, is_current_state={current_pos == 0}", LogArea.NAVIGATION)
            
            # Check if we're in current state (0) or history state (1+)
            is_current_state = current_pos == 0
            
            # POST-GENERATION HANDLING: Only update navigation controls, don't restore state
            if self._just_finished_generation:
                if self.debug_enabled:
                    debug(r"Post-generation update - only updating navigation controls", LogArea.NAVIGATION)
                self.preview_panel.update_navigation_controls(
                    current_pos, total_count, can_go_back, can_go_forward
                )
                return
            
            # Set styling immediately based on state to prevent flashing
            if is_current_state:
                debug(r"Showing CURRENT state (0/{total_count})", LogArea.NAVIGATION)
                # Set current state styling first to prevent flash
                self.preview_panel.set_history_state(False, total_count)
                self._show_current_state()
            else:
                debug(r"Showing HISTORY state ({current_pos}/{total_count})", LogArea.NAVIGATION)
                # Set history state styling first to prevent flash
                self.preview_panel.set_history_state(True, total_count)
                # We're in history state, restore from history entry
                self._restore_from_history_entry()
            
            self.preview_panel.update_navigation_controls(
                current_pos, total_count, can_go_back, can_go_forward
            )
    
    def _show_current_state(self):
        """Show the current state of the fields (not from history)."""
        if self.debug_enabled:
            info(r"DEBUG NAV: _show_current_state called", LogArea.GENERAL)
            current_pos, total_count = self.history_manager.get_navigation_info()
            info(r"DEBUG NAV: _show_current_state at position {current_pos}/{total_count}", LogArea.GENERAL)
            info(r"DEBUG NAV: _cached_current_state exists: {self._cached_current_state is not None}", LogArea.GENERAL)
        
        # If we have a cached current state, restore it first
        if self._cached_current_state:
            if self.debug_enabled:
                info(r"DEBUG NAV: Restoring cached current state in _show_current_state", LogArea.GENERAL)
            self._restore_cached_current_state()
        else:
            if self.debug_enabled:
                info(r"DEBUG NAV: No cached current state available in _show_current_state", LogArea.GENERAL)
        
        # Live preview removed; do not generate or update here
        if self.debug_enabled:
            debug(r"Live preview disabled; awaiting Generate action for Final Prompt", LogArea.NAVIGATION)
    
    def _save_to_history(self, final_prompt: str = "", summary_text: str = "", seed: Optional[int] = None):
        """Save current state to history using PromptState."""
        if self.debug_enabled:
            debug(r"DEBUG NAV: Saving to history", LogArea.NAVIGATION)
        
        # Capture current state as PromptState
        prompt_state = self.capture_current_state()
        
        # Override with provided values if specified
        if final_prompt:
            prompt_state.final_prompt = final_prompt
        # Summary removed
        if seed is not None:
            prompt_state.seed = seed
        
        # Add to history
        self.history_manager.add_entry(prompt_state)
        
        # Update navigation controls - but skip during generation to prevent infinite loops
        if not getattr(self, '_generating_prompt', False):
            self._update_history_navigation()
        elif self.debug_enabled:
            debug(r"Skipping navigation update during generation", LogArea.BATCH)
    
    def _schedule_preview_update(self):
        """Schedule a debounced preview update (Qt best practice to prevent signal cascading)."""
        # PREVENT INFINITE RECURSION: Skip if we're currently restoring state
        if hasattr(self, '_restoring_state') and self._restoring_state:
            if self.debug_enabled:
                debug(r"Skipping preview update during state restoration", LogArea.NAVIGATION)
            return
        
        # Additional protection: Skip if we're in the middle of template loading
        if hasattr(self, '_loading_template') and self._loading_template:
            if self.debug_enabled:
                debug(r"Skipping preview update during template loading", LogArea.NAVIGATION)
            return
        
        # Suppression window after template load
        if hasattr(self, '_suppress_preview_updates') and self._suppress_preview_updates:
            if self.debug_enabled:
                debug(r"Skipping preview update during suppression window", LogArea.NAVIGATION)
            return
        
        # Cycle detection: rate-limit scheduler calls
        now = time.monotonic()
        if now - self._dbg_last_reset_time > 2.0:
            self._dbg_prev_sched_count = 0
            self._dbg_prev_update_count = 0
            self._dbg_last_reset_time = now
        self._dbg_prev_sched_count += 1
        if self._dbg_prev_sched_count > self._dbg_cycle_threshold:
            import traceback
            stack = ''.join(traceback.format_stack(limit=8))
            error(r"Preview scheduler call flood detected; temporarily suppressing updates\n{stack}", LogArea.NAVIGATION)
            self._suppress_preview_updates = True
            QTimer.singleShot(500, lambda: setattr(self, '_suppress_preview_updates', False))
            return

        if hasattr(self, '_preview_update_timer'):
            if self.debug_enabled:
                try:
                    sender_obj = self.sender()
                    sender_name = getattr(sender_obj, 'objectName', lambda: '')() if sender_obj else ''
                    sender_type = type(sender_obj).__name__ if sender_obj else 'None'
                    debug(r"Starting debounced preview timer - sender={sender_type} {sender_name}", LogArea.NAVIGATION)
                except Exception:
                    debug(r"Starting debounced preview timer", LogArea.NAVIGATION)
            self._preview_update_timer.start(100)  # 100ms debounce

    def _save_all_prompts(self):
        """Save all prompts (placeholder for future implementation)."""
        # TODO: Implement save all prompts functionality
        info(r"Save all prompts functionality not yet implemented", LogArea.GENERAL)

    def capture_current_state(self) -> PromptState:
        """Capture the current application state as a PromptState object."""
        if self.debug_enabled:
            info(r"DEBUG NAV: Capturing current state as PromptState", LogArea.GENERAL)
        
        # Collect field values and tags
        field_values = {}
        field_tags = {}
        
        for field_key, widget in self.field_widgets.items():
            if hasattr(widget, 'get_value'):
                field_values[field_key] = widget.get_value()
            elif hasattr(widget, 'toPlainText'):
                field_values[field_key] = widget.toPlainText()
            
            if hasattr(widget, 'get_tags'):
                field_tags[field_key] = widget.get_tags()
        
        # Get current metadata
        seed = self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0
        filters = self._get_selected_filters()
        llm_model = self.llm_widget.get_value() if hasattr(self, 'llm_widget') else ""
        target_model = "seedream"  # Default target model
        
        # Get current generated content
        summary_text = ""
        final_prompt = ""
        if hasattr(self, 'preview_panel'):
            summary_text = ""  # Summary removed
            final_prompt = self.preview_panel.get_final_prompt()
        
        # Create PromptState
        prompt_state = PromptState(
            field_values=field_values,
            field_tags=field_tags,
            seed=seed,
            filters=filters,
            llm_model=llm_model,
            target_model=target_model,
            summary_text=summary_text,
            final_prompt=final_prompt
        )
        
        if self.debug_enabled:
            debug(r"Captured PromptState with {len(field_values)} fields and {len(field_tags)} tag sets", LogArea.NAVIGATION)
        
        return prompt_state
    
    def restore_from_prompt_state(self, prompt_state: PromptState, restore_final_prompt: bool = True):
        """Restore the application state from a PromptState object."""
        if self.debug_enabled:
            info(r"DEBUG NAV: Restoring from PromptState", LogArea.GENERAL)
        
        # Set flag to prevent recursive calls
        self._restoring_state = True
        
        # Temporarily disable widget updates to avoid visible cycling during bulk changes
        try:
            self._updates_were_enabled = self.updatesEnabled()
        except Exception:
            self._updates_were_enabled = True
        self.setUpdatesEnabled(False)
        
        # Block ALL field widget signals during restoration
        self._block_all_field_signals()
        
        try:
            # Restore field values and tags
            for field_key, widget in self.field_widgets.items():
                if field_key in prompt_state.field_values:
                    value = prompt_state.field_values[field_key]
                    if hasattr(widget, 'set_value'):
                        widget.set_value(value)
                    elif hasattr(widget, 'setPlainText'):
                        widget.setPlainText(value)
                
                if field_key in prompt_state.field_tags:
                    tags = prompt_state.field_tags[field_key]
                    if hasattr(widget, 'set_tags'):
                        widget.set_tags(tags)
            
            # Restore metadata
            if hasattr(self, 'seed_widget'):
                self.seed_widget.set_value(prompt_state.seed)
            
            # Restore filters
            self._set_selected_filters(prompt_state.filters)
            
            # Restore LLM model
            if hasattr(self, 'llm_widget'):
                self.llm_widget.set_value(prompt_state.llm_model)
            
            # Restore generated content only if requested
            if restore_final_prompt and hasattr(self, 'preview_panel'):
                if prompt_state.final_prompt:
                    self.preview_panel.set_final_prompt(prompt_state.final_prompt)
            
            if self.debug_enabled:
                debug(r"Restored PromptState with {len(prompt_state.field_values)} fields", LogArea.NAVIGATION)
                
        finally:
            # Unblock signals
            self._unblock_all_field_signals()
            
            # Clear flag immediately (no timer needed)
            self._restoring_state = False
            
            # Re-enable updates
            try:
                self.setUpdatesEnabled(self._updates_were_enabled)
                self.update()
            except Exception:
                pass

    def _get_ollama_process_info(self):
        """Get detailed information about Ollama processes for debugging."""
        info("=== Ollama Process Information ===", LogArea.OLLAMA)
        
        # Check our tracked process
        if self._ollama_process:
            info(f"Tracked process PID: {self._ollama_process.pid}", LogArea.OLLAMA)
            info(f"Tracked process returncode: {self._ollama_process.returncode}", LogArea.OLLAMA)
            info(f"Tracked process still running: {self._ollama_process.returncode is None}", LogArea.OLLAMA)
        else:
            info("No tracked Ollama process", LogArea.OLLAMA)
        
        # Check all ollama.exe processes
        try:
            result = subprocess.run(
                'tasklist //FI "IMAGENAME eq ollama.exe" //FO CSV',
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    info(f"Found {len(lines)-1} ollama.exe processes:", LogArea.OLLAMA)
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            info(f"  {line.strip()}", LogArea.OLLAMA)
                else:
                    info("No ollama.exe processes found via tasklist", LogArea.OLLAMA)
            else:
                info(f"tasklist failed: {result.stderr}", LogArea.OLLAMA)
        except Exception as e:
            info(f"Error checking tasklist: {e}", LogArea.OLLAMA)
        
        # Check parent-child relationships using wmic
        try:
            result = subprocess.run(
                'wmic process where name="ollama.exe" get ProcessId,ParentProcessId,CommandLine /format:csv',
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    info("Ollama process hierarchy:", LogArea.OLLAMA)
                    for line in lines[1:]:  # Skip header
                        if line.strip() and 'ollama.exe' in line:
                            parts = line.split(',')
                            if len(parts) >= 3:
                                pid = parts[1].strip()
                                parent_pid = parts[2].strip()
                                cmdline = parts[3].strip() if len(parts) > 3 else "N/A"
                                info(f"  PID: {pid}, Parent: {parent_pid}, Cmd: {cmdline}", LogArea.OLLAMA)
                else:
                    info("No ollama.exe processes found via wmic", LogArea.OLLAMA)
            else:
                info(f"wmic failed: {result.stderr}", LogArea.OLLAMA)
        except Exception as e:
            info(f"Error checking wmic: {e}", LogArea.OLLAMA)
        
        info("=== End Ollama Process Information ===", LogArea.OLLAMA)

    def _realize_summary(self):
        """Handle realize button click - update summary with realized values using current seed."""
        try:
            # Get current seed
            current_seed = self._get_current_seed()
            
            # Create PromptData object with current seed (realized values)
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
                llm_instructions=""
            )
            
            # Generate the raw prompt preview using the realized values
            raw_preview = self._get_prompt_engine().get_prompt_preview(prompt_data)
            
            # Update the summary text
            self.preview_panel.set_summary_text(raw_preview)
            
            debug(f"PROMPT: Previewed summary with seed {current_seed}", LogArea.PROMPT)
            
        except Exception as e:
            error(f"Failed to preview summary: {e}", LogArea.GENERAL)
            QMessageBox.warning(self, "Error", f"Failed to preview summary: {str(e)}")
    
    def _get_current_prompt_data(self):
        """Get current prompt data from all fields without randomization."""
        return PromptData(
            style=self.style_widget.get_current_text() if hasattr(self, 'style_widget') else "",
            setting=self.setting_widget.get_current_text() if hasattr(self, 'setting_widget') else "",
            weather=self.weather_widget.get_current_text() if hasattr(self, 'weather_widget') else "",
            date_time=self.datetime_widget.get_current_text() if hasattr(self, 'datetime_widget') else "",
            subjects=self.subjects_widget.get_current_text() if hasattr(self, 'subjects_widget') else "",
            pose_action=self.pose_widget.get_current_text() if hasattr(self, 'pose_widget') else "",
            camera=self.camera_widget.get_current_text() if hasattr(self, 'camera_widget') else "",
            framing_action=self.framing_widget.get_current_text() if hasattr(self, 'framing_widget') else "",
            grading=self.grading_widget.get_current_text() if hasattr(self, 'grading_widget') else "",
            details=self.details_widget.get_current_text() if hasattr(self, 'details_widget') else "",
            llm_instructions=""
        )
    
    def _get_current_seed(self):
        """Get the current seed value."""
        return self.seed_widget.get_value() if hasattr(self, 'seed_widget') else 0

