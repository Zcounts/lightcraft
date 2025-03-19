"""
Equipment data models for the LightCraft application.
Defines models for lights, cameras, and set elements.
"""

import uuid
from datetime import datetime


class Item:
    """Base class for all items in a lighting diagram."""
    
    def __init__(self, name="New Item"):
        """
        Initialize a new item.
        
        Args:
            name: The item name
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.visible = True
        self.created_at = datetime.now()
        self.modified_at = self.created_at
    
    def to_dict(self):
        """
        Convert item to dictionary for serialization.
        
        Returns:
            dict: Item data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "visible": self.visible,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an item from dictionary data.
        
        Args:
            data: Dictionary of item data
        
        Returns:
            Item: New item instance
        """
        item = cls(name=data.get("name", "Unnamed Item"))
        item.id = data.get("id", str(uuid.uuid4()))
        item.x = data.get("x", 0)
        item.y = data.get("y", 0)
        item.rotation = data.get("rotation", 0)
        item.visible = data.get("visible", True)
        
        # Convert ISO format strings to datetime objects
        if "created_at" in data:
            item.created_at = datetime.fromisoformat(data["created_at"])
        if "modified_at" in data:
            item.modified_at = datetime.fromisoformat(data["modified_at"])
        
        return item


class LightingEquipment(Item):
    """Model for lighting equipment."""
    
    def __init__(self, name="New Light"):
        """
        Initialize a new lighting equipment item.
        
        Args:
            name: The light name
        """
        super().__init__(name)
        self.equipment_type = "Generic"  # Fresnel, HMI, LED Panel, etc.
        self.power = 650  # Wattage
        self.beam_angle = 35  # Degrees
        self.color_temperature = 5600  # Kelvin
        self.intensity = 100  # Percentage
        self.color = "#FFFFFF"  # Hex color
        self.fixture_type = "spotlight"  # spotlight, floodlight, practical, etc.
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "equipment_type": self.equipment_type,
            "power": self.power,
            "beam_angle": self.beam_angle,
            "color_temperature": self.color_temperature,
            "intensity": self.intensity,
            "color": self.color,
            "fixture_type": self.fixture_type
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary data."""
        light = super().from_dict(data)
        light.equipment_type = data.get("equipment_type", "Generic")
        light.power = data.get("power", 650)
        light.beam_angle = data.get("beam_angle", 35)
        light.color_temperature = data.get("color_temperature", 5600)
        light.intensity = data.get("intensity", 100)
        light.color = data.get("color", "#FFFFFF")
        light.fixture_type = data.get("fixture_type", "spotlight")
        return light


class Camera(Item):
    """Model for camera positions."""
    
    def __init__(self, name="New Camera"):
        """
        Initialize a new camera item.
        
        Args:
            name: The camera name
        """
        super().__init__(name)
        self.camera_type = "Main"  # Main, Secondary, POV, etc.
        self.lens_mm = 35  # Focal length
        self.height = 170  # Camera height in cm
        self.shot_type = "Medium"  # Wide, Medium, Close-up, etc.
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "camera_type": self.camera_type,
            "lens_mm": self.lens_mm,
            "height": self.height,
            "shot_type": self.shot_type
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary data."""
        camera = super().from_dict(data)
        camera.camera_type = data.get("camera_type", "Main")
        camera.lens_mm = data.get("lens_mm", 35)
        camera.height = data.get("height", 170)
        camera.shot_type = data.get("shot_type", "Medium")
        return camera


class SetElement(Item):
    """Model for set elements like walls, doors, etc."""
    
    def __init__(self, name="New Element", element_type="Wall"):
        """
        Initialize a new set element.
        
        Args:
            name: The element name
            element_type: Type of element (Wall, Door, Window, etc.)
        """
        super().__init__(name)
        self.element_type = element_type
        self.width = 200  # Width in cm
        self.height = 10  # Height/thickness in cm
        self.thickness = 10  # For walls, doors, windows
        self.color = "#AAAAAA"  # Hex color
        self.material = "Wood"  # Material type
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "element_type": self.element_type,
            "width": self.width,
            "height": self.height,
            "thickness": self.thickness,
            "color": self.color,
            "material": self.material
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary data."""
        element = super().from_dict(data)
        element.element_type = data.get("element_type", "Wall")
        element.width = data.get("width", 200)
        element.height = data.get("height", 10)
        element.thickness = data.get("thickness", 10)
        element.color = data.get("color", "#AAAAAA")
        element.material = data.get("material", "Wood")
        return element
