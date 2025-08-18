"""
Preview panel for displaying generated prompts.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class PreviewPanel:
    """Panel for displaying prompt preview and final output."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_text = ""
        self.is_final = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the preview panel widgets."""
        # Main container
        self.frame = ttk.LabelFrame(self.parent, text="Prompt Summary", padding="5")
        
        # Model info labels
        self.model_info_label = ttk.Label(
            self.frame,
            text="Target: Seedream 3.0",
            font=("Arial", 9, "italic")
        )
        self.model_info_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.llm_info_label = ttk.Label(
            self.frame,
            text="LLM: deepseek-r1:8b",
            font=("Arial", 9, "italic")
        )
        self.llm_info_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Preview text area
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame,
            height=12,  # Increased height for better visibility
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#212529",
            relief=tk.SUNKEN,
            borderwidth=1,
            padx=10,
            pady=10
        )
        
        self.scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_frame = ttk.Frame(self.frame)
        self.status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            font=("Arial", 8)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.char_count_label = ttk.Label(
            self.status_frame,
            text="0 characters",
            font=("Arial", 8)
        )
        self.char_count_label.pack(side=tk.RIGHT)
        
        # Set initial text
        self.text_widget.insert(tk.END, "Enter your prompt components above to see a preview here...")
        self.text_widget.config(state=tk.DISABLED)
    
    def update_preview(self, text: str, is_final: bool = False):
        """
        Update the preview with new text.
        
        Args:
            text: The text to display
            is_final: Whether this is the final generated prompt
        """
        self.current_text = text
        self.is_final = is_final
        
        # Update frame title based on state
        if is_final:
            self.frame.configure(text="Final Prompt")
        else:
            self.frame.configure(text="Prompt Summary")
        
        # Enable text widget for editing
        self.text_widget.config(state=tk.NORMAL)
        
        # Clear existing content
        self.text_widget.delete("1.0", tk.END)
        
        if text:
            # Insert new text
            self.text_widget.insert(tk.END, text)
            
            # Apply formatting based on whether it's final or preview
            if is_final:
                self.text_widget.config(
                    bg="#e8f5e8",
                    fg="#1a472a",
                    font=("Consolas", 10, "bold")
                )
                self.status_label.config(text="Final Prompt Generated")
            else:
                self.text_widget.config(
                    bg="#f8f9fa",
                    fg="#212529",
                    font=("Consolas", 10)
                )
                self.status_label.config(text="Preview")
        else:
            # Show placeholder text
            self.text_widget.insert(tk.END, "Enter your prompt components above to see a preview here...")
            self.text_widget.config(
                bg="#f8f9fa",
                fg="#6c757d",
                font=("Consolas", 10, "italic")
            )
            self.status_label.config(text="Ready")
        
        # Update character count
        char_count = len(text) if text else 0
        self.char_count_label.config(text=f"{char_count} characters")
        
        # Disable text widget to prevent editing
        self.text_widget.config(state=tk.DISABLED)
        
        # Scroll to top
        self.text_widget.see("1.0")
    
    def update_model_info(self, model_name: str):
        """
        Update the target model information display.
        
        Args:
            model_name: Name of the selected target model
        """
        # Capitalize model name for display
        display_name = model_name.capitalize()
        
        # Add version info for known models
        if model_name.lower() == "seedream":
            display_name = "Seedream 3.0"
        elif model_name.lower() == "veo":
            display_name = "Google Veo"
        elif model_name.lower() == "flux":
            display_name = "Stability AI Flux"
        
        self.model_info_label.config(text=f"Target: {display_name}")
    
    def update_llm_info(self, llm_model: str):
        """
        Update the LLM information display.
        
        Args:
            llm_model: Name of the selected LLM model
        """
        self.llm_info_label.config(text=f"LLM: {llm_model}")
    
    def get_current_text(self) -> str:
        """Get the current text content."""
        return self.current_text
    
    def clear_preview(self):
        """Clear the preview and reset to initial state."""
        self.update_preview("")
    
    def highlight_syntax(self, text: str) -> str:
        """
        Apply basic syntax highlighting to the prompt text.
        
        Args:
            text: The text to highlight
            
        Returns:
            Text with basic formatting applied
        """
        # This is a simple implementation - could be enhanced with more sophisticated highlighting
        highlighted = text
        
        # Highlight common prompt elements
        import re
        
        # Highlight camera specifications
        highlighted = re.sub(
            r'(\d+mm|lens|Arri|Alexa|RED|Canon|Sony)',
            r'**\1**',
            highlighted
        )
        
        # Highlight time references
        highlighted = re.sub(
            r'(\d+am|\d+pm|morning|afternoon|evening|night)',
            r'*\1*',
            highlighted
        )
        
        # Highlight action words
        action_words = ['dollies', 'pans', 'tilts', 'zooms', 'tracks', 'walks', 'sits', 'stands']
        for word in action_words:
            highlighted = highlighted.replace(word, f'__{word}__')
        
        return highlighted
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)
