"""
Snippet management system with content rating support and JSON storage.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class ContentRating(Enum):
    """Content rating levels."""
    PG = "PG"
    NSFW = "NSFW"
    HENTAI = "Hentai"


class SnippetManager:
    """Manages dynamic snippets based on content rating with JSON storage."""
    
    def __init__(self):
        self.user_data_dir = self._get_user_data_dir()
        self.snippets_dir = self.user_data_dir / "snippets"
        self.snippets_dir.mkdir(parents=True, exist_ok=True)
        
        # Default snippets (PG only)
        self.default_snippets = self._get_default_snippets()
        
        # Load user snippets
        self.user_snippets = self._load_user_snippets()
        
        # Current content rating
        self.current_rating = ContentRating.PG
    
    def _get_user_data_dir(self) -> Path:
        """Get the appropriate user data directory for the platform."""
        system = platform.system().lower()
        
        if system == "windows":
            base_dir = Path(os.environ.get("APPDATA", ""))
            return base_dir / "FlipFlopPrompt"
        elif system == "darwin":  # macOS
            base_dir = Path.home() / "Library" / "Application Support"
            return base_dir / "FlipFlopPrompt"
        else:  # Linux and others
            base_dir = Path.home() / ".config"
            return base_dir / "FlipFlopPrompt"
    
    def _get_default_snippets(self) -> Dict[str, Dict[str, Any]]:
        """Get default PG snippets."""
        return {
            "environment": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "weather": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "date_time": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "subjects": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "subjects_pose_and_action": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "camera": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "camera_framing_and_action": {
                "rating": "PG",
                "categories": {
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
                }
            },
            "color_grading_&_mood": {
                "rating": "PG",
                "categories": {
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
        }
    
    def _load_user_snippets(self) -> Dict[str, Dict[str, Any]]:
        """Load user-defined snippets from JSON files."""
        user_snippets = {}
        
        # Load from individual field files
        for field_name in self.default_snippets.keys():
            file_path = self.snippets_dir / f"{field_name}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        user_snippets[field_name] = json.load(f)
                except Exception as e:
                    print(f"Error loading snippets for {field_name}: {e}")
        
        return user_snippets
    
    def set_content_rating(self, rating: ContentRating):
        """Set the current content rating."""
        self.current_rating = rating
    
    def get_snippets_for_field(self, field_name: str, content_rating: str = "PG") -> Optional[Dict[str, List[str]]]:
        """Get snippets for a specific field based on content rating."""
        # Convert string rating to ContentRating enum
        try:
            rating_enum = ContentRating[content_rating.upper()]
        except KeyError:
            rating_enum = ContentRating.PG
        
        # Check user snippets first
        if field_name in self.user_snippets:
            user_data = self.user_snippets[field_name]
            if self._is_rating_appropriate_for_rating(user_data.get("rating", "PG"), rating_enum):
                return user_data.get("categories", {})
        
        # Fall back to default snippets
        if field_name in self.default_snippets:
            default_data = self.default_snippets[field_name]
            if self._is_rating_appropriate_for_rating(default_data.get("rating", "PG"), rating_enum):
                return default_data.get("categories", {})
        
        return None
    
    def _is_rating_appropriate(self, snippet_rating: str) -> bool:
        """Check if a snippet's rating is appropriate for current content rating."""
        return self._is_rating_appropriate_for_rating(snippet_rating, self.current_rating)
    
    def _is_rating_appropriate_for_rating(self, snippet_rating: str, content_rating: ContentRating) -> bool:
        """Check if a snippet's rating is appropriate for a given content rating."""
        rating_hierarchy = {
            ContentRating.PG: ["PG"],
            ContentRating.NSFW: ["PG", "NSFW"],
            ContentRating.HENTAI: ["PG", "NSFW", "Hentai"]
        }
        
        current_allowed = rating_hierarchy.get(content_rating, ["PG"])
        return snippet_rating in current_allowed
    
    def add_snippet(self, field_name: str, category: str, snippet: str, rating: str = "PG"):
        """Add a new snippet to user snippets."""
        if field_name not in self.user_snippets:
            self.user_snippets[field_name] = {
                "rating": rating,
                "categories": {}
            }
        
        if category not in self.user_snippets[field_name]["categories"]:
            self.user_snippets[field_name]["categories"][category] = []
        
        if snippet not in self.user_snippets[field_name]["categories"][category]:
            self.user_snippets[field_name]["categories"][category].append(snippet)
            self._save_field_snippets(field_name)
    
    def remove_snippet(self, field_name: str, category: str, snippet: str):
        """Remove a snippet from user snippets."""
        if (field_name in self.user_snippets and 
            category in self.user_snippets[field_name]["categories"] and
            snippet in self.user_snippets[field_name]["categories"][category]):
            
            self.user_snippets[field_name]["categories"][category].remove(snippet)
            self._save_field_snippets(field_name)
    
    def _save_field_snippets(self, field_name: str):
        """Save snippets for a specific field to JSON file."""
        if field_name in self.user_snippets:
            file_path = self.snippets_dir / f"{field_name}.json"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.user_snippets[field_name], f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving snippets for {field_name}: {e}")
    
    def get_user_data_dir(self) -> Path:
        """Get the user data directory path."""
        return self.user_data_dir
    
    def get_snippets_dir(self) -> Path:
        """Get the snippets directory path."""
        return self.snippets_dir
    
    def export_snippets(self, file_path: Path):
        """Export all user snippets to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_snippets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error exporting snippets: {e}")
    
    def import_snippets(self, file_path: Path):
        """Import snippets from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_snippets = json.load(f)
            
            for field_name, field_data in imported_snippets.items():
                self.user_snippets[field_name] = field_data
                self._save_field_snippets(field_name)
        except Exception as e:
            print(f"Error importing snippets: {e}")


# Global snippet manager instance
snippet_manager = SnippetManager()
