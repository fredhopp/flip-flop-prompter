# FlipFlopPrompt - AI Model Prompt Formulation Tool

## Project Overview
A Python-based application that helps formulate prompts for various text-to-image and text-to-video models (Seedream, Veo, Flux, Wan, Hailuo) with both GUI and CLI interfaces.

## Target Models & Research Status
- **Seedream**: Technical documentation available (arXiv:2504.11346)
- **Veo**: Research needed for official prompt guidelines
- **Flux**: Research needed for official prompt guidelines  
- **Wan**: Research needed for official prompt guidelines
- **Hailuo**: Research needed for official prompt guidelines

## Technical Architecture

### Core Components
1. **Prompt Engine**: Core logic for prompt generation and model-specific formatting
2. **GUI Interface**: Tkinter-based user interface
3. **CLI Interface**: Command-line interface for ComfyUI integration
4. **Model Adapters**: Model-specific prompt formatting logic
5. **LLM Integration**: Optional AI-powered prompt refinement

### Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (built-in, lightweight, cross-platform)
- **CLI Framework**: argparse (built-in)
- **Optional LLM**: OpenAI GPT API for prompt refinement
- **Packaging**: PyInstaller for distribution

## Development Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Project structure setup
- [ ] Basic prompt engine implementation
- [ ] Model research and documentation gathering
- [ ] Unit testing framework

### Phase 2: GUI Development (Week 2)
- [ ] Tkinter GUI with all required fields
- [ ] Field validation and formatting
- [ ] Real-time preview functionality
- [ ] Save/load prompt templates

### Phase 3: CLI Interface (Week 3)
- [ ] Command-line argument parsing
- [ ] ComfyUI integration scripts
- [ ] Batch processing capabilities

### Phase 4: Model-Specific Features (Week 4)
- [ ] Model adapter implementations
- [ ] Prompt optimization for each model
- [ ] Model-specific validation rules

### Phase 5: Advanced Features (Week 5)
- [ ] LLM integration for prompt refinement
- [ ] Template library
- [ ] Export/import functionality

### Phase 6: Testing & Deployment (Week 6)
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Packaging and distribution

## File Structure
```
FlipFlopPrompt/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── prompt_engine.py
│   │   ├── model_adapters.py
│   │   └── llm_integration.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── field_widgets.py
│   │   └── preview_panel.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── command_line.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── test_prompt_engine.py
│   ├── test_model_adapters.py
│   └── test_gui.py
├── docs/
│   ├── user_guide.md
│   ├── api_reference.md
│   └── model_specifics.md
├── templates/
│   ├── seedream_prompts.json
│   ├── veo_prompts.json
│   └── ...
├── requirements.txt
├── setup.py
├── main.py
└── README.md
```

## GUI Field Specifications

### Required Fields
1. **Environment** (Text Input)
   - Example: "interior, hotel lobby"
   - Validation: Non-empty, descriptive

2. **Weather** (Text Input)
   - Example: "sunny with a few clouds"
   - Validation: Optional, descriptive

3. **Date and Time** (DateTime Picker)
   - Example: "7am"
   - Format: 12/24 hour format

4. **Subjects** (Text Area)
   - Example: "a 20yo man, a woman in her 40s"
   - Validation: Non-empty, comma-separated

5. **Subjects Pose and Action** (Text Area)
   - Example: "The man stands looking at the woman who is seated on a lounge"
   - Validation: Descriptive actions

6. **Camera** (Text Input)
   - Example: "shot on a 22mm lens on Arri Alexa"
   - Validation: Technical specifications

7. **Camera Framing and Action** (Text Area)
   - Example: "The camera starts 5m away and dollies in"
   - Validation: Movement descriptions

8. **Grading** (Text Input)
   - Example: "color should look like captured on Fuji Xperia film"
   - Validation: Color/style descriptions

### Output Display
- Real-time preview at bottom of GUI
- Copy-to-clipboard functionality
- Export options (text, JSON)

## CLI Interface Design

### Command Structure
```bash
python main.py --model seedream --environment "hotel lobby" --weather "sunny" --time "7am" --subjects "20yo man, woman in 40s" --pose "man stands looking at woman" --camera "22mm lens Arri Alexa" --framing "camera dollies in" --grading "Fuji Xperia film"
```

### ComfyUI Integration
- Script that can be called from ComfyUI nodes
- JSON output format for easy parsing
- Batch processing capabilities

## Model-Specific Considerations

### Seedream 3.0
- Based on technical report analysis
- Specific prompt structure requirements
- Image quality parameters

### Veo, Flux, Wan, Hailuo
- Research needed for optimal prompt formats
- Model-specific keywords and parameters
- Quality and style preferences

## Success Metrics
- [ ] All target models supported
- [ ] GUI responsive and user-friendly
- [ ] CLI integration with ComfyUI working
- [ ] Prompt quality improvement measurable
- [ ] Cross-platform compatibility
- [ ] Comprehensive documentation

## Risk Mitigation
- **Model API Changes**: Modular adapter design
- **GUI Complexity**: Start simple, iterate
- **LLM Integration**: Optional feature, fallback to rule-based
- **Performance**: Optimize for real-time preview
- **Compatibility**: Test on multiple platforms

## Next Steps
1. Set up development environment
2. Research model-specific documentation
3. Create basic project structure
4. Implement core prompt engine
5. Build minimal GUI prototype
