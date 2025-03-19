"""
Equipment factory for the LightCraft application.
Provides factory methods for creating equipment model objects from equipment data.
"""

from lightcraft.models.equipment import LightingEquipment, Camera, SetElement
from lightcraft.models.equipment_data import EQUIPMENT_LIBRARY, get_equipment_by_id


class EquipmentFactory:
    """
    Factory for creating equipment model objects.
    """
    
    @staticmethod
    def create_equipment_from_data(equipment_id, position=None):
        """
        Create an equipment model object from equipment data.
        
        Args:
            equipment_id: ID of the equipment in the library
            position: Optional position (x, y) for the equipment
        
        Returns:
            Equipment model object or None if not found
        """
        # Get equipment data from library
        equipment_data = get_equipment_by_id(equipment_id)
        if not equipment_data:
            return None
        
        # Determine equipment type
        category = equipment_data["category"]
        
        # Set position if provided
        x = position[0] if position and len(position) >= 2 else 0
        y = position[1] if position and len(position) >= 2 else 0
        
        # Create object based on category
        if category == "lights":
            # Create lighting equipment
            light = LightingEquipment(name=equipment_data["name"])
            
            # Set position
            light.x = x
            light.y = y
            
            # Set properties from equipment data
            if "properties" in equipment_data:
                props = equipment_data["properties"]
                
                if "power" in props:
                    light.power = props["power"]
                
                if "beam_angle" in props:
                    light.beam_angle = props["beam_angle"]
                
                if "color_temperature" in props:
                    light.color_temperature = props["color_temperature"]
                
                if "color" in props:
                    light.color = props["color"]
                
                if "equipment_type" in props:
                    light.equipment_type = props["equipment_type"]
                
                if "fixture_type" in props:
                    light.fixture_type = props["fixture_type"]
                
                if "intensity" in props:
                    light.intensity = 100  # Start at full intensity
                else:
                    light.intensity = 100
            
            return light
            
        elif category == "camera":
            # Create camera
            camera = Camera(name=equipment_data["name"])
            
            # Set position
            camera.x = x
            camera.y = y
            
            # Set properties from equipment data
            if "properties" in equipment_data:
                props = equipment_data["properties"]
                
                if "focal_length" in props:
                    camera.lens_mm = props["focal_length"]
                elif "lens_mm" in props:
                    camera.lens_mm = props["lens_mm"]
                else:
                    camera.lens_mm = 35  # Default focal length
                
                if "height" in props:
                    camera.height = props["height"]
                else:
                    camera.height = 170  # Default camera height
                
                if "equipment_type" in props:
                    camera.camera_type = props["equipment_type"]
                else:
                    camera.camera_type = "Main"
            
            return camera
            
        elif category == "set" or category == "grip":
            # Create set element
            element_type = ""
            
            # Determine element type based on subcategory and equipment type
            if "subcategory" in equipment_data:
                subcategory = equipment_data["subcategory"]
                if subcategory == "walls":
                    element_type = "Wall"
                elif subcategory == "doors":
                    element_type = "Door"
                elif subcategory == "furniture":
                    element_type = "Furniture"
                elif subcategory == "control":  # Grip equipment
                    if "properties" in equipment_data and "equipment_type" in equipment_data["properties"]:
                        element_type = equipment_data["properties"]["equipment_type"]
                    else:
                        element_type = "Flag"  # Default for light control
            
            # Create the set element
            element = SetElement(name=equipment_data["name"], element_type=element_type)
            
            # Set position
            element.x = x
            element.y = y
            
            # Set properties from equipment data
            if "properties" in equipment_data:
                props = equipment_data["properties"]
                
                if "width" in props:
                    element.width = props["width"]
                
                if "height" in props:
                    element.height = props["height"]
                
                if "thickness" in props:
                    element.thickness = props["thickness"]
                elif element_type in ["Wall", "Door", "Window"]:
                    element.thickness = 10  # Default thickness for walls
                
                if "color" in props:
                    element.color = props["color"]
                
                if "material" in props:
                    element.material = props["material"]
            
            return element
        
        # Unknown category
        return None
