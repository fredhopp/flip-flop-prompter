# Flip-Flop Prompter

A Python-based tool for formulating prompts for various text-to-image and text-to-video AI models including Seedream, Veo, Flux, Wan, and Hailuo.

> **🤖 AI-Generated Project**: This entire project was created with the assistance of **Cursor**, an AI-powered code editor and development assistant. The codebase, architecture, documentation, and implementation were all developed through (limited) human-AI collaboration.

## ⚠️ Important: Ollama Requirement

**This tool requires [Ollama](https://ollama.ai/) to be installed and running locally for LLM-powered prompt refinement.**

- **Ollama Server**: Must be running on `localhost:11434` for LLM integration
- **Local LLM Models**: Uses your local Ollama models (e.g., `deepseek-r1:8b`, `gemma3:4b`)
- **Fallback Mode**: Works without Ollama using basic prompt formatting
- **No Cloud Dependencies**: All LLM processing happens locally on your machine

If you don't have Ollama installed or don't want to use local LLMs, the tool will fall back to basic prompt concatenation.

## Features

- **GUI Interface**: User-friendly graphical interface with structured input fields
- **CLI Interface**: Command-line interface for automation and ComfyUI integration
- **LLM-Powered Refinement**: Uses local Ollama models for intelligent prompt optimization
- **Model-Specific Optimization**: Tailored prompt formatting for each supported model
- **Real-time Preview**: See your prompt as you build it
- **Template System**: Save and reuse prompt templates
- **Export Options**: Copy to clipboard or export in various formats
- **Local Processing**: All LLM operations happen locally via Ollama

## Supported Models

- **Seedream 3.0**: Based on technical documentation
- **Veo**: Google's text-to-video model
- **Flux**: Stability AI's video model
- **Wan**: Video generation model
- **Hailuo**: Text-to-video model

## Installation

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- **[Ollama](https://ollama.ai/)** (for LLM-powered prompt refinement)
  - Install from [ollama.ai](https://ollama.ai/)
  - Pull at least one model: `ollama pull deepseek-r1:8b`
  - Start the server: `ollama serve`

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/flip-flop-prompter.git
cd flip-flop-prompter

# Install dependencies
pip install -r requirements.txt

# Start Ollama server (required for LLM features)
ollama serve

# In another terminal, pull a model (optional but recommended)
ollama pull deepseek-r1:8b

# Run the application
python main.py
```

## Usage

### GUI Mode
```bash
python main.py --gui
```
Or simply:
```bash
python main.py
```

### CLI Mode
```bash
python main.py --model seedream \
    --environment "hotel lobby" \
    --weather "sunny with a few clouds" \
    --time "7am" \
    --subjects "a 20yo man, a woman in her 40s" \
    --pose "The man stands looking at the woman who is seated on a lounge" \
    --camera "shot on a 22mm lens on Arri Alexa" \
    --framing "The camera starts 5m away and dollies in" \
    --grading "color should look like captured on Fuji Xperia film"
```

### ComfyUI Integration
```bash
python main.py --model seedream --json --environment "hotel lobby" --subjects "20yo man" --pose "standing"
```

## Input Fields

1. **Environment**: Setting and location (e.g., "interior, hotel lobby")
2. **Weather**: Atmospheric conditions (e.g., "sunny with a few clouds")
3. **Date and Time**: Time of day (e.g., "7am")
4. **Subjects**: People or objects in the scene (e.g., "a 20yo man, a woman in her 40s")
5. **Subjects Pose and Action**: What the subjects are doing (e.g., "The man stands looking at the woman")
6. **Camera**: Technical specifications (e.g., "shot on a 22mm lens on Arri Alexa")
7. **Camera Framing and Action**: Camera movement and positioning (e.g., "camera dollies in")
8. **Grading**: Color and style (e.g., "Fuji Xperia film look")

## Development

### Project Structure
```
flip-flop-prompter/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
├── templates/     # Prompt templates
└── main.py        # Entry point
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Cursor AI** - This entire project was created with the assistance of Cursor, an AI-powered code editor and development assistant
- Seedream team for their technical documentation
- The open-source AI community for inspiration
- ComfyUI community for integration ideas
