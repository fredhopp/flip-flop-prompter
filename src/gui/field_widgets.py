"""
Custom field widgets for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from datetime import datetime, timedelta
import calendar
from .snippet_widgets import SnippetDropdown, SNIPPET_DATA

# Try to import tkcalendar, fallback to basic implementation
try:
    from tkcalendar import Calendar
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("Warning: tkcalendar not available. Install with: pip install tkcalendar")


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
        
        # Input frame for entry and snippet dropdown
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=tk.X, pady=(2, 0))
        
        # Entry field
        self.entry = ttk.Entry(input_frame, width=width)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add snippet dropdown if snippets are available for this field
        field_name = self.label.lower().replace(":", "").replace(" ", "_")
        self.snippet_dropdown = SnippetDropdown(
            input_frame,
            field_name,
            self._on_snippet_select
        )
        self.snippet_dropdown.pack(side=tk.RIGHT)
        
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
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        current_value = self.get_value()
        if current_value:
            # Append to existing value
            new_value = current_value + ", " + snippet
        else:
            # Set as new value
            new_value = snippet
        
        self.set_value(new_value)
        self._trigger_change()
    
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
        
        # Text area with scrollbar and snippet dropdown
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
        # Add snippet dropdown if snippets are available for this field
        field_name = self.label.lower().replace(":", "").replace(" ", "_")
        snippet_frame = ttk.Frame(self.frame)
        snippet_frame.pack(fill=tk.X, pady=(2, 0))
        self.snippet_dropdown = SnippetDropdown(
            snippet_frame,
            field_name,
            self._on_snippet_select
        )
        self.snippet_dropdown.pack(side=tk.RIGHT)
        
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
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        current_value = self.get_value()
        if current_value:
            # Append to existing value
            new_value = current_value + ", " + snippet
        else:
            # Set as new value
            new_value = snippet
        
        self.set_value(new_value)
        self._trigger_change()
    
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
    """Date and time input field with calendar popup."""
    
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
        self.entry = ttk.Entry(input_frame, width=30)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Calendar button
        self.calendar_btn = ttk.Button(
            input_frame,
            text="📅",
            width=3,
            command=self._show_calendar
        )
        self.calendar_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Add snippet dropdown if snippets are available for this field
        field_name = self.label.lower().replace(":", "").replace(" ", "_")
        self.snippet_dropdown = SnippetDropdown(
            input_frame,
            field_name,
            self._on_snippet_select
        )
        self.snippet_dropdown.pack(side=tk.RIGHT)
        
        # Set default to current date/time
        current_time = datetime.now()
        default_value = current_time.strftime("%Y-%m-%d %H:%M")
        self.entry.insert(0, default_value)
        
        # Bind change events
        self.entry.bind('<KeyRelease>', self._trigger_change)
        self.entry.bind('<FocusOut>', self._trigger_change)
    
    def _show_calendar(self):
        """Show calendar popup for date selection."""
        # Create popup window
        popup = tk.Toplevel(self.parent)
        popup.title("Select Date and Time")
        popup.geometry("300x400")
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (300 // 2)
        y = (popup.winfo_screenheight() // 2) - (400 // 2)
        popup.geometry(f"300x400+{x}+{y}")
        
        if CALENDAR_AVAILABLE:
            # Use tkcalendar if available
            cal = Calendar(popup, selectmode='day', date_pattern='y-mm-dd')
            cal.pack(pady=10)
            
            # Time selection
            time_frame = ttk.Frame(popup)
            time_frame.pack(pady=10)
            
            ttk.Label(time_frame, text="Time:").pack()
            
            time_input_frame = ttk.Frame(time_frame)
            time_input_frame.pack()
            
            # Hour selection
            hour_var = tk.StringVar(value=str(datetime.now().hour))
            hour_combo = ttk.Combobox(time_input_frame, textvariable=hour_var, 
                                    values=[str(i).zfill(2) for i in range(24)], 
                                    width=3, state="readonly")
            hour_combo.pack(side=tk.LEFT, padx=2)
            
            ttk.Label(time_input_frame, text=":").pack(side=tk.LEFT)
            
            # Minute selection
            minute_var = tk.StringVar(value=str(datetime.now().minute))
            minute_combo = ttk.Combobox(time_input_frame, textvariable=minute_var,
                                      values=[str(i).zfill(2) for i in range(0, 60, 5)], 
                                      width=3, state="readonly")
            minute_combo.pack(side=tk.LEFT, padx=2)
            
            # Buttons
            button_frame = ttk.Frame(popup)
            button_frame.pack(pady=10)
            
            def set_datetime():
                selected_date = cal.get_date()
                selected_time = f"{hour_var.get()}:{minute_var.get()}"
                datetime_str = f"{selected_date} {selected_time}"
                self.entry.delete(0, tk.END)
                self.entry.insert(0, datetime_str)
                self._trigger_change()
                popup.destroy()
            
            ttk.Button(button_frame, text="Set", command=set_datetime).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)
            
        else:
            # Fallback to basic date/time input
            ttk.Label(popup, text="Date (YYYY-MM-DD):").pack(pady=5)
            date_entry = ttk.Entry(popup)
            date_entry.pack(pady=5)
            date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            ttk.Label(popup, text="Time (HH:MM):").pack(pady=5)
            time_entry = ttk.Entry(popup)
            time_entry.pack(pady=5)
            time_entry.insert(0, datetime.now().strftime("%H:%M"))
            
            def set_datetime():
                try:
                    date_str = date_entry.get()
                    time_str = time_entry.get()
                    datetime_str = f"{date_str} {time_str}"
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, datetime_str)
                    self._trigger_change()
                    popup.destroy()
                except:
                    pass
            
            button_frame = ttk.Frame(popup)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Set", command=set_datetime).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)
    
    def _on_snippet_select(self, snippet: str):
        """Handle snippet selection."""
        current_value = self.get_value()
        if current_value:
            # Append to existing value
            new_value = current_value + ", " + snippet
        else:
            # Set as new value
            new_value = snippet
        
        self.set_value(new_value)
        self._trigger_change()
    
    def get_value(self) -> str:
        """Get the current value."""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the current value."""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)
