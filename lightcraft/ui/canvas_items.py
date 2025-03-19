"""
Canvas item classes for the LightCraft application.
Provides graphical representations of scene items on the canvas.
"""

from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, 
    QGraphicsPathItem, QGraphicsPolygonItem, QGraphicsItemGroup,
    QGraphicsSimpleTextItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainterPath, QPolygonF, 
    QTransform, QPainter, QFont
)
import math


class CanvasItem(QGraphicsItem):
    """
    Base class for all canvas items.
    Provides common functionality for all item types.
    """
    
    def __init__(self, model_item=None, parent=None):
        """
        Initialize the canvas item.
        
        Args:
            model_item: The data model item this canvas item represents
            parent: Parent item
        """
        super().__init__(parent)
        
        # Store reference to model item
        self.model_item = model_item
        
        # Set flags for interactivity
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Display settings
        self.label_visible = True
        self.show_measurements = False
        self.handle_size = 8
        self.selected_pen_width = 2
        self.hover_pen_width = 1.5
        self.default_pen_width = 1.0
        
        # Selection handles (for rotation, scaling, etc.)
        self.handles = {}
        self.handle_cursors = {}
        
        # Initialize handles (will be positioned in subclasses)
        self.create_handles()
        
        # For drag operations
        self.drag_start_pos = QPointF()
        self.drag_original_position = QPointF()
        self.drag_original_rotation = 0
        self.drag_original_rect = QRectF()
        
        # For undo/redo
        self.last_pos = QPointF()
        self.last_rotation = 0
        self.last_size = QSizeF()
        
        # Initialize from model item if provided
        if model_item:
            self.update_from_model()
    
    def create_handles(self):
        """Create selection handles for the item."""
        # Will be implemented in subclasses
        pass
    
    def position_handles(self):
        """Position the selection handles based on the item's bounds."""
        # Will be implemented in subclasses
        pass
    
    def update_handles_visibility(self):
        """Update visibility of handles based on selection state."""
        selected = self.isSelected()
        for handle in self.handles.values():
            handle.setVisible(selected)
    
    def update_from_model(self):
        """Update visual representation from model data."""
        if not self.model_item:
            return
        
        # Set position from model
        self.setPos(self.model_item.x, self.model_item.y)
        
        # Set rotation from model
        self.setRotation(self.model_item.rotation)
        
        # Store initial values for undo/redo
        self.last_pos = self.pos()
        self.last_rotation = self.rotation()
    
    def update_model_from_item(self):
        """Update model data from visual representation."""
        if not self.model_item:
            return
        
        # Update position in model
        self.model_item.x = self.pos().x()
        self.model_item.y = self.pos().y()
        
        # Update rotation in model
        self.model_item.rotation = self.rotation()
    
    def itemChange(self, change, value):
        """
        Handle item changes, such as selection or position changes.
        
        Args:
            change: The parameter that changed
            value: The new value
        
        Returns:
            The adjusted value
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            # Selection state changed
            self.update_handles_visibility()
        
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # Store original position for potential undo operation
            if self.drag_start_pos.isNull():
                self.drag_start_pos = self.pos()
        
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Position has changed, update handles
            self.position_handles()
            
            # Update model
            self.update_model_from_item()
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        # Store starting position for drag operations
        self.drag_start_pos = event.pos()
        self.drag_original_position = self.pos()
        self.drag_original_rotation = self.rotation()
        
        # Check if a handle was clicked
        clicked_handle = self.handle_at(event.pos())
        if clicked_handle:
            # We're interacting with a handle
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        else:
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        clicked_handle = self.handle_at(self.drag_start_pos)
        if clicked_handle:
            # Handle drag
            if clicked_handle == "rotate":
                self.handle_rotation(event)
            else:
                self.handle_resize(event, clicked_handle)
        else:
            # Normal drag
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        # Reset drag start position
        self.drag_start_pos = QPointF()
        
        # Re-enable movement
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        # Update model
        self.update_model_from_item()
        
        super().mouseReleaseEvent(event)
    
    def handle_at(self, pos):
        """
        Find a handle at the given position.
        
        Args:
            pos: Position to check in item coordinates
        
        Returns:
            Handle name or None if no handle at position
        """
        for name, handle in self.handles.items():
            if handle.isVisible() and handle.contains(handle.mapFromItem(self, pos)):
                return name
        return None
    
    def handle_rotation(self, event):
        """
        Handle rotation via a handle drag.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        # Calculate angle between center of item and current mouse position
        center = self.boundingRect().center()
        original_angle = math.atan2(self.drag_start_pos.y() - center.y(),
                                    self.drag_start_pos.x() - center.x())
        current_angle = math.atan2(event.pos().y() - center.y(),
                                  event.pos().x() - center.x())
        
        # Calculate rotation angle in degrees
        angle_delta = (current_angle - original_angle) * 180 / math.pi
        
        # Apply rotation
        self.setRotation(self.drag_original_rotation + angle_delta)
        
        # Update handles
        self.position_handles()
    
    def handle_resize(self, event, handle_name):
        """
        Handle resizing via a handle drag.
        
        Args:
            event: QGraphicsSceneMouseEvent
            handle_name: Name of the handle being dragged
        """
        # Will be implemented in subclasses
        pass


class LightItem(CanvasItem):
    """
    Canvas item representing a light.
    """
    
    def __init__(self, model_item=None, parent=None):
        """
        Initialize a light item.
        
        Args:
            model_item: The data model item this canvas item represents
            parent: Parent item
        """
        super().__init__(model_item, parent)
        
        # Light-specific properties
        self.light_color = QColor("#FFCC00")
        self.beam_color = QColor(255, 204, 0, 40)  # Semi-transparent
        self.beam_angle = 45  # degrees
        
        # Create visual elements
        self.body = QGraphicsEllipseItem(-15, -15, 30, 30, self)
        self.body.setPen(QPen(Qt.GlobalColor.black, self.default_pen_width))
        self.body.setBrush(QBrush(self.light_color))
        
        # Light beam representation
        self.beam = QGraphicsPolygonItem(self)
        self.beam.setPen(QPen(Qt.GlobalColor.transparent))
        self.beam.setBrush(QBrush(self.beam_color))
        
        # Label
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFont(QFont("Arial", 8))
        self.label.setBrush(QBrush(Qt.GlobalColor.black))
        
        # Update beam shape
        self.update_beam()
        
        # Update from model
        self.update_from_model()
    
    def update_beam(self):
        """Update the light beam representation based on beam angle."""
        if not self.model_item:
            return
            
        # Create a polygon for the beam
        beam_length = 100  # Length of beam
        half_angle = self.beam_angle / 2
        
        # Calculate beam width at the end
        end_width = beam_length * math.tan(math.radians(half_angle))
        
        # Create the beam polygon
        polygon = QPolygonF()
        polygon.append(QPointF(0, 0))  # Start at center of light
        polygon.append(QPointF(beam_length, -end_width))  # Top corner
        polygon.append(QPointF(beam_length, end_width))  # Bottom corner
        
        self.beam.setPolygon(polygon)
    
    def update_from_model(self):
        """Update visual representation from model data."""
        super().update_from_model()
        
        if not self.model_item:
            return
        
        # Update label
        self.label.setText(self.model_item.name)
        
        # Position label below light
        text_rect = self.label.boundingRect()
        self.label.setPos(-text_rect.width() / 2, 20)
        
        # Update beam angle
        if hasattr(self.model_item, 'beam_angle'):
            self.beam_angle = self.model_item.beam_angle
            self.update_beam()
        
        # Update light color
        if hasattr(self.model_item, 'color') and self.model_item.color:
            self.light_color = QColor(self.model_item.color)
            beam_color = QColor(self.light_color)
            beam_color.setAlpha(40)  # Make beam semi-transparent
            
            self.body.setBrush(QBrush(self.light_color))
            self.beam.setBrush(QBrush(beam_color))
    
    def create_handles(self):
        """Create selection handles for the light item."""
        # Rotation handle
        self.handles["rotate"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["rotate"].setPen(QPen(Qt.GlobalColor.blue, 1))
        self.handles["rotate"].setBrush(QBrush(QColor(0, 0, 255, 128)))
        self.handles["rotate"].setVisible(False)
        
        # Beam angle handle
        self.handles["beam"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["beam"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["beam"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["beam"].setVisible(False)
        
        # Set cursor shapes for handles
        self.handle_cursors = {
            "rotate": Qt.CursorShape.PointingHandCursor,
            "beam": Qt.CursorShape.SizeVerCursor
        }
    
    def position_handles(self):
        """Position the selection handles based on the light's properties."""
        # Position rotation handle above the light
        self.handles["rotate"].setPos(0, -40)
        
        # Position beam angle handle at the edge of the beam
        beam_radius = 50  # Distance from center
        angle = math.radians(self.beam_angle / 2)
        self.handles["beam"].setPos(beam_radius, beam_radius * math.tan(angle))
    
    def handle_resize(self, event, handle_name):
        """
        Handle resizing via a handle drag.
        
        Args:
            event: QGraphicsSceneMouseEvent
            handle_name: Name of the handle being dragged
        """
        if handle_name == "beam":
            # Calculate new beam angle from handle position
            pos = event.pos()
            
            # Calculate angle from horizontal to mouse position
            angle = math.degrees(math.atan2(pos.y(), pos.x()))
            
            # Beam angle is twice this angle (from center line to outer edge)
            new_beam_angle = abs(angle) * 2
            
            # Constrain to reasonable values (5° to 180°)
            new_beam_angle = max(5, min(180, new_beam_angle))
            
            # Update beam angle
            self.beam_angle = new_beam_angle
            self.update_beam()
            
            # Update model
            if self.model_item and hasattr(self.model_item, 'beam_angle'):
                self.model_item.beam_angle = new_beam_angle
    
    def boundingRect(self):
        """
        Get the bounding rectangle of the item.
        
        Returns:
            QRectF: The bounding rectangle
        """
        return self.body.boundingRect().united(self.beam.boundingRect()).united(self.label.boundingRect())
    
    def paint(self, painter, option, widget):
        """
        Paint method is empty as painting is handled by child items.
        
        Args:
            painter: QPainter
            option: QStyleOptionGraphicsItem
            widget: QWidget
        """
        # No painting needed here, child items do their own painting
        pass


class ModifierItem(CanvasItem):
    """
    Canvas item representing a lighting modifier (flag, floppy, etc).
    """
    
    def __init__(self, model_item=None, parent=None):
        """
        Initialize a modifier item.
        
        Args:
            model_item: The data model item this canvas item represents
            parent: Parent item
        """
        super().__init__(model_item, parent)
        
        # Modifier types with their shapes and colors
        self.modifier_types = {
            "flag": {"shape": "rect", "color": "#111111"},
            "floppy": {"shape": "rect", "color": "#222222"},
            "neg": {"shape": "rect", "color": "#333333"},
            "scrim": {"shape": "rect", "color": "#444444", "pattern": "dots"},
            "cutter": {"shape": "rect", "color": "#555555", "pattern": "stripes"},
            "diffusion": {"shape": "rect", "color": "#DDDDDD", "pattern": "grid"}
        }
        
        # Default modifier properties
        self.modifier_type = "flag"
        self.modifier_color = QColor("#111111")
        self.width = 60
        self.height = 30
        self.pattern = None
        
        # Create visual elements
        self.body = QGraphicsRectItem(-self.width/2, -self.height/2, 
                                     self.width, self.height, self)
        self.body.setPen(QPen(Qt.GlobalColor.black, self.default_pen_width))
        self.body.setBrush(QBrush(self.modifier_color))
        
        # Create pattern if needed
        self.pattern_item = None
        
        # Label
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFont(QFont("Arial", 8))
        self.label.setBrush(QBrush(Qt.GlobalColor.white))
        
        # Update from model
        self.update_from_model()
    
    def update_pattern(self):
        """Update the pattern representation based on the modifier type."""
        # Remove existing pattern if any
        if self.pattern_item and self.pattern_item.scene():
            self.scene().removeItem(self.pattern_item)
            self.pattern_item = None
        
        if not self.pattern:
            return
            
        # Create pattern based on type
        if self.pattern == "dots":
            # Create a dot pattern (simplified with some representative dots)
            self.pattern_item = QGraphicsItemGroup(self)
            spacing = 10
            for x in range(-int(self.width/2) + 5, int(self.width/2), spacing):
                for y in range(-int(self.height/2) + 5, int(self.height/2), spacing):
                    dot = QGraphicsEllipseItem(x, y, 2, 2, self.pattern_item)
                    dot.setBrush(QBrush(Qt.GlobalColor.white))
                    dot.setPen(Qt.PenStyle.NoPen)
        
        elif self.pattern == "stripes":
            # Create a striped pattern
            self.pattern_item = QGraphicsItemGroup(self)
            spacing = 8
            for y in range(-int(self.height/2) + 4, int(self.height/2), spacing):
                line = QGraphicsRectItem(-self.width/2, y, self.width, 1, self.pattern_item)
                line.setBrush(QBrush(Qt.GlobalColor.white))
                line.setPen(Qt.PenStyle.NoPen)
        
        elif self.pattern == "grid":
            # Create a grid pattern
            self.pattern_item = QGraphicsItemGroup(self)
            spacing = 10
            # Horizontal lines
            for y in range(-int(self.height/2) + 5, int(self.height/2), spacing):
                line = QGraphicsRectItem(-self.width/2, y, self.width, 1, self.pattern_item)
                line.setBrush(QBrush(Qt.GlobalColor.white))
                line.setPen(Qt.PenStyle.NoPen)
            
            # Vertical lines
            for x in range(-int(self.width/2) + 5, int(self.width/2), spacing):
                line = QGraphicsRectItem(x, -self.height/2, 1, self.height, self.pattern_item)
                line.setBrush(QBrush(Qt.GlobalColor.white))
                line.setPen(Qt.PenStyle.NoPen)
    
    def update_from_model(self):
        """Update visual representation from model data."""
        super().update_from_model()
        
        if not self.model_item:
            return
        
        # Update label
        self.label.setText(self.model_item.name)
        
        # Position label in center of modifier
        text_rect = self.label.boundingRect()
        self.label.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
        
        # Update modifier type and appearance
        if hasattr(self.model_item, 'element_type'):
            self.modifier_type = self.model_item.element_type.lower()
            
            # Apply type-specific properties if valid type
            if self.modifier_type in self.modifier_types:
                type_info = self.modifier_types[self.modifier_type]
                
                # Apply color
                if "color" in type_info:
                    self.modifier_color = QColor(type_info["color"])
                    self.body.setBrush(QBrush(self.modifier_color))
                
                # Apply pattern
                if "pattern" in type_info:
                    self.pattern = type_info["pattern"]
                else:
                    self.pattern = None
                
                self.update_pattern()
        
        # Update dimensions
        if hasattr(self.model_item, 'width'):
            self.width = self.model_item.width
        
        if hasattr(self.model_item, 'height'):
            self.height = self.model_item.height
        
        # Update rectangle
        self.body.setRect(-self.width/2, -self.height/2, self.width, self.height)
        
        # Update pattern after dimension change
        self.update_pattern()
    
    def create_handles(self):
        """Create selection handles for the modifier item."""
        # Rotation handle
        self.handles["rotate"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["rotate"].setPen(QPen(Qt.GlobalColor.blue, 1))
        self.handles["rotate"].setBrush(QBrush(QColor(0, 0, 255, 128)))
        self.handles["rotate"].setVisible(False)
        
        # Resize handles for corners
        self.handles["top_left"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["top_left"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["top_left"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["top_left"].setVisible(False)
        
        self.handles["top_right"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["top_right"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["top_right"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["top_right"].setVisible(False)
        
        self.handles["bottom_left"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["bottom_left"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["bottom_left"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["bottom_left"].setVisible(False)
        
        self.handles["bottom_right"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["bottom_right"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["bottom_right"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["bottom_right"].setVisible(False)
        
        # Set cursor shapes for handles
        self.handle_cursors = {
            "rotate": Qt.CursorShape.PointingHandCursor,
            "top_left": Qt.CursorShape.SizeFDiagCursor,
            "top_right": Qt.CursorShape.SizeBDiagCursor,
            "bottom_left": Qt.CursorShape.SizeBDiagCursor,
            "bottom_right": Qt.CursorShape.SizeFDiagCursor
        }
    
    def position_handles(self):
        """Position the selection handles based on the modifier's dimensions."""
        # Position rotation handle above the modifier
        self.handles["rotate"].setPos(0, -self.height/2 - 20)
        
        # Position resize handles at corners
        self.handles["top_left"].setPos(-self.width/2, -self.height/2)
        self.handles["top_right"].setPos(self.width/2, -self.height/2)
        self.handles["bottom_left"].setPos(-self.width/2, self.height/2)
        self.handles["bottom_right"].setPos(self.width/2, self.height/2)
    
    def handle_resize(self, event, handle_name):
        """
        Handle resizing via a handle drag.
        
        Args:
            event: QGraphicsSceneMouseEvent
            handle_name: Name of the handle being dragged
        """
        # Get mouse position in item coordinates
        pos = event.pos()
        
        # Initial rectangle before resize
        old_rect = QRectF(-self.width/2, -self.height/2, self.width, self.height)
        
        # New rectangle after resize
        new_rect = QRectF(old_rect)
        
        if handle_name == "top_left":
            new_rect.setTopLeft(pos)
        elif handle_name == "top_right":
            new_rect.setTopRight(pos)
        elif handle_name == "bottom_left":
            new_rect.setBottomLeft(pos)
        elif handle_name == "bottom_right":
            new_rect.setBottomRight(pos)
        
        # Ensure minimum size
        if new_rect.width() < 10 or new_rect.height() < 10:
            return
        
        # Calculate the center offset to maintain the position
        center_offset = new_rect.center() - old_rect.center()
        
        # Apply new size
        self.width = new_rect.width()
        self.height = new_rect.height()
        
        # Update rectangle
        self.body.setRect(-self.width/2, -self.height/2, self.width, self.height)
        
        # Update position to keep the center of the item at the same place
        self.setPos(self.mapToScene(center_offset))
        
        # Update model
        if self.model_item:
            if hasattr(self.model_item, 'width'):
                self.model_item.width = self.width
            if hasattr(self.model_item, 'height'):
                self.model_item.height = self.height
        
        # Update pattern after resize
        self.update_pattern()
        
        # Update handles position
        self.position_handles()
    
    def boundingRect(self):
        """
        Get the bounding rectangle of the item.
        
        Returns:
            QRectF: The bounding rectangle
        """
        return self.body.boundingRect().united(self.label.boundingRect())
    
    def paint(self, painter, option, widget):
        """
        Paint method is empty as painting is handled by child items.
        
        Args:
            painter: QPainter
            option: QStyleOptionGraphicsItem
            widget: QWidget
        """
        # No painting needed here, child items do their own painting
        pass


class CameraItem(CanvasItem):
    """
    Canvas item representing a camera.
    """
    
    def __init__(self, model_item=None, parent=None):
        """
        Initialize a camera item.
        
        Args:
            model_item: The data model item this canvas item represents
            parent: Parent item
        """
        super().__init__(model_item, parent)
        
        # Camera-specific properties
        self.camera_color = QColor("#333333")
        self.view_color = QColor(51, 51, 51, 40)  # Semi-transparent
        self.view_angle = 60  # Field of view in degrees
        
        # Create visual elements
        # Camera body (triangle pointing in direction of view)
        self.body = QGraphicsPolygonItem(self)
        self.update_body()
        
        # Camera view representation (viewing frustum)
        self.view = QGraphicsPolygonItem(self)
        self.view.setPen(QPen(Qt.GlobalColor.transparent))
        self.view.setBrush(QBrush(self.view_color))
        self.update_view()
        
        # Label
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFont(QFont("Arial", 8))
        self.label.setBrush(QBrush(Qt.GlobalColor.black))
        
        # Update from model
        self.update_from_model()
    
    def update_body(self):
        """Update the camera body representation."""
        # Create a triangle for the camera body
        polygon = QPolygonF()
        polygon.append(QPointF(0, -10))  # Top
        polygon.append(QPointF(-15, 10))  # Bottom left
        polygon.append(QPointF(15, 10))  # Bottom right
        
        self.body.setPolygon(polygon)
        self.body.setPen(QPen(Qt.GlobalColor.black, self.default_pen_width))
        self.body.setBrush(QBrush(self.camera_color))
    
    def update_view(self):
        """Update the camera view representation based on field of view."""
        if not self.model_item:
            return
            
        # Create a polygon for the view
        view_length = 120  # Length of view
        half_angle = self.view_angle / 2
        
        # Calculate view width at the end
        end_width = view_length * math.tan(math.radians(half_angle))
        
        # Create the view polygon (facing up)
        polygon = QPolygonF()
        polygon.append(QPointF(0, 0))  # Start at center of camera
        polygon.append(QPointF(-end_width, -view_length))  # Left corner
        polygon.append(QPointF(end_width, -view_length))  # Right corner
        
        self.view.setPolygon(polygon)
    
    def update_from_model(self):
        """Update visual representation from model data."""
        super().update_from_model()
        
        if not self.model_item:
            return
        
        # Update label
        self.label.setText(self.model_item.name)
        
        # Position label below camera
        text_rect = self.label.boundingRect()
        self.label.setPos(-text_rect.width() / 2, 15)
        
        # Update view angle based on lens focal length
        if hasattr(self.model_item, 'lens_mm') and self.model_item.lens_mm > 0:
            # Approximate field of view based on 35mm equivalent focal length
            # This is a simplified calculation
            self.view_angle = min(120, max(5, 60 / (self.model_item.lens_mm / 35)))
            self.update_view()
    
    def create_handles(self):
        """Create selection handles for the camera item."""
        # Rotation handle
        self.handles["rotate"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["rotate"].setPen(QPen(Qt.GlobalColor.blue, 1))
        self.handles["rotate"].setBrush(QBrush(QColor(0, 0, 255, 128)))
        self.handles["rotate"].setVisible(False)
        
        # Lens/FOV handle
        self.handles["lens"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["lens"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["lens"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["lens"].setVisible(False)
        
        # Set cursor shapes for handles
        self.handle_cursors = {
            "rotate": Qt.CursorShape.PointingHandCursor,
            "lens": Qt.CursorShape.SizeVerCursor
        }
    
    def position_handles(self):
        """Position the selection handles based on the camera's properties."""
        # Position rotation handle above the camera
        self.handles["rotate"].setPos(0, -40)
        
        # Position lens handle at the edge of the view
        view_radius = 60  # Distance from center
        angle = math.radians(self.view_angle / 2)
        self.handles["lens"].setPos(view_radius * math.sin(angle), -view_radius * math.cos(angle))
    
    def handle_resize(self, event, handle_name):
        """
        Handle resizing via a handle drag.
        
        Args:
            event: QGraphicsSceneMouseEvent
            handle_name: Name of the handle being dragged
        """
        if handle_name == "lens":
            # Calculate new field of view from handle position
            pos = event.pos()
            
            # Calculate angle from vertical to mouse position
            # (0 degrees is up in our coordinate system)
            angle = math.degrees(math.atan2(pos.x(), -pos.y()))
            
            # Field of view is twice this angle (from center line to outer edge)
            new_view_angle = abs(angle) * 2
            
            # Constrain to reasonable values (5° to 120°)
            new_view_angle = max(5, min(120, new_view_angle))
            
            # Update view angle
            self.view_angle = new_view_angle
            self.update_view()
            
            # Update model - convert FOV to approximate lens mm
            if self.model_item and hasattr(self.model_item, 'lens_mm'):
                # Simplified conversion from FOV to focal length (35mm equivalent)
                self.model_item.lens_mm = max(8, min(200, 60 / (new_view_angle / 60)))
    
    def boundingRect(self):
        """
        Get the bounding rectangle of the item.
        
        Returns:
            QRectF: The bounding rectangle
        """
        return self.body.boundingRect().united(self.view.boundingRect()).united(self.label.boundingRect())
    
    def paint(self, painter, option, widget):
        """
        Paint method is empty as painting is handled by child items.
        
        Args:
            painter: QPainter
            option: QStyleOptionGraphicsItem
            widget: QWidget
        """
        # No painting needed here, child items do their own painting
        pass


class WallItem(CanvasItem):
    """
    Canvas item representing a wall.
    """
    
    def __init__(self, model_item=None, parent=None):
        """
        Initialize a wall item.
        
        Args:
            model_item: The data model item this canvas item represents
            parent: Parent item
        """
        super().__init__(model_item, parent)
        
        # Wall-specific properties
        self.wall_color = QColor("#AAAAAA")
        self.wall_width = 10  # Thickness of wall
        self.wall_length = 100  # Length of wall
        
        # Create visual elements
        self.wall = QGraphicsRectItem(-self.wall_length/2, -self.wall_width/2, 
                                     self.wall_length, self.wall_width, self)
        self.wall.setPen(QPen(Qt.GlobalColor.black, self.default_pen_width))
        self.wall.setBrush(QBrush(self.wall_color))
        
        # Label
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFont(QFont("Arial", 8))
        self.label.setBrush(QBrush(Qt.GlobalColor.black))
        
        # Measurement text
        self.measurement = QGraphicsSimpleTextItem(self)
        self.measurement.setFont(QFont("Arial", 7))
        self.measurement.setBrush(QBrush(Qt.GlobalColor.darkGray))
        
        # Update from model
        self.update_from_model()
    
    def update_from_model(self):
        """Update visual representation from model data."""
        super().update_from_model()
        
        if not self.model_item:
            return
        
        # Update label
        self.label.setText(self.model_item.name)
        
        # Position label above the wall
        text_rect = self.label.boundingRect()
        self.label.setPos(-text_rect.width() / 2, -self.wall_width - text_rect.height() - 5)
        
        # Update wall dimensions
        if hasattr(self.model_item, 'width'):
            self.wall_length = self.model_item.width
        
        if hasattr(self.model_item, 'thickness'):
            self.wall_width = self.model_item.thickness
        
        # Update wall rectangle
        self.wall.setRect(-self.wall_length/2, -self.wall_width/2, 
                        self.wall_length, self.wall_width)
        
        # Update wall color
        if hasattr(self.model_item, 'color') and self.model_item.color:
            self.wall_color = QColor(self.model_item.color)
            self.wall.setBrush(QBrush(self.wall_color))
        
        # Update measurement
        self.update_measurement()
    
    def update_measurement(self):
        """Update the measurement text."""
        # Convert wall length to feet or meters based on settings
        # For now, we'll just show in feet as an example
        feet = self.wall_length / 30.0  # Assuming 30 px = 1 foot for example
        
        # Format measurement text
        measurement_text = f"{feet:.1f}'"
        self.measurement.setText(measurement_text)
        
        # Position measurement text centered on the wall
        text_rect = self.measurement.boundingRect()
        self.measurement.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
        
        # Set measurement visibility based on setting
        self.measurement.setVisible(self.show_measurements)
    
    def create_handles(self):
        """Create selection handles for the wall item."""
        # Rotation handle
        self.handles["rotate"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["rotate"].setPen(QPen(Qt.GlobalColor.blue, 1))
        self.handles["rotate"].setBrush(QBrush(QColor(0, 0, 255, 128)))
        self.handles["rotate"].setVisible(False)
        
        # Length handles
        self.handles["left"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["left"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["left"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["left"].setVisible(False)
        
        self.handles["right"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["right"].setPen(QPen(Qt.GlobalColor.green, 1))
        self.handles["right"].setBrush(QBrush(QColor(0, 255, 0, 128)))
        self.handles["right"].setVisible(False)
        
        # Thickness handles
        self.handles["top"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["top"].setPen(QPen(Qt.GlobalColor.red, 1))
        self.handles["top"].setBrush(QBrush(QColor(255, 0, 0, 128)))
        self.handles["top"].setVisible(False)
        
        self.handles["bottom"] = QGraphicsEllipseItem(-4, -4, 8, 8, self)
        self.handles["bottom"].setPen(QPen(Qt.GlobalColor.red, 1))
        self.handles["bottom"].setBrush(QBrush(QColor(255, 0, 0, 128)))
        self.handles["bottom"].setVisible(False)
        
        # Set cursor shapes for handles
        self.handle_cursors = {
            "rotate": Qt.CursorShape.PointingHandCursor,
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor
        }
    
    def position_handles(self):
        """Position the selection handles based on the wall's properties."""
        # Position rotation handle above the wall
        self.handles["rotate"].setPos(0, -self.wall_width/2 - 30)
        
        # Position length handles at the ends of the wall
        self.handles["left"].setPos(-self.wall_length/2, 0)
        self.handles["right"].setPos(self.wall_length/2, 0)
        
        # Position thickness handles at the edges of the wall
        self.handles["top"].setPos(0, -self.wall_width/2)
        self.handles["bottom"].setPos(0, self.wall_width/2)
    
    def handle_resize(self, event, handle_name):
        """
        Handle resizing via a handle drag.
        
        Args:
            event: QGraphicsSceneMouseEvent
            handle_name: Name of the handle being dragged
        """
        # Get current transform to account for rotation
        transform = self.transform()
        
        # Get mouse position in item coordinates
        pos = event.pos()
        
        if handle_name in ["left", "right"]:
            # Resize wall length
            if handle_name == "left":
                # Calculate new wall length when dragging left handle
                delta = pos.x() + self.wall_length/2
                new_length = self.wall_length - delta * 2
                
                # Update position to keep the right end fixed
                if new_length > 20:  # Minimum length
                    self.setPos(self.mapToScene(QPointF(delta/2, 0)))
            else:  # right handle
                # Calculate new wall length when dragging right handle
                delta = pos.x() - self.wall_length/2
                new_length = self.wall_length + delta * 2
                
                # Update position to keep the left end fixed
                if new_length > 20:  # Minimum length
                    self.setPos(self.mapToScene(QPointF(delta/2, 0)))
            
            # Apply new length if above minimum
            if new_length > 20:
                self.wall_length = new_length
                self.wall.setRect(-self.wall_length/2, -self.wall_width/2, 
                                self.wall_length, self.wall_width)
                
                # Update model
                if self.model_item and hasattr(self.model_item, 'width'):
                    self.model_item.width = self.wall_length
        
        elif handle_name in ["top", "bottom"]:
            # Resize wall thickness
            if handle_name == "top":
                # Calculate new wall thickness when dragging top handle
                delta = pos.y() + self.wall_width/2
                new_width = self.wall_width - delta * 2
                
                # Update position to keep the bottom edge fixed
                if new_width > 2:  # Minimum thickness
                    self.setPos(self.mapToScene(QPointF(0, delta/2)))
            else:  # bottom handle
                # Calculate new wall thickness when dragging bottom handle
                delta = pos.y() - self.wall_width/2
                new_width = self.wall_width + delta * 2
                
                # Update position to keep the top edge fixed
                if new_width > 2:  # Minimum thickness
                    self.setPos(self.mapToScene(QPointF(0, delta/2)))
            
            # Apply new thickness if above minimum
            if new_width > 2:
                self.wall_width = new_width
                self.wall.setRect(-self.wall_length/2, -self.wall_width/2, 
                                self.wall_length, self.wall_width)
                
                # Update model
                if self.model_item and hasattr(self.model_item, 'thickness'):
                    self.model_item.thickness = self.wall_width
        
        # Update handles position and measurement after resize
        self.position_handles()
        self.update_measurement()
    
    def boundingRect(self):
        """
        Get the bounding rectangle of the item.
        
        Returns:
            QRectF: The bounding rectangle
        """
        return self.wall.boundingRect().united(self.label.boundingRect()).united(self.measurement.boundingRect())
    
    def paint(self, painter, option, widget):
        """
        Paint method is empty as painting is handled by child items.
        
        Args:
            painter: QPainter
            option: QStyleOptionGraphicsItem
            widget: QWidget
        """
        # No painting needed here, child items do their own painting
        pass
