# Development Workflow & Preferences

## Development Workflow Preferences
- **Always ask for confirmation before pushing to git**
- **Execute commands directly rather than just suggest them**
- **Prefer bash commands over manual instructions**

## Project Setup
- **Virtual Environment**: `.venv` (not `venv`)
- **Shell**: Git Bash on Windows
- **Working Directory**: `Z:/Dev/FlipFlopPrompt`

## Development Commands
```bash
# Activate virtual environment
source .venv/Scripts/activate

# Run GUI application
python main.py --gui

# Run CLI application
python main.py --cli

# Install dependencies
pip install -r requirements.txt
```

## Git Workflow
- Always stage changes with `git add .`
- Use descriptive commit messages
- Push to `origin main` branch
- Ask for confirmation before any git push operations

## Code Style & Standards
- Follow existing code structure and patterns
- Use descriptive variable and function names
- Add comments for complex logic
- Maintain consistent indentation (4 spaces)

## Testing & Validation
- Test GUI changes by running the application
- Verify snippet functionality after changes
- Check that all buttons and interactions work
- Validate JSON syntax in snippet files

## File Organization
- Keep GUI components in `src/gui/`
- Core logic in `src/core/`
- Utilities in `src/utils/`
- Snippets in `data/snippets/`
- User data in home directory via `theme_manager.user_data_dir`

## Common Issues & Solutions
- **JSON parsing errors**: Check for missing braces or commas in snippet files
- **Import errors**: Ensure virtual environment is activated
- **GUI not updating**: Check that change callbacks are properly connected
- **Button styling**: Use `tk.Button` with explicit `bg="#0066cc"` and `fg="#ffffff"`

## Development Priorities
1. **High Priority**: Clean up unnecessary dependencies
2. **Next**: PySide6 migration (critical for future development)
3. **Future**: Randomization system, AI service integrations

---

**Last Updated**: August 2025
**Purpose**: Serve as persistent memory for development workflow preferences and project context
