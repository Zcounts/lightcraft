"""
Scene data model for the LightCraft application.
Represents a single scene in a lighting design project.
"""

import uuid
from datetime import datetime


class Scene:
    """
    Scene data model representing a single scene in a lighting project.
    Contains lighting equipment, set elements, and scene metadata.
    """
    
    def __init__(self, name="New Scene"):
        """
        Initialize a new scene.
        
        Args:
            name: The scene name
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.now()
        self.modified_at = self.created_at
        self.description = ""
        
        # Scene items
        self.lights = []  # List of lighting equipment
        self.set_elements = []  # List of set elements (walls, doors, etc.)
        self.cameras = []  # List of camera positions
        
        # Scene dimensions and settings
        self.width = 1000
        self.height = 800
        self.background_color = "#FFFFFF"
        self.scale = 1.0  # 1 unit = X meters/feet
        
        # Scene metadata (for film production)
        self.production_name = ""
        self.scene_number = ""
        self.location = ""
        self.date = ""
        self.director = ""
        self.dp = ""  # Director of Photography
        self.gaffer = ""
    
    def add_item(self, item, category):
        """
        Add an item to the scene.
        
        Args:
            item: Item to add
            category: Category to add the item to ("lights", "set_elements", or "cameras")
        
        Returns:
            bool: True if added successfully, False otherwise
        """
        if category == "lights":
            self.lights.append(item)
        elif category == "set_elements":
            self.set_elements.append(item)
        elif category == "cameras":
            self.cameras.append(item)
        else:
            return False
        
        self.modified_at = datetime.now()
        return True
    
    def remove_item(self, item_id, category=None):
        """
        Remove an item from the scene.
        
        Args:
            item_id: ID of the item to remove
            category: Category to remove from, or None to search all categories
        
        Returns:
            bool: True if removed successfully, False if not found
        """
        categories = [category] if category else ["lights", "set_elements", "cameras"]
        
        for cat in categories:
            items = getattr(self, cat)
            for i, item in enumerate(items):
                if item.id == item_id:
                    del items[i]
                    self.modified_at = datetime.now()
                    return True
        
        return False
    
    def get_item(self, item_id, category=None):
        """
        Get an item by ID.
        
        Args:
            item_id: ID of the item to get
            category: Category to search in, or None to search all categories
        
        Returns:
            Item object or None if not found
        """
        categories = [category] if category else ["lights", "set_elements", "cameras"]
        
        for cat in categories:
            items = getattr(self, cat)
            for item in items:
                if item.id == item_id:
                    return item
        
        return None
    
    def get_all_items(self):
        """
        Get all items in the scene.
        
        Returns:
            list: Combined list of all items
        """
        return self.lights + self.set_elements + self.cameras
    
    def to_dict(self):
        """
        Convert scene to dictionary for serialization.
        
        Returns:
            dict: Scene data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "description": self.description,
            "width": self.width,
            "height": self.height,
            "background_color": self.background_color,
            "scale": self.scale,
            "production_name": self.production_name,
            "scene_number": self.scene_number,
            "location": self.location,
            "date": self.date,
            "director": self.director,
            "dp": self.dp,
            "gaffer": self.gaffer,
            "lights": [light.to_dict() for light in self.lights],
            "set_elements": [element.to_dict() for element in self.set_elements],
            "cameras": [camera.to_dict() for camera in self.cameras]
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a scene from dictionary data.
        
        Args:
            data: Dictionary of scene data
        
        Returns:
            Scene: New scene instance
        """
        from .equipment import LightingEquipment, SetElement, Camera
        
        scene = cls(name=data["name"])
        scene.id = data["id"]
        scene.created_at = datetime.fromisoformat(data["created_at"])
        scene.modified_at = datetime.fromisoformat(data["modified_at"])
        scene.description = data.get("description", "")
        scene.width = data.get("width", 1000)
        scene.height = data.get("height", 800)
        scene.background_color = data.get("background_color", "#FFFFFF")
        scene.scale = data.get("scale", 1.0)
        
        scene.production_name = data.get("production_name", "")
        scene.scene_number = data.get("scene_number", "")
        scene.location = data.get("location", "")
        scene.date = data.get("date", "")
        scene.director = data.get("director", "")
        scene.dp = data.get("dp", "")
        scene.gaffer = data.get("gaffer", "")
        
        # Create lights
        for light_data in data.get("lights", []):
            light = LightingEquipment.from_dict(light_data)
            scene.lights.append(light)
        
        # Create set elements
        for element_data in data.get("set_elements", []):
            element = SetElement.from_dict(element_data)
            scene.set_elements.append(element)
        
        # Create cameras
        for camera_data in data.get("cameras", []):
            camera = Camera.from_dict(camera_data)
            scene.cameras.append(camera)
        
        return scene
