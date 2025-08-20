# FlipFlopPrompt TODO List

## ✅ **Completed Tasks**

### **Core Functionality**
- [x] **Complete PySide6 GUI implementation** (modern Qt-based interface)
- [x] Prompt generation engine
- [x] LLM integration with Ollama
- [x] Model-specific prompt formatting
- [x] **Enhanced "Families" system** (replaces content rating)
- [x] Snippet system with JSON files
- [x] Template loading/saving system
- [x] Preferences saving/loading with family persistence
- [x] Debug system with file logging
- [x] **Tag-based snippet system** with randomization
- [x] **Dynamic snippet filtering** based on selected families

### **PySide6 GUI Implementation (Major Achievement)**
- [x] **Complete PySide6 migration** - Modern Qt-based interface
- [x] **Professional light theme** - Blue accent buttons and modern scrollbars
- [x] **Tag-based input system** - Inline tags with colors and editing
- [x] **Dynamic snippet popup** - Category blocks rearrange on window resize
- [x] **Auto-expanding Additional Details** - 1-4 lines with scrollbar
- [x] **Family preferences persistence** - Saves selections between sessions
- [x] **Real-time Ollama integration** - Dynamic model population and connection testing
- [x] **Proper window resize behavior** - Only preview panel expands
- [x] **Professional button layout** - 2px spacing with equal distribution
- [x] **Fixed text clipping issues** - Snippet buttons and input fields
- [x] **Hierarchical snippet categories** - Gender/Age/Profession properly displayed
- [x] **Side-by-side model selection** - Target Diffusion + LLM models
- [x] **Fixed-height status bar** - Word/character count at bottom
- [x] **Copy to Clipboard** - Added to main action row
- [x] **Clear All Fields** - Renamed and repositioned button
- [x] **Seed-based randomization** - Deterministic random snippet selection
- [x] **Tag color coding** - Different colors for different tag types
- [x] **Dynamic snippet updates** - Real-time filtering when families change

### **Data Management**
- [x] User data directories setup
- [x] Snippet management system
- [x] Template system
- [x] Preferences persistence
- [x] Debug file generation

## 🔄 **In Progress**

### **Project Cleanup**
- [x] **Remove legacy Tkinter files** - Cleaned up old GUI implementation
- [x] **Remove unused main.py** - PySide6 version is now the standard
- [ ] **Clean up unnecessary dependencies** - Remove unused packages from requirements.txt
- [ ] **Update documentation** - Ensure TODO.md and DEVELOPMENT.md are current

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
- [x] **Fix prompt preview functionality** - Now updates interactively based on user input
- [x] **Remove legacy Tkinter files** - Cleaned up old GUI implementation
- [ ] **Optimize application startup time** - Reduce from 4-5 seconds to 1-2 seconds
  - [ ] Profile startup performance to identify bottlenecks
  - [ ] Optimize snippet loading (consider lazy loading or caching)
  - [ ] Optimize GUI initialization (reduce widget creation overhead)
  - [ ] Consider async loading for non-critical components
  - [ ] Profile and optimize import times
- [ ] **Implement batch processing system** - Handle multiple prompts efficiently
  - [ ] Design batch processing interface
  - [ ] Implement batch prompt generation
  - [ ] Add batch export functionality
  - [ ] Consider progress tracking for large batches
- [ ] **Fix tag field height expansion** - Fields need to expand height to fit tags
  - [ ] Implement dynamic height adjustment for tag fields
  - [ ] Ensure all tags are visible without requiring wide window resize
  - [ ] Add minimum height constraints for tag fields
  - [ ] Test tag wrapping and overflow behavior
- [ ] **Improve LLM prompt refinement** - Remove "Okay..." and other non-instructional text
  - [ ] Update LLM prompts to be more specific about output format
  - [ ] Filter out conversational responses and keep only instructional prose
  - [ ] Add post-processing to clean up LLM responses
  - [ ] Test with various LLM models to ensure consistent output
- [ ] **Clean up unnecessary dependencies** - Remove unused packages from requirements.txt and .venv
  - [ ] Remove PyYAML (not used in main code)
  - [ ] Remove jsonschema (not used in main code)
  - [ ] Remove openai (not used in main code)
  - [ ] Update requirements.txt to only include actually used packages
  - [ ] Verify all imports are either standard Python or in requirements.txt
- [ ] **Expand snippet subcategories** - Add 2-3 subcategories to every snippet JSON file
  - [ ] Review existing snippet files and identify logical subcategory groupings
  - [ ] Create subcategories with at least 3 items each for relevance
  - [ ] Add missing items to subcategories that have fewer than 3 items
  - [ ] Ensure subcategories make logical sense for the field they belong to
  - [ ] Test subcategory display and filtering in the GUI
- [ ] **Add prompt history navigation** - Keep history of generated final prompts
  - [ ] Store generated prompts in memory during session
  - [ ] Add navigation arrows at bottom of preview frame: `<- 1/5 ->`
  - [ ] Allow browsing through previously generated prompts
  - [ ] Show current position in history (e.g., "1/5" for first of five prompts)
  - [ ] Limit history to reasonable number (e.g., 10-20 prompts)
  - [ ] Clear history when starting new session or clearing fields
- [ ] **Expand camera choices** - Add more camera types to snippets
- [ ] **Improve LLM prompt quality** - Better prompts when fields are empty
- [ ] **Test all functionality** - Ensure everything works after changes

### **Medium Priority**
- [ ] **Add more snippet categories** - Expand existing snippet files
- [ ] **Improve error handling** - Better error messages and recovery
- [ ] **Add keyboard shortcuts** - Common operations like Ctrl+S, Ctrl+N
- [ ] **Add tooltips** - Help text for fields and buttons
- [ ] **Add status bar** - Show current status and operations

### **Low Priority**
- [ ] **Add export formats** - Export to different formats (JSON, YAML, etc.)
- [ ] **Add import functionality** - Import prompts from other formats
- [ ] **Add batch processing** - Process multiple prompts at once
- [ ] **Add statistics** - Track usage and prompt generation stats
- [ ] **Add backup/restore** - Backup user data and settings

## 🐛 **Known Issues**

### **Critical**
- [x] Prompt preview not updating correctly
- [ ] Some snippet dropdowns may not work properly
- [ ] LLM connection status may not be accurate

### **Minor**
- [ ] Window sizing could be more responsive
- [ ] Some text may be cut off in smaller windows
- [ ] Menu styling could be improved

## 🚀 **Future Enhancements**

### **High Priority**
- [x] **Migrate to PySide6** - Replace Tkinter with modern Qt-based GUI framework (COMPLETED)
- [ ] **Expand snippet categories** - Add more variety to existing snippet files
- [ ] **Improve randomization system** - Add more sophisticated random selection algorithms
- [ ] **Randomization system** - Generate variations with pinned/random fields
  - [ ] **Field pinning** - Allow specific fields to be "pinned" (fixed) while others randomize
  - [ ] **Batch generation** - Generate multiple prompt variations at once
  - [ ] **Seed system** - ComfyUI-style seed management (fixed/increment/random)
  - [ ] **Batch file saving** - Save generated prompts as numbered individual files
  - [ ] **Variation controls** - GUI to select which fields to randomize vs pin

### **GUI Improvements**
- [ ] **Dark mode toggle** - Simple light/dark theme switch
- [ ] **Customizable layouts** - Allow users to rearrange fields
- [ ] **Drag and drop** - Drag snippets between fields
- [ ] **Auto-save** - Automatically save work in progress
- [ ] **Undo/Redo** - History of changes

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
7. **Clean up unnecessary dependencies** - Remove unused packages and update requirements.txt

### **Sprint 2 (PySide6 Migration)**
1. **Migrate to PySide6** - Critical foundation for all future development
2. Port all existing widgets to PySide6
3. Update theme system for PySide6
4. Test all functionality in new framework
5. Optimize performance and UI responsiveness

### **Sprint 3 (Randomization System)**
1. Implement field pinning system
2. Add seed management (fixed/increment/random)
3. Create batch generation interface
4. Add variation controls GUI
5. Implement batch file saving

### **Sprint 4 (Unified Service Architecture)**
1. Design service abstraction layer
2. Create service plugin system
3. Implement service comparison framework
4. Add service health monitoring
5. Create service fallback mechanism

### **Sprint 5 (Wavespeed.ai Integration)**
1. Set up API key management and encryption
2. Create preferences window for service configuration
3. Implement basic image display and gallery
4. Add model selection and resolution controls
5. Implement price calculation system

### **Sprint 6 (ComfyUI Integration)**
1. Implement workflow loading from .json files
2. Create parameter mapping system
3. Add status monitoring and progress tracking
4. Implement result retrieval and display
5. Add error handling and validation

### **Sprint 7 (Advanced Features)**
1. Add video generation support for Wavespeed.ai
2. Implement multi-service batch processing
3. Create generation history and result management
4. Add progress indicators and error handling
5. Implement quality settings and style presets

---

## 📋 **Project Context & Technical Decisions**

### **Current Architecture**
- **GUI Framework**: **PySide6 (modern Qt-based interface)**
- **Modern PySide6 GUI**: Qt-based interface with professional styling
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
├── gui/            # Dual GUI support (Tkinter + PySide6)
│   ├── *_qt.py     # PySide6 components (modern)
│   └── *.py        # Tkinter components (legacy)
├── utils/          # Utilities (snippet manager, theme manager)
└── cli/            # Command line interface
data/
└── snippets/       # JSON snippet files by family/content rating
```

### **Important Implementation Details**
- **Interactive Preview**: All field widgets have `change_callback=self._update_preview`
- **LLM Integration**: Uses Ollama with models like `deepseek-coder:6.7b`
- **Error Handling**: JSON parsing errors handled gracefully
- **Theme System**: Simplified to basic colors only
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
