## ��� CRITICAL WORKFLOW RULE - NEVER BREAK THIS ���
- **NEVER push to git without explicit user confirmation first**
- **ALWAYS ask: "Ready to commit and push these changes?" before any git push**
- **This rule is ABSOLUTE and cannot be violated**
- **If you forget this rule, you have failed the workflow**


# Development Workflow & Preferences

## Development Workflow Preferences
- **Always ask for confirmation before pushing to git**
- **Execute commands directly rather than just suggest them**
- **Prefer bash commands over manual instructions**
- **Clean up test processes** - Don't leave hanging Python processes when testing

## Project Setup
- **Virtual Environment**: `.venv` (not `venv`)**
- **Shell**: Git Bash on Windows
- **Working Directory**: `Z:/Dev/FlipFlopPrompt`
- **GUI Framework**: PySide6 (Qt-based) - Tkinter has been completely removed
- **Entry Point**: `main_qt.py` (legacy `main.py` removed)

## Development Commands
```bash
# Activate virtual environment
source .venv/Scripts/activate

# Run PySide6 GUI (standard)
python main_qt.py --gui

# Run CLI application
python main_qt.py --cli

# Install dependencies
pip install -r requirements.txt

# Clean up hanging processes (if needed)
taskkill //F //IM python.exe
```

## Current Architecture
- **GUI**: Modern PySide6 with tag-based input system
- **Snippets**: JSON files with unified key-value structure (name/content/description)
- **Tag System**: Inline tags with colors (blue=snippets, green=user text, orange=categories, yellow=subcategories)
- **Randomization**: Seed-based deterministic random snippet selection
- **Families**: Dynamic filtering system with real-time snippet updates
- **LLM Integration**: Ollama with dynamic model population and connection testing
- **Logging**: Comprehensive GUI interaction logging with debug mode integration

## Git Workflow
## ��� GIT PUSH CONFIRMATION RULE ���
**BEFORE ANY git push command, you MUST ask:**

```
"Ready to commit and push these changes?

Changes include:
- [list of changes]

Should I proceed with the commit and push?"
```

**This is a MANDATORY step that cannot be skipped.**

- Always stage changes with `git add .`
- Use descriptive commit messages
- Push to `origin main` branch
- **��� MANDATORY: Ask for confirmation before any git push operations**
- Clean up temporary files before committing

## Code Style & Standards
- Follow existing code structure and patterns
- Use descriptive variable and function names
- Add comments for complex logic
- Maintain consistent indentation (4 spaces)
- Use "family" terminology instead of "rating" for content filtering

## Testing & Validation
- Test GUI changes by running the application
- Verify snippet functionality after changes
- Check that all buttons and interactions work
- Validate JSON syntax in snippet files
- Test family filtering and dynamic snippet updates
- Verify tag colors and editing functionality

## File Organization
- **GUI Components**: `src/gui/*_qt.py` (PySide6 only, Tkinter removed)
- **Core Logic**: `src/core/` (prompt engine, data models, LLM integration)
- **Utilities**: `src/utils/` (snippet manager, theme manager)
- **Snippets**: `data/snippets/` (JSON files with family/LLM_rating fields)
- **User Data**: Home directory via `theme_manager.user_data_dir`
- **Templates**: JSON format, saved in user data directory

## Key Technical Decisions
- **Snippet Structure**: Unified key-value format (`name`/`content`/`description`) with `family` field for filtering, `LLM_rating` for AI context
- **Tag Colors**: Cold colors for static (blue/green), hot colors for random (orange/yellow)
- **Family Filtering**: Strict matching (no hierarchy) - PG only shows PG content
- **GUI Styling**: Blue accent buttons (`#0066cc`) with modern scrollbars
- **Window Behavior**: Only preview panel expands on resize, status bar fixed height
- **LLM Instructions**: Full content displayed in tooltips, clean button names

## Common Issues & Solutions
- **JSON parsing errors**: Check for missing braces or commas in snippet files
- **Import errors**: Ensure virtual environment is activated
- **GUI not updating**: Check that change callbacks are properly connected
- **Button styling**: Use PySide6 QPushButton with CSS stylesheets
- **Tag colors not showing**: Check paintEvent implementation in InlineTagWidget
- **Snippet popup issues**: Verify families filtering and dynamic updates
- **Startup performance**: MainWindow creation takes ~4.8s (snippet loading bottleneck)
- **Process cleanup**: Use `taskkill //F //IM python.exe` to clean hanging processes

## Performance Considerations
- **Startup Time**: ✅ **OPTIMIZED: 1.209s** (was 4-5 seconds, target achieved!)
- **Bottleneck**: MainWindow creation (was 4.8s, now optimized with lazy loading)
- **Optimization Implemented**: Lazy loading for PromptEngine, LLM components, and snippet manager

## Development Priorities
1. **High Priority**: ✅ **COMPLETED** - Optimize startup time (4-5s → 1.209s)
2. **High Priority**: ✅ **COMPLETED** - Clean up unnecessary dependencies
3. **High Priority**: Implement batch processing system
4. **Next**: Expand snippet subcategories and add prompt history navigation
5. **Future**: AI service integrations and advanced features

## Recent Major Changes
- **JSON Structure Refactoring**: Unified all snippet files to key-value format with proper tooltips
- **GUI Logging System**: Comprehensive logging of user interactions with debug mode integration
- **PySide6 Migration**: Complete migration from Tkinter to modern Qt-based GUI
- **Tag System**: Implemented inline tag-based input with colors and editing
- **Family System**: Replaced content rating with family filtering (PG/NSFW/Hentai)
- **Randomization**: Added seed-based deterministic random snippet selection
- **Project Cleanup**: Removed all legacy Tkinter files and unused dependencies

---

**Last Updated**: December 2024
**Purpose**: Serve as persistent memory for development workflow preferences and project context
