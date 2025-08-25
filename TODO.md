# FlipFlopPrompt TODO List

## 🤖 **AI-Assisted Development**

**This project is developed with AI assistance using Cursor IDE and Claude Sonnet 4.**
- **Primary AI Assistant**: Claude Sonnet 4 (via Cursor IDE)
- **Development Environment**: Cursor IDE with AI code completion and assistance
- **AI Integration**: Continuous AI assistance for code review, bug fixes, feature implementation, and documentation
- **Development Approach**: Collaborative AI-human development with iterative refinement
- **AI Contributions**: Code architecture, bug fixes, feature implementation, documentation, testing, and optimization

---

## 🏆 **Major Achievements Completed (August 2025)**

### **Core System Architecture**
- ✅ **Complete PySide6 Migration** - Modern Qt-based interface replacing Tkinter
- ✅ **PromptState Class Implementation** - Unified state management using dataclass for all prompt-related state
- ✅ **Comprehensive Logging System** - Migrated all print() statements to logging system with LogLevel and LogArea
- ✅ **Tag Validation System** - Visual feedback for missing tags with red styling and tooltips
- ✅ **Template System Refactoring** - New PromptState-based template format with backward compatibility
- ✅ **Infinite Recursion Fixes** - Resolved history navigation and template loading recursion issues
- ✅ **LLM Request Functionality** - Fixed Ollama integration with proper model selection and validation

### **GUI & User Experience**
- ✅ **Professional Light/Dark Themes** - JSON-based theme system with customization
- ✅ **Tag-Based Input System** - Inline tags with colors and editing
- ✅ **Dynamic Snippet Filtering** - Real-time updates based on selected filters
- ✅ **Font Awesome Icons** - Professional industry-standard icons throughout
- ✅ **Compact UI Layout** - Optimized spacing and field heights for better tag visibility
- ✅ **Ollama Integration** - Dynamic model population and connection testing
- ✅ **History Navigation** - Session-only prompt history with 0/X state caching
- ✅ **Preview Panel Enhancement** - State-based preview system with Summary/Final Prompt tabs

### **Performance & Optimization**
- ✅ **Startup Time Optimization** - Reduced from 4-5 seconds to 1.209s
- ✅ **Dependency Cleanup** - Removed unused packages from requirements.txt
- ✅ **Lazy Loading Implementation** - Optimized component loading for better performance

### **Data Management**
- ✅ **Unified JSON Structure** - All snippets use consistent key-value format
- ✅ **Template System** - JSON format with versioning and backward compatibility
- ✅ **Preferences Persistence** - User settings saved between sessions
- ✅ **User Data Directories** - Proper organization of user-specific data

---

## 🔄 **In Progress**

### **Snippet System Enhancement**
- [ ] **Expand snippet subcategories** - Add 2-3 subcategories to every snippet JSON file
  - [ ] Review existing snippet files and identify logical subcategory groupings
  - [ ] Create subcategories with at least 3 items each for relevance
  - [ ] Add missing items to subcategories that have fewer than 3 items
  - [ ] Ensure subcategories make logical sense for the field they belong to
  - [ ] Test subcategory display and filtering in the GUI

### **Preview Panel Enhancement**
- [ ] **Add prompt history navigation** - Keep history of generated final prompts
  - [ ] Store generated prompts in memory during session
  - [ ] Add navigation arrows at bottom of preview frame: `<- 1/5 ->`
  - [ ] Allow browsing through previously generated prompts
  - [ ] Show current position in history (e.g., "1/5" for first of five prompts)
  - [ ] Limit history to reasonable number (e.g., 10-20 prompts)
  - [ ] Clear history when starting new session or clearing fields

## 📋 **Pending Tasks**

### **High Priority**
- [ ] **Rename "Families" to "Filters"** - Update terminology throughout the application
  - [ ] Change menu "Families" to "Filters"  
  - [ ] Edit all snippet JSON files to use "filter" instead of "family" (e.g., "family": "PG" becomes "filter": "PG")
  - [ ] Update all code that reads snippets to account for the field name change
  - [ ] Update UI text and labels to reflect "Filters" terminology
  - [ ] Update documentation and comments to use "Filters" terminology
- [ ] **Implement batch processing system** - Handle multiple prompts efficiently
  - [ ] Design batch processing interface
  - [ ] Implement batch prompt generation
  - [ ] Add batch export functionality
  - [ ] Consider progress tracking for large batches
- [ ] **Implement undo system** - Allow undoing realize operations and other actions
  - [ ] Add undo/redo functionality for realize operations
  - [ ] Store action history for undo/redo
  - [ ] Add keyboard shortcuts (Ctrl+Z, Ctrl+Y)
  - [ ] Add undo/redo buttons to UI

### **Template Enhancement**
- [ ] **Embed snippet metadata in templates** - Share and grow keyword database
  - [ ] Add preferences UI under Tools/Preferences menu
  - [ ] Add option to embed "tag definitions" in template files
  - [ ] Save JSON metadata of used categories/items in templates
  - [ ] Check metadata against user's available snippet files on load
  - [ ] Offer to save missing snippet files to user's folder
  - [ ] Implement snippet sharing mechanism for community growth
- [ ] **Test new LLM instruction** - Test "The output should be strictly a very detailed instructional prompt, leave out any conversational wording"
  - [ ] Test with deepseek-r1:8b model
  - [ ] Test with llama3.1-8b-uncensored-v2-q4.gguf model
  - [ ] Compare results with current instruction
  - [ ] Update system prompts if effective
  - [ ] Update LLM prompts to be more specific about output format
  - [ ] Filter out conversational responses and keep only instructional prose
  - [ ] Add post-processing to clean up LLM responses
  - [ ] Test with various LLM models to ensure consistent output

### **Medium Priority**
- [ ] **Add more snippet categories** - Expand existing snippet files
- [ ] **Improve error handling** - Better error messages and recovery
- [ ] **Add keyboard shortcuts** - Common operations like Ctrl+S, Ctrl+N
- [ ] **Add tooltips** - Help text for fields and buttons
- [ ] **Add status bar** - Show current status and operations
- [ ] **Expand command-line options** - Add more startup options for better user control
  - [ ] `--theme <theme_name>` - Start with a specific theme (light/dark)
  - [ ] `--config <path>` - Use a custom config file
  - [ ] `--log-level <level>` - Set specific logging level (debug/info/warning/error)
  - [ ] `--no-splash` - Skip splash screen
  - [ ] `--reset-preferences` - Reset all user preferences on startup
  - [ ] `--portable` - Run in portable mode (no user data persistence)
  - [ ] `--help` - Show detailed help with all available options
- [ ] **Expand camera choices** - Add more camera types to snippets
- [ ] **Improve LLM prompt quality** - Better prompts when fields are empty
- [ ] **Test all functionality** - Ensure everything works after changes

### **Low Priority**
- [ ] **Add export formats** - Export to different formats (JSON, YAML, etc.)
- [ ] **Add import functionality** - Import prompts from other formats
- [ ] **Add statistics** - Track usage and prompt generation stats
- [ ] **Add backup/restore** - Backup user data and settings

## 🐛 **Known Issues**

### **Minor**
- [ ] Window sizing could be more responsive
- [ ] Some text may be cut off in smaller windows
- [ ] Menu styling could be improved
- [ ] Batch frame composition: slight grey halo/incorrect bg around Size/Seed widgets in light/dark themes. Track and fix by unifying palette roles and subcontrol styling without losing native arrows.

## 🚀 **Future Enhancements**

### **High Priority**
- [ ] **Expand snippet categories** - Add more variety to existing snippet files
- [ ] **Improve randomization system** - Add more sophisticated random selection algorithms
- ~~**Randomization system** - Generate variations with pinned/random fields~~ (No longer relevant)
  - ~~**Field pinning** - Allow specific fields to be "pinned" (fixed) while others randomize~~ (No longer relevant)
  - ~~**Batch generation** - Generate multiple prompt variations at once~~ (No longer relevant)
  - ~~**Seed system** - ComfyUI-style seed management (fixed/increment/random)~~ (No longer relevant)
  - ~~**Batch file saving** - Save generated prompts as numbered individual files~~ (No longer relevant)
  - ~~**Variation controls** - GUI to select which fields to randomize vs pin~~ (No longer relevant)

### **GUI Improvements**
- [ ] **Customizable layouts** - Allow users to rearrange fields
- [ ] **Drag and drop** - Drag snippets between fields
- [ ] **Auto-save** - Automatically save work in progress

### **Functionality**
- [ ] **Prompt templates** - Pre-built prompt templates
- [ ] **Prompt validation** - Check prompt quality and completeness
- [ ] **Prompt optimization** - Suggest improvements
- [ ] **Multi-language support** - Internationalization
- [ ] **Plugin system** - Allow third-party extensions

### **Integration**
- [ ] **Unified service architecture** - Common interface for multiple AI services
  - [ ] **Service abstraction layer** - Common interface for different AI services
  - [ ] **Service plugin system** - Modular architecture for adding new services
  - [ ] **Service comparison** - Compare capabilities and pricing across services
  - [ ] **Service fallback** - Automatic fallback if primary service fails
  - [ ] **Multi-service batch** - Submit to multiple services simultaneously
  - [ ] **Service-specific optimizations** - Optimize prompts for each service
  - [ ] **Service health monitoring** - Monitor service availability and performance

- [ ] **Wavespeed.ai integration** - Direct image generation service (within unified architecture)
  - [ ] **API key management** - Secure storage of API keys in encrypted user folder
  - [ ] **Preferences window** - GUI for API key input and service configuration
  - [ ] **Image display** - Single image viewer and batch thumbnail gallery
  - [ ] **Gallery navigation** - Click-to-expand thumbnails with navigation controls
  - [ ] **Resolution selection** - Model-specific resolution options
  - [ ] **Price calculation** - Real-time cost estimation based on model/resolution/video length
  - [ ] **Model selection** - Choose from available Wavespeed.ai models
  - [ ] **Video support** - Video generation with length controls
  - [ ] **Batch processing** - Submit multiple prompts for batch generation
  - [ ] **Result management** - Download, save, and organize generated images/videos
  - [ ] **Generation history** - Track and review past generations
  - [ ] **Error handling** - Graceful handling of API failures and rate limits
  - [ ] **Progress indicators** - Show generation progress and estimated time
  - [ ] **Quality settings** - Adjust generation quality and parameters
  - [ ] **Prompt optimization** - Auto-optimize prompts for better results
  - [ ] **Style presets** - Pre-configured style settings for different models

- [ ] **ComfyUI integration** - Direct integration with ComfyUI (simplified approach)
  - [ ] **Workflow loading** - Load predefined .json workflow files from user folder
  - [ ] **Parameter mapping** - Map prompt data to existing workflow node parameters
  - [ ] **Status monitoring** - Real-time feedback on workflow loading and processing
  - [ ] **Progress tracking** - Show current status and progress of generation
  - [ ] **Result retrieval** - Download and display generated images
  - [ ] **Error handling** - Graceful handling of workflow failures

- [ ] **API support** - REST API for external tools

## 📝 **Documentation Tasks**

- [x] Update README.md with current project state
- [ ] Create user manual
- [ ] Create developer documentation
- [ ] Add code comments and docstrings
- [ ] Create video tutorials

## 🧪 **Testing Tasks**

- [ ] **Unit tests** - Test individual components
- [ ] **Integration tests** - Test full workflow
- [ ] **GUI tests** - Test user interface
- [ ] **Performance tests** - Test with large datasets
- [ ] **Cross-platform tests** - Test on different OS

## 📦 **Deployment Tasks**

- [ ] **Create installer** - Windows/Mac/Linux installers
- [ ] **Create executable** - PyInstaller or similar
- [ ] **Create Docker image** - Containerized version
- [ ] **Setup CI/CD** - Automated testing and deployment
- [ ] **Create release notes** - Document changes

## 🎯 **Current Sprint Goals**

### **Sprint 1 (Current)**
1. ✅ Simplify theming system
2. ✅ Fix button positioning
3. ✅ Implement template system
4. ✅ Update field names
5. ✅ Fix GUI and snippet issues
6. ✅ Fix prompt preview
7. ✅ Clean up unnecessary dependencies

### **Sprint 2 (Randomization System) - NO LONGER RELEVANT**
1. ~~Implement field pinning system~~ (No longer relevant)
2. ~~Add seed management (fixed/increment/random)~~ (No longer relevant)
3. ~~Create batch generation interface~~ (No longer relevant)
4. ~~Add variation controls GUI~~ (No longer relevant)
5. ~~Implement batch file saving~~ (No longer relevant)

### **Sprint 3 (Unified Service Architecture)**
1. Design service abstraction layer
2. Create service plugin system
3. Implement service comparison framework
4. Add service health monitoring
5. Create service fallback mechanism

### **Sprint 4 (Wavespeed.ai Integration)**
1. Set up API key management and encryption
2. Create preferences window for service configuration
3. Implement basic image display and gallery
4. Add model selection and resolution controls
5. Implement price calculation system

### **Sprint 5 (ComfyUI Integration)**
1. Implement workflow loading from .json files
2. Create parameter mapping system
3. Add status monitoring and progress tracking
4. Implement result retrieval and display
5. Add error handling and validation

### **Sprint 6 (Advanced Features)**
1. Add video generation support for Wavespeed.ai
2. Implement multi-service batch processing
3. Create generation history and result management
4. Add progress indicators and error handling
5. Implement quality settings and style presets

---

## 📋 **Project Context & Technical Decisions**

### **Current Architecture**
- **GUI Framework**: **PySide6 (modern Qt-based interface)**
- **Virtual Environment**: `.venv` (not `venv`)
- **User Data**: Stored in user's home directory via `theme_manager.user_data_dir`
- **Snippets**: JSON files in `data/snippets/` with family/content rating system
- **Templates**: JSON format, saved in user data directory
- **Preferences**: Family selections and model preferences persist between sessions
- **Dependencies**: PySide6, requests, and development tools

### **Key Technical Decisions Made**
- **Snippet Organization**: Fixed redundant categories (removed "Standing", renamed "Camera Type" to "Digital Cameras", etc.)
- **GUI Styling**: Blue buttons (`#0066cc`) with white text, consistent across all buttons
- **Preview Behavior**: Grey placeholder text when empty, black text when content present
- **Field Names**: "environment" renamed to "setting" throughout the codebase
- **Content Rating**: Affects available LLM models (filters out `gemma:2b` for NSFW content)

### **File Structure**
```
src/
├── core/           # Core prompt generation logic
├── gui/            # PySide6 GUI components
│   └── *_qt.py     # PySide6 components (modern)
├── utils/          # Utilities (snippet manager, theme manager)
└── cli/            # Command line interface
data/
└── snippets/       # JSON snippet files by family/content rating
```

### **Important Implementation Details**
- **Interactive Preview**: All field widgets have `change_callback=self._update_preview`
- **LLM Integration**: Uses Ollama with models like `deepseek-coder:6.7b`
- **Error Handling**: JSON parsing errors handled gracefully
- **Theme System**: JSON-based themes with hot-reload capability
- **Debug System**: Creates timestamped folders with debug files

### **Known Working Features**
- ✅ Interactive prompt preview updates
- ✅ Snippet system with pretty names (no underscores in UI)
- ✅ Template loading/saving
- ✅ Content rating system
- ✅ Blue button styling consistency
- ✅ Placeholder text behavior
- ✅ File operations (save prompt, load template)

---

**Last Updated:** August 2025
**Next Review:** After Sprint 1 completion
