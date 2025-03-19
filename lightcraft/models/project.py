"""
Project data model for the LightCraft application.
Represents the overall project structure and metadata.
"""

import os
import json
import uuid
from datetime import datetime


class Project:
    """
    Project data model representing a lighting design project.
    Contains scenes and project-level metadata.
    """
    
    def __init__(self, name="New Project"):
        """
        Initialize a new project.
        
        Args:
            name: The project name
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.now()
        self.modified_at = self.created_at
        self.description = ""
        self.author = ""
        self.scenes = []  # List of Scene objects
        self.file_path = None  # Path to saved project file if any
        self.version = "0.1.0"  # Project file version
        
        # Project settings
        self.settings = {
            "grid_enabled": True,
            "grid_size": 20,
            "grid_color": "#CCCCCC",
            "default_unit": "meter",  # meter, foot, etc.
            "scale": 1.0,  # 1 unit = X meters/feet
        }
    
    def add_scene(self, scene):
        """
        Add a scene to the project.
        
        Args:
            scene: Scene object to add
        """
        self.scenes.append(scene)
        self.modified_at = datetime.now()
    
    def remove_scene(self, scene_id):
        """
        Remove a scene from the project.
        
        Args:
            scene_id: ID of the scene to remove
        
        Returns:
            bool: True if the scene was removed, False if not found
        """
        for i, scene in enumerate(self.scenes):
            if scene.id == scene_id:
                del self.scenes[i]
                self.modified_at = datetime.now()
                return True
        return False
    
    def get_scene(self, scene_id):
        """
        Get a scene by ID.
        
        Args:
            scene_id: ID of the scene to get
        
        Returns:
            Scene object or None if not found
        """
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None
    
    def to_dict(self):
        """
        Convert project to dictionary for serialization.
        
        Returns:
            dict: Project data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "settings": self.settings,
            "scenes": [scene.to_dict() for scene in self.scenes]
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a project from dictionary data.
        
        Args:
            data: Dictionary of project data
        
        Returns:
            Project: New project instance
        """
        from .scene import Scene  # Import here to avoid circular imports
        
        project = cls(name=data["name"])
        project.id = data["id"]
        project.created_at = datetime.fromisoformat(data["created_at"])
        project.modified_at = datetime.fromisoformat(data["modified_at"])
        project.description = data["description"]
        project.author = data["author"]
        project.version = data["version"]
        project.settings = data["settings"]
        
        # Create scenes
        for scene_data in data["scenes"]:
            scene = Scene.from_dict(scene_data)
            project.scenes.append(scene)
        
        return project
    
    def save(self, file_path=None):
        """
        Save the project to a file.
        
        Args:
            file_path: Path to save the project file, or None to use existing path
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        if file_path:
            self.file_path = file_path
        
        if not self.file_path:
            return False
        
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            self.modified_at = datetime.now()
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    @classmethod
    def load(cls, file_path):
        """
        Load a project from a file.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            Project: Loaded project or None if failed
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            project = cls.from_dict(data)
            project.file_path = file_path
            return project
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
