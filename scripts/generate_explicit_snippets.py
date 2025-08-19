#!/usr/bin/env python3
"""
Script to generate NSFW and Hentai snippets for the snippet manager.
This script creates explicit content snippets for adult scenarios.
"""

import json
import sys
from pathlib import Path
import os

# Get the user data directory for snippets
def get_user_data_dir():
    """Get the user data directory for storing snippets."""
    if sys.platform == "win32":
        # Windows
        return Path.home() / "AppData" / "Local" / "FlipFlopPrompt" / "snippets"
    elif sys.platform == "darwin":
        # macOS
        return Path.home() / "Library" / "Application Support" / "FlipFlopPrompt" / "snippets"
    else:
        # Linux
        return Path.home() / ".local" / "share" / "FlipFlopPrompt" / "snippets"

def generate_nsfw_snippets():
    """Generate NSFW snippets."""
    nsfw_snippets = {
        "subjects_pose_and_action": {
            "rating": "NSFW",
            "categories": {
                "Intimate Actions": [
                    "kissing passionately",
                    "embracing intimately",
                    "touching sensually",
                    "caressing gently",
                    "holding close",
                    "whispering seductively",
                    "gazing into eyes",
                    "stroking hair",
                    "massaging shoulders",
                    "dancing seductively"
                ],
                "Suggestive Poses": [
                    "leaning seductively",
                    "posing provocatively",
                    "striking a sensual pose",
                    "displaying curves",
                    "showing skin",
                    "wearing revealing clothing",
                    "in lingerie",
                    "partially undressed",
                    "wearing tight clothing",
                    "showing cleavage"
                ],
                "Adult Interactions": [
                    "flirting suggestively",
                    "making advances",
                    "being seductive",
                    "showing interest",
                    "being playful",
                    "teasing gently",
                    "being coy",
                    "showing desire",
                    "being passionate",
                    "being romantic"
                ]
            }
        },
        "environment": {
            "rating": "NSFW",
            "categories": {
                "Intimate Settings": [
                    "bedroom",
                    "hotel room",
                    "private suite",
                    "romantic restaurant",
                    "dimly lit bar",
                    "secluded beach",
                    "private garden",
                    "luxury apartment",
                    "penthouse",
                    "private club"
                ],
                "Atmospheric Lighting": [
                    "candlelight",
                    "soft mood lighting",
                    "dim ambient light",
                    "romantic lighting",
                    "warm golden light",
                    "intimate lighting",
                    "sultry atmosphere",
                    "seductive lighting",
                    "passionate lighting",
                    "romantic glow"
                ]
            }
        },
        "color_grading_&_mood": {
            "rating": "NSFW",
            "categories": {
                "Adult Moods": [
                    "sensual",
                    "passionate",
                    "romantic",
                    "seductive",
                    "intimate",
                    "sultry",
                    "alluring",
                    "tempting",
                    "desirable",
                    "enticing"
                ],
                "Adult Styles": [
                    "romantic",
                    "passionate",
                    "sensual",
                    "seductive",
                    "intimate",
                    "adult",
                    "mature",
                    "sophisticated",
                    "elegant",
                    "luxurious"
                ]
            }
        }
    }
    
    return nsfw_snippets


def generate_hentai_snippets():
    """Generate Hentai snippets with explicit content."""
    hentai_snippets = {
        "subjects_pose_and_action": {
            "rating": "Hentai",
            "categories": {
                "Explicit Actions": [
                    "naked",
                    "completely nude",
                    "wearing only underwear",
                    "in revealing lingerie",
                    "partially clothed",
                    "showing full body",
                    "displaying everything",
                    "in compromising position",
                    "being intimate",
                    "engaging in adult activities"
                ],
                "Explicit Poses": [
                    "spread eagle",
                    "on all fours",
                    "bent over",
                    "lying seductively",
                    "posing provocatively",
                    "showing private parts",
                    "exposing body",
                    "in sexual position",
                    "being submissive",
                    "being dominant"
                ],
                "Adult Toys": [
                    "using vibrator",
                    "with dildo",
                    "using sex toys",
                    "with handcuffs",
                    "wearing collar",
                    "with blindfold",
                    "using restraints",
                    "with lubricant",
                    "using strap-on",
                    "with anal beads"
                ],
                "Explicit Scenarios": [
                    "masturbating",
                    "self-pleasuring",
                    "touching intimately",
                    "exploring body",
                    "being aroused",
                    "showing excitement",
                    "being wet",
                    "showing erection",
                    "being hard",
                    "showing desire"
                ]
            }
        },
        "environment": {
            "rating": "Hentai",
            "categories": {
                "Adult Locations": [
                    "bedroom with toys",
                    "sex dungeon",
                    "adult club",
                    "strip club",
                    "brothel",
                    "adult store",
                    "private studio",
                    "adult theater",
                    "swinger club",
                    "adult resort"
                ],
                "Adult Props": [
                    "sex toys scattered",
                    "adult furniture",
                    "bondage equipment",
                    "mirrors on walls",
                    "adult posters",
                    "lubricant bottles",
                    "condom wrappers",
                    "adult magazines",
                    "pornographic art",
                    "adult decorations"
                ]
            }
        },
        "subjects": {
            "rating": "Hentai",
            "categories": {
                "Adult Descriptions": [
                    "naked woman",
                    "nude man",
                    "stripper",
                    "escort",
                    "prostitute",
                    "porn star",
                    "adult model",
                    "sex worker",
                    "exotic dancer",
                    "adult performer"
                ],
                "Body Types": [
                    "curvy woman",
                    "muscular man",
                    "petite girl",
                    "well-endowed",
                    "large breasts",
                    "big penis",
                    "tight body",
                    "toned muscles",
                    "slim figure",
                    "voluptuous curves"
                ],
                "Adult Clothing": [
                    "lingerie",
                    "thong",
                    "g-string",
                    "fishnet stockings",
                    "corset",
                    "bustier",
                    "garter belt",
                    "stockings",
                    "high heels",
                    "adult costume"
                ]
            }
        },
        "color_grading_&_mood": {
            "rating": "Hentai",
            "categories": {
                "Explicit Moods": [
                    "aroused",
                    "horny",
                    "lustful",
                    "passionate",
                    "desperate",
                    "needy",
                    "wild",
                    "uninhibited",
                    "dirty",
                    "naughty"
                ],
                "Adult Styles": [
                    "pornographic",
                    "explicit",
                    "adult content",
                    "hentai style",
                    "anime porn",
                    "adult animation",
                    "explicit art",
                    "adult illustration",
                    "porn art",
                    "adult manga"
                ]
            }
        }
    }
    
    return hentai_snippets


def save_snippets_to_files(snippets, rating):
    """Save snippets to individual JSON files."""
    snippets_dir = get_user_data_dir()
    snippets_dir.mkdir(parents=True, exist_ok=True)
    
    for field_name, field_data in snippets.items():
        file_path = snippets_dir / f"{field_name}_{rating.lower()}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(field_data, f, indent=2, ensure_ascii=False)
            print(f"Saved {field_name}_{rating.lower()}.json")
        except Exception as e:
            print(f"Error saving {field_name}_{rating.lower()}.json: {e}")


def main():
    """Generate and save explicit snippets."""
    print("Generating NSFW snippets...")
    nsfw_snippets = generate_nsfw_snippets()
    save_snippets_to_files(nsfw_snippets, "NSFW")
    
    print("\nGenerating Hentai snippets...")
    hentai_snippets = generate_hentai_snippets()
    save_snippets_to_files(hentai_snippets, "Hentai")
    
    snippets_dir = get_user_data_dir()
    print(f"\nSnippets saved to: {snippets_dir}")
    print("\nTo use these snippets:")
    print("1. Copy the desired rating files to the main snippet files")
    print("2. Or modify the snippet manager to load rating-specific files")
    print("3. Set the content rating in the application to see appropriate snippets")


if __name__ == "__main__":
    main()
