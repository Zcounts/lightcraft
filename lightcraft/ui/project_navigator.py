"""
Project Navigator for the LightCraft application.
Provides UI for managing projects and scenes.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMenu, QInputDialog, QMessageBox, QFrame,
    QSplitter, QFileDialog, QApplication, QToolButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData, QPoint
from PyQt6.QtGui import QIcon, QDrag, QPixmap, QAction

import os


class SceneItem(QListWidgetItem):
    """Custom list widget item for scenes."""
    
    def __init__(self, scene_id, scene_name, parent=None):
        """
        Initialize the scene item.
        
        Args:
            scene_id: ID of the scene
            scene_name: Name of the scene
            parent: Parent widget
        """
        super().__init__(parent)
        self.scene_id = scene_id
        self.setText(scene_name)
        # Future: Add thumbnail/icon
        #self.setIcon(QIcon())


class ProjectNavigator(QWidget):
    """
    Project navigator widget for managing projects and scenes.
    Displayed at the bottom of the main window.
    """
    
    # Project signals
    project_created = pyqtSignal(str, str)  # name, description
    project_opened = pyqtSignal(str)        # project_id
    project_saved = pyqtSignal(str)  # project_id
    project_closed = pyqtSignal()
    
    # Project file signals
    project_file_opened = pyqtSignal(str)   # file_path
    project_file_saved = pyqtSignal(str)    # file_path
    
    # Scene signals
    scene_selected = pyqtSignal(str)        # scene_id
    scene_created = pyqtSignal(str, str)    # name, description
    scene_renamed = pyqtSignal(str, str)    # scene_id, new_name
    scene_deleted = pyqtSignal(str)         # scene_id
    scene_duplicated = pyqtSignal(str)      # scene_id
    
    # Other signals
    scenes_reordered = pyqtSignal(list)     # scene_id_list
    
    def __init__(self, parent=None):
        """
        Initialize the project navigator.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Project manager reference (set externally)
        self.project_manager = None
        
        # Current project and scene
        self.current_project_id = None
        self.current_scene_id = None
        
        # Set up UI
        self.setup_ui()
        
        # Connect signals
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        
        # Header with project info and buttons
        self.header_layout = QHBoxLayout()
        
        # Project label
        self.project_label = QLabel("No Project")
        self.project_label.setStyleSheet("font-weight: bold;")
        self.header_layout.addWidget(self.project_label, 1)
        
        # Project menu button
        self.project_menu_btn = QToolButton()
        self.project_menu_btn.setText("Project")
        self.project_menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setup_project_menu()
        self.header_layout.addWidget(self.project_menu_btn)
        
        # Add header to main layout
        self.layout.addLayout(self.header_layout)
        
        # Scene list with header
        self.scenes_layout = QVBoxLayout()
        
        # Scenes header
        self.scenes_header = QHBoxLayout()
        self.scenes_label = QLabel("Scenes")
        self.scenes_label.setStyleSheet("font-weight: bold;")
        self.scenes_header.addWidget(self.scenes_label, 1)
        
        # Add scene button
        self.add_scene_btn = QPushButton("Add Scene")
        self.add_scene_btn.setFixedWidth(80)
        self.scenes_header.addWidget(self.add_scene_btn)
        
        self.scenes_layout.addLayout(self.scenes_header)
        
        # Scene list
        self.scene_list = QListWidget()
        self.scene_list.setDragEnabled(True)
        self.scene_list.setAcceptDrops(True)
        self.scene_list.setDropIndicatorShown(True)
        self.scene_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.scene_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.scene_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.scenes_layout.addWidget(self.scene_list)
        
        # Add scenes layout to main layout
        self.layout.addLayout(self.scenes_layout)
        
        # Initial state
        self.update_ui_state(False)
    
    def setup_project_menu(self):
        """Set up the project menu."""
        self.project_menu = QMenu(self)
        
        # New project action
        self.new_project_action = QAction("New Project", self)
        self.project_menu.addAction(self.new_project_action)
        
        # Open project actions
        self.open_project_action = QAction("Open Project...", self)
        self.project_menu.addAction(self.open_project_action)
        
        self.project_menu.addSeparator()
        
        # Save project actions
        self.save_project_action = QAction("Save", self)
        self.project_menu.addAction(self.save_project_action)
        
        self.save_as_action = QAction("Save As...", self)
        self.project_menu.addAction(self.save_as_action)
        
        self.project_menu.addSeparator()
        
        # Close project action
        self.close_project_action = QAction("Close Project", self)
        self.project_menu.addAction(self.close_project_action)
        
        # Set menu for button
        self.project_menu_btn.setMenu(self.project_menu)
    
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Project menu actions
        self.new_project_action.triggered.connect(self.on_new_project)
        self.open_project_action.triggered.connect(self.on_open_project)
        self.save_project_action.triggered.connect(self.on_save_project)
        self.save_as_action.triggered.connect(self.on_save_project_as)
        self.close_project_action.triggered.connect(self.on_close_project)
        
        # Scene controls
        self.add_scene_btn.clicked.connect(self.on_add_scene)
        self.scene_list.itemClicked.connect(self.on_scene_clicked)
        self.scene_list.customContextMenuRequested.connect(self.on_scene_context_menu)
        self.scene_list.model().rowsMoved.connect(self.on_scenes_reordered)
    
    def set_project_manager(self, project_manager):
        """
        Set the project manager.
        
        Args:
            project_manager: ProjectManager instance
        """
        self.project_manager = project_manager
        
        # Connect to project manager signals
        if self.project_manager:
            self.project_manager.project_created.connect(self.on_project_loaded)
            self.project_manager.project_loaded.connect(self.on_project_loaded)
            self.project_manager.project_closed.connect(self.on_project_closed)
            self.project_manager.scene_created.connect(self.on_scene_added)
            self.project_manager.scene_loaded.connect(self.on_scene_loaded)
            self.project_manager.scene_deleted.connect(self.on_scene_deleted)
            self.project_manager.project_changed.connect(self.on_project_changed)
    
    def update_ui_state(self, has_project):
        """
        Update the UI state based on whether a project is open.
        
        Args:
            has_project: Whether a project is currently open
        """
        # Update button states
        self.save_project_action.setEnabled(has_project)
        self.save_as_action.setEnabled(has_project)
        self.close_project_action.setEnabled(has_project)
        self.add_scene_btn.setEnabled(has_project)
        
        # Update scene list visibility
        self.scene_list.setEnabled(has_project)
        self.scenes_label.setEnabled(has_project)
    
    def on_new_project(self):
        """Handle new project action."""
        # Get project name from user
        name, ok = QInputDialog.getText(
            self, "New Project", "Project Name:", text="New Project"
        )
        
        if ok and name:
            description, _ = QInputDialog.getText(
                self, "Project Description", "Description (optional):"
            )
            
            # Emit signal to create new project
            self.project_created.emit(name, description)
    
    def on_open_project(self):
        """Handle open project action."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "LightCraft Projects (*.lightcraft)"
        )
        
        if file_path:
            # Emit signal to open project file
            self.project_file_opened.emit(file_path)
    
    def on_save_project(self):
        """Handle save project action."""
        self.project_saved.emit()
    
    def on_save_project_as(self):
        """Handle save project as action."""
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", "LightCraft Projects (*.lightcraft)"
        )
        
        if file_path:
            # Add extension if missing
            if not file_path.endswith('.lightcraft'):
                file_path += '.lightcraft'
                
            # Emit signal to save project to file
            self.project_file_saved.emit(file_path)

    def on_save_project(self):
        """Handle save project action."""
        if self.project_manager and self.project_manager.current_project_id:
            self.project_saved.emit(self.project_manager.current_project_id)
        else:
            # If no project is open, do a save as
            self.on_save_project_as()
    
    def on_close_project(self):
        """Handle close project action."""
        self.project_closed.emit()
    
    def on_add_scene(self):
        """Handle add scene button."""
        # Get scene name from user
        name, ok = QInputDialog.getText(
            self, "New Scene", "Scene Name:", text="New Scene"
        )
        
        if ok and name:
            description, _ = QInputDialog.getText(
                self, "Scene Description", "Description (optional):"
            )
            
            # Emit signal to create new scene
            self.scene_created.emit(name, description)
    
    def on_scene_clicked(self, item):
        """
        Handle scene selection.
        
        Args:
            item: Selected scene item
        """
        if hasattr(item, 'scene_id'):
            # Emit signal to select scene
            self.scene_selected.emit(item.scene_id)
    
    def on_scene_context_menu(self, position):
        """
        Show context menu for scenes.
        
        Args:
            position: Position where right-click occurred
        """
        # Get the item at the position
        item = self.scene_list.itemAt(position)
        if not item:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        rename_action = menu.addAction("Rename")
        duplicate_action = menu.addAction("Duplicate")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Show menu and get selected action
        action = menu.exec(self.scene_list.mapToGlobal(position))
        
        # Handle selected action
        if action == rename_action:
            self.rename_scene(item)
        elif action == duplicate_action:
            self.duplicate_scene(item)
        elif action == delete_action:
            self.delete_scene(item)
    
    def rename_scene(self, item):
        """
        Rename a scene.
        
        Args:
            item: Scene item to rename
        """
        if hasattr(item, 'scene_id'):
            # Get new name from user
            name, ok = QInputDialog.getText(
                self, "Rename Scene", "Scene Name:", text=item.text()
            )
            
            if ok and name:
                # Emit signal to rename scene
                self.scene_renamed.emit(item.scene_id, name)
                
                # Update item text
                item.setText(name)
    
    def duplicate_scene(self, item):
        """
        Duplicate a scene.
        
        Args:
            item: Scene item to duplicate
        """
        if hasattr(item, 'scene_id'):
            # Emit signal to duplicate scene
            self.scene_duplicated.emit(item.scene_id)
    
    def delete_scene(self, item):
        """
        Delete a scene.
        
        Args:
            item: Scene item to delete
        """
        if hasattr(item, 'scene_id'):
            # Confirm deletion
            reply = QMessageBox.question(
                self, "Delete Scene",
                f"Are you sure you want to delete scene '{item.text()}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Emit signal to delete scene
                self.scene_deleted.emit(item.scene_id)
    
    def on_scenes_reordered(self):
        """Handle scenes being reordered via drag and drop."""
        # Get scene IDs in new order
        scene_ids = []
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            if hasattr(item, 'scene_id'):
                scene_ids.append(item.scene_id)
        
        # Emit signal with new order
        if scene_ids:
            self.scenes_reordered.emit(scene_ids)
    
    def on_project_loaded(self, project_id):
        """
        Handle project loaded event.
        
        Args:
            project_id: ID of the loaded project
        """
        if not self.project_manager:
            return
        
        # Update current project
        self.current_project_id = project_id
        
        # Get project info
        project_info = self.project_manager.get_project_info()
        if project_info:
            self.project_label.setText(project_info.get('name', 'Unnamed Project'))
        
        # Update UI state
        self.update_ui_state(True)
        
        # Populate scene list
        self.populate_scenes()
    
    def on_project_closed(self):
        """Handle project closed event."""
        # Clear current project
        self.current_project_id = None
        self.current_scene_id = None
        
        # Update UI
        self.project_label.setText("No Project")
        self.scene_list.clear()
        self.update_ui_state(False)
    
    def on_scene_added(self, scene_id):
        """
        Handle scene added event.
        
        Args:
            scene_id: ID of the added scene
        """
        if not self.project_manager:
            return
        
        # Get scene info
        scene_info = self.project_manager.get_scene_info(scene_id)
        if not scene_info:
            return
        
        # Add to scene list
        item = SceneItem(scene_id, scene_info['name'])
        self.scene_list.addItem(item)
        
        # Select the new scene
        self.scene_list.setCurrentItem(item)
        self.current_scene_id = scene_id
    
    def on_scene_loaded(self, scene_id):
        """
        Handle scene loaded event.
        
        Args:
            scene_id: ID of the loaded scene
        """
        self.current_scene_id = scene_id
        
        # Select the scene in the list
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            if hasattr(item, 'scene_id') and item.scene_id == scene_id:
                self.scene_list.setCurrentItem(item)
                break
    
    def on_scene_deleted(self, scene_id):
        """
        Handle scene deleted event.
        
        Args:
            scene_id: ID of the deleted scene
        """
        # Remove from scene list
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            if hasattr(item, 'scene_id') and item.scene_id == scene_id:
                self.scene_list.takeItem(i)
                break
    
    def populate_scenes(self):
        """Populate the scene list with scenes from current project."""
        if not self.project_manager or not self.current_project_id:
            return
        
        # Clear scene list
        self.scene_list.clear()
        
        # Get project scenes
        scenes = self.project_manager.get_project_scenes()
        
        # Add scenes to list
        for scene in scenes:
            item = SceneItem(scene['id'], scene['name'])
            self.scene_list.addItem(item)
            
            # Select current scene if any
            if self.current_scene_id and scene['id'] == self.current_scene_id:
                self.scene_list.setCurrentItem(item)
    
    def on_project_changed(self, has_changes):
        """
        Handle project changed event.
        
        Args:
            has_changes: Whether project has unsaved changes
        """
        # Update project label to indicate unsaved changes
        project_info = self.project_manager.get_project_info()
        if project_info:
            name = project_info.get('name', 'Unnamed Project')
            if has_changes:
                self.project_label.setText(f"{name} *")
            else:
                self.project_label.setText(name)
