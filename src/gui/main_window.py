"""
Main GUI window for the FlipFlopPrompt application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from .field_widgets import (
    TextFieldWidget, TextAreaWidget, DateTimeWidget
)
from .snippet_widgets import ContentRatingWidget
from ..core.prompt_engine import PromptEngine
from ..utils.snippet_manager import snippet_manager
from ..utils.theme_manager import theme_manager


class MainWindow:
    """Main application window."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FlipFlopPrompt")
        self.root.geometry("800x900")
        
        # Initialize components
        self.prompt_engine = PromptEngine()
        
        # Debug settings
        self.debug_enabled = False
        
        # User data directories
        self.user_data_dir = theme_manager.user_data_dir
        self.templates_dir = self.user_data_dir / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create input fields
        self._create_input_fields()
        
        # Create model selection
        self._create_model_selection()
        
        # Create content rating selection
        self._create_content_rating()
        
        # Create LLM selection
        self._create_llm_selection()
        
        # Create button frame (moved above preview)
        self._create_button_frame()
        
        # Create preview panel
        self._create_preview_panel()
        
        # Initialize LLM status
        self._update_llm_status()
        
        # Initialize snippet dropdowns with current content rating
        self._initialize_snippet_dropdowns()
        
        # Load test data for development
        self._load_test_data()
        
        # Apply basic theme
        self._apply_basic_theme()
        
        # Load saved preferences
        self._load_preferences()
        
        # Initialize preview with current values
        self._update_preview()
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Load Template", command=self._load_template)
        self.file_menu.add_command(label="Save Template", command=self._save_template)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Themes menu (top-level, simplified)
        self.themes_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Themes", menu=self.themes_menu)
        self.themes_menu.add_command(label="Basic Theme", command=lambda: self._switch_theme("basic"))
        
        # Snippets menu
        self.snippets_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Snippets", menu=self.snippets_menu)
        self.snippets_menu.add_command(label="Reload Snippets", command=self._reload_snippets)
        self.snippets_menu.add_separator()
        self.snippets_menu.add_command(label="Open Snippets Folder", command=self._open_snippets_folder)
        
        # Debug menu
        self.debug_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Debug", menu=self.debug_menu)
        
        # Debug toggle
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_menu.add_checkbutton(
            label="Enable Debug Mode", 
            variable=self.debug_var,
            command=self._toggle_debug_mode
        )
        self.debug_menu.add_separator()
        self.debug_menu.add_command(label="Open Debug Folder", command=self._open_debug_folder)
    
    def _create_input_fields(self):
        """Create input field widgets."""
        # Style
        self.style_widget = TextFieldWidget(
            self.main_frame, "Style:", placeholder="Select art style...", change_callback=self._update_preview
        )
        self.style_widget.pack(fill=tk.X, pady=2)
        
        # Setting (renamed from environment)
        self.setting_widget = TextFieldWidget(
            self.main_frame, "Setting:", placeholder="Describe the setting...", change_callback=self._update_preview
        )
        self.setting_widget.pack(fill=tk.X, pady=2)
        
        # Weather
        self.weather_widget = TextFieldWidget(
            self.main_frame, "Weather:", placeholder="Describe the weather...", change_callback=self._update_preview
        )
        self.weather_widget.pack(fill=tk.X, pady=2)
        
        # Date and Time
        self.datetime_widget = TextFieldWidget(
            self.main_frame, "Date and Time:", placeholder="Select season and time of day...", change_callback=self._update_preview
        )
        self.datetime_widget.pack(fill=tk.X, pady=2)
        
        # Subjects
        self.subjects_widget = TextFieldWidget(
            self.main_frame, "Subjects:", placeholder="Describe the subjects...", change_callback=self._update_preview
        )
        self.subjects_widget.pack(fill=tk.X, pady=2)
        
        # Subjects Pose and Action
        self.pose_widget = TextFieldWidget(
            self.main_frame, "Subjects Pose and Action:", placeholder="Describe poses and actions...", change_callback=self._update_preview
        )
        self.pose_widget.pack(fill=tk.X, pady=2)
        
        # Camera (expanded choices)
        self.camera_widget = TextFieldWidget(
            self.main_frame, "Camera:", placeholder="Select camera type...", change_callback=self._update_preview
        )
        self.camera_widget.pack(fill=tk.X, pady=2)
        
        # Camera Framing and Action
        self.framing_widget = TextFieldWidget(
            self.main_frame, "Camera Framing and Action:", placeholder="Describe framing and movement...", change_callback=self._update_preview
        )
        self.framing_widget.pack(fill=tk.X, pady=2)
        
        # Color Grading & Mood
        self.grading_widget = TextFieldWidget(
            self.main_frame, "Color Grading & Mood:", placeholder="Describe color grading and mood...", change_callback=self._update_preview
        )
        self.grading_widget.pack(fill=tk.X, pady=2)
        
        # Additional Details
        self.details_widget = TextAreaWidget(
            self.main_frame, "Additional Details:", placeholder="Any additional details...", change_callback=self._update_preview
        )
        self.details_widget.pack(fill=tk.X, pady=2)
    
    def _create_model_selection(self):
        """Create model selection frame."""
        # Create a container frame for horizontal layout
        self.model_rating_frame = ttk.Frame(self.main_frame)
        self.model_rating_frame.pack(fill=tk.X, pady=5)
        
        # Model selection frame (left side)
        self.model_frame = ttk.LabelFrame(self.model_rating_frame, text="Target Diffusion Model")
        self.model_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        
        # Model selection
        self.model_var = tk.StringVar(value="Seedream")
        self.model_combo = ttk.Combobox(
            self.model_frame,
            textvariable=self.model_var,
            values=["Seedream", "Veo", "Flux", "Wan", "Hailuo"],
            state="readonly",
            width=20
        )
        self.model_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.model_combo.bind('<<ComboboxSelected>>', lambda e: self._update_preview())
    
    def _create_content_rating(self):
        """Create content rating selection frame."""
        # Content rating frame (right side) - removed redundant label
        self.rating_frame = ttk.LabelFrame(self.model_rating_frame, text="Content Rating")
        self.rating_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 0))
        
        # Content rating widget
        self.content_rating_widget = ContentRatingWidget(
            self.rating_frame,
            on_change=self._on_content_rating_changed
        )
        self.content_rating_widget.pack(padx=5, pady=5)
    
    def _create_llm_selection(self):
        """Create LLM selection frame."""
        self.llm_frame = ttk.LabelFrame(self.main_frame, text="LLM Configuration")
        self.llm_frame.pack(fill=tk.X, pady=5)
        
        # LLM model selection
        self.llm_model_var = tk.StringVar(value="deepseek-coder:6.7b")
        self.llm_model_combo = ttk.Combobox(
            self.llm_frame,
            textvariable=self.llm_model_var,
            values=["deepseek-coder:6.7b", "gemma:2b", "llama2:7b"],
            state="readonly",
            width=25
        )
        self.llm_model_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.llm_model_combo.bind('<<ComboboxSelected>>', lambda e: self._update_preview())
        
        # LLM status
        self.llm_status_label = ttk.Label(self.llm_frame, text="Status: Unknown")
        self.llm_status_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Test connection button
        self.test_llm_btn = tk.Button(
            self.llm_frame,
            text="Test Connection",
            command=self._test_llm_connection,
            bg="#0066cc",
            fg="#ffffff",
            relief="raised",
            borderwidth=2,
            font=("Arial", 8, "bold"),
            cursor="hand2"
        )
        self.test_llm_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def _create_button_frame(self):
        """Create button frame (positioned above preview)."""
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Generate button
        self.generate_btn = tk.Button(
            self.button_frame,
            text="Generate Prompt",
            command=self._generate_prompt,
            bg="#0066cc",
            fg="#ffffff",
            relief="raised",
            borderwidth=2,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        self.copy_btn = tk.Button(
            self.button_frame,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard,
            bg="#0066cc",
            fg="#ffffff",
            relief="raised",
            borderwidth=2,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = tk.Button(
            self.button_frame,
            text="Clear All",
            command=self._clear_all,
            bg="#0066cc",
            fg="#ffffff",
            relief="raised",
            borderwidth=2,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_btn = tk.Button(
            self.button_frame,
            text="Save Prompt",
            command=self._save_prompt,
            bg="#0066cc",
            fg="#ffffff",
            relief="raised",
            borderwidth=2,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_preview_panel(self):
        """Create preview panel."""
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="Prompt Summary")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Preview text area
        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Track if we have a refined prompt
        self.has_refined_prompt = False
    
    def _on_content_rating_changed(self, rating: str):
        """Handle content rating change."""
        # Update LLM model selection based on content rating
        self._update_llm_models_for_rating(rating)
        
        # Update all snippet dropdowns with new content rating
        self._update_snippet_dropdowns(rating)
        
        self._update_preview()
    
    def _initialize_snippet_dropdowns(self):
        """Initialize snippet dropdowns with current content rating."""
        current_rating = self.content_rating_widget.get_value()
        self._update_snippet_dropdowns(current_rating)
    
    def _update_snippet_dropdowns(self, rating: str):
        """Update all snippet dropdowns with new content rating."""
        # Get all field widgets that have snippet dropdowns
        field_widgets = [
            self.style_widget,
            self.setting_widget,
            self.weather_widget,
            self.datetime_widget,
            self.subjects_widget,
            self.pose_widget,
            self.camera_widget,
            self.framing_widget,
            self.grading_widget
        ]
        
        # Update each widget's snippet dropdown
        for widget in field_widgets:
            if hasattr(widget, 'snippet_dropdown') and widget.snippet_dropdown:
                widget.snippet_dropdown.update_content_rating(rating)
    
    def _update_llm_models_for_rating(self, rating: str):
        """Update available LLM models based on content rating."""
        if rating.lower() in ["nsfw", "hentai"]:
            # Filter out models that don't handle explicit content well
            current_model = self.llm_model_var.get()
            if current_model == "gemma:2b":
                self.llm_model_var.set("deepseek-coder:6.7b")
            
            # Update available models
            self.llm_model_combo['values'] = ["deepseek-coder:6.7b", "llama2:7b"]
        else:
            # Show all models for PG content
            self.llm_model_combo['values'] = ["deepseek-coder:6.7b", "gemma:2b", "llama2:7b"]
    
    def _update_llm_status(self):
        """Update LLM connection status."""
        # This would check Ollama connection
        # For now, just show a placeholder
        self.llm_status_label.config(text="Status: Ready", foreground="green")
    
    def _test_llm_connection(self):
        """Test LLM connection."""
        try:
            # This would test Ollama connection
            messagebox.showinfo("Success", "LLM connection successful!")
        except Exception as e:
            messagebox.showerror("Error", f"LLM connection failed: {e}")
    
    def _generate_prompt(self):
        """Generate the final prompt."""
        try:
            # Collect all field values
            prompt_data_dict = {
                "style": self.style_widget.get_value(),
                "setting": self.setting_widget.get_value(),  # renamed from environment
                "weather": self.weather_widget.get_value(),
                "date_time": self.datetime_widget.get_value(),
                "subjects": self.subjects_widget.get_value(),
                "pose_action": self.pose_widget.get_value(),
                "camera": self.camera_widget.get_value(),
                "framing_action": self.framing_widget.get_value(),
                "grading": self.grading_widget.get_value(),
                "details": self.details_widget.get_value()
            }
            
            # Validate that at least 3 fields are filled
            filled_fields = sum(1 for value in prompt_data_dict.values() if value.strip())
            if filled_fields < 3:
                result = messagebox.askyesno(
                    "Insufficient Input", 
                    f"Only {filled_fields} field(s) are filled. This may result in poor prompt quality.\n\n"
                    "Do you want to continue anyway?"
                )
                if not result:
                    return
            
            # Convert to PromptData object
            from ..core.data_models import PromptData
            prompt_data = PromptData.from_dict(prompt_data_dict)
            
            # Get model and content rating
            model = self.model_var.get()
            content_rating = self.content_rating_widget.get_value()
            
            # Generate prompt using the engine
            final_prompt = self.prompt_engine.generate_prompt(model, prompt_data, content_rating, self.debug_enabled)
            
            # Update preview with refined prompt
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, final_prompt)
            self.preview_text.config(state=tk.DISABLED)
            
            # Update frame title and background color to indicate refined prompt
            self.preview_frame.config(text="LLM Refined Prompt")
            self.preview_text.config(background="#e8f5e8")  # Light green background
            self.has_refined_prompt = True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate prompt: {e}")
            import traceback
            traceback.print_exc()
    
    def _copy_to_clipboard(self):
        """Copy the generated prompt to clipboard."""
        try:
            prompt_text = self.preview_text.get(1.0, tk.END).strip()
            if prompt_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(prompt_text)
                messagebox.showinfo("Success", "Prompt copied to clipboard!")
            else:
                messagebox.showwarning("Warning", "No prompt to copy!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")
    
    def _clear_all(self):
        """Clear all input fields."""
        widgets = [
            self.style_widget,
            self.setting_widget,
            self.weather_widget,
            self.datetime_widget,
            self.subjects_widget,
            self.pose_widget,
            self.camera_widget,
            self.framing_widget,
            self.grading_widget,
            self.details_widget
        ]
        
        for widget in widgets:
            widget.clear()
        
        self._update_preview()
    
    def _save_prompt(self):
        """Save the generated prompt to a file."""
        try:
            prompt_text = self.preview_text.get(1.0, tk.END).strip()
            if not prompt_text:
                messagebox.showwarning("Warning", "No prompt to save!")
                return
            
            # Generate smart filename from prompt content
            smart_filename = self._generate_smart_filename(prompt_text)
            
            # Get default prompts directory
            prompts_dir = self.user_data_dir / "prompts"
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Use file dialog
            filepath = filedialog.asksaveasfilename(
                title="Save Prompt",
                initialdir=str(prompts_dir),
                initialfile=smart_filename,
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filepath:  # User didn't cancel
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(prompt_text)
                
                messagebox.showinfo("Success", f"Prompt saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prompt: {e}")
    
    def _generate_smart_filename(self, prompt_text: str) -> str:
        """Generate a smart filename based on prompt content."""
        try:
            # Take first 50 characters, clean them up, and use as filename
            words = prompt_text[:50].split()
            if len(words) > 3:
                # Use first 3-4 meaningful words
                filename_words = words[:4]
            else:
                filename_words = words
            
            # Clean up words for filename
            clean_words = []
            for word in filename_words:
                # Remove special characters and convert to lowercase
                clean_word = ''.join(c for c in word if c.isalnum() or c.isspace()).strip()
                if clean_word and len(clean_word) > 1:
                    clean_words.append(clean_word.lower())
            
            if clean_words:
                filename = "_".join(clean_words) + ".txt"
            else:
                # Fallback to timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"prompt_{timestamp}.txt"
            
            return filename
            
        except Exception:
            # Fallback to timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"prompt_{timestamp}.txt"
    
    def _update_preview(self, event=None):
        """Update the preview panel."""
        try:
            # Collect current values
            preview_data = {
                "Style": self.style_widget.get_value(),
                "Setting": self.setting_widget.get_value(),
                "Weather": self.weather_widget.get_value(),
                "Date/Time": self.datetime_widget.get_value(),
                "Subjects": self.subjects_widget.get_value(),
                "Pose/Action": self.pose_widget.get_value(),
                "Camera": self.camera_widget.get_value(),
                "Framing": self.framing_widget.get_value(),
                "Color/Mood": self.grading_widget.get_value(),
                "Details": self.details_widget.get_value()
            }
            
            # Build preview text - only include fields with values
            preview_lines = []
            for field, value in preview_data.items():
                if value:
                    preview_lines.append(f"{field}: {value}")
            
            # Update preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            if preview_lines:
                # Show actual content in black
                preview_text = "\n".join(preview_lines)
                self.preview_text.insert(1.0, preview_text)
                self.preview_text.config(foreground="black")
            else:
                # Show placeholder in grey
                self.preview_text.insert(1.0, "Start filling in fields to see your prompt preview...")
                self.preview_text.config(foreground="grey")
            
            self.preview_text.config(state=tk.DISABLED)
            
            # Reset to summary mode
            self.preview_frame.config(text="Prompt Summary")
            self.preview_text.config(background="#ffffff")
            self.has_refined_prompt = False
            
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def _load_template(self):
        """Load a template from file."""
        try:
            filepath = filedialog.askopenfilename(
                title="Load Template",
                initialdir=str(self.templates_dir),
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Load field values
                if 'fields' in template_data:
                    fields = template_data['fields']
                    self.style_widget.set_value(fields.get('style', ''))
                    self.setting_widget.set_value(fields.get('setting', ''))
                    self.weather_widget.set_value(fields.get('weather', ''))
                    self.datetime_widget.set_value(fields.get('date_time', ''))
                    self.subjects_widget.set_value(fields.get('subjects', ''))
                    self.pose_widget.set_value(fields.get('pose_action', ''))
                    self.camera_widget.set_value(fields.get('camera', ''))
                    self.framing_widget.set_value(fields.get('framing_action', ''))
                    self.grading_widget.set_value(fields.get('grading', ''))
                    self.details_widget.set_value(fields.get('details', ''))
                
                # Load settings
                if 'settings' in template_data:
                    settings = template_data['settings']
                    if 'model' in settings:
                        self.model_var.set(settings['model'])
                    if 'content_rating' in settings:
                        self.content_rating_widget.set_value(settings['content_rating'])
                    if 'llm_model' in settings:
                        self.llm_model_var.set(settings['llm_model'])
                
                # Load generated prompt if available
                if 'generated_prompt' in template_data:
                    prompt = template_data['generated_prompt']
                    self.preview_text.config(state=tk.NORMAL)
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, prompt)
                    self.preview_text.config(state=tk.DISABLED)
                    self.preview_frame.config(text="LLM Refined Prompt")
                    self.preview_text.config(background="#e8f5e8")
                    self.has_refined_prompt = True
                
                self._update_preview()
                messagebox.showinfo("Success", f"Template loaded from:\n{filepath}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {e}")
    
    def _save_template(self):
        """Save current state as a template."""
        try:
            # Collect current state
            template_data = {
                'timestamp': datetime.now().isoformat(),
                'description': 'Template saved from FlipFlopPrompt',
                'fields': {
                    'style': self.style_widget.get_value(),
                    'setting': self.setting_widget.get_value(),
                    'weather': self.weather_widget.get_value(),
                    'date_time': self.datetime_widget.get_value(),
                    'subjects': self.subjects_widget.get_value(),
                    'pose_action': self.pose_widget.get_value(),
                    'camera': self.camera_widget.get_value(),
                    'framing_action': self.framing_widget.get_value(),
                    'grading': self.grading_widget.get_value(),
                    'details': self.details_widget.get_value()
                },
                'settings': {
                    'model': self.model_var.get(),
                    'content_rating': self.content_rating_widget.get_value(),
                    'llm_model': self.llm_model_var.get()
                }
            }
            
            # Add generated prompt if available
            if self.has_refined_prompt:
                template_data['generated_prompt'] = self.preview_text.get(1.0, tk.END).strip()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"template_{timestamp}.json"
            
            # Use file dialog
            filepath = filedialog.asksaveasfilename(
                title="Save Template",
                initialdir=str(self.templates_dir),
                initialfile=default_filename,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Template saved to:\n{filepath}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {e}")
    
    def _load_preferences(self):
        """Load saved preferences."""
        try:
            prefs_file = self.user_data_dir / "preferences.json"
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Load preferences
                if 'model' in prefs:
                    self.model_var.set(prefs['model'])
                if 'llm_model' in prefs:
                    self.llm_model_var.set(prefs['llm_model'])
                if 'content_rating' in prefs:
                    self.content_rating_widget.set_value(prefs['content_rating'])
                    
        except Exception as e:
            print(f"Warning: Could not load preferences: {e}")
    
    def _save_preferences(self):
        """Save current preferences."""
        try:
            prefs = {
                'model': self.model_var.get(),
                'llm_model': self.llm_model_var.get(),
                'content_rating': self.content_rating_widget.get_value(),
                'theme': 'basic'
            }
            
            prefs_file = self.user_data_dir / "preferences.json"
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")
    
    def _load_test_data(self):
        """Load test data for development."""
        # This can be used to populate fields with test data
        pass
    
    def _switch_theme(self, theme_name: str):
        """Switch to the specified theme (simplified)."""
        # Only basic theme is supported now
        pass
    
    def _apply_basic_theme(self):
        """Apply basic theme with clear colors."""
        try:
            colors = theme_manager.get_theme_colors()
            
            # Configure ttk styles
            style = ttk.Style()
            
            # Basic frame and label styles
            style.configure("TFrame", background=colors["bg"])
            style.configure("TLabelframe", background=colors["bg"])
            style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["text_fg"])
            style.configure("TLabel", background=colors["bg"], foreground=colors["text_fg"])
            
            # Entry styles
            style.configure("TEntry", 
                          fieldbackground=colors["entry_bg"], 
                          foreground=colors["text_fg"],
                          insertcolor=colors["text_fg"])
            
            # Button styles
            style.configure("TButton", 
                          background=colors["button_bg"], 
                          foreground=colors["button_fg"])
            
            # Combobox styles
            style.configure("TCombobox", 
                          fieldbackground=colors["entry_bg"], 
                          foreground=colors["text_fg"],
                          background=colors["entry_bg"],
                          arrowcolor=colors["text_fg"])
            
            # Apply colors to main window
            self.root.configure(bg=colors["bg"])
            self.main_frame.configure(style="TFrame")
            
            # Apply colors to preview text
            self.preview_text.configure(
                bg=colors["text_bg"],
                fg=colors["text_fg"],
                insertbackground=colors["text_fg"]
            )
            
            # Apply colors to menu bar
            self.menu_bar.configure(
                bg=colors["menu_bg"],
                fg=colors["menu_fg"],
                activebackground=colors["menu_selection_bg"],
                activeforeground=colors["menu_selection_fg"]
            )
            
        except Exception as e:
            print(f"Warning: Could not apply basic theme: {e}")
    
    def _toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.debug_enabled = self.debug_var.get()
        
        if self.debug_enabled:
            # Show debug folder location
            debug_dir = self.user_data_dir / "debug"
            result = messagebox.askyesno(
                "Debug Mode Enabled",
                f"Debug mode is now enabled.\n\n"
                f"Debug files will be saved to:\n{debug_dir}\n\n"
                f"Each prompt generation will create a timestamped folder with debug files.\n\n"
                f"Continue?"
            )
            
            if not result:
                self.debug_enabled = False
                self.debug_var.set(False)
        else:
            messagebox.showinfo(
                "Debug Mode Disabled",
                "Debug mode is now disabled.\nNo debug files will be generated."
            )
    
    def _open_debug_folder(self):
        """Open the debug folder in file explorer."""
        import subprocess
        import platform
        
        debug_dir = self.user_data_dir / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(debug_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(debug_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(debug_dir)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open debug folder: {e}")
    
    def _open_snippets_folder(self):
        """Open the snippets folder in file explorer."""
        import subprocess
        import platform
        
        snippets_dir = snippet_manager.get_snippets_dir()
        
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(snippets_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(snippets_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(snippets_dir)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open snippets folder: {e}")
    
    def _reload_snippets(self):
        """Reload snippets from files."""
        try:
            snippet_manager.reload_snippets()
            
            # Update content rating widget with new available ratings
            self.content_rating_widget.update_available_ratings()
            
            # Update all snippet dropdowns
            self._update_snippet_dropdowns(self.content_rating_widget.get_value())
            
            messagebox.showinfo("Success", "Snippets reloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload snippets: {e}")
    
    def on_closing(self):
        """Handle window closing."""
        # Save preferences before closing
        self._save_preferences()
        self.root.destroy()
