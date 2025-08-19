"""
Main GUI window for FlipFlopPrompt.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Dict, Any, Optional

from ..core.prompt_engine import PromptEngine
from ..core.data_models import PromptData
from .field_widgets import TextFieldWidget, TextAreaWidget, DateTimeWidget
from .preview_panel import PreviewPanel
from .snippet_widgets import ContentRatingWidget


class MainWindow:
    """Main application window."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Flip-Flop Prompter - AI Model Prompt Formulation Tool")
        self.root.geometry("1200x1200")
        self.root.minsize(1000, 1000)
        
        # Initialize components
        self.prompt_engine = PromptEngine()
        self.current_prompt_data = PromptData()
        
        # Create GUI elements
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Set up real-time updates
        self._setup_real_time_updates()
        
        # Initialize LLM status
        self._update_llm_status()
        
        # Load test data for development
        self._load_test_data()
        
        # Update preview with test data
        self._update_preview()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Flip-Flop Prompter", 
            font=("Arial", 16, "bold")
        )
        
        # Target Diffusion Model selection
        self.model_frame = ttk.LabelFrame(self.main_frame, text="Target Diffusion Model", padding="5")
        self.model_var = tk.StringVar(value="seedream")
        self.model_combo = ttk.Combobox(
            self.model_frame,
            textvariable=self.model_var,
            values=self.prompt_engine.get_supported_models(),
            state="readonly",
            width=20
        )
        
        # Content Rating selection
        self.content_rating_widget = ContentRatingWidget(
            self.model_frame,
            on_change=self._on_content_rating_changed
        )
        
        # LLM Model selection
        self.llm_frame = ttk.LabelFrame(self.main_frame, text="LLM Model for Prompt Refinement", padding="5")
        self.llm_var = tk.StringVar(value="deepseek-r1:8b")
        
        # Get available LLM models
        llm_info = self.prompt_engine.get_llm_info()
        if llm_info["available"] and llm_info.get("ollama_available"):
            # Try to get available Ollama models
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    llm_models = [model.get("name", "") for model in models if model.get("name")]
                    # Sort models for better UX
                    llm_models.sort()
                else:
                    llm_models = ["deepseek-r1:8b", "gemma3:4b"]
            except:
                llm_models = ["deepseek-r1:8b", "gemma3:4b"]
        else:
            llm_models = ["No LLM available"]
        
        self.llm_combo = ttk.Combobox(
            self.llm_frame,
            textvariable=self.llm_var,
            values=llm_models,
            state="readonly",
            width=30
        )
        
        # LLM Status
        self.llm_status_label = ttk.Label(
            self.llm_frame,
            text="LLM Status: Checking...",
            font=("Arial", 9)
        )
        
        # Input fields
        self.fields_frame = ttk.LabelFrame(self.main_frame, text="Prompt Components", padding="5")
        
        # Environment
        self.environment_widget = TextFieldWidget(
            self.fields_frame,
            label="Environment:",
            placeholder="e.g., interior, hotel lobby",
            width=60
        )
        
        # Weather
        self.weather_widget = TextFieldWidget(
            self.fields_frame,
            label="Weather:",
            placeholder="e.g., sunny with a few clouds",
            width=60
        )
        
        # Date and Time
        self.datetime_widget = DateTimeWidget(
            self.fields_frame,
            label="Date and Time:",
            placeholder="e.g., 7am"
        )
        
        # Subjects
        self.subjects_widget = TextAreaWidget(
            self.fields_frame,
            label="Subjects:",
            placeholder="e.g., a 20yo man, a woman in her 40s",
            height=3,
            width=60
        )
        
        # Pose and Action
        self.pose_widget = TextAreaWidget(
            self.fields_frame,
            label="Subjects Pose and Action:",
            placeholder="e.g., The man stands looking at the woman who is seated on a lounge",
            height=4,
            width=60
        )
        
        # Camera
        self.camera_widget = TextFieldWidget(
            self.fields_frame,
            label="Camera:",
            placeholder="e.g., shot on a 22mm lens on Arri Alexa",
            width=60
        )
        
        # Camera Framing and Action
        self.framing_widget = TextAreaWidget(
            self.fields_frame,
            label="Camera Framing and Action:",
            placeholder="e.g., The camera starts 5m away and dollies in",
            height=3,
            width=60
        )
        
        # Color Grading and Mood
        self.grading_widget = TextFieldWidget(
            self.fields_frame,
            label="Color Grading & Mood:",
            placeholder="e.g., warm golden hour lighting, cinematic color grading like Fuji Xperia film",
            width=60
        )
        
        # Buttons frame (will be moved to bottom)
        self.buttons_frame = ttk.Frame(self.main_frame)
        
        self.generate_btn = ttk.Button(
            self.buttons_frame,
            text="Generate Prompt",
            command=self._generate_prompt
        )
        
        self.copy_btn = ttk.Button(
            self.buttons_frame,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard
        )
        
        self.save_btn = ttk.Button(
            self.buttons_frame,
            text="Save Template",
            command=self._save_template
        )
        
        self.load_btn = ttk.Button(
            self.buttons_frame,
            text="Load Template",
            command=self._load_template
        )
        
        self.clear_btn = ttk.Button(
            self.buttons_frame,
            text="Clear All",
            command=self._clear_all
        )
        
        # Preview panel (will be created in _setup_layout)
        self.preview_panel = None
    
    def _setup_layout(self):
        """Set up the layout of widgets."""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label.pack(pady=(0, 10))
        
        # Target Diffusion Model selection
        self.model_frame.pack(fill=tk.X, pady=(0, 10))
        self.model_combo.pack(pady=5)
        self.content_rating_widget.pack(pady=5)
        
        # Fields frame
        self.fields_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid layout for fields
        fields = [
            self.environment_widget,
            self.weather_widget,
            self.datetime_widget,
            self.subjects_widget,
            self.pose_widget,
            self.camera_widget,
            self.framing_widget,
            self.grading_widget
        ]
        
        for i, field in enumerate(fields):
            field.pack(fill=tk.X, pady=2)
        
        # LLM Model selection
        self.llm_frame.pack(fill=tk.X, pady=(0, 10))
        self.llm_combo.pack(pady=5)
        self.llm_status_label.pack(pady=2)
        
        # Create and pack preview panel
        self.preview_panel = PreviewPanel(self.main_frame)
        self.preview_panel.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Buttons frame (always at bottom)
        self.buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons = [
            self.generate_btn,
            self.copy_btn,
            self.save_btn,
            self.load_btn,
            self.clear_btn
        ]
        
        for btn in buttons:
            btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def _bind_events(self):
        """Bind event handlers."""
        self.model_combo.bind('<<ComboboxSelected>>', self._on_model_changed)
        self.llm_combo.bind('<<ComboboxSelected>>', self._on_llm_changed)
    
    def _setup_real_time_updates(self):
        """Set up real-time preview updates."""
        # Bind text change events to all input widgets
        widgets = [
            self.environment_widget,
            self.weather_widget,
            self.datetime_widget,
            self.subjects_widget,
            self.pose_widget,
            self.camera_widget,
            self.framing_widget,
            self.grading_widget
        ]
        
        for widget in widgets:
            widget.bind_change_event(self._update_preview)
    
    def _update_preview(self, event=None):
        """Update the preview panel with current data."""
        try:
            # Get current data from widgets
            prompt_data = self._get_current_data()
            
            # Update preview
            preview_text = self.prompt_engine.get_prompt_preview(prompt_data)
            self.preview_panel.update_preview(preview_text)
            
        except Exception as e:
            self.preview_panel.update_preview(f"Error updating preview: {str(e)}")
    
    def _get_current_data(self) -> PromptData:
        """Get current data from all input widgets."""
        return PromptData(
            environment=self.environment_widget.get_value(),
            weather=self.weather_widget.get_value(),
            date_time=self.datetime_widget.get_value(),
            subjects=self.subjects_widget.get_value(),
            pose_action=self.pose_widget.get_value(),
            camera=self.camera_widget.get_value(),
            framing_action=self.framing_widget.get_value(),
            grading=self.grading_widget.get_value()
        )
    
    def _generate_prompt(self):
        """Generate the final prompt for the selected model."""
        try:
            # Get current data
            prompt_data = self._get_current_data()
            
            # Validate data
            errors = self.prompt_engine.validate_prompt_data(prompt_data)
            if errors:
                error_msg = "Please fix the following errors:\n" + "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("Validation Errors", error_msg)
                return
            
            # Generate prompt using selected target model
            model = self.model_var.get()
            content_rating = self.content_rating_widget.get_rating()
            final_prompt = self.prompt_engine.generate_prompt(model, prompt_data, content_rating)
            
            # Update preview with final prompt
            self.preview_panel.update_preview(final_prompt, is_final=True)
            
            # Show success message
            messagebox.showinfo("Success", "Prompt generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate prompt: {str(e)}")
    
    def _copy_to_clipboard(self):
        """Copy the current preview to clipboard."""
        try:
            text = self.preview_panel.get_current_text()
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Success", "Text copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
    
    def _save_template(self):
        """Save current data as a template."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                prompt_data = self._get_current_data()
                template_data = {
                    'target_model': self.model_var.get(),
                    'llm_model': self.llm_var.get(),
                    'data': prompt_data.to_dict()
                }
                
                with open(filename, 'w') as f:
                    json.dump(template_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Template saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")
    
    def _load_template(self):
        """Load a template from file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    template_data = json.load(f)
                
                # Load target model
                if 'target_model' in template_data:
                    self.model_var.set(template_data['target_model'])
                
                # Load LLM model
                if 'llm_model' in template_data:
                    self.llm_var.set(template_data['llm_model'])
                
                # Load data
                if 'data' in template_data:
                    prompt_data = PromptData.from_dict(template_data['data'])
                    self._set_data(prompt_data)
                
                messagebox.showinfo("Success", f"Template loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {str(e)}")
    
    def _set_data(self, prompt_data: PromptData):
        """Set data in all input widgets."""
        self.environment_widget.set_value(prompt_data.environment)
        self.weather_widget.set_value(prompt_data.weather)
        self.datetime_widget.set_value(prompt_data.date_time)
        self.subjects_widget.set_value(prompt_data.subjects)
        self.pose_widget.set_value(prompt_data.pose_action)
        self.camera_widget.set_value(prompt_data.camera)
        self.framing_widget.set_value(prompt_data.framing_action)
        self.grading_widget.set_value(prompt_data.grading)
    
    def _clear_all(self):
        """Clear all input fields."""
        widgets = [
            self.environment_widget,
            self.weather_widget,
            self.datetime_widget,
            self.subjects_widget,
            self.pose_widget,
            self.camera_widget,
            self.framing_widget,
            self.grading_widget
        ]
        
        for widget in widgets:
            widget.set_value("")
        
        self.preview_panel.update_preview("")
    
    def _on_model_changed(self, event=None):
        """Handle target model selection change."""
        model = self.model_var.get()
        self.preview_panel.update_model_info(model)
        self._update_preview()
    
    def _update_llm_status(self):
        """Update the LLM status display."""
        llm_info = self.prompt_engine.get_llm_info()
        if llm_info["available"]:
            self.llm_status_label.config(
                text=f"✓ LLM Available: {llm_info['provider']}",
                foreground="green"
            )
        else:
            self.llm_status_label.config(
                text="✗ No LLM available - using basic formatting",
                foreground="red"
            )
    
    def _on_llm_changed(self, event=None):
        """Handle LLM model selection change."""
        llm_model = self.llm_var.get()
        self.preview_panel.update_llm_info(llm_model)
        
        # Update the LLM model in the prompt engine
        self.prompt_engine.update_llm_model(llm_model)
        
        self._update_preview()
        
        # Update LLM status
        self._update_llm_status()
    
    def _on_content_rating_changed(self, rating: str):
        """Handle content rating change."""
        # Update LLM model selection based on content rating
        self._update_llm_models_for_rating(rating)
        self._update_preview()
    
    def _update_llm_models_for_rating(self, rating: str):
        """Update available LLM models based on content rating."""
        llm_info = self.prompt_engine.get_llm_info()
        if llm_info["available"] and llm_info.get("ollama_available"):
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    all_models = [model.get("name", "") for model in models if model.get("name")]
                    
                    # Filter models based on content rating
                    if rating == "PG":
                        # Use general models for PG content
                        llm_models = [m for m in all_models if any(x in m.lower() for x in ["deepseek", "gemma", "llama", "mistral"])]
                    elif rating == "NSFW":
                        # Use models that can handle NSFW content
                        llm_models = [m for m in all_models if any(x in m.lower() for x in ["deepseek", "llama", "mistral"])]
                    elif rating == "Hentai":
                        # Use models that can handle explicit content
                        llm_models = [m for m in all_models if any(x in m.lower() for x in ["deepseek", "llama"])]
                    else:
                        llm_models = all_models
                    
                    # Sort models for better UX
                    llm_models.sort()
                    
                    # Update combobox values
                    self.llm_combo['values'] = llm_models
                    
                    # Set default model if current one is not in filtered list
                    current_model = self.llm_var.get()
                    if current_model not in llm_models and llm_models:
                        self.llm_var.set(llm_models[0])
                        self.prompt_engine.update_llm_model(llm_models[0])
                else:
                    # Fallback to default models
                    if rating == "PG":
                        llm_models = ["deepseek-r1:8b", "gemma3:4b"]
                    elif rating == "NSFW":
                        llm_models = ["deepseek-r1:8b", "llama3.1:8b"]
                    elif rating == "Hentai":
                        llm_models = ["deepseek-r1:8b"]
                    else:
                        llm_models = ["deepseek-r1:8b", "gemma3:4b"]
                    
                    self.llm_combo['values'] = llm_models
            except:
                # Fallback to default models
                if rating == "PG":
                    llm_models = ["deepseek-r1:8b", "gemma3:4b"]
                elif rating == "NSFW":
                    llm_models = ["deepseek-r1:8b", "llama3.1:8b"]
                elif rating == "Hentai":
                    llm_models = ["deepseek-r1:8b"]
                else:
                    llm_models = ["deepseek-r1:8b", "gemma3:4b"]
                
                self.llm_combo['values'] = llm_models
    
    def _load_test_data(self):
        """Load test data for development and testing."""
        test_data = PromptData(
            environment="luxurious hotel lobby with marble floors and crystal chandeliers",
            weather="sunny with golden hour light streaming through large windows",
            date_time="late afternoon, around 5:30 PM",
            subjects="a sophisticated woman in her early 30s wearing an elegant black dress, a businessman in his 40s in a tailored suit",
            pose_action="the woman sits gracefully on a plush velvet sofa, the man stands nearby looking at his watch, they exchange glances",
            camera="shot on Arri Alexa with 35mm lens, shallow depth of field",
            framing_action="camera starts wide establishing the lobby, then slowly dollies in to focus on the couple, ending with a medium close-up",
            grading="warm cinematic lighting with golden tones, color grading inspired by Roger Deakins' style"
        )
        
        self._set_data(test_data)
