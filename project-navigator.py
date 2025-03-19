"""
Project controller for the LightCraft application.
Coordinates project and scene management with UI components.
"""

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication, QInputDialog

import os
import sys
from datetime import datetime

from lightcraft.controllers.project_manager import ProjectManager
from lightcraft.models.project_file import ProjectFile


class ProjectController(QObject):
    """
    Controller for managing projects and scenes.
    Connects the project manager with UI components.
    """
    
    # Signals
    application_close_requested = pyqtSignal(bool)  # Can close?
    
    # Project signals
    project_created = pyqtSignal(str)  # Project ID
    project_loaded = pyqtSignal(str)   # Project ID
    project_saved = pyqtSignal(str)    # Project ID
    project_closed = pyqtSignal()
    
    # File signals
    project_file_opened = pyqtSignal(str)  # File path
    project_file_saved = pyqtSignal(str)   # File path
    
    def __init__(self, scene_controller, parent=None):
        """
        Initialize the project controller.
        
        Args:
            scene_controller: The scene controller instance
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.scene_controller = scene_controller
        
        # Create project manager
        self.project_manager = ProjectManager(scene_controller, self)
        
        # Project navigator reference (set externally)
        self.project_navigator = None
        
        # Auto-save timer
        self.auto_save_timer = None
        
        # Initialize auto-save
        self._init_auto_save()
    
    def _init_auto_save(self):
        """Initialize auto-save timer."""
        # Create timer for auto-save
        self.auto_save_timer = QTimer(self)
        
        # Get auto-save interval from settings (default 5 minutes)
        interval = 300
        if hasattr(self.project_manager.db, 'get_setting'):
            interval_str = self.project_manager.db.get_setting('auto_save_interval', '300')
            try:
                interval = int(interval_str)
            except ValueError:
                interval = 300
        
        # Set timer interval
        self.auto_save_timer.setInterval(interval * 1000)  # Convert to milliseconds
        
        # Connect timer signal
        self.auto_save_timer.timeout.connect(self.perform_auto_save)
        
        # Start the timer
        self.auto_save_timer.start()
    
    def set_project_navigator(self, navigator):
        """
        Set the project navigator reference.
        
        Args:
            navigator: ProjectNavigator instance
        """
        self.project_navigator = navigator
        
        if self.project_navigator:
            # Set the project manager in the navigator
            self.project_navigator.set_project_manager(self.project_manager)
            
            # Connect navigator signals
            self._connect_navigator_signals()
    
    def _connect_navigator_signals(self):
        """Connect to project navigator signals."""
        # Project signals
        self.project_navigator.project_created.connect(self.create_project)
        self.project_navigator.project_opened.connect(self.open_project)
        self.project_navigator.project_saved.connect(self.save_project)
        self.project_navigator.project_closed.connect(self.close_project)
        
        # Project file signals
        self.project_navigator.project_file_opened.connect(self.open_project_file)
        self.project_navigator.project_file_saved.connect(self.save_project_to_file)
        
        # Scene signals
        self.project_navigator.scene_selected.connect(self.load_scene)
        self.project_navigator.scene_created.connect(self.create_scene)
        self.project_navigator.scene_renamed.connect(self.rename_scene)
        self.project_navigator.scene_deleted.connect(self.delete_scene)
        self.project_navigator.scene_duplicated.connect(self.duplicate_scene)
        
        # Other signals
        self.project_navigator.scenes_reordered.connect(self.reorder_scenes)
    
    def create_project(self, name, description=""):
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Optional project description
        
        Returns:
            Project ID if successful, None otherwise
        """
        # Check for unsaved changes
        if self.project_manager.has_unsaved_changes:
            # Show confirmation dialog
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Unsaved Changes",
                "There are unsaved changes in the current project. Save before creating a new project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return None
            elif reply == QMessageBox.StandardButton.Yes:
                # Save current project first
                if not self.save_project():
                    # If save failed or was cancelled, abort
                    return None
        
        # Create the project
        project_id = self.project_manager.create_new_project(name, description)
        if project_id:
            self.project_created.emit(project_id)
        
        return project_id
    
    def open_project(self, project_id):
        """
        Open a project.
        
        Args:
            project_id: ID of the project to open
        
        Returns:
            True if successful, False otherwise
        """
        # Check for unsaved changes
        if self.project_manager.has_unsaved_changes:
            # Show confirmation dialog
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Unsaved Changes",
                "There are unsaved changes in the current project. Save before opening another project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            elif reply == QMessageBox.StandardButton.Yes:
                # Save current project first
                if not self.save_project():
                    # If save failed or was cancelled, abort
                    return False
        
        # Open the project
        success = self.project_manager.load_project(project_id)
        if success:
            self.project_loaded.emit(project_id)
        
        return success
    
    def open_project_file(self, file_path):
        """
        Open a project from a file.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            Project ID if successful, None otherwise
        """
        # Check if file exists
        if not os.path.exists(file_path):
            QMessageBox.critical(
                QApplication.activeWindow(),
                "File Not Found",
                f"Project file not found: {file_path}"
            )
            return None
        
        # Check for unsaved changes
        if self.project_manager.has_unsaved_changes:
            # Show confirmation dialog
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Unsaved Changes",
                "There are unsaved changes in the current project. Save before opening another project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return None
            elif reply == QMessageBox.StandardButton.Yes:
                # Save current project first
                if not self.save_project():
                    # If save failed or was cancelled, abort
                    return None
        
        # Load project from file
        try:
            # Use ProjectFile to load the file
            project_data, scenes_data, thumbnails = ProjectFile.load_project(file_path)
            
            if not project_data:
                QMessageBox.critical(
                    QApplication.activeWindow(),
                    "Error Opening Project",
                    "Failed to open project file. The file may be corrupted or in an unsupported format."
                )
                return None
            
            # Close current project if any
            if self.project_manager.current_project_id:
                self.project_manager.close_project()
            
            # Create new project in database
            project_id = self.project_manager.db.create_project(project_data)
            if not project_id:
                raise Exception("Failed to create project in database")
            
            # Create scenes in database
            for scene_data in scenes_data:
                scene_data['project_id'] = project_id
                scene_id = self.project_manager.db.create_scene(scene_data)
                
                # Add thumbnail if available
                if thumbnails and scene_id in thumbnails:
                    self.project_manager.db.update_scene_thumbnail(scene_id, thumbnails[scene_id])
            
            # Set the file path
            self.project_manager.db.update_project(project_id, {'file_path': file_path})
            
            # Load the project
            self.project_manager.load_project(project_id)
            
            # Emit signal
            self.project_file_opened.emit(file_path)
            self.project_loaded.emit(project_id)
            
            return project_id
        except Exception as e:
            QMessageBox.critical(
                QApplication.activeWindow(),
                "Error Opening Project",
                f"An error occurred while opening the project file: {str(e)}"
            )
            return None
    
    def save_project(self):
        """
        Save the current project.
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, nothing to save
        if not self.project_manager.current_project_id:
            return False
        
        # If project doesn't have a file path yet, do Save As
        if not self.project_manager.current_file_path:
            return self.save_project_as()
        
        # Save to existing file path
        success = self.save_project_to_file(self.project_manager.current_file_path)
        if success:
            self.project_saved.emit(self.project_manager.current_project_id)
        
        return success
    
    def save_project_as(self):
        """
        Save the current project to a new file.
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, nothing to save
        if not self.project_manager.current_project_id:
            return False
        
        # Show file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            QApplication.activeWindow(),
            "Save Project As",
            "",
            "LightCraft Projects (*.lightcraft)"
        )
        
        if not file_path:
            # User cancelled
            return False
        
        # Add extension if not provided
        if not file_path.endswith('.lightcraft'):
            file_path += '.lightcraft'
        
        # Save to selected file
        success = self.save_project_to_file(file_path)
        if success:
            self.project_file_saved.emit(file_path)
            self.project_saved.emit(self.project_manager.current_project_id)
        
        return success
    
    def save_project_to_file(self, file_path):
        """
        Save the current project to a specific file.
        
        Args:
            file_path: Path to save to
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, nothing to save
        if not self.project_manager.current_project_id:
            return False
        
        try:
            # Save current scene first
            if self.project_manager.current_scene_id:
                self.project_manager.save_current_scene()
            
            # Get project data
            project_data = self.project_manager.get_project_info()
            if not project_data:
                raise Exception("Failed to get project data")
            
            # Get all scenes
            scenes = []
            for scene_info in self.project_manager.get_project_scenes():
                scene_data = self.project_manager.get_scene_info(scene_info['id'])
                if scene_data:
                    scenes.append(scene_data)
            
            # Get thumbnails
            thumbnails = {}
            for scene in scenes:
                thumbnail_data = self.project_manager.db.get_scene_thumbnail(scene['id'])
                if thumbnail_data:
                    thumbnails[scene['id']] = thumbnail_data
            
            # Update file path in project data
            project_data['file_path'] = file_path
            self.project_manager.db.update_project(
                self.project_manager.current_project_id,
                {'file_path': file_path}
            )
            
            # Save to file using ProjectFile
            success = ProjectFile.save_project(file_path, project_data, scenes, thumbnails)
            
            if success:
                # Update file path in project manager
                self.project_manager.current_file_path = file_path
                
                # Clear unsaved changes flag
                self.project_manager.has_unsaved_changes = False
                self.project_manager.project_changed.emit(False)
                
                # Emit signal
                self.project_file_saved.emit(file_path)
                
                return True
            else:
                raise Exception("Failed to save project file")
        except Exception as e:
            QMessageBox.critical(
                QApplication.activeWindow(),
                "Error Saving Project",
                f"An error occurred while saving the project file: {str(e)}"
            )
            return False
    
    def close_project(self):
        """
        Close the current project.
        
        Returns:
            True if closed, False if cancelled
        """
        # If no project is open, nothing to close
        if not self.project_manager.current_project_id:
            return True
        
        # Check for unsaved changes
        if self.project_manager.has_unsaved_changes:
            # Show confirmation dialog
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Unsaved Changes",
                "There are unsaved changes in the current project. Save before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            elif reply == QMessageBox.StandardButton.Yes:
                # Save current project first
                if not self.save_project():
                    # If save failed or was cancelled, abort
                    return False
        
        # Close the project
        success = self.project_manager.close_project()
        if success:
            self.project_closed.emit()
        
        return success
    
    def create_scene(self, name, description=""):
        """
        Create a new scene in the current project.
        
        Args:
            name: Scene name
            description: Optional scene description
        
        Returns:
            Scene ID if successful, None otherwise
        """
        # If no project is open, can't create a scene
        if not self.project_manager.current_project_id:
            return None
        
        # Create the scene
        scene_id = self.project_manager.create_scene(name, description)
        
        return scene_id
    
    def load_scene(self, scene_id):
        """
        Load a scene.
        
        Args:
            scene_id: ID of the scene to load
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, can't load a scene
        if not self.project_manager.current_project_id:
            return False
        
        # Check for unsaved changes
        if self.project_manager.has_unsaved_changes:
            # Show confirmation dialog
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Unsaved Changes",
                "There are unsaved changes in the current scene. Save before switching?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            elif reply == QMessageBox.StandardButton.Yes:
                # Save current scene first
                if not self.project_manager.save_current_scene():
                    # If save failed, abort
                    return False
        
        # Check for auto-save
        auto_save = self.project_manager.check_for_auto_save(scene_id)
        if auto_save:
            # Show dialog asking to recover from auto-save
            auto_save_time = datetime.fromisoformat(auto_save['created_at'])
            formatted_time = auto_save_time.strftime("%Y-%m-%d %H:%M:%S")
            
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Auto-Save Recovery",
                f"An auto-saved version of this scene from {formatted_time} was found. Would you like to recover it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Load from auto-save
                return self.project_manager.recover_from_auto_save(scene_id)
        
        # Load the scene normally
        return self.project_manager.load_scene(scene_id)
    
    def rename_scene(self, scene_id, new_name):
        """
        Rename a scene.
        
        Args:
            scene_id: ID of the scene to rename
            new_name: New name for the scene
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, can't rename a scene
        if not self.project_manager.current_project_id:
            return False
        
        # Rename the scene
        return self.project_manager.rename_scene(scene_id, new_name)
    
    def delete_scene(self, scene_id):
        """
        Delete a scene.
        
        Args:
            scene_id: ID of the scene to delete
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, can't delete a scene
        if not self.project_manager.current_project_id:
            return False
        
        # Confirm deletion
        scene_info = self.project_manager.get_scene_info(scene_id)
        scene_name = scene_info['name'] if scene_info else "this scene"
        
        reply = QMessageBox.question(
            QApplication.activeWindow(),
            "Delete Scene",
            f"Are you sure you want to delete the scene '{scene_name}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # Delete the scene
        return self.project_manager.delete_scene(scene_id)
    
    def duplicate_scene(self, scene_id):
        """
        Duplicate a scene.
        
        Args:
            scene_id: ID of the scene to duplicate
        
        Returns:
            ID of the new scene if successful, None otherwise
        """
        # If no project is open, can't duplicate a scene
        if not self.project_manager.current_project_id:
            return None
        
        # Get new name for the copy
        scene_info = self.project_manager.get_scene_info(scene_id)
        scene_name = scene_info['name'] if scene_info else "Scene"
        
        new_name = f"Copy of {scene_name}"
        
        # Duplicate the scene
        return self.project_manager.duplicate_scene(scene_id, new_name)
    
    def reorder_scenes(self, scene_order):
        """
        Reorder scenes.
        
        Args:
            scene_order: List of scene IDs in the new order
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open, can't reorder scenes
        if not self.project_manager.current_project_id:
            return False
        
        # Reorder the scenes
        return self.project_manager.reorder_scenes(scene_order)
    
    def perform_auto_save(self):
        """
        Perform auto-save for the current scene.
        
        Returns:
            True if successful, False otherwise
        """
        # If no project is open or no scene is active, nothing to save
        if (not self.project_manager.current_project_id or 
            not self.project_manager.current_scene_id):
            return False
        
        # If no changes, no need to auto-save
        if not self.project_manager.has_unsaved_changes:
            return False
        
        # Perform auto-save
        return self.project_manager.perform_auto_save()
    
    def can_application_close(self):
        """
        Check if the application can be closed.
        Shows prompts for unsaved changes if needed.
        
        Returns:
            True if can close, False if should cancel
        """
        # If no project is open or no unsaved changes, can close
        if (not self.project_manager.current_project_id or 
            not self.project_manager.has_unsaved_changes):
            return True
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            QApplication.activeWindow(),
            "Unsaved Changes",
            "There are unsaved changes in the current project. Save before exiting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        elif reply == QMessageBox.StandardButton.Yes:
            # Save current project first
            if not self.save_project():
                # If save failed or was cancelled, abort
                return False
        
        # Can close
        return True
    
    def application_close_event(self, event):
        """
        Handle application close event.
        
        Args:
            event: QCloseEvent
        """
        if self.can_application_close():
            event.accept()
            # Clean up resources
            if self.auto_save_timer:
                self.auto_save_timer.stop()
            if self.project_manager.db:
                self.project_manager.db.disconnect()
        else:
            event.ignore()
