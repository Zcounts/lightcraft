"""
Canvas Area for the LightCraft application.
Provides the main drawing area where lighting diagrams are created and manipulated.
"""

from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout,
    QGraphicsItem, QGraphicsItemGroup, QGraphicsRectItem,
    QGraphicsTextItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent,
    QUndoStack, QUndoCommand
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize, QSizeF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QTransform,
    QPolygonF, QPainterPath
)

import math
from enum import Enum
from lightcraft.config import GRID_SIZE, GRID_COLOR, GRID_ENABLED
from lightcraft.ui.canvas_items import (
    CanvasItem, LightItem, CameraItem, WallItem, ModifierItem
)


# Unit system enumeration
class UnitSystem(Enum):
    METRIC = 1
    IMPERIAL = 2


# Command for the undo stack
class ItemMoveCommand(QUndoCommand):
    """
    Command for moving items in the scene.
    Used for undo/redo functionality.
    """
    
    def __init__(self, items, old_positions, new_positions):
        """
        Initialize the move command.
        
        Args:
            items: List of items that were moved
            old_positions: List of original positions
            new_positions: List of new positions
        """
        super().__init__("Move Items")
        self.items = items
        self.old_positions = old_positions
        self.new_positions = new_positions
    
    def undo(self):
        """Undo the move operation."""
        for i, item in enumerate(self.items):
            if item.scene():
                item.setPos(self.old_positions[i])
                item.update_model_from_item()
    
    def redo(self):
        """Redo the move operation."""
        for i, item in enumerate(self.items):
            if item.scene():
                item.setPos(self.new_positions[i])
                item.update_model_from_item()


class ItemRotateCommand(QUndoCommand):
    """
    Command for rotating items in the scene.
    Used for undo/redo functionality.
    """
    
    def __init__(self, items, old_rotations, new_rotations):
        """
        Initialize the rotate command.
        
        Args:
            items: List of items that were rotated
            old_rotations: List of original rotations
            new_rotations: List of new rotations
        """
        super().__init__("Rotate Items")
        self.items = items
        self.old_rotations = old_rotations
        self.new_rotations = new_rotations
    
    def undo(self):
        """Undo the rotation operation."""
        for i, item in enumerate(self.items):
            if item.scene():
                item.setRotation(self.old_rotations[i])
                item.update_model_from_item()
    
    def redo(self):
        """Redo the rotation operation."""
        for i, item in enumerate(self.items):
            if item.scene():
                item.setRotation(self.new_rotations[i])
                item.update_model_from_item()


class ItemResizeCommand(QUndoCommand):
    """
    Command for resizing items in the scene.
    Used for undo/redo functionality.
    """
    
    def __init__(self, item, old_size, new_size, property_names):
        """
        Initialize the resize command.
        
        Args:
            item: Item that was resized
            old_size: Original size (can be custom format depending on the item)
            new_size: New size
            property_names: Names of properties to update in model
        """
        super().__init__("Resize Item")
        self.item = item
        self.old_size = old_size
        self.new_size = new_size
        self.property_names = property_names
    
    def undo(self):
        """Undo the resize operation."""
        if not self.item.scene():
            return
            
        # Apply old size (implementation depends on item type)
        self._apply_size(self.old_size)
    
    def redo(self):
        """Redo the resize operation."""
        if not self.item.scene():
            return
            
        # Apply new size
        self._apply_size(self.new_size)
    
    def _apply_size(self, size):
        """
        Apply the given size to the item.
        
        Args:
            size: Size to apply
        """
        # Handle different item types
        if isinstance(self.item, WallItem):
            # For walls, size is [length, width]
            self.item.wall_length = size[0]
            self.item.wall_width = size[1]
            self.item.wall.setRect(-size[0]/2, -size[1]/2, size[0], size[1])
            
            # Update model
            if self.item.model_item:
                if hasattr(self.item.model_item, self.property_names[0]):
                    setattr(self.item.model_item, self.property_names[0], size[0])
                if hasattr(self.item.model_item, self.property_names[1]):
                    setattr(self.item.model_item, self.property_names[1], size[1])
            
            # Update handles
            self.item.position_handles()
            self.item.update_measurement()
            
        elif isinstance(self.item, ModifierItem):
            # For modifiers, size is [width, height]
            self.item.width = size[0]
            self.item.height = size[1]
            self.item.body.setRect(-size[0]/2, -size[1]/2, size[0], size[1])
            
            # Update model
            if self.item.model_item:
                if hasattr(self.item.model_item, self.property_names[0]):
                    setattr(self.item.model_item, self.property_names[0], size[0])
                if hasattr(self.item.model_item, self.property_names[1]):
                    setattr(self.item.model_item, self.property_names[1], size[1])
