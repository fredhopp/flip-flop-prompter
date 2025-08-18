"""
Validation utilities for FlipFlopPrompt.
"""

import re
from typing import List, Dict, Any, Optional
from ..core.data_models import PromptData


class Validator:
    """Validation utilities for prompt data and user inputs."""
    
    @staticmethod
    def validate_prompt_data(prompt_data: PromptData) -> List[str]:
        """
        Validate prompt data and return list of errors.
        
        Args:
            prompt_data: Prompt data to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Required fields
        if not prompt_data.environment.strip():
            errors.append("Environment is required")
        
        if not prompt_data.subjects.strip():
            errors.append("Subjects are required")
        
        if not prompt_data.pose_action.strip():
            errors.append("Subject pose and action is required")
        
        # Field-specific validation
        errors.extend(Validator._validate_environment(prompt_data.environment))
        errors.extend(Validator._validate_subjects(prompt_data.subjects))
        errors.extend(Validator._validate_pose_action(prompt_data.pose_action))
        errors.extend(Validator._validate_camera(prompt_data.camera))
        errors.extend(Validator._validate_framing_action(prompt_data.framing_action))
        errors.extend(Validator._validate_grading(prompt_data.grading))
        errors.extend(Validator._validate_weather(prompt_data.weather))
        errors.extend(Validator._validate_date_time(prompt_data.date_time))
        
        return errors
    
    @staticmethod
    def _validate_environment(environment: str) -> List[str]:
        """Validate environment field."""
        errors = []
        
        if environment and len(environment.strip()) < 3:
            errors.append("Environment description should be at least 3 characters")
        
        if environment and len(environment.strip()) > 200:
            errors.append("Environment description should be less than 200 characters")
        
        return errors
    
    @staticmethod
    def _validate_subjects(subjects: str) -> List[str]:
        """Validate subjects field."""
        errors = []
        
        if subjects and len(subjects.strip()) < 5:
            errors.append("Subject description should be at least 5 characters")
        
        if subjects and len(subjects.strip()) > 300:
            errors.append("Subject description should be less than 300 characters")
        
        # Check for common subject patterns
        if subjects:
            subject_text = subjects.lower()
            if not any(word in subject_text for word in ['man', 'woman', 'person', 'people', 'child', 'boy', 'girl']):
                errors.append("Subject description should include people or characters")
        
        return errors
    
    @staticmethod
    def _validate_pose_action(pose_action: str) -> List[str]:
        """Validate pose and action field."""
        errors = []
        
        if pose_action and len(pose_action.strip()) < 10:
            errors.append("Pose and action description should be at least 10 characters")
        
        if pose_action and len(pose_action.strip()) > 500:
            errors.append("Pose and action description should be less than 500 characters")
        
        return errors
    
    @staticmethod
    def _validate_camera(camera: str) -> List[str]:
        """Validate camera field."""
        errors = []
        
        if camera and len(camera.strip()) < 5:
            errors.append("Camera description should be at least 5 characters")
        
        if camera and len(camera.strip()) > 200:
            errors.append("Camera description should be less than 200 characters")
        
        # Check for common camera terms
        if camera:
            camera_text = camera.lower()
            camera_terms = ['lens', 'mm', 'arri', 'alexa', 'red', 'canon', 'sony', 'shot', 'camera']
            if not any(term in camera_text for term in camera_terms):
                errors.append("Camera description should include technical specifications")
        
        return errors
    
    @staticmethod
    def _validate_framing_action(framing_action: str) -> List[str]:
        """Validate camera framing and action field."""
        errors = []
        
        if framing_action and len(framing_action.strip()) < 5:
            errors.append("Camera framing description should be at least 5 characters")
        
        if framing_action and len(framing_action.strip()) > 300:
            errors.append("Camera framing description should be less than 300 characters")
        
        return errors
    
    @staticmethod
    def _validate_grading(grading: str) -> List[str]:
        """Validate grading field."""
        errors = []
        
        if grading and len(grading.strip()) < 5:
            errors.append("Grading description should be at least 5 characters")
        
        if grading and len(grading.strip()) > 200:
            errors.append("Grading description should be less than 200 characters")
        
        return errors
    
    @staticmethod
    def _validate_weather(weather: str) -> List[str]:
        """Validate weather field."""
        errors = []
        
        if weather and len(weather.strip()) < 3:
            errors.append("Weather description should be at least 3 characters")
        
        if weather and len(weather.strip()) > 100:
            errors.append("Weather description should be less than 100 characters")
        
        return errors
    
    @staticmethod
    def _validate_date_time(date_time: str) -> List[str]:
        """Validate date and time field."""
        errors = []
        
        if date_time and len(date_time.strip()) < 2:
            errors.append("Date/time description should be at least 2 characters")
        
        if date_time and len(date_time.strip()) > 50:
            errors.append("Date/time description should be less than 50 characters")
        
        # Check for common time patterns
        if date_time:
            time_text = date_time.lower()
            time_patterns = [
                r'\d+am', r'\d+pm', r'\d+:\d+', r'morning', r'afternoon', 
                r'evening', r'night', r'dawn', r'dusk', r'sunrise', r'sunset'
            ]
            
            if not any(re.search(pattern, time_text) for pattern in time_patterns):
                errors.append("Date/time should include a time reference")
        
        return errors
    
    @staticmethod
    def validate_model_name(model_name: str) -> List[str]:
        """Validate model name."""
        errors = []
        
        valid_models = ['seedream', 'veo', 'flux', 'wan', 'hailuo']
        
        if not model_name:
            errors.append("Model name is required")
        elif model_name.lower() not in valid_models:
            errors.append(f"Invalid model name. Must be one of: {', '.join(valid_models)}")
        
        return errors
    
    @staticmethod
    def validate_file_path(file_path: str) -> List[str]:
        """Validate file path."""
        errors = []
        
        if not file_path:
            errors.append("File path is required")
        elif len(file_path) > 500:
            errors.append("File path is too long")
        
        # Check for invalid characters (basic check)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in file_path for char in invalid_chars):
            errors.append("File path contains invalid characters")
        
        return errors
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any]) -> List[str]:
        """
        Validate JSON structure for templates.
        
        Args:
            data: JSON data to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        required_fields = ['data']
        optional_fields = ['model', 'metadata']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check data structure
        if 'data' in data and isinstance(data['data'], dict):
            data_errors = Validator._validate_prompt_data_dict(data['data'])
            errors.extend(data_errors)
        elif 'data' in data:
            errors.append("Field 'data' must be an object")
        
        return errors
    
    @staticmethod
    def _validate_prompt_data_dict(data: Dict[str, Any]) -> List[str]:
        """Validate prompt data dictionary structure."""
        errors = []
        
        expected_fields = [
            'environment', 'weather', 'date_time', 'subjects', 
            'pose_action', 'camera', 'framing_action', 'grading'
        ]
        
        for field in expected_fields:
            if field not in data:
                errors.append(f"Missing field in data: {field}")
            elif not isinstance(data[field], str):
                errors.append(f"Field '{field}' must be a string")
        
        return errors
