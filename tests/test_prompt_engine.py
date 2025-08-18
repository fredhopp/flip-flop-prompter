"""
Unit tests for the prompt engine.
"""

import unittest
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.prompt_engine import PromptEngine, PromptData


class TestPromptData(unittest.TestCase):
    """Test cases for PromptData class."""
    
    def test_prompt_data_creation(self):
        """Test creating PromptData with default values."""
        data = PromptData()
        self.assertEqual(data.environment, "")
        self.assertEqual(data.subjects, "")
        self.assertEqual(data.pose_action, "")
    
    def test_prompt_data_with_values(self):
        """Test creating PromptData with specific values."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man",
            pose_action="standing"
        )
        self.assertEqual(data.environment, "hotel lobby")
        self.assertEqual(data.subjects, "a man")
        self.assertEqual(data.pose_action, "standing")
    
    def test_to_dict(self):
        """Test converting PromptData to dictionary."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man",
            pose_action="standing"
        )
        result = data.to_dict()
        
        expected = {
            'environment': 'hotel lobby',
            'weather': '',
            'date_time': '',
            'subjects': 'a man',
            'pose_action': 'standing',
            'camera': '',
            'framing_action': '',
            'grading': ''
        }
        
        self.assertEqual(result, expected)
    
    def test_from_dict(self):
        """Test creating PromptData from dictionary."""
        data_dict = {
            'environment': 'hotel lobby',
            'subjects': 'a man',
            'pose_action': 'standing'
        }
        
        data = PromptData.from_dict(data_dict)
        self.assertEqual(data.environment, "hotel lobby")
        self.assertEqual(data.subjects, "a man")
        self.assertEqual(data.pose_action, "standing")


class TestPromptEngine(unittest.TestCase):
    """Test cases for PromptEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = PromptEngine()
    
    def test_initialization(self):
        """Test PromptEngine initialization."""
        self.assertIsNotNone(self.engine.model_adapters)
        self.assertIn('seedream', self.engine.model_adapters)
        self.assertIn('veo', self.engine.model_adapters)
    
    def test_get_supported_models(self):
        """Test getting list of supported models."""
        models = self.engine.get_supported_models()
        expected_models = ['seedream', 'veo', 'flux', 'wan', 'hailuo']
        
        for model in expected_models:
            self.assertIn(model, models)
    
    def test_validate_prompt_data_empty(self):
        """Test validation with empty data."""
        data = PromptData()
        errors = self.engine.validate_prompt_data(data)
        
        self.assertIn("Environment is required", errors)
        self.assertIn("Subjects are required", errors)
        self.assertIn("Subject pose and action is required", errors)
    
    def test_validate_prompt_data_valid(self):
        """Test validation with valid data."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man",
            pose_action="standing and looking around"
        )
        errors = self.engine.validate_prompt_data(data)
        
        self.assertEqual(len(errors), 0)
    
    def test_validate_prompt_data_short_descriptions(self):
        """Test validation with short descriptions."""
        data = PromptData(
            environment="a",  # Too short
            subjects="b",     # Too short
            pose_action="c"   # Too short
        )
        errors = self.engine.validate_prompt_data(data)
        
        self.assertIn("Environment description should be more detailed", errors)
        self.assertIn("Subject description should be more detailed", errors)
    
    def test_get_prompt_preview(self):
        """Test generating prompt preview."""
        data = PromptData(
            environment="hotel lobby",
            weather="sunny",
            subjects="a man",
            pose_action="standing"
        )
        
        preview = self.engine.get_prompt_preview(data)
        
        self.assertIn("Setting: hotel lobby", preview)
        self.assertIn("Weather: sunny", preview)
        self.assertIn("Subjects: a man", preview)
        self.assertIn("Action: standing", preview)
    
    def test_get_prompt_preview_empty(self):
        """Test generating preview with empty data."""
        data = PromptData()
        preview = self.engine.get_prompt_preview(data)
        
        self.assertEqual(preview, "")
    
    def test_generate_prompt_invalid_model(self):
        """Test generating prompt with invalid model."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man",
            pose_action="standing"
        )
        
        with self.assertRaises(ValueError):
            self.engine.generate_prompt("invalid_model", data)
    
    def test_generate_prompt_valid(self):
        """Test generating prompt with valid model."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man",
            pose_action="standing"
        )
        
        prompt = self.engine.generate_prompt("seedream", data)
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_export_prompt_data_json(self):
        """Test exporting prompt data as JSON."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man"
        )
        
        result = self.engine.export_prompt_data(data, 'json')
        
        self.assertIn('"environment": "hotel lobby"', result)
        self.assertIn('"subjects": "a man"', result)
    
    def test_export_prompt_data_text(self):
        """Test exporting prompt data as text."""
        data = PromptData(
            environment="hotel lobby",
            subjects="a man"
        )
        
        result = self.engine.export_prompt_data(data, 'text')
        
        self.assertIn("Setting: hotel lobby", result)
        self.assertIn("Subjects: a man", result)
    
    def test_export_prompt_data_invalid_format(self):
        """Test exporting with invalid format."""
        data = PromptData()
        
        with self.assertRaises(ValueError):
            self.engine.export_prompt_data(data, 'invalid_format')
    
    def test_import_prompt_data_json(self):
        """Test importing prompt data from JSON."""
        json_data = '{"environment": "hotel lobby", "subjects": "a man"}'
        
        data = self.engine.import_prompt_data(json_data, 'json')
        
        self.assertEqual(data.environment, "hotel lobby")
        self.assertEqual(data.subjects, "a man")
    
    def test_import_prompt_data_invalid_format(self):
        """Test importing with invalid format."""
        with self.assertRaises(ValueError):
            self.engine.import_prompt_data("data", 'invalid_format')


if __name__ == '__main__':
    unittest.main()
