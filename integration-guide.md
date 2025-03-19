# LightCraft Project Management Integration Guide

This guide explains how to integrate the project management functionality into the LightCraft application. The project management system provides a comprehensive solution for creating, saving, and managing lighting diagram projects, including scene management, thumbnails, and version history.

## Overview of Components

1. **Database Layer**
   - `ProjectDatabase`: SQLite storage for projects, scenes, and version history

2. **Data Models**
   - `ProjectFile`: Handles serialization/deserialization of project files

3. **Business Logic**
   - `ProjectManager`: Manages project and scene operations, auto-save

4. **Controllers**
   - `ProjectController`: Coordinates UI interactions with business logic

5. **UI Components**
   - `ProjectNavigator`: User interface for project and scene management

## Integration Steps

### 1. Update Configuration

First, add the necessary configuration settings to `config.py`:

```python
# File paths
import os
import tempfile

# Application data directory
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".lightcraft")

# Database file
DATABASE_FILE = os.path.join(APP_DATA_DIR, "lightcraft.db")

# Auto-save settings
AUTO_SAVE_ENABLED = True
AUTO_SAVE_INTERVAL = 300  # seconds (5 minutes)
```

### 2. Add New Files to Project Structure

Add these new files to your project:

```
lightcraft/
├── models/
│   ├── project_db.py       # Database management
│   ├── project_file.py     # Project file format
│
├── controllers/
│   ├── project_manager.py  # Project management logic
│   ├── project_controller.py  # Controller between UI and logic
│
└── ui/
    └── project_navigator.py  # Project UI components
```

### 3. Update Scene Controller

Modify the `SceneController` to support saving/loading scenes:

```python
# Add to scene_controller.py

def clear_scene(self):
    """Clear the current scene."""
    # Remove all items
    self.selected_items = []
    
    # Reset current scene
    self.current_scene = None
    
    # Create new empty scene
    self.new_scene("Empty Scene")
    
    # Emit scene changed signal
    self.scene_changed.emit()

def new_scene(self, name):
    """Create a new empty scene."""
    from lightcraft.models.scene import Scene
    
    # Create new scene
    self.current_scene = Scene(name=name)
    
    # Emit scene changed signal
    self.scene_changed.emit()
```

### 4. Modify Main Window

Update the main window to integrate the project navigator UI:

```python
# Add to main_window.py imports
from lightcraft.ui.project_navigator import ProjectNavigator
from lightcraft.controllers.project_controller import ProjectController

# Add to MainWindow.__init__
def __init__(self, settings: QSettings, parent=None):
    # Existing initialization code...
    
    # Initialize scene controller
    self.scene_controller = SceneController(self)
    
    # Initialize canvas controller
    self.canvas_controller = CanvasController(self.scene_controller, self.canvas_area)
    
    # Initialize project controller
    self.project_controller = ProjectController(self.scene_controller, self)
    
    # Set up project navigator
    self.setup_project_navigator()
    
    # Connect signals
    self.connect_signals()

# Add these new methods
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
```

### 5. Add File Operations to the Menu

Update the `setup_menu_bar` method in the main window:

```python
def setup_menu_bar(self):
    """Set up the application menu bar."""
    menu_bar = self.menuBar()
    
    # File menu
    file_menu = menu_bar.addMenu("&File")
    
    # New project action
    new_project_action = QAction("&New Project", self)
    new_project_action.setShortcut("Ctrl+N")
    new_project_action.triggered.connect(self.on_new_project)
    file_menu.addAction(new_project_action)
    
    # Open project action
    open_project_action = QAction("&Open Project", self)
    open_project_action.setShortcut("Ctrl+O")
    open_project_action.triggered.connect(self.on_open_project)
    file_menu.addAction(open_project_action)
    
    file_menu.addSeparator()
    
    # Save action
    save_action = QAction("&Save", self)
    save_action.setShortcut("Ctrl+S")
    save_action.triggered.connect(self.on_save_project)
    file_menu.addAction(save_action)
    
    # Save as action
    save_as_action = QAction("Save &As...", self)
    save_as_action.setShortcut("Ctrl+Shift+S")
    save_as_action.triggered.connect(self.on_save_project_as)
    file_menu.addAction(save_as_action)
    
    file_menu.addSeparator()
    
    # Exit action
    exit_action = QAction("E&xit", self)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(self.close)
    file_menu.addAction(exit_action)
    
    # Add rest of your menus...

# Add these handler methods
def on_new_project(self):
    """Handle new project action."""
    if hasattr(self, 'project_navigator'):
        self.project_navigator.on_new_project()

def on_open_project(self):
    """Handle open project action."""
    if hasattr(self, 'project_navigator'):
        self.project_navigator.on_open_project()

def on_save_project(self):
    """Handle save project action."""
    if hasattr(self, 'project_navigator'):
        self.project_navigator.on_save_project()

def on_save_project_as(self):
    """Handle save project as action."""
    if hasattr(self, 'project_navigator'):
        self.project_navigator.on_save_project_as()
```

### 6. Testing the Integration

After implementing these changes, you should be able to:

1. Create new projects
2. Save projects to .lightcraft files
3. Open saved projects
4. Create, rename, delete, and duplicate scenes
5. Reorganize scenes with drag and drop
6. See scene thumbnails in the navigator
7. Get auto-save recovery prompts if application crashes

## Error Handling

The implementation includes comprehensive error handling:

1. **Database Errors**: All database operations include try/except blocks with detailed error messages
2. **File Operations**: File saving and loading have error handling with user-friendly messages
3. **Unsaved Changes**: Prompts to save unsaved changes before potentially destructive operations
4. **Auto-save Recovery**: System checks for auto-saves when loading a scene

## Important Notes

### Auto-save Mechanism

The auto-save system works by:
1. Creating a timer that triggers at regular intervals (default: 5 minutes)
2. Storing scene data in the database without affecting the main saved file
3. Offering to recover from auto-save when loading a scene with auto-save data

### SQLite Database

The SQLite database is used to store:
1. Project metadata
2. Scene data
3. Thumbnails
4. Version history
5. Auto-save data

This allows the application to maintain state even when projects aren't explicitly saved to files.

### Project File Format

The .lightcraft file format is a compressed ZIP archive containing:
1. project.json - Project and scene data
2. thumbnails/ - Folder with scene thumbnails

## Next Steps

After integrating this project management system, consider these enhancements:

1. Add recent projects list to the File menu
2. Implement version history browsing and restoration
3. Add project and scene templates
4. Implement scene import/export
5. Add cloud storage integration

## Troubleshooting

If you encounter issues:

1. **Database Initialization Failed**: Check file permissions in the application data directory
2. **File Save Failed**: Ensure the target directory is writable
3. **UI Elements Not Updating**: Verify signal connections between components
4. **Auto-save Not Working**: Check if the timer is being started correctly

By following this guide, you should have a fully functional project management system integrated into your LightCraft application.
