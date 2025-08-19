"""
Command-line interface for FlipFlopPrompt.
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional

from ..core.prompt_engine import PromptEngine
from ..core.data_models import PromptData


class CLIInterface:
    """Command-line interface for FlipFlopPrompt."""
    
    def __init__(self):
        self.prompt_engine = PromptEngine()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="FlipFlopPrompt - AI Model Prompt Formulation Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Generate a prompt for Seedream
  python main.py --model seedream --environment "hotel lobby" --subjects "20yo man" --pose "standing"

  # Generate JSON output for ComfyUI
  python main.py --model veo --json --environment "interior" --weather "sunny" --time "7am"

  # Use a template file
  python main.py --template my_template.json

  # List supported models
  python main.py --list-models
            """
        )
        
        # Model selection
        parser.add_argument(
            '--model', '-m',
            choices=self.prompt_engine.get_supported_models(),
            default='seedream',
            help='Target AI model (default: seedream)'
        )
        
        # Input fields
        parser.add_argument(
            '--environment', '-e',
            help='Environment/setting (e.g., "interior, hotel lobby")'
        )
        
        parser.add_argument(
            '--weather', '-w',
            help='Weather conditions (e.g., "sunny with a few clouds")'
        )
        
        parser.add_argument(
            '--time', '-t',
            help='Date and time (e.g., "7am")'
        )
        
        parser.add_argument(
            '--subjects', '-s',
            help='Subjects in the scene (e.g., "a 20yo man, a woman in her 40s")'
        )
        
        parser.add_argument(
            '--pose', '-p',
            help='Subject pose and action (e.g., "The man stands looking at the woman")'
        )
        
        parser.add_argument(
            '--camera', '-c',
            help='Camera specifications (e.g., "shot on a 22mm lens on Arri Alexa")'
        )
        
        parser.add_argument(
            '--framing', '-f',
            help='Camera framing and action (e.g., "camera dollies in")'
        )
        
        parser.add_argument(
            '--grading', '-g',
            help='Color grading/style (e.g., "Fuji Xperia film look")'
        )
        
        parser.add_argument(
            '--llm-model',
            help='LLM model to use for refinement (e.g., deepseek-r1:8b, gemma3:4b)'
        )
        
        parser.add_argument(
            '--content-rating',
            choices=['PG', 'NSFW', 'Hentai'],
            default='PG',
            help='Content rating for the prompt (default: PG)'
        )
        
        # Output options
        parser.add_argument(
            '--json', '-j',
            action='store_true',
            help='Output in JSON format (useful for ComfyUI integration)'
        )
        
        parser.add_argument(
            '--output', '-o',
            help='Output file path (default: stdout)'
        )
        
        parser.add_argument(
            '--template', '-T',
            help='Load prompt data from template file'
        )
        
        # Utility options
        parser.add_argument(
            '--list-models', '-l',
            action='store_true',
            help='List all supported models and exit'
        )
        
        parser.add_argument(
            '--validate', '-V',
            action='store_true',
            help='Validate input data without generating prompt'
        )
        
        parser.add_argument(
            '--preview', '-P',
            action='store_true',
            help='Show preview without model-specific formatting'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Verbose output'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI interface.
        
        Args:
            args: Command line arguments (if None, uses sys.argv)
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            parsed_args = self.parser.parse_args(args)
            
            # Handle special commands
            if parsed_args.list_models:
                self._list_models()
                return 0
            
            # Update LLM model if specified
            if parsed_args.llm_model:
                self.prompt_engine.update_llm_model(parsed_args.llm_model)
            
            # Load template if specified
            if parsed_args.template:
                prompt_data = self._load_template(parsed_args.template)
            else:
                # Create prompt data from arguments
                prompt_data = self._create_prompt_data(parsed_args)
            
            # Validate data if requested
            if parsed_args.validate:
                return self._validate_data(prompt_data)
            
            # Generate output
            if parsed_args.preview:
                output = self.prompt_engine.get_prompt_preview(prompt_data)
            else:
                output = self.prompt_engine.generate_prompt(parsed_args.model, prompt_data, parsed_args.content_rating)
            
            # Format output
            if parsed_args.json:
                output_data = self._create_json_output(parsed_args.model, prompt_data, output)
                output = json.dumps(output_data, indent=2)
            
            # Write output
            self._write_output(output, parsed_args.output)
            
            if parsed_args.verbose:
                print(f"Generated prompt for {parsed_args.model} model", file=sys.stderr)
            
            return 0
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            if '--verbose' in (args or sys.argv):
                import traceback
                traceback.print_exc()
            return 1
    
    def _list_models(self):
        """List all supported models."""
        print("Supported Models:")
        print("=" * 50)
        
        for model_name in self.prompt_engine.get_supported_models():
            adapter = self.prompt_engine.model_adapters[model_name]
            info = adapter.get_model_info()
            
            print(f"\n{model_name.upper()}")
            print(f"  Description: {info['description']}")
            print(f"  Features: {', '.join(info['supported_features'])}")
        
        # Show LLM status
        print("\n" + "=" * 50)
        print("LLM Integration Status:")
        
        llm_info = self.prompt_engine.get_llm_info()
        if llm_info["available"]:
            print(f"  ✓ LLM Available: {llm_info['provider']}")
            print(f"  ✓ Ollama: {'Available' if llm_info.get('ollama_available') else 'Not available'}")
            print("  ✓ Prompts will be refined using LLM for better quality")
        else:
            print("  ✗ No LLM provider available")
            print("  ✗ Install Ollama to use LLM features")
            print("  ✗ Prompts will use basic adapter formatting")
    
    def _create_prompt_data(self, args) -> PromptData:
        """Create PromptData from command line arguments."""
        return PromptData(
            environment=args.environment or "",
            weather=args.weather or "",
            date_time=args.time or "",
            subjects=args.subjects or "",
            pose_action=args.pose or "",
            camera=args.camera or "",
            framing_action=args.framing or "",
            grading=args.grading or ""
        )
    
    def _load_template(self, template_path: str) -> PromptData:
        """Load prompt data from template file."""
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            if 'data' not in template_data:
                raise ValueError("Template file must contain 'data' field")
            
            return PromptData.from_dict(template_data['data'])
            
        except FileNotFoundError:
            raise ValueError(f"Template file not found: {template_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in template file: {template_path}")
    
    def _validate_data(self, prompt_data: PromptData) -> int:
        """Validate prompt data and return exit code."""
        errors = self.prompt_engine.validate_prompt_data(prompt_data)
        
        if errors:
            print("Validation Errors:", file=sys.stderr)
            for error in errors:
                print(f"  • {error}", file=sys.stderr)
            return 1
        else:
            print("✓ All data is valid", file=sys.stderr)
            return 0
    
    def _create_json_output(self, model: str, prompt_data: PromptData, final_prompt: str) -> Dict[str, Any]:
        """Create JSON output for ComfyUI integration."""
        return {
            'model': model,
            'prompt': final_prompt,
            'data': prompt_data.to_dict(),
            'metadata': {
                'generator': 'FlipFlopPrompt',
                'version': '0.1.0',
                'timestamp': self._get_timestamp()
            }
        }
    
    def _write_output(self, output: str, output_path: Optional[str]):
        """Write output to file or stdout."""
        if output_path:
            with open(output_path, 'w') as f:
                f.write(output)
        else:
            print(output)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Main entry point for CLI."""
    cli = CLIInterface()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
