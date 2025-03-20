"""
Main Window for the LightCraft application.
Contains the primary UI layout and panel organization.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QHBoxLayout, 
    QWidget, QDockWidget, QMenuBar, QToolBar, QStatusBar, 
    QApplication, QMenu, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QAction, QIcon
from lightcraft.controllers.scene_controller import SceneController
from lightcraft.controllers.project_controller import ProjectController
from lightcraft.ui.project_navigator import ProjectNavigator
from lightcraft.ui.canvas_area import CanvasArea
from lightcraft.ui.tool_palette import ToolPalette
from lightcraft.ui.properties_panel import PropertiesPanel
from lightcraft.ui.project_navigator import ProjectNavigator
from lightcraft.ui.equipment_library import EquipmentLibraryPanel
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
        self.equipment_library = None
        
        # Controllers (set by integration module)
        self.scene_controller = None
        self.tool_controller = None
        self.project_controller = None
        self.canvas_controller = None
        
        # Initialize UI
        self.init_ui()
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
        
        # Left panel splitter for tool palette and equipment library
        self.left_panel_widget = QWidget()
        self.left_panel_layout = QVBoxLayout(self.left_panel_widget)
        self.left_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel_layout.setSpacing(0)
        
        # Initialize panels
        self.tool_palette = ToolPalette(self)
        self.equipment_library = EquipmentLibraryPanel(self)
        self.canvas_area = CanvasArea(self)
        self.properties_panel = PropertiesPanel(self)
        self.project_navigator = ProjectNavigator(self)
        
        # Add tool palette and equipment library to left panel
        self.left_panel_splitter = QSplitter(Qt.Orientation.Vertical)
        self.left_panel_splitter.addWidget(self.tool_palette)
        self.left_panel_splitter.addWidget(self.equipment_library)
        self.left_panel_splitter.setSizes([int(DEFAULT_WINDOW_HEIGHT * 0.4), 
                                          int(DEFAULT_WINDOW_HEIGHT * 0.6)])
        self.left_panel_layout.addWidget(self.left_panel_splitter)
        
        # Add panels to horizontal splitter
        self.h_splitter.addWidget(self.left_panel_widget)
        self.h_splitter.addWidget(self.canvas_area)
        self.h_splitter.addWidget(self.properties_panel)
        
        # Vertical splitter for main content and project navigator
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h_splitter)
        # Don't add the project navigator here, it will be added later
        
        # Add vertical splitter to main layout
        self.main_layout.addWidget(self.v_splitter)

        # The scene controller and project controller will be initialized by the integration module
        # See setup_application_components in integration.py
        
        # Connect signals
        self.connect_signals()
        
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
        
        self.new_action = QAction("&New Project", self)
        self.new_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_action)
        
        self.open_action = QAction("&Open Project", self)
        self.open_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_action)
        
        file_menu.addSeparator()
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        self.preferences_action = QAction("&Preferences", self)
        edit_menu.addAction(self.preferences_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(self.zoom_out_action)
        
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
        
        # Add new project button
        new_project_btn = QAction(QIcon(), "New Project", self)
        new_project_btn.triggered.connect(self.on_new_project)
        toolbar.addAction(new_project_btn)
        
        # Add open project button
        open_project_btn = QAction(QIcon(), "Open Project", self)
        open_project_btn.triggered.connect(self.on_open_project)
        toolbar.addAction(open_project_btn)
        
        # Add save project button
        save_project_btn = QAction(QIcon(), "Save Project", self)
        save_project_btn.triggered.connect(self.on_save_project)
        toolbar.addAction(save_project_btn)
        
        toolbar.addSeparator()
        
        # Add undo button
        undo_btn = QAction(QIcon(), "Undo", self)
        undo_btn.triggered.connect(lambda: self.canvas_controller.undo() if self.canvas_controller else None)
        toolbar.addAction(undo_btn)
        
        # Add redo button
        redo_btn = QAction(QIcon(), "Redo", self)
        redo_btn.triggered.connect(lambda: self.canvas_controller.redo() if self.canvas_controller else None)
        toolbar.addAction(redo_btn)
    
    def load_settings(self):
        """Load user settings."""
        # Window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        # Window state
        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))
    
    def save_settings(self):
        """Save user settings."""
        # Window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Window state
        self.settings.setValue("windowState", self.saveState())
    
    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About LightCraft",
            f"<h3>LightCraft</h3>"
            f"<p>A lighting diagram designer for film shoots.</p>"
            f"<p>Version: 0.1.0</p>"
        )

    def setup_project_navigator(self):
        """Set up the project navigator panel."""
        # Create project navigator
        self.project_navigator = ProjectNavigator(self)
        
        # Set project controller
        self.project_controller.set_project_navigator(self.project_navigator)
        
        # Replace the existing project navigator with our enhanced version
        if hasattr(self, 'v_splitter') and hasattr(self, 'project_navigator'):
            self.v_splitter.replaceWidget(1, self.project_navigator)
        
    def connect_signals(self):
        """Connect signals for application components."""
        # Connect close event handler
        QApplication.instance().aboutToQuit.connect(self.on_application_quit)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Check if we can close (unsaved changes)
        if self.project_controller.can_application_close():
            # Save window settings
            self.save_settings()
            event.accept()
        else:
            event.ignore()
    
    def on_application_quit(self):
        """Handle application quit event."""
        # Clean up resources
        if hasattr(self, 'project_controller'):
            if hasattr(self.project_controller, 'project_manager'):
                if hasattr(self.project_controller.project_manager, 'db'):
                    self.project_controller.project_manager.db.disconnect()
    
    def on_new_project(self):
        """Handle new project action."""
        if self.project_controller:
            # Get project name from user
            name, ok = QInputDialog.getText(
                self, "New Project", "Project Name:", QLineEdit.EchoMode.Normal, "New Project"
            )
            
            if ok and name:
                project_id = self.project_controller.create_project(name)
                
                if project_id:
                    self.statusBar.showMessage(f"Created new project: {name}", 3000)
    
    def on_open_project(self):
        """Handle open project action."""
        if self.project_controller:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Project", "", "LightCraft Projects (*.lightcraft)"
            )
            
            if file_path:
                self.project_controller.project_file_opened.emit(file_path)
                self.statusBar.showMessage(f"Opened project: {file_path}", 3000)
    
    def on_save_project(self):
        """Handle save project action."""
        if self.project_controller:
            self.project_controller.project_saved.emit()
            self.statusBar.showMessage("Project saved", 3000)
    
    def on_save_project_as(self):
        """Handle save project as action."""
        if self.project_controller:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project As", "", "LightCraft Projects (*.lightcraft)"
            )
            
            if file_path:
                if not file_path.endswith('.lightcraft'):
                    file_path += '.lightcraft'
                
                self.project_controller.project_file_saved.emit(file_path)
                self.statusBar.showMessage(f"Project saved as: {file_path}", 3000)
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event: QKeyEvent
        """
        # Delete key to delete selected items
        if event.key() == Qt.Key.Key_Delete:
            if self.canvas_controller:
                self.canvas_controller.handle_tool_action("delete", {})
        
        # Esc key to cancel current operation or deselect
        elif event.key() == Qt.Key.Key_Escape:
            if self.canvas_area and self.canvas_area.scene:
                self.canvas_area.scene.clearSelection()
                
                # Cancel any ongoing operation
                if hasattr(self.canvas_area.scene, 'preview_item') and self.canvas_area.scene.preview_item:
                    self.canvas_area.scene.removeItem(self.canvas_area.scene.preview_item)
                    self.canvas_area.scene.preview_item = None
        
        # Tool shortcuts
        elif event.key() == Qt.Key.Key_S:
            # Select tool
            if self.tool_palette:
                self.tool_palette.select_tool("select")
        elif event.key() == Qt.Key.Key_R:
            # Rotate tool
            if self.tool_palette:
                self.tool_palette.select_tool("rotate")
        elif event.key() == Qt.Key.Key_W:
            # Wall tool
            if self.tool_palette:
                self.tool_palette.select_tool("wall")
        elif event.key() == Qt.Key.Key_L:
            # Light tool (spot light)
            if self.tool_palette:
                self.tool_palette.select_tool("light-spot")
        elif event.key() == Qt.Key.Key_C:
            # Camera tool
            if self.tool_palette:
                self.tool_palette.select_tool("camera")
        
        # Call parent implementation
        super().keyPressEvent(event)
