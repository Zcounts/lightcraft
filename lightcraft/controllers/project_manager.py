"""
Project manager for the LightCraft application.
Handles project and scene management logic.
"""

import os
import json
import threading
import time
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from lightcraft.models.project_db import ProjectDatabase
from lightcraft.models.equipment import LightingEquipment, Camera, SetElement
from lightcraft.config import APP_DATA_DIR


class ProjectManager(QObject):
    """
    Manager for projects and scenes.
    Handles saving, loading, and auto-saving projects.
    """
    
    # Signals
    project_created = pyqtSignal(str)  # Project ID
    project_loaded = pyqtSignal(str)   # Project ID
    project_saved = pyqtSignal(str)    # Project ID
    project_closed = pyqtSignal()
    
    scene_created = pyqtSignal(str)    # Scene ID
    scene_loaded = pyqtSignal(str)     # Scene ID
    scene_saved = pyqtSignal(str)      # Scene ID
    scene_deleted = pyqtSignal(str)    # Scene ID
    
    auto_save_triggered = pyqtSignal()
    project_changed = pyqtSignal(bool) # Has unsaved changes
    
    def __init__(self, scene_controller, parent=None):
        """
        Initialize the project manager.
        
        Args:
            scene_controller: The scene controller instance
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.scene_controller = scene_controller
        self.db = ProjectDatabase()
        
        # Current project and scene
        self.current_project_id = None
        self.current_scene_id = None
        
        # Project file path
        self.current_file_path = None
        
        # Track changes
        self.has_unsaved_changes = False
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # seconds (5 minutes)
        self.auto_save_timer = None
        
        # Initialize auto-save timer
        self._init_auto_save()
        
        # Connect to scene controller signals
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect to scene controller signals."""
        if hasattr(self.scene_controller, 'scene_changed'):
            self.scene_controller.scene_changed.connect(self._on_scene_changed)
        
        if hasattr(self.scene_controller, 'item_added'):
            self.scene_controller.item_added.connect(self._on_scene_changed)
        
        if hasattr(self.scene_controller, 'item_removed'):
            self.scene_controller.item_removed.connect(self._on_scene_changed)
        
        if hasattr(self.scene_controller, 'item_modified'):
            self.scene_controller.item_modified.connect(self._on_scene_changed)
    
    def _init_auto_save(self):
        """Initialize auto-save timer."""
        # Get auto-save interval from settings
        interval_str = self.db.get_setting('auto_save_interval', '300')
        self.auto_save_interval = int(interval_str)
        
        # Create timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.perform_auto_save)
        
        # Start timer if auto-save is enabled
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.auto_save_interval * 1000)
    
    def create_new_project(self, name, description=None):
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Optional project description
        
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            # If there's an existing project with unsaved changes, prompt to save
            if self.current_project_id and self.has_unsaved_changes:
                return None  # Should be handled by UI
            
            # Create project data
            project_data = {
                'name': name,
                'description': description,
                'create_default_scene': True  # Create a default scene
            }
            
            # Create project in database
            project_id = self.db.create_project(project_data)
            if not project_id:
                return None
            
            # Get first scene ID
            scenes = self.db.get_project_scenes(project_id)
            first_scene_id = scenes[0]['id'] if scenes else None
            
            # Set as current project
            self.current_project_id = project_id
            self.current_scene_id = first_scene_id
            self.current_file_path = None
            self.has_unsaved_changes = False
            
            # Load scene in scene controller
            if first_scene_id:
                self._load_scene_data(first_scene_id)
            
            # Emit signals
            self.project_created.emit(project_id)
            if first_scene_id:
                self.scene_loaded.emit(first_scene_id)
            
            return project_id
        except Exception as e:
            print(f"Error creating new project: {e}")
            return None
    
    def load_project(self, project_id):
        """
        Load a project.
        
        Args:
            project_id: ID of the project to load
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # If there's an existing project with unsaved changes, prompt to save
            if self.current_project_id and self.has_unsaved_changes:
                return False  # Should be handled by UI
            
            # Get project data
            project = self.db.get_project(project_id)
            if not project:
                return False
            
            # Get first scene
            scenes = self.db.get_project_scenes(project_id)
            first_scene_id = scenes[0]['id'] if scenes else None
            
            # Set as current project
            self.current_project_id = project_id
            self.current_scene_id = first_scene_id
            self.current_file_path = project.get('file_path')
            self.has_unsaved_changes = False
            
            # Update last opened timestamp
            self.db.update_project(project_id, {
                'last_opened_at': datetime.now().isoformat()
            })
            
            # Load scene in scene controller
            if first_scene_id:
                self._load_scene_data(first_scene_id)
            
            # Emit signals
            self.project_loaded.emit(project_id)
            if first_scene_id:
                self.scene_loaded.emit(first_scene_id)
            
            return True
        except Exception as e:
            print(f"Error loading project: {e}")
            return False
    
    def load_project_from_file(self, file_path):
        """
        Load a project from a file.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            # If there's an existing project with unsaved changes, prompt to save
            if self.current_project_id and self.has_unsaved_changes:
                return None  # Should be handled by UI
            
            # Read file
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            
            # Check format
            if 'project' not in file_data or 'scenes' not in file_data:
                raise ValueError("Invalid project file format")
            
            # Import project
            project_data = file_data['project']
            project_data['file_path'] = file_path
            
            # Create project in database
            project_id = self.db.create_project(project_data)
            if not project_id:
                return None
            
            # Import scenes
            for scene_data in file_data['scenes']:
                scene_data['project_id'] = project_id
                self.db.create_scene(scene_data)
            
            # Get first scene
            scenes = self.db.get_project_scenes(project_id)
            first_scene_id = scenes[0]['id'] if scenes else None
            
            # Set as current project
            self.current_project_id = project_id
            self.current_scene_id = first_scene_id
            self.current_file_path = file_path
            self.has_unsaved_changes = False
            
            # Load scene in scene controller
            if first_scene_id:
                self._load_scene_data(first_scene_id)
            
            # Emit signals
            self.project_loaded.emit(project_id)
            if first_scene_id:
                self.scene_loaded.emit(first_scene_id)
            
            return project_id
        except Exception as e:
            print(f"Error loading project from file: {e}")
            return None
    
    def save_project(self, file_path=None):
        """
        Save the current project.
        
        Args:
            file_path: Optional path to save to (for Save As)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id:
                return False
            
            # Save current scene first
            if self.current_scene_id:
                self.save_current_scene()
            
            # Update file path if provided
            if file_path:
                self.current_file_path = file_path
                self.db.update_project(self.current_project_id, {
                    'file_path': file_path
                })
            
            # If we have a file path, save to file
            if self.current_file_path:
                self._save_to_file(self.current_file_path)
            
            # Clear unsaved changes flag
            self.has_unsaved_changes = False
            self.project_changed.emit(False)
            
            # Emit signal
            self.project_saved.emit(self.current_project_id)
            
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_to_file(self, file_path):
        """
        Save the current project to a file.
        
        Args:
            file_path: Path to save to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get project data
            project = self.db.get_project(self.current_project_id)
            if not project:
                return False
            
            # Get all scenes
            scenes = []
            for scene_info in self.db.get_project_scenes(self.current_project_id):
                scene_data = self.db.get_scene(scene_info['id'])
                scenes.append(scene_data)
            
            # Create file data
            file_data = {
                'project': project,
                'scenes': scenes,
                'format_version': '1.0',
                'save_date': datetime.now().isoformat()
            }
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def close_project(self):
        """
        Close the current project.
        
        Returns:
            True if closed, False if cancelled
        """
        # If there are unsaved changes, prompt to save
        if self.has_unsaved_changes:
            return False  # Should be handled by UI
        
        # Clear current project
        self.current_project_id = None
        self.current_scene_id = None
        self.current_file_path = None
        self.has_unsaved_changes = False
        
        # Clear scene controller
        self.scene_controller.clear_scene()
        
        # Emit signal
        self.project_closed.emit()
        
        return True
    
    def create_scene(self, name, description=None):
        """
        Create a new scene in the current project.
        
        Args:
            name: Scene name
            description: Optional scene description
        
        Returns:
            Scene ID if successful, None otherwise
        """
        try:
            if not self.current_project_id:
                return None
            
            # Save current scene first
            if self.current_scene_id and self.has_unsaved_changes:
                self.save_current_scene()
            
            # Create scene data
            scene_data = {
                'project_id': self.current_project_id,
                'name': name,
                'description': description
            }
            
            # Create scene in database
            scene_id = self.db.create_scene(scene_data)
            if not scene_id:
                return None
            
            # Create empty scene in scene controller
            self.scene_controller.clear_scene()
            
            # Set as current scene
            self.current_scene_id = scene_id
            self.has_unsaved_changes = True
            
            # Generate thumbnail
            self._update_scene_thumbnail(scene_id)
            
            # Emit signals
            self.scene_created.emit(scene_id)
            self.scene_loaded.emit(scene_id)
            self.project_changed.emit(True)
            
            return scene_id
        except Exception as e:
            print(f"Error creating scene: {e}")
            return None
    
    def load_scene(self, scene_id):
        """
        Load a scene.
        
        Args:
            scene_id: ID of the scene to load
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id:
                return False
            
            # Check if scene belongs to current project
            scene = self.db.get_scene(scene_id)
            if not scene or scene['project_id'] != self.current_project_id:
                return False
            
            # If current scene has unsaved changes, prompt to save
            if self.current_scene_id and self.has_unsaved_changes:
                return False  # Should be handled by UI
            
            # Load scene data into scene controller
            if not self._load_scene_data(scene_id):
                return False
            
            # Set as current scene
            self.current_scene_id = scene_id
            self.has_unsaved_changes = False
            
            # Emit signal
            self.scene_loaded.emit(scene_id)
            
            return True
        except Exception as e:
            print(f"Error loading scene: {e}")
            return False
    
    def _load_scene_data(self, scene_id):
        """
        Load scene data into the scene controller.
        
        Args:
            scene_id: ID of the scene to load
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get scene data
            scene = self.db.get_scene(scene_id)
            if not scene:
                return False
            
            # Check for auto-save data
            auto_save = self.db.get_auto_save(scene['project_id'], scene_id)
            if auto_save:
                # Handle auto-save recovery (UI should prompt user)
                # For now, we'll just use the saved data
                pass
            
            # Clear current scene
            self.scene_controller.clear_scene()
            
            # Create new scene in scene controller
            self.scene_controller.new_scene(scene['name'])
            
            # Load items into scene
            if 'lights' in scene:
                for light_data in scene.get('lights', []):
                    light = LightingEquipment.from_dict(light_data)
                    self.scene_controller.add_item('light', light)
            
            if 'cameras' in scene:
                for camera_data in scene.get('cameras', []):
                    camera = Camera.from_dict(camera_data)
                    self.scene_controller.add_item('camera', camera)
            
            if 'set_elements' in scene:
                for element_data in scene.get('set_elements', []):
                    element = SetElement.from_dict(element_data)
                    self.scene_controller.add_item('set_element', element)
            
            # Set scene metadata
            if hasattr(self.scene_controller.current_scene, 'description'):
                self.scene_controller.current_scene.description = scene.get('description', '')
            
            return True
        except Exception as e:
            print(f"Error loading scene data: {e}")
            return False
    
    def save_current_scene(self):
        """
        Save the current scene.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id or not self.current_scene_id:
                return False
            
            # Get current scene data from scene controller
            scene_data = self._get_current_scene_data()
            if not scene_data:
                return False
            
            # Update scene in database
            if not self.db.update_scene(self.current_scene_id, scene_data):
                return False
            
            # Create version snapshot
            self.db.create_version(
                self.current_project_id, 
                self.current_scene_id, 
                scene_data,
                f"Auto version at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Clear auto-save for this scene
            self.db.clear_auto_save(self.current_project_id, self.current_scene_id)
            
            # Update scene thumbnail
            self._update_scene_thumbnail(self.current_scene_id)
            
            # Clear unsaved changes flag
            self.has_unsaved_changes = False
            self.project_changed.emit(False)
            
            # Emit signal
            self.scene_saved.emit(self.current_scene_id)
            
            return True
        except Exception as e:
            print(f"Error saving scene: {e}")
            return False
    
    def _get_current_scene_data(self):
        """
        Get current scene data from scene controller.
        
        Returns:
            Dictionary with scene data or None if failed
        """
        try:
            if not hasattr(self.scene_controller, 'current_scene'):
                return None
            
            current_scene = self.scene_controller.current_scene
            if not current_scene:
                return None
            
            # Create scene data dictionary
            scene_data = {
                'name': current_scene.name,
                'description': getattr(current_scene, 'description', '')
            }
            
            # Add items
            scene_data['lights'] = [light.to_dict() for light in current_scene.lights]
            scene_data['cameras'] = [camera.to_dict() for camera in current_scene.cameras]
            scene_data['set_elements'] = [element.to_dict() for element in current_scene.set_elements]
            
            return scene_data
        except Exception as e:
            print(f"Error getting current scene data: {e}")
            return None
    
    def delete_scene(self, scene_id):
        """
        Delete a scene.
        
        Args:
            scene_id: ID of the scene to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id:
                return False
            
            # Check if scene belongs to current project
            scene = self.db.get_scene(scene_id)
            if not scene or scene['project_id'] != self.current_project_id:
                return False
            
            # Check if it's the only scene
            scenes = self.db.get_project_scenes(self.current_project_id)
            if len(scenes) <= 1:
                # Can't delete the only scene
                return False
            
            # Delete scene from database
            if not self.db.delete_scene(scene_id):
                return False
            
            # If the deleted scene was current, load another scene
            if self.current_scene_id == scene_id:
                # Get first available scene
                remaining_scenes = self.db.get_project_scenes(self.current_project_id)
                if remaining_scenes:
                    new_scene_id = remaining_scenes[0]['id']
                    self.load_scene(new_scene_id)
                else:
                    # No scenes left (shouldn't happen)
                    self.current_scene_id = None
                    self.scene_controller.clear_scene()
            
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.project_changed.emit(True)
            
            # Emit signal
            self.scene_deleted.emit(scene_id)
            
            return True
        except Exception as e:
            print(f"Error deleting scene: {e}")
            return False
    
    def duplicate_scene(self, scene_id, new_name=None):
        """
        Duplicate a scene.
        
        Args:
            scene_id: ID of the scene to duplicate
            new_name: Optional name for the new scene
        
        Returns:
            ID of the new scene if successful, None otherwise
        """
        try:
            if not self.current_project_id:
                return None
            
            # Check if scene belongs to current project
            scene = self.db.get_scene(scene_id)
            if not scene or scene['project_id'] != self.current_project_id:
                return None
            
            # Save current scene first if it has unsaved changes
            if self.current_scene_id and self.has_unsaved_changes:
                self.save_current_scene()
            
            # Duplicate scene in database
            new_scene_id = self.db.duplicate_scene(scene_id, new_name)
            if not new_scene_id:
                return None
            
            # Load the new scene
            self.load_scene(new_scene_id)
            
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.project_changed.emit(True)
            
            # Emit signals
            self.scene_created.emit(new_scene_id)
            
            return new_scene_id
        except Exception as e:
            print(f"Error duplicating scene: {e}")
            return None
    
    def rename_scene(self, scene_id, new_name):
        """
        Rename a scene.
        
        Args:
            scene_id: ID of the scene to rename
            new_name: New name for the scene
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id:
                return False
            
            # Check if scene belongs to current project
            scene = self.db.get_scene(scene_id)
            if not scene or scene['project_id'] != self.current_project_id:
                return False
            
            # Update scene in database
            if not self.db.update_scene(scene_id, {'name': new_name}):
                return False
            
            # Update scene controller if this is the current scene
            if self.current_scene_id == scene_id and hasattr(self.scene_controller, 'current_scene'):
                self.scene_controller.current_scene.name = new_name
            
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.project_changed.emit(True)
            
            return True
        except Exception as e:
            print(f"Error renaming scene: {e}")
            return False
    
    def reorder_scenes(self, scene_order):
        """
        Reorder scenes.
        
        Args:
            scene_order: List of scene IDs in the new order
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id:
                return False
            
            # Update scene order in database
            if not self.db.reorder_scenes(self.current_project_id, scene_order):
                return False
            
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.project_changed.emit(True)
            
            return True
        except Exception as e:
            print(f"Error reordering scenes: {e}")
            return False
    
    def _update_scene_thumbnail(self, scene_id):
        """
        Update scene thumbnail.
        
        Args:
            scene_id: ID of the scene
        """
        try:
            # Generate thumbnail from scene
            thumbnail_data = self.db.generate_thumbnail_from_scene(scene_id)
            if thumbnail_data:
                # Save thumbnail to database
                self.db.update_scene_thumbnail(scene_id, thumbnail_data)
                
                # If this is the current project's first scene, update project thumbnail too
                scenes = self.db.get_project_scenes(self.current_project_id)
                if scenes and scenes[0]['id'] == scene_id:
                    self.db.update_project_thumbnail(self.current_project_id, thumbnail_data)
        except Exception as e:
            print(f"Error updating scene thumbnail: {e}")
    
    def _on_scene_changed(self, *args):
        """
        Handle scene changes.
        
        Args:
            *args: Arguments from the signal
        """
        # Set unsaved changes flag
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.project_changed.emit(True)
    
    def perform_auto_save(self):
        """Perform auto-save for the current scene."""
        try:
            if not self.current_project_id or not self.current_scene_id:
                return
            
            if not self.has_unsaved_changes:
                return
            
            # Get current scene data
            scene_data = self._get_current_scene_data()
            if not scene_data:
                return
            
            # Save to auto-save table
            self.db.create_auto_save(
                self.current_project_id, 
                self.current_scene_id, 
                scene_data
            )
            
            # Emit signal
            self.auto_save_triggered.emit()
        except Exception as e:
            print(f"Error performing auto-save: {e}")
    
    def check_for_auto_save(self, scene_id):
        """
        Check if there's an auto-save for a scene.
        
        Args:
            scene_id: ID of the scene to check
        
        Returns:
            Auto-save data or None if not found
        """
        if not self.current_project_id:
            return None
            
        return self.db.get_auto_save(self.current_project_id, scene_id)
    
    def recover_from_auto_save(self, scene_id):
        """
        Recover a scene from auto-save.
        
        Args:
            scene_id: ID of the scene to recover
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.current_project_id:
                return False
            
            # Get auto-save data
            auto_save = self.db.get_auto_save(self.current_project_id, scene_id)
            if not auto_save or 'data' not in auto_save:
                return False
            
            # Load auto-save data into scene controller
            self.scene_controller.clear_scene()
            
            # Create new scene in scene controller
            scene = self.db.get_scene(scene_id)
            if not scene:
                return False
                
            self.scene_controller.new_scene(scene['name'])
            
            # Load items into scene
            auto_save_data = auto_save['data']
            
            if 'lights' in auto_save_data:
                for light_data in auto_save_data.get('lights', []):
                    light = LightingEquipment.from_dict(light_data)
                    self.scene_controller.add_item('light', light)
            
            if 'cameras' in auto_save_data:
                for camera_data in auto_save_data.get('cameras', []):
                    camera = Camera.from_dict(camera_data)
                    self.scene_controller.add_item('camera', camera)
            
            if 'set_elements' in auto_save_data:
                for element_data in auto_save_data.get('set_elements', []):
                    element = SetElement.from_dict(element_data)
                    self.scene_controller.add_item('set_element', element)
            
            # Set scene metadata
            if 'description' in auto_save_data and hasattr(self.scene_controller.current_scene, 'description'):
                self.scene_controller.current_scene.description = auto_save_data.get('description', '')
            
            # Set current scene
            self.current_scene_id = scene_id
            self.has_unsaved_changes = True
            
            # Emit signals
            self.scene_loaded.emit(scene_id)
            self.project_changed.emit(True)
            
            return True
        except Exception as e:
            print(f"Error recovering from auto-save: {e}")
            return False
    
    def get_project_scenes(self):
        """
        Get all scenes for the current project.
        
        Returns:
            List of scene dictionaries
        """
        if not self.current_project_id:
            return []
            
        return self.db.get_project_scenes(self.current_project_id)
    
    def get_scene_info(self, scene_id):
        """
        Get information about a scene.
        
        Args:
            scene_id: ID of the scene
        
        Returns:
            Scene data or None if not found
        """
        return self.db.get_scene(scene_id)
    
    def get_project_info(self):
        """
        Get information about the current project.
        
        Returns:
            Project data or None if no project loaded
        """
        if not self.current_project_id:
            return None
            
        return self.db.get_project(self.current_project_id)
    
    def get_recent_projects(self, limit=5):
        """
        Get recent projects.
        
        Args:
            limit: Maximum number of projects to return
        
        Returns:
            List of project dictionaries
        """
        return self.db.get_recent_projects(limit)
    
    def create_version_snapshot(self, description=None):
        """
        Create a version snapshot of the current scene.
        
        Args:
            description: Optional description for the version
        
        Returns:
            Version ID if successful, None otherwise
        """
        try:
            if not self.current_project_id or not self.current_scene_id:
                return None
            
            # Get current scene data
            scene_data = self._get_current_scene_data()
            if not scene_data:
                return None
            
            # Create version in database
            version_id = self.db.create_version(
                self.current_project_id, 
                self.current_scene_id, 
                scene_data, 
                description
            )
            
            return version_id
        except Exception as e:
            print(f"Error creating version snapshot: {e}")
            return None
    
    def get_version_history(self):
        """
        Get version history for the current scene.
        
        Returns:
            List of version dictionaries
        """
        if not self.current_project_id or not self.current_scene_id:
            return []
            
        return self.db.get_versions(self.current_project_id, self.current_scene_id)
    
    def restore_version(self, version_id):
        """
        Restore a scene to a specific version.
        
        Args:
            version_id: ID of the version to restore
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get version data
            version_data = self.db.get_version_data(version_id)
            if not version_data:
                return False
            
            # Save current state as a new version
            self.create_version_snapshot("Auto version before restore")
            
            # Clear scene controller
            self.scene_controller.clear_scene()
            
            # Create new scene in scene controller
            self.scene_controller.new_scene(version_data.get('name', 'Restored Scene'))
            
            # Load items into scene
            if 'lights' in version_data:
                for light_data in version_data.get('lights', []):
                    light = LightingEquipment.from_dict(light_data)
                    self.scene_controller.add_item('light', light)
            
            if 'cameras' in version_data:
                for camera_data in version_data.get('cameras', []):
                    camera = Camera.from_dict(camera_data)
                    self.scene_controller.add_item('camera', camera)
            
            if 'set_elements' in version_data:
                for element_data in version_data.get('set_elements', []):
                    element = SetElement.from_dict(element_data)
                    self.scene_controller.add_item('set_element', element)
            
            # Set scene metadata
            if 'description' in version_data and hasattr(self.scene_controller.current_scene, 'description'):
                self.scene_controller.current_scene.description = version_data.get('description', '')
            
            # Set unsaved changes flag
            self.has_unsaved_changes = True
            self.project_changed.emit(True)
            
            # Emit signals
            self.scene_loaded.emit(self.current_scene_id)
            
            return True
        except Exception as e:
            print(f"Error restoring version: {e}")
            return False
            
    def set_auto_save_settings(self, enabled, interval=None):
        """
        Set auto-save settings.
        
        Args:
            enabled: Whether auto-save is enabled
            interval: Optional interval in seconds
        """
        self.auto_save_enabled = enabled
        
        if interval is not None:
            self.auto_save_interval = interval
            self.db.set_setting('auto_save_interval', str(interval))
        
        # Update timer
        if self.auto_save_timer:
            if self.auto_save_enabled:
                self.auto_save_timer.start(self.auto_save_interval * 1000)
            else:
                self.auto_save_timer.stop()
