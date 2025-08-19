"""
Field widgets for the FlipFlopPrompt application.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Callable, Dict, Any
from ..utils import snippet_manager


class FieldWidget:
    """Base class for field widgets."""
    
    def __init__(self, parent, label: str, placeholder: str = "", change_callback: Callable = None):
        self.parent = parent
        self.label_text = label
        self.placeholder = placeholder
        self.change_callback = change_callback
        
        # Create the widget container
        self.container = ttk.Frame(parent)
        
        # Create widgets
        self._create_widgets()
        
        # Bind events
        self._bind_events()
    
    def _create_widgets(self):
        """Create the widget components. Override in subclasses."""
        pass
    
    def _bind_events(self):
        """Bind events. Override in subclasses."""
        pass
    
    def _trigger_change(self, event=None):
        """Trigger the change callback."""
        if self.change_callback:
            self.change_callback(event)
    
    def _get_field_name_from_label(self, label: str) -> str:
        """Convert label to field name for snippet lookup."""
        # Remove colon and convert to lowercase
        field_name = label.lower().replace(":", "").replace(" ", "_")
        
        # Special mappings for field names
        field_mappings = {
            "date_and_time": "date_time",
            "subjects_pose_and_action": "subjects_pose_and_action", 
            "camera_framing_and_action": "camera_framing_and_action",
            "color_grading_&_mood": "color_grading_&_mood",
            "additional_details": "details"
        }
        
        # Pretty name mappings for display
        pretty_name_mappings = {
            "setting": "Setting",
            "weather": "Weather",
            "date_time": "Date & Time",
            "subjects": "Subjects",
            "subjects_pose_and_action": "Subjects Pose & Action",
            "camera": "Camera",
            "camera_framing_and_action": "Camera Framing & Action",
            "color_grading_&_mood": "Color Grading & Mood",
            "additional_details": "Additional Details"
        }
        
        return field_mappings.get(field_name, field_name)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        return self.container.pack(**kwargs)
    
    def get_value(self) -> str:
        """Get the current value. Override in subclasses."""
        return ""
    
    def set_value(self, value: str):
        """Set the current value. Override in subclasses."""
        pass
    
    def clear(self):
        """Clear the field value. Override in subclasses."""
        pass


class TextFieldWidget(FieldWidget):
    """Text field widget with snippet support."""
    
    def _create_widgets(self):
        """Create the text field widget."""
        # Label
        self.label_widget = ttk.Label(self.container, text=self.label_text)
        self.label_widget.pack(anchor=tk.W)
        
        # Input frame
        input_frame = ttk.Frame(self.container)
        input_frame.pack(fill=tk.X, pady=2)
        
        # Entry field
        self.entry = ttk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Set placeholder if provided
        if self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground='gray')
            self._placeholder_active = True
        else:
            self._placeholder_active = False
        
        # Snippet dropdown
        field_name = self._get_field_name_from_label(self.label_text)
        self.snippet_dropdown = snippet_manager.create_snippet_dropdown(
            input_frame, field_name, self._on_snippet_select
        )
        self.snippet_dropdown.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _bind_events(self):
        """Bind events to the entry field."""
        self.entry.bind('<KeyRelease>', self._trigger_change)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        # Clear placeholder if active
        if hasattr(self, '_placeholder_active') and self._placeholder_active:
            self.entry.delete(0, tk.END)
            self._placeholder_active = False
        
        current_value = self.entry.get()
        
        # Toggle behavior: if snippet is already in the field, remove it
        if snippet in current_value:
            # Remove the snippet and clean up extra spaces/commas
            new_value = current_value.replace(snippet, "").strip()
            new_value = new_value.replace(",,", ",").strip(",")
        else:
            # Add the snippet
            if current_value:
                new_value = f"{current_value}, {snippet}"
            else:
                new_value = snippet
        
        # Set the new value and ensure text is black
        self.entry.delete(0, tk.END)
        self.entry.insert(0, new_value)
        self.entry.config(foreground='black')
        
        self._trigger_change()
    
    def get_value(self) -> str:
        """Get the current value."""
        value = self.entry.get()
        # Return empty string if placeholder is active
        if hasattr(self, '_placeholder_active') and self._placeholder_active:
            return ""
        return value
    
    def set_value(self, value: str):
        """Set the current value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    
    def clear(self):
        """Clear the field value."""
        self.entry.delete(0, tk.END)
    
    def _on_focus_in(self, event):
        """Handle focus in event for placeholder."""
        if hasattr(self, '_placeholder_active') and self._placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground='black')
            self._placeholder_active = False
    
    def _on_focus_out(self, event):
        """Handle focus out event for placeholder."""
        if hasattr(self, '_placeholder_active') and not self.entry.get().strip() and self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground='gray')
            self._placeholder_active = True


class TextAreaWidget(FieldWidget):
    """Text area widget with snippet support."""
    
    def _create_widgets(self):
        """Create the text area widget."""
        # Label
        self.label_widget = ttk.Label(self.container, text=self.label_text)
        self.label_widget.pack(anchor=tk.W)
        
        # Input frame
        input_frame = ttk.Frame(self.container)
        input_frame.pack(fill=tk.X, pady=2)
        
        # Text area
        self.text_area = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)
        
        # Snippet dropdown
        field_name = self._get_field_name_from_label(self.label_text)
        self.snippet_dropdown = snippet_manager.create_snippet_dropdown(
            input_frame, field_name, self._on_snippet_select
        )
        self.snippet_dropdown.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _bind_events(self):
        """Bind events to the text area."""
        self.text_area.bind('<KeyRelease>', self._trigger_change)
        self.text_area.bind('<FocusOut>', self._trigger_change)
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        current_value = self.get_value()
        
        # Toggle behavior: if snippet is already in the field, remove it
        if snippet in current_value:
            # Remove the snippet and clean up extra spaces/commas
            new_value = current_value.replace(snippet, "").strip()
            new_value = new_value.replace(",,", ",").strip(",")
        else:
            # Add the snippet
            if current_value:
                new_value = f"{current_value}, {snippet}"
            else:
                new_value = snippet
        
        # Set the new value and ensure text is black
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, new_value)
        self.text_area.config(foreground='black')
        
        self._trigger_change()
    
    def get_value(self) -> str:
        """Get the current value."""
        return self.text_area.get(1.0, tk.END).strip()
    
    def set_value(self, value: str):
        """Set the current value."""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, value)
    
    def clear(self):
        """Clear the field value."""
        self.text_area.delete(1.0, tk.END)


class DateTimeWidget(FieldWidget):
    """Date and time widget with snippet support."""
    
    def _create_widgets(self):
        """Create the date/time widget."""
        # Label
        self.label_widget = ttk.Label(self.container, text=self.label_text)
        self.label_widget.pack(anchor=tk.W)
        
        # Input frame
        input_frame = ttk.Frame(self.container)
        input_frame.pack(fill=tk.X, pady=2)
        
        # Entry field
        self.entry = ttk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Snippet dropdown
        field_name = self._get_field_name_from_label(self.label_text)
        self.snippet_dropdown = snippet_manager.create_snippet_dropdown(
            input_frame, field_name, self._on_snippet_select
        )
        self.snippet_dropdown.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _bind_events(self):
        """Bind events to the entry field."""
        self.entry.bind('<KeyRelease>', self._trigger_change)
        self.entry.bind('<FocusOut>', self._trigger_change)
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        current_value = self.get_value()
        
        # Toggle behavior: if snippet is already in the field, remove it
        if snippet in current_value:
            # Remove the snippet and clean up extra spaces/commas
            new_value = current_value.replace(snippet, "").strip()
            new_value = new_value.replace(",,", ",").strip(",")
        else:
            # Add the snippet
            if current_value:
                new_value = f"{current_value}, {snippet}"
            else:
                new_value = snippet
        
        # Set the new value and ensure text is black
        self.entry.delete(0, tk.END)
        self.entry.insert(0, new_value)
        self.entry.config(foreground='black')
        
        self._trigger_change()
    
    def get_value(self) -> str:
        """Get the current value."""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the current value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    
    def clear(self):
        """Clear the field value."""
        self.entry.delete(0, tk.END)
