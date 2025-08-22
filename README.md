
# Flip-Flop Prompter

A powerful AI image generation prompt builder with a clean, user-friendly interface. Create, refine, and save prompts for various AI image generation models.

## 🤖 **AI-Assisted Development**

**This project is developed with AI assistance using Cursor IDE and Claude Sonnet 4.**
- **Primary AI Assistant**: Claude Sonnet 4 (via Cursor IDE)
- **Development Environment**: Cursor IDE with AI code completion and assistance
- **AI Integration**: Continuous AI assistance for code review, bug fixes, feature implementation, and documentation
- **Development Approach**: Collaborative AI-human development with iterative refinement
- **AI Contributions**: Code architecture, bug fixes, feature implementation, documentation, testing, and optimization

## ✨ Features

### **Core Functionality**
- **LLM Integration**: Uses Ollama for local, free prompt refinement
- **Content Family System**: PG, NSFW, and Hentai families with appropriate filtering
- **Snippet System**: Quick selection from categorized prompt elements
- **Template System**: Save and load complete prompt configurations
- **Real-time Preview**: See your prompt as you build it
- **Realize Functionality**: Convert random category tags to specific snippet items

### **User Interface**
- **Modern PySide6 GUI**: Professional Qt-based interface with native look and feel
- **Dark/Light Theme Support**: Complete theme system with JSON-based customization
- **Tag-Based Input System**: Inline tags with color coding (blue=snippets, orange=categories, yellow=subcategories, purple=user text)
- **Real-time Preview**: Live preview with deterministic randomization
- **Realize Functionality**: Convert random category tags to specific snippet items
- **Professional Design**: Modern scrollbars, responsive layout, and optimized spacing

### **Data Management**
- **User Data Folders**: Automatic organization of snippets, templates, and preferences
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Persistent Settings**: Remembers your preferences between sessions
- **Debug System**: Optional detailed logging for troubleshooting

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8 or higher
- Ollama (for LLM functionality)

### **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FlipFlopPrompt.git
   cd FlipFlopPrompt
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Ollama (if using LLM features):
   ```bash
   ollama serve
   ```

### **Running the Application**
**PySide6 Interface (Standard):**
```bash
python main.py --debug  # With debug logging
python main.py          # Standard mode
```

## 📖 Usage

### **Basic Workflow**
1. **Set Content Families**: Select appropriate content families (PG/NSFW/Hentai) for snippet filtering
2. **Fill Fields**: Use the form fields to describe your image
3. **Use Snippets**: Click snippet buttons for quick suggestions
4. **Preview**: See your prompt in real-time
5. **Generate**: Click "Generate Prompt" for LLM refinement
6. **Realize**: Use the realize button (❗) to convert random tags to specific items
7. **Save**: Save your prompt or template for later use

### **Field Descriptions**
- **Style**: Art style (painting, photorealistic, anime, etc.)
- **Setting**: Environment and location
- **Weather**: Atmospheric conditions
- **Date and Time**: Season and time of day
- **Subjects**: Main subjects in the image
- **Pose and Action**: How subjects are positioned/acting
- **Camera**: Camera type and characteristics
- **Framing and Action**: Camera angle and movement
- **Color/Mood**: Visual style and atmosphere
- **Details**: Any extra information

### **Tag System**
- **Blue Tags**: Static snippet items (click to add/remove)
- **Orange Tags**: Random category tags (randomized on preview/generation)
- **Yellow Tags**: Random subcategory tags (randomized on preview/generation)
- **Purple Tags**: User-typed text (double-click to edit)
- **Realize Button (❗)**: Convert all random tags to specific items using current seed

### **Snippets**
- Click the "Snippets" button next to any field
- Browse categories and click items to add/remove them
- Snippets are filtered by selected families (PG/NSFW/Hentai)
- Supports toggle behavior (click again to remove)
- Categories and subcategories appear as random tags (orange/yellow)

### **Templates**
- **Save Template**: File → Save Template (saves current state)
- **Load Template**: File → Load Template (restores saved state)
- Templates include all field values, settings, and generated prompts
- Stored in user data folder for easy access

## 🗂️ File Structure

```
FlipFlopPrompt/
├── main.py                    # PySide6 entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── TODO.md                   # Development tasks
├── .gitignore                # Git ignore rules
├── src/                      # Source code
│   ├── core/                 # Core functionality
│   │   ├── data_models.py
│   │   ├── prompt_engine.py
│   │   ├── llm_integration.py
│   │   └── model_adapters.py
│   ├── gui/                  # User interface
│   │   ├── main_window_qt.py      # PySide6 GUI
│   │   ├── field_widgets_qt.py    # PySide6 widgets
│   │   ├── snippet_widgets_qt.py  # PySide6 snippets  
│   │   ├── preview_panel_qt.py    # PySide6 preview
│   │   ├── tag_widgets_qt.py      # Tag system components
│   │   ├── inline_tag_input_qt.py # Inline tag input
│   │   └── tag_field_widgets_qt.py # Tag field widgets
│   ├── utils/                # Utilities
│   │   ├── snippet_manager.py
│   │   └── theme_manager.py
│   └── cli/                  # Command line interface
└── data/                     # Application data
    └── snippets/             # Default snippet files
```

## ⚙️ Configuration

### **User Data Directory**
The application creates a user data directory to store:
- **Snippets**: Custom snippet files
- **Templates**: Saved prompt templates
- **Prompts**: Generated prompts
- **Preferences**: Application settings
- **Debug**: Debug logs (when enabled)

**Location:**
- Windows: `%APPDATA%\FlipFlopPrompt\`
- macOS: `~/Library/Application Support/FlipFlopPrompt/`
- Linux: `~/.config/FlipFlopPrompt/`

### **Content Families**
- **PG**: Family-friendly content
- **NSFW**: Adult content (non-explicit)
- **Hentai**: Explicit adult content
- **Dynamic Filtering**: Snippets are filtered based on selected families

### **LLM Models**
The application supports various Ollama models:
- **deepseek-coder:6.7b**: Recommended for prompt refinement
- **gemma:2b**: Lightweight option (PG content only)
- **llama2:7b**: General purpose

## 🔧 Development

### **Running in Development Mode**
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run with debug logging
python main.py --debug

# Run standard mode
python main.py
```

### **Debug Mode**
Enable debug mode in the Debug menu to:
- Generate detailed logs
- Save LLM input/output
- Track prompt generation steps
- Debug files saved to user data directory

### **Adding Snippets**
1. Create JSON files in the user snippets directory
2. Follow the snippet format (see existing files)
3. Use Tools → Reload Snippets to load new snippets without restarting
4. Snippets are automatically categorized by field and family

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Update TODO.md with new tasks
- Test on multiple platforms
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Python and PySide6 (Qt)
- Modern GUI powered by Qt framework via PySide6
- LLM integration powered by Ollama
- Inspired by the need for better AI prompt tools
- Community feedback and contributions

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions

---

**Version**: 1.1.0  
**Last Updated**: August 2025  
**Status**: Active Development
