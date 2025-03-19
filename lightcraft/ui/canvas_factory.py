"""
Canvas item factory for the LightCraft application.
Provides methods for creating canvas items from model items.
"""

from lightcraft.models.equipment import LightingEquipment, SetElement, Camera, Item
from lightcraft.ui.canvas_items import (
    LightItem, CameraItem, WallItem, ModifierItem
)


class CanvasItemFactory:
    """
    Factory for creating canvas items from model items.
    Maps model item types to canvas item classes.
    """
    
    @staticmethod
    def create_item(model_item):
        """
        Create a canvas item based on the model item type.
        
        Args:
            model_item: The model item to create a canvas item for
        
        Returns:
            CanvasItem: The created canvas item or None if type not recognized
        """
        if isinstance(model_item, LightingEquipment):
            return LightItem(model_item)
        elif isinstance(model_item, Camera):
            return CameraItem(model_item)
        elif isinstance(model_item, SetElement):
            # Choose appropriate visual representation based on element type
            if hasattr(model_item, 'element_type'):
                if model_item.element_type.lower() in ['wall', 'door', 'window']:
                    return WallItem(model_item)
                elif model_item.element_type.lower() in ['flag', 'floppy', 'neg', 'scrim', 'cutter', 'diffusion']:
                    return ModifierItem(model_item)
            
            # Default to wall for other set elements
            return WallItem(model_item)
        
        return None
    
    @staticmethod
    def create_from_type(item_type, model_item=None):
        """
        Create a canvas item based on a type string and optional model item.
        
        Args:
            item_type: String identifier for item type
            model_item: Optional model item to associate with the canvas item
        
        Returns:
            CanvasItem: The created canvas item or None if type not recognized
        """
        item_map = {
            'light': LightItem,
            'spot_light': LightItem,
            'flood_light': LightItem,
            'led_panel': LightItem,
            'camera': CameraItem,
            'wall': WallItem,
            'door': WallItem,
            'window': WallItem,
            'flag': ModifierItem,
            'floppy': ModifierItem,
            'scrim': ModifierItem,
            'diffusion': ModifierItem
        }
        
        if item_type in item_map:
            # Create the canvas item
            return item_map[item_type](model_item)
        
        return None
    
    @staticmethod
    def create_preview_item(item_type):
        """
        Create a preview item for drag operations.
        
        Args:
            item_type: Type of item to preview
        
        Returns:
            CanvasItem: A preview item or None if type not recognized
        """
        # This could be expanded for different preview types
        return CanvasItemFactory.create_from_type(item_type)
