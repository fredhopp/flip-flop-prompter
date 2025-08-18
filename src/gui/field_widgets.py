"""
Custom field widgets for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class FieldWidget:
    """Base class for field widgets."""
    
    def __init__(self, parent, label: str, **kwargs):
        self.parent = parent
        self.label = label
        self.change_callback: Optional[Callable] = None
        
        self._create_widgets(**kwargs)
    
    def _create_widgets(self, **kwargs):
        """Create the widget components. Override in subclasses."""
        pass
    
    def get_value(self) -> str:
        """Get the current value. Override in subclasses."""
        return ""
    
    def set_value(self, value: str):
        """Set the current value. Override in subclasses."""
        pass
    
    def bind_change_event(self, callback: Callable):
        """Bind a callback for when the value changes."""
        self.change_callback = callback
    
    def _trigger_change(self, event=None):
        """Trigger the change callback."""
        if self.change_callback:
            self.change_callback(event)


class TextFieldWidget(FieldWidget):
    """Single-line text input field."""
    
    def _create_widgets(self, placeholder: str = "", width: int = 40, **kwargs):
        # Container frame
        self.frame = ttk.Frame(self.parent)
        
        # Label
        self.label_widget = ttk.Label(self.frame, text=self.label)
        self.label_widget.pack(anchor=tk.W)
        
        # Entry field
        self.entry = ttk.Entry(self.frame, width=width)
        self.entry.pack(fill=tk.X, pady=(2, 0))
        
        # Placeholder functionality
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.normal_color = 'black'
        
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(foreground=self.placeholder_color)
            self.entry.bind('<FocusIn>', self._on_focus_in)
            self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Bind change events
        self.entry.bind('<KeyRelease>', self._trigger_change)
        self.entry.bind('<FocusOut>', self._trigger_change)
    
    def get_value(self) -> str:
        """Get the current value."""
        value = self.entry.get()
        if value == self.placeholder:
            return ""
        return value
    
    def set_value(self, value: str):
        """Set the current value."""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.config(foreground=self.normal_color)
        elif self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground=self.placeholder_color)
    
    def _on_focus_in(self, event):
        """Handle focus in event for placeholder."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground=self.normal_color)
    
    def _on_focus_out(self, event):
        """Handle focus out event for placeholder."""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground=self.placeholder_color)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)


class TextAreaWidget(FieldWidget):
    """Multi-line text input field."""
    
    def _create_widgets(self, placeholder: str = "", height: int = 3, width: int = 40, **kwargs):
        # Container frame
        self.frame = ttk.Frame(self.parent)
        
        # Label
        self.label_widget = ttk.Label(self.frame, text=self.label)
        self.label_widget.pack(anchor=tk.W)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
        self.text_widget = tk.Text(
            text_frame,
            height=height,
            width=width,
            wrap=tk.WORD,
            font=("Arial", 9)
        )
        
        self.scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Placeholder functionality
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.normal_color = 'black'
        
        if placeholder:
            self.text_widget.insert(tk.END, placeholder)
            self.text_widget.config(foreground=self.placeholder_color)
            self.text_widget.bind('<FocusIn>', self._on_focus_in)
            self.text_widget.bind('<FocusOut>', self._on_focus_out)
        
        # Bind change events
        self.text_widget.bind('<KeyRelease>', self._trigger_change)
        self.text_widget.bind('<FocusOut>', self._trigger_change)
    
    def get_value(self) -> str:
        """Get the current value."""
        value = self.text_widget.get("1.0", tk.END).strip()
        if value == self.placeholder:
            return ""
        return value
    
    def set_value(self, value: str):
        """Set the current value."""
        self.text_widget.delete("1.0", tk.END)
        if value:
            self.text_widget.insert("1.0", value)
            self.text_widget.config(foreground=self.normal_color)
        elif self.placeholder:
            self.text_widget.insert("1.0", self.placeholder)
            self.text_widget.config(foreground=self.placeholder_color)
    
    def _on_focus_in(self, event):
        """Handle focus in event for placeholder."""
        if self.text_widget.get("1.0", tk.END).strip() == self.placeholder:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.config(foreground=self.normal_color)
    
    def _on_focus_out(self, event):
        """Handle focus out event for placeholder."""
        if not self.text_widget.get("1.0", tk.END).strip():
            self.text_widget.insert("1.0", self.placeholder)
            self.text_widget.config(foreground=self.placeholder_color)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)


class DateTimeWidget(FieldWidget):
    """Date and time input widget."""
    
    def _create_widgets(self, placeholder: str = "", **kwargs):
        # Container frame
        self.frame = ttk.Frame(self.parent)
        
        # Label
        self.label_widget = ttk.Label(self.frame, text=self.label)
        self.label_widget.pack(anchor=tk.W)
        
        # Input frame
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=tk.X, pady=(2, 0))
        
        # Entry field
        self.entry = ttk.Entry(input_frame, width=20)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Removed quick time buttons to save space
        
        # Placeholder functionality
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.normal_color = 'black'
        
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(foreground=self.placeholder_color)
            self.entry.bind('<FocusIn>', self._on_focus_in)
            self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Bind change events
        self.entry.bind('<KeyRelease>', self._trigger_change)
        self.entry.bind('<FocusOut>', self._trigger_change)
    
    def get_value(self) -> str:
        """Get the current value."""
        value = self.entry.get()
        if value == self.placeholder:
            return ""
        return value
    
    def set_value(self, value: str):
        """Set the current value."""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.config(foreground=self.normal_color)
        elif self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground=self.placeholder_color)
    
    def _set_time(self, time: str):
        """Set a quick time value."""
        self.set_value(time)
        self._trigger_change()
    
    def _on_focus_in(self, event):
        """Handle focus in event for placeholder."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground=self.normal_color)
    
    def _on_focus_out(self, event):
        """Handle focus out event for placeholder."""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground=self.placeholder_color)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)
