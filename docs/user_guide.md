# FlipFlopPrompt User Guide

## Getting Started

### Installation

1. **Prerequisites**: Python 3.8 or higher
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run the application**: `python main.py`

### Quick Start

1. **GUI Mode**: Run `python main.py` to start the graphical interface
2. **CLI Mode**: Use command-line arguments for automation

## GUI Interface

### Main Window Layout

The GUI is divided into several sections:

1. **Model Selection**: Choose your target AI model
2. **Input Fields**: Fill in the prompt components
3. **Action Buttons**: Generate, copy, save, and load prompts
4. **Preview Panel**: See your prompt in real-time

### Input Fields

#### Required Fields

- **Environment**: The setting or location (e.g., "interior, hotel lobby")
- **Subjects**: People or objects in the scene (e.g., "a 20yo man, a woman in her 40s")
- **Subjects Pose and Action**: What the subjects are doing (e.g., "The man stands looking at the woman")

#### Optional Fields

- **Weather**: Atmospheric conditions (e.g., "sunny with a few clouds")
- **Date and Time**: Time of day (e.g., "7am")
- **Camera**: Technical specifications (e.g., "shot on a 22mm lens on Arri Alexa")
- **Camera Framing and Action**: Camera movement and positioning (e.g., "camera dollies in")
- **Grading**: Color and style (e.g., "Fuji Xperia film look")

### Features

#### Real-time Preview
As you type in the input fields, the preview panel updates automatically to show how your prompt will look.

#### Model-Specific Formatting
Each AI model has its own optimal prompt format. The application automatically formats your input for the selected model.

#### Template System
- **Save Templates**: Click "Save Template" to save your current prompt as a reusable template
- **Load Templates**: Click "Load Template" to load a previously saved template
- **Template Files**: Templates are saved as JSON files for easy sharing

#### Copy to Clipboard
Click "Copy to Clipboard" to copy the generated prompt for use in other applications.

## Command Line Interface

### Basic Usage

```bash
# Generate a prompt for Seedream
python main.py --model seedream --environment "hotel lobby" --subjects "20yo man" --pose "standing"

# Generate JSON output for ComfyUI
python main.py --model veo --json --environment "interior" --weather "sunny" --time "7am"

# Use a template file
python main.py --template my_template.json

# List supported models
python main.py --list-models
```

### Command Line Options

#### Model Selection
- `--model, -m`: Choose target model (seedream, veo, flux, wan, hailuo)

#### Input Fields
- `--environment, -e`: Environment/setting
- `--weather, -w`: Weather conditions
- `--time, -t`: Date and time
- `--subjects, -s`: Subjects in the scene
- `--pose, -p`: Subject pose and action
- `--camera, -c`: Camera specifications
- `--framing, -f`: Camera framing and action
- `--grading, -g`: Color grading/style

#### Output Options
- `--json, -j`: Output in JSON format
- `--output, -o`: Output file path
- `--template, -T`: Load from template file

#### Utility Options
- `--list-models, -l`: List supported models
- `--validate, -V`: Validate input data
- `--preview, -P`: Show preview without model formatting
- `--verbose, -v`: Verbose output

## Supported Models

### Seedream 3.0
- **Best for**: Cinematic video generation
- **Strengths**: High-quality output, good with complex scenes
- **Format**: Structured with clear sections

### Google Veo
- **Best for**: Natural language descriptions
- **Strengths**: Understanding complex scenes, high quality
- **Format**: Flowing narrative style

### Stability AI Flux
- **Best for**: Creative and artistic content
- **Strengths**: Stylized output, artistic direction
- **Format**: Artistic and descriptive

### Wan
- **Best for**: Realistic video generation
- **Strengths**: Human interactions, detailed scenes
- **Format**: Realistic and natural

### Hailuo
- **Best for**: Versatile video generation
- **Strengths**: Various styles, comprehensive descriptions
- **Format**: Detailed and structured

## ComfyUI Integration

### JSON Output
Use the `--json` flag to get output suitable for ComfyUI:

```bash
python main.py --model seedream --json --environment "hotel lobby" --subjects "20yo man" --pose "standing"
```

### Output Format
The JSON output includes:
- `model`: Target model name
- `prompt`: Generated prompt text
- `data`: Original input data
- `metadata`: Generation information

### Integration Steps
1. Generate prompt with `--json` flag
2. Copy the JSON output
3. Use in ComfyUI nodes that accept JSON input
4. Extract the `prompt` field for use

## Tips for Better Prompts

### Environment Descriptions
- Be specific about location and setting
- Include relevant details (lighting, atmosphere)
- Mention architectural or environmental features

### Subject Descriptions
- Include age, gender, clothing, appearance
- Describe multiple subjects clearly
- Mention background characters if relevant

### Action Descriptions
- Be specific about movements and interactions
- Include emotional context
- Describe timing and sequence

### Camera Specifications
- Include lens focal length
- Mention camera brand/model
- Specify technical details

### Visual Style
- Reference specific film stocks or looks
- Describe color grading preferences
- Mention lighting style

## Troubleshooting

### Common Issues

#### GUI Not Starting
- Check Python version (3.8+ required)
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- Try CLI mode as fallback

#### Import Errors
- Install dependencies: `pip install -r requirements.txt`
- Check Python path and virtual environment

#### Validation Errors
- Fill in all required fields
- Check field length requirements
- Ensure proper formatting

#### Model Not Supported
- Use `--list-models` to see available models
- Check model name spelling
- Update to latest version

### Getting Help

- **Documentation**: Check the docs folder
- **Examples**: Look at template files
- **CLI Help**: Use `python main.py --help`
- **Verbose Mode**: Use `--verbose` flag for detailed output

## Advanced Features

### Configuration
The application creates a config file at `~/.flipflopprompt/config.json` with user preferences.

### Template Library
Create and share template files for common prompt types.

### Batch Processing
Use CLI mode with scripts for batch prompt generation.

### Custom Model Adapters
Extend the application with custom model adapters for new AI models.
