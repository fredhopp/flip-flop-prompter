"""
Snippet widgets for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional
from ..utils.snippet_manager import snippet_manager


class SnippetDropdown:
    """Hierarchical dropdown for prompt snippets that stays open."""
    
    def __init__(self, parent, field_name: str, on_select: Callable[[str], None], content_rating: str = "PG"):
        self.parent = parent
        self.field_name = field_name
        self.on_select = on_select
        self.content_rating = content_rating
        self.popup = None
        
        # Get snippets from snippet manager
        self.snippets = snippet_manager.get_snippets_for_field(field_name, content_rating)
        
        self._create_widgets()
    
    def update_content_rating(self, new_rating: str):
        """Update the content rating and refresh snippets."""
        self.content_rating = new_rating
        self.snippets = snippet_manager.get_snippets_for_field(self.field_name, new_rating)
        if self.popup:
            self.popup.destroy()
            self.popup = None
    
    def _create_widgets(self):
        """Create the dropdown widget."""
        self.button = tk.Button(
            self.parent, 
            text="Snippets", 
            command=self._show_popup,
            bg="#0066cc",
            fg="#ffffff",
            relief="raised",
            borderwidth=2,
            font=("Arial", 8, "bold"),
            cursor="hand2"
        )
    
    def _show_popup(self):
        """Show the snippet selection popup."""
        if self.popup:
            self.popup.destroy()
            self.popup = None
            return
        
        # Create popup window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title(f"Snippets - {self._get_pretty_field_name()}")
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        # Position popup next to the button (to the right)
        self.button.update_idletasks()
        button_x = self.button.winfo_rootx()
        button_y = self.button.winfo_rooty()
        button_width = self.button.winfo_width()
        
        # Position to the right of the button
        popup_x = button_x + button_width + 5
        popup_y = button_y
        
        # Ensure popup doesn't go off-screen
        screen_width = self.popup.winfo_screenwidth()
        if popup_x + 400 > screen_width:  # 400 is estimated popup width
            popup_x = button_x - 400 - 5  # Position to the left instead
        
        self.popup.geometry(f"+{popup_x}+{popup_y}")
        
        # Handle popup close
        self.popup.protocol("WM_DELETE_WINDOW", self._close_popup)
        
        # Create main frame
        main_frame = ttk.Frame(self.popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create horizontal scrollable frame
        canvas = tk.Canvas(main_frame)
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Build snippet buttons in horizontal layout
        self._build_snippet_buttons_horizontal(scrollable_frame)
        
        # Pack canvas first
        canvas.pack(side="top", fill="both", expand=True)
        
        # Resize popup to fit content
        self.popup.update_idletasks()
        content_width = scrollable_frame.winfo_reqwidth()
        content_height = scrollable_frame.winfo_reqheight()
        
        # Set reasonable limits
        max_width = min(800, content_width + 50)
        max_height = min(600, content_height + 100)
        
        self.popup.geometry(f"{max_width}x{max_height}")
        
        # Only show scrollbars if content exceeds popup size
        self.popup.update_idletasks()
        if content_width > max_width - 50:
            h_scrollbar.pack(side="bottom", fill="x")
        if content_height > max_height - 100:
            v_scrollbar.pack(side="right", fill="y")
    
    def _build_snippet_buttons_horizontal(self, parent):
        """Build snippet selection buttons in horizontal layout."""
        if not self.snippets:
            ttk.Label(parent, text="No snippets available").pack(pady=10)
            return
        
        # Create a frame for each category
        for category, items in self.snippets.items():
            # Category frame
            category_frame = ttk.LabelFrame(parent, text=category)
            category_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            if isinstance(items, list):
                # Simple category with list of items
                for item in items:
                    btn = tk.Button(
                        category_frame, 
                        text=item, 
                        command=lambda i=item: self._select_item(i),
                        bg="#ffffff",
                        fg="#000000",
                        relief="flat",
                        borderwidth=1,
                        font=("Arial", 8),
                        cursor="hand2",
                        width=15,  # Fixed width for better layout
                        anchor="w"  # Left-align text
                    )
                    # Add hover effects
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e6f3ff"))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#ffffff"))
                    btn.pack(fill="x", pady=1, padx=2)
                    
            elif isinstance(items, dict):
                # Nested category structure
                for subcategory, subitems in items.items():
                    if isinstance(subitems, list):
                        # Subcategory label
                        sub_label = ttk.Label(category_frame, text=subcategory, font=("TkDefaultFont", 9, "italic"))
                        sub_label.pack(pady=(5, 2), anchor="w")
                        
                        for item in subitems:
                            btn = tk.Button(
                                category_frame, 
                                text=item, 
                                command=lambda i=item: self._select_item(i),
                                bg="#ffffff",
                                fg="#000000",
                                relief="flat",
                                borderwidth=1,
                                font=("Arial", 8),
                                cursor="hand2",
                                width=15,  # Fixed width for better layout
                                anchor="w"  # Left-align text
                            )
                            # Add hover effects
                            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e6f3ff"))
                            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#ffffff"))
                            btn.pack(fill="x", pady=1, padx=2)
    
    def _build_snippet_buttons(self, parent):
        """Build snippet selection buttons (vertical layout - kept for compatibility)."""
        if not self.snippets:
            ttk.Label(parent, text="No snippets available").pack(pady=10)
            return
        
        for category, items in self.snippets.items():
            # Category label
            category_label = ttk.Label(parent, text=category, font=("TkDefaultFont", 10, "bold"))
            category_label.pack(pady=(10, 5), anchor="w")
            
            if isinstance(items, list):
                # Simple category with list of items
                for item in items:
                    btn = ttk.Button(
                        parent, 
                        text=item, 
                        command=lambda i=item: self._select_item(i)
                    )
                    btn.pack(fill="x", pady=1)
                    
            elif isinstance(items, dict):
                # Nested category structure
                for subcategory, subitems in items.items():
                    if isinstance(subitems, list):
                        # Subcategory label
                        sub_label = ttk.Label(parent, text=f"  {subcategory}", font=("TkDefaultFont", 9, "italic"))
                        sub_label.pack(pady=(5, 2), anchor="w")
                        
                        for item in subitems:
                            btn = ttk.Button(
                                parent, 
                                text=f"    {item}", 
                                command=lambda i=item: self._select_item(i)
                            )
                            btn.pack(fill="x", pady=1)
    
    def _select_item(self, item: str):
        """Handle item selection."""
        self.on_select(item)
        # Don't close popup - let user select multiple items
    
    def _get_pretty_field_name(self):
        """Get a pretty display name for the field."""
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
        return pretty_name_mappings.get(self.field_name, self.field_name.replace("_", " ").title())
    
    def _close_popup(self):
        """Close the popup."""
        if self.popup:
            self.popup.destroy()
            self.popup = None
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.button.pack(**kwargs)


class ContentRatingWidget:
    """Widget for selecting content rating."""
    
    def __init__(self, parent, on_change: Optional[Callable[[str], None]] = None):
        self.parent = parent
        self.on_change = on_change
        
        # Get available ratings from snippet manager
        self.available_ratings = snippet_manager.get_available_ratings()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the rating selection widget."""
        # Create frame
        self.frame = ttk.Frame(self.parent)
        
        # Label
        self.label = ttk.Label(self.frame, text="Content Rating:")
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Rating variable
        self.rating_var = tk.StringVar(value="PG")
        
        # Rating combobox
        self.rating_combo = ttk.Combobox(
            self.frame,
            textvariable=self.rating_var,
            values=self.available_ratings,
            state="readonly",
            width=15
        )
        self.rating_combo.pack(side=tk.LEFT)
        self.rating_combo.bind('<<ComboboxSelected>>', self._on_change)
    
    def _on_change(self, event=None):
        """Handle rating change."""
        if self.on_change:
            self.on_change(self.rating_var.get())
    
    def get_rating(self) -> str:
        """Get the current rating."""
        return self.rating_var.get()
    
    def get_value(self) -> str:
        """Get the current rating (alias for get_rating)."""
        return self.rating_var.get()
    
    def set_rating(self, rating: str):
        """Set the rating."""
        self.rating_var.set(rating)
    
    def set_value(self, value: str):
        """Set the value (alias for set_rating)."""
        self.rating_var.set(value)
    
    def update_available_ratings(self):
        """Update the available ratings from snippet manager."""
        self.available_ratings = snippet_manager.get_available_ratings()
        self.rating_combo['values'] = self.available_ratings
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)


# Predefined snippet data
SNIPPET_DATA = {
    "environment": {
        "Location": [
            "hotel lobby",
            "restaurant",
            "office building",
            "apartment",
            "house",
            "park",
            "beach",
            "forest",
            "city street",
            "subway station",
            "airport",
            "hospital",
            "school",
            "library",
            "museum",
            "theater",
            "gym",
            "spa",
            "rooftop",
            "basement"
        ],
        "Architecture": [
            "marble floors",
            "crystal chandeliers",
            "glass walls",
            "wooden beams",
            "stone walls",
            "modern minimalist",
            "art deco",
            "gothic",
            "victorian",
            "industrial",
            "mediterranean",
            "japanese zen",
            "scandinavian",
            "rustic",
            "luxury",
            "abandoned",
            "futuristic",
            "steampunk"
        ],
        "Lighting": [
            "natural light",
            "golden hour",
            "blue hour",
            "moonlight",
            "candlelight",
            "neon lights",
            "spotlights",
            "ambient lighting",
            "dramatic shadows",
            "soft diffused light"
        ]
    },
    
    "weather": {
        "Conditions": [
            "sunny",
            "cloudy",
            "overcast",
            "rainy",
            "stormy",
            "foggy",
            "misty",
            "snowy",
            "windy",
            "calm"
        ],
        "Atmosphere": [
            "golden hour light",
            "blue hour",
            "dramatic clouds",
            "clear sky",
            "storm clouds",
            "light rain",
            "heavy rain",
            "snow falling",
            "fog rolling in"
        ]
    },
    
    "date_time": {
        "Time of Day": [
            "dawn",
            "morning",
            "noon",
            "afternoon",
            "sunset",
            "dusk",
            "night",
            "midnight"
        ],
        "Specific Times": [
            "6am",
            "7am",
            "8am",
            "9am",
            "10am",
            "11am",
            "12pm",
            "1pm",
            "2pm",
            "3pm",
            "4pm",
            "5pm",
            "6pm",
            "7pm",
            "8pm",
            "9pm",
            "10pm",
            "11pm",
            "12am"
        ]
    },
    
    "subjects": {
        "Human": {
            "Gender": [
                "man",
                "woman",
                "boy",
                "girl"
            ],
            "Age": [
                "teenager",
                "young adult",
                "middle-aged",
                "elderly"
            ],
            "Profession": [
                "businessman",
                "businesswoman",
                "doctor",
                "nurse",
                "teacher",
                "student",
                "artist",
                "musician",
                "chef",
                "waiter",
                "police officer",
                "firefighter",
                "soldier",
                "pilot",
                "scientist"
            ]
        },
        "Animal": [
            "dog",
            "cat",
            "horse",
            "bird",
            "fish",
            "rabbit",
            "hamster",
            "guinea pig",
            "ferret",
            "snake",
            "lizard",
            "turtle"
        ],
        "Vehicle": [
            "car",
            "motorcycle",
            "bicycle",
            "truck",
            "bus",
            "train",
            "airplane",
            "helicopter",
            "boat",
            "ship",
            "yacht"
        ],
        "Object": [
            "glass bottle",
            "book",
            "phone",
            "laptop",
            "coffee cup",
            "wine glass",
            "flower vase",
            "picture frame",
            "mirror",
            "clock",
            "candle",
            "lamp"
        ]
    },
    
    "subjects_pose_and_action": {
        "Standing": [
            "standing",
            "standing tall",
            "leaning against wall",
            "arms crossed",
            "hands in pockets",
            "pointing",
            "waving",
            "posing",
            "looking around"
        ],
        "Sitting": [
            "sitting",
            "sitting cross-legged",
            "sitting on floor",
            "sitting on chair",
            "sitting on sofa",
            "sitting on bench",
            "sitting on stairs",
            "lounging",
            "relaxing"
        ],
        "Movement": [
            "walking",
            "running",
            "jumping",
            "dancing",
            "climbing",
            "falling",
            "flying",
            "swimming",
            "crawling",
            "sliding"
        ],
        "Interaction": [
            "looking at",
            "talking to",
            "holding hands",
            "hugging",
            "kissing",
            "fighting",
            "playing",
            "working together",
            "arguing",
            "laughing",
            "crying",
            "smiling",
            "frowning"
        ],
        "Actions": [
            "reading",
            "writing",
            "cooking",
            "cleaning",
            "driving",
            "exercising",
            "sleeping",
            "eating",
            "drinking",
            "smoking",
            "praying",
            "meditating"
        ]
    },
    
    "camera": {
        "Camera Type": [
            "Arri Alexa",
            "RED camera",
            "Canon C300",
            "Sony FX9",
            "Blackmagic URSA",
            "Canon 5D Mark IV",
            "Nikon D850",
            "Sony A7R IV",
            "Leica M10",
            "Hasselblad X1D",
            "iPhone",
            "GoPro"
        ],
        "Film Cameras": [
            "Leica M6",
            "Nikon F3",
            "Canon AE-1",
            "Pentax K1000",
            "Hasselblad 500C/M",
            "Mamiya RB67",
            "Rolleiflex TLR",
            "Polaroid SX-70"
        ],
        "Lens": [
            "wide angle lens",
            "telephoto lens",
            "macro lens",
            "fisheye lens",
            "anamorphic lens",
            "prime lens",
            "zoom lens"
        ],
        "Settings": [
            "shallow depth of field",
            "deep depth of field",
            "low angle",
            "high angle",
            "eye level",
            "close-up",
            "extreme close-up",
            "medium shot",
            "long shot",
            "extreme long shot"
        ]
    },
    
    "camera_framing_and_action": {
        "Movement": [
            "dollies in",
            "dollies out",
            "pans left",
            "pans right",
            "tilts up",
            "tilts down",
            "zooms in",
            "zooms out",
            "tracks left",
            "tracks right",
            "cranes up",
            "cranes down",
            "steadicam",
            "handheld",
            "static shot"
        ],
        "Composition": [
            "rule of thirds",
            "centered composition",
            "leading lines",
            "symmetrical",
            "asymmetrical",
            "framed within frame",
            "negative space",
            "close-up",
            "medium shot",
            "wide shot",
            "extreme close-up",
            "long shot",
            "establishing shot"
        ],
        "Camera Position": [
            "low angle",
            "high angle",
            "eye level",
            "bird's eye view",
            "worm's eye view",
            "dutch angle",
            "over the shoulder",
            "point of view"
        ]
    },
    
    "color_grading_&_mood": {
        "Film Look": [
            "Fuji Xperia",
            "Kodak Portra",
            "Cinestill 800T",
            "Ilford HP5",
            "Kodak Tri-X",
            "Fuji Provia",
            "Kodak Ektachrome",
            "Fuji Superia",
            "Kodak Gold",
            "Agfa Vista"
        ],
        "Color Temperature": [
            "warm",
            "cool",
            "neutral",
            "golden",
            "blue",
            "green",
            "purple",
            "orange",
            "teal",
            "magenta"
        ],
        "Style": [
            "cinematic",
            "vintage",
            "modern",
            "retro",
            "futuristic",
            "noir",
            "romantic",
            "dramatic",
            "comedy",
            "horror",
            "documentary",
            "commercial",
            "artistic",
            "minimalist"
        ],
        "Mood": [
            "melancholic",
            "uplifting",
            "mysterious",
            "peaceful",
            "energetic",
            "calm",
            "tense",
            "joyful",
            "sad",
            "hopeful",
            "dark",
            "bright",
            "moody",
            "cheerful"
        ]
    }
}
