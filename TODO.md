# FlipFlopPrompt TODO List

## ✅ **Completed Tasks**

### **Core Functionality**
- [x] Basic GUI with Tkinter
- [x] Prompt generation engine
- [x] LLM integration with Ollama
- [x] Model-specific prompt formatting
- [x] Content rating system
- [x] Snippet system with JSON files
- [x] Template loading/saving system
- [x] Preferences saving/loading
- [x] Debug system with file logging

### **GUI Improvements**
- [x] Simplified theming (basic colors only)
- [x] Repositioned buttons above prompt summary
- [x] Renamed "environment" to "setting"
- [x] Removed redundant "Content Rating" label
- [x] Removed "View" menu, made "Themes" top-level
- [x] Fixed save prompt functionality
- [x] Added template system to File menu

### **Data Management**
- [x] User data directories setup
- [x] Snippet management system
- [x] Template system
- [x] Preferences persistence
- [x] Debug file generation

## 🔄 **In Progress**

### **Camera Choices Expansion**
- [ ] Add still photography options
- [ ] Add modern DSLR options  
- [ ] Add iconic film camera options
- [ ] Update camera snippets with new choices

## 📋 **Pending Tasks**

### **High Priority**
- [x] **Fix prompt preview functionality** - Now updates interactively based on user input
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
- [ ] **Migrate to PySide6** - Replace Tkinter with modern Qt-based GUI framework (CRITICAL - affects all future development)
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

**Last Updated:** August 2025
**Next Review:** After Sprint 1 completion
