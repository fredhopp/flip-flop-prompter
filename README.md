# FlipFlopPrompt

A powerful AI image generation prompt builder with a clean, user-friendly interface. Create, refine, and save prompts for various AI image generation models.

## ✨ Features

### **Core Functionality**
- **Multi-Model Support**: Generate prompts optimized for Seedream, Veo, Flux, Wan, and Hailuo
- **LLM Integration**: Uses Ollama for local, free prompt refinement
- **Content Rating System**: PG, NSFW, and custom ratings with appropriate filtering
- **Snippet System**: Quick selection from categorized prompt elements
- **Template System**: Save and load complete prompt configurations
- **Real-time Preview**: See your prompt as you build it

### **User Interface**
- **Modern PySide6 GUI**: Professional Qt-based interface with native look and feel
- **Legacy Tkinter Support**: Backward compatibility for older systems  
- **Clean Design**: Light theme with blue accent buttons and modern scrollbars
- **Responsive Layout**: Dynamic snippet categories and proper window resizing
- **Auto-expanding Fields**: Additional Details field grows from 1-4 lines automatically
- **Professional Spacing**: Optimized button layout and field positioning

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
**Modern PySide6 Interface (Recommended):**
```bash
python main_qt.py --gui
```

**Legacy Tkinter Interface:**
```bash
python main.py --gui
```

## 📖 Usage

### **Basic Workflow**
1. **Select Model**: Choose your target AI image generation model
2. **Set Content Rating**: Select appropriate content rating (affects LLM filtering)
3. **Fill Fields**: Use the form fields to describe your image
4. **Use Snippets**: Click snippet buttons for quick suggestions
5. **Preview**: See your prompt in real-time
6. **Generate**: Click "Generate Prompt" for LLM refinement
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
- **Color Grading & Mood**: Visual style and atmosphere
- **Additional Details**: Any extra information

### **Snippets**
- Click the "Snippets" button next to any field
- Browse categories and click items to add/remove them
- Snippets are filtered by content rating
- Supports toggle behavior (click again to remove)

### **Templates**
- **Save Template**: File → Save Template (saves current state)
- **Load Template**: File → Load Template (restores saved state)
- Templates include all field values, settings, and generated prompts
- Stored in user data folder for easy access

## 🗂️ File Structure

```
FlipFlopPrompt/
├── main.py                    # Legacy Tkinter entry point
├── main_qt.py                 # Modern PySide6 entry point (recommended)
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
│   │   ├── main_window.py         # Tkinter GUI (legacy)
│   │   ├── main_window_qt.py      # PySide6 GUI (modern)
│   │   ├── field_widgets.py       # Tkinter widgets
│   │   ├── field_widgets_qt.py    # PySide6 widgets
│   │   ├── snippet_widgets.py     # Tkinter snippets
│   │   ├── snippet_widgets_qt.py  # PySide6 snippets  
│   │   ├── preview_panel.py       # Tkinter preview
│   │   └── preview_panel_qt.py    # PySide6 preview
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

### **Content Ratings**
- **PG**: Family-friendly content
- **NSFW**: Adult content (non-explicit)
- **Hentai**: Explicit adult content
- **Custom**: User-defined ratings

### **LLM Models**
The application supports various Ollama models:
- **deepseek-coder:6.7b**: Recommended for prompt refinement
- **gemma:2b**: Lightweight option (PG content only)
- **llama2:7b**: General purpose

## 🔧 Development

### **Running in Development Mode**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run modern PySide6 version
python main_qt.py --gui

# Run legacy Tkinter version  
python main.py --gui
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
3. Use the "Reload Snippets" menu option
4. Snippets are automatically categorized by field and rating

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update TODO.md with new tasks
- Test on multiple platforms
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Python, PySide6 (Qt), and legacy Tkinter support
- Modern GUI powered by Qt framework via PySide6
- LLM integration powered by Ollama
- Inspired by the need for better AI prompt tools
- Community feedback and contributions

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Wiki**: Check the wiki for detailed documentation

---

**Version**: 1.0.0  
**Last Updated**: August 2025  
**Status**: Active Development
