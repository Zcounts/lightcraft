"""
Main Window for the LightCraft application.
Contains the primary UI layout and panel organization.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QHBoxLayout, 
    QWidget, QDockWidget, QMenuBar, QToolBar, QStatusBar, 
    QApplication, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QAction, QIcon

from lightcraft.ui.canvas_area import CanvasArea
from lightcraft.ui.tool_palette import ToolPalette
from lightcraft.ui.properties_panel import PropertiesPanel
from lightcraft.ui.project_navigator import ProjectNavigator
from lightcraft.config import (
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT,
    TOOL_PALETTE_WIDTH, PROPERTIES_PANEL_WIDTH, PROJECT_NAVIGATOR_HEIGHT
)


class MainWindow(QMainWindow):
    """
    Main window class for the LightCraft application.
    Responsible for setting up the UI layout with all panels.
    """
    
    def __init__(self, settings: QSettings, parent=None):
        """
        Initialize the main window.
        
        Args:
            settings: QSettings object for storing/retrieving user preferences
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings = settings
        
        # Core UI components
        self.canvas_area = None
        self.tool_palette = None
        self.properties_panel = None
        self.project_navigator = None
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        self.load_settings()
        
        self.setWindowTitle("LightCraft - Lighting Diagram Designer")
    
    def init_ui(self):
        """Set up the main UI components and layout."""
        # Set up central widget with main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout using splitters for resizable panels
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Horizontal splitter for left panel, canvas, and right panel
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Initialize panels
        self.tool_palette = ToolPalette(self)
        self.canvas_area = CanvasArea(self)
        self.properties_panel = PropertiesPanel(self)
        self.project_navigator = ProjectNavigator(self)
        
        # Add panels to horizontal splitter
        self.h_splitter.addWidget(self.tool_palette)
        self.h_splitter.addWidget(self.canvas_area)
        self.h_splitter.addWidget(self.properties_panel)
        
        # Vertical splitter for main content and project navigator
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.project_navigator)
        
        # Add vertical splitter to main layout
        self.main_layout.addWidget(self.v_splitter)
        
        # Set initial splitter sizes based on config percentages
        window_width = DEFAULT_WINDOW_WIDTH
        window_height = DEFAULT_WINDOW_HEIGHT
        
        tool_width = int(window_width * TOOL_PALETTE_WIDTH / 100)
        properties_width = int(window_width * PROPERTIES_PANEL_WIDTH / 100)
        canvas_width = window_width - tool_width - properties_width
        
        self.h_splitter.setSizes([tool_width, canvas_width, properties_width])
        
        main_height = int(window_height * (100 - PROJECT_NAVIGATOR_HEIGHT) / 100)
        navigator_height = int(window_height * PROJECT_NAVIGATOR_HEIGHT / 100)
        
        self.v_splitter.setSizes([main_height, navigator_height])
        
        # Set up menu bar
        self.setup_menu_bar()
        
        # Set up toolbar
        self.setup_tool_bar()
        
        # Set up status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Set window size
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    
    def setup_menu_bar(self):
        """Set up the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        preferences_action = QAction("&Preferences", self)
        edit_menu.addAction(preferences_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def setup_tool_bar(self):
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Will add toolbar actions in future prompts
    
    def setup_connections(self):
        """Set up signal/slot connections between components."""
        # Will be implemented as components are developed
        pass
    
    def load_settings(self):
        """Load user settings."""
        # Will be implemented in future prompts
        pass
    
    def save_settings(self):
        """Save user settings."""
        # Will be implemented in future prompts
        pass
    
    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About LightCraft",
            f"<h3>LightCraft</h3>"
            f"<p>A lighting diagram designer for film shoots.</p>"
            f"<p>Version: 0.1.0</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Will add confirmation dialog and settings saving in future prompts
        self.save_settings()
        event.accept()
