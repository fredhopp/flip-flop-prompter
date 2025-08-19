"""
Snippet widgets for providing hierarchical prompt suggestions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional


class SnippetDropdown:
    """Hierarchical dropdown for prompt snippets."""
    
    def __init__(self, parent, snippets: Dict[str, List[str]], on_select: Callable[[str], None]):
        self.parent = parent
        self.snippets = snippets
        self.on_select = on_select
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the dropdown widget."""
        # Create a frame for the dropdown
        self.frame = ttk.Frame(self.parent)
        
        # Create the dropdown button
        self.dropdown_btn = ttk.Button(
            self.frame,
            text="📝",
            width=3,
            command=self._show_menu
        )
        self.dropdown_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Create the popup menu
        self.menu = tk.Menu(self.parent, tearoff=0)
        self._build_menu()
    
    def _build_menu(self):
        """Build the hierarchical menu from snippets."""
        self.menu.delete(0, tk.END)
        
        for category, items in self.snippets.items():
            if isinstance(items, list):
                # Simple list of items
                category_menu = tk.Menu(self.menu, tearoff=0)
                for item in items:
                    category_menu.add_command(
                        label=item,
                        command=lambda i=item: self._select_item(i)
                    )
                self.menu.add_cascade(label=category, menu=category_menu)
            elif isinstance(items, dict):
                # Nested dictionary
                category_menu = tk.Menu(self.menu, tearoff=0)
                for subcategory, subitems in items.items():
                    if isinstance(subitems, list):
                        subcategory_menu = tk.Menu(category_menu, tearoff=0)
                        for item in subitems:
                            subcategory_menu.add_command(
                                label=item,
                                command=lambda i=item: self._select_item(i)
                            )
                        category_menu.add_cascade(label=subcategory, menu=subcategory_menu)
                self.menu.add_cascade(label=category, menu=category_menu)
    
    def _show_menu(self):
        """Show the dropdown menu."""
        try:
            x = self.dropdown_btn.winfo_rootx()
            y = self.dropdown_btn.winfo_rooty() + self.dropdown_btn.winfo_height()
            self.menu.post(x, y)
        except Exception as e:
            print(f"Error showing menu: {e}")
    
    def _select_item(self, item: str):
        """Handle item selection."""
        self.on_select(item)
    
    def pack(self, **kwargs):
        """Pack the widget."""
        self.frame.pack(**kwargs)


class ContentRatingWidget:
    """Widget for selecting content rating."""
    
    def __init__(self, parent, on_change: Optional[Callable[[str], None]] = None):
        self.parent = parent
        self.on_change = on_change
        self.rating_var = tk.StringVar(value="PG")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the content rating widget."""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        self.label = ttk.Label(self.frame, text="Content Rating:")
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Dropdown
        self.rating_combo = ttk.Combobox(
            self.frame,
            textvariable=self.rating_var,
            values=["PG", "NSFW", "Hentai"],
            state="readonly",
            width=10
        )
        self.rating_combo.pack(side=tk.LEFT)
        self.rating_combo.bind('<<ComboboxSelected>>', self._on_change)
    
    def _on_change(self):
        """Handle rating change."""
        if self.on_change:
            self.on_change(self.rating_var.get())
    
    def get_rating(self) -> str:
        """Get the current rating."""
        return self.rating_var.get()
    
    def set_rating(self, rating: str):
        """Set the rating."""
        self.rating_var.set(rating)
    
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
