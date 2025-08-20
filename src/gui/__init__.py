"""
GUI components for FlipFlopPrompt.
"""

# Tkinter version (legacy)
from .main_window import MainWindow as MainWindowTk
from .field_widgets import FieldWidget, TextFieldWidget as TextFieldWidgetTk, TextAreaWidget as TextAreaWidgetTk, DateTimeWidget as DateTimeWidgetTk
from .preview_panel import PreviewPanel as PreviewPanelTk
from .snippet_widgets import SnippetDropdown as SnippetDropdownTk, ContentRatingWidget as ContentRatingWidgetTk

# PySide6 version (new)
try:
    from .main_window_qt import MainWindow as MainWindowQt
    from .field_widgets_qt import TextFieldWidget as TextFieldWidgetQt, TextAreaWidget as TextAreaWidgetQt, DateTimeWidget as DateTimeWidgetQt
    from .preview_panel_qt import PreviewPanel as PreviewPanelQt
    from .snippet_widgets_qt import (
        SnippetDropdown as SnippetDropdownQt, 
        ContentRatingWidget as ContentRatingWidgetQt,
        ModelSelectionWidget,
        LLMSelectionWidget
    )
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# Default exports (backwards compatibility)
MainWindow = MainWindowTk
TextFieldWidget = TextFieldWidgetTk
TextAreaWidget = TextAreaWidgetTk
DateTimeWidget = DateTimeWidgetTk
PreviewPanel = PreviewPanelTk
SnippetDropdown = SnippetDropdownTk
ContentRatingWidget = ContentRatingWidgetTk

__all__ = [
    # Legacy Tkinter components
    'MainWindowTk',
    'FieldWidget',
    'TextFieldWidgetTk', 
    'TextAreaWidgetTk',
    'DateTimeWidgetTk',
    'PreviewPanelTk',
    'SnippetDropdownTk',
    'ContentRatingWidgetTk',
    
    # Default exports (backwards compatibility)
    'MainWindow',
    'TextFieldWidget',
    'TextAreaWidget',
    'DateTimeWidget',
    'PreviewPanel',
    'SnippetDropdown',
    'ContentRatingWidget',
    
    # Qt availability flag
    'QT_AVAILABLE'
]

# Add Qt components if available
if QT_AVAILABLE:
    __all__.extend([
        'MainWindowQt',
        'TextFieldWidgetQt',
        'TextAreaWidgetQt',
        'DateTimeWidgetQt',
        'PreviewPanelQt',
        'SnippetDropdownQt',
        'ContentRatingWidgetQt',
        'ModelSelectionWidget',
        'LLMSelectionWidget'
    ])
