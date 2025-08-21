"""
GUI components for FlipFlopPrompt.
"""

# PySide6 version (current)
try:
    from .main_window_qt import MainWindow
    from .field_widgets_qt import TextFieldWidget, TextAreaWidget, DateTimeWidget
    from .preview_panel_qt import PreviewPanel
    from .snippet_widgets_qt import (
        SnippetDropdown, 
        ContentRatingWidget,
        LLMSelectionWidget
    )
    from .tag_field_widgets_qt import TagTextFieldWidget, TagTextAreaWidget, SeedFieldWidget
    from .tag_widgets_qt import Tag, TagType
    from .inline_tag_input_qt import InlineTagWidget, InlineTagInputWidget
    
    QT_AVAILABLE = True
except ImportError as e:
    print(f"Error importing PySide6 components: {e}")
    QT_AVAILABLE = False

__all__ = [
    # Main components
    'MainWindow',
    'TextFieldWidget',
    'TextAreaWidget', 
    'DateTimeWidget',
    'PreviewPanel',
    'SnippetDropdown',
    'ContentRatingWidget',
    'LLMSelectionWidget',
    
    # Tag system components
    'TagTextFieldWidget',
    'TagTextAreaWidget', 
    'SeedFieldWidget',
    'Tag',
    'TagType',
    'InlineTagWidget',
    'InlineTagInputWidget',
    
    # Qt availability flag
    'QT_AVAILABLE'
]