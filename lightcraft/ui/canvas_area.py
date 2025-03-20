"""
Canvas Area for the LightCraft application.
Provides the main drawing area where lighting diagrams are created and manipulated.
"""

from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout,
    QGraphicsItem, QGraphicsItemGroup, QGraphicsRectItem,
    QGraphicsTextItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent
)
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QUndoStack
from PyQt6.QtGui import QUndoCommand
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize, QMimeData
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QTransform,
    QPolygonF, QPainterPath, QDrag
)

import math
from lightcraft.config import GRID_SIZE, GRID_COLOR, GRID_ENABLED
from lightcraft.ui.canvas_items import CanvasItem


class CanvasArea(QWidget):
    """
    Canvas area widget for creating and editing lighting diagrams.
    Contains a QGraphicsView and QGraphicsScene for diagram items.
    """
    
    # Signals
    item_selected = pyqtSignal(object)  # Canvas item selected
    item_moved = pyqtSignal(object)     # Canvas item moved
    item_resized = pyqtSignal(object)   # Canvas item resized
    item_rotated = pyqtSignal(object)   # Canvas item rotated
    
    def __init__(self, parent=None):
        """
        Initialize the canvas area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scene first, if not already done
        self.scene = LightingScene(self)
        self.view = LightingView(self.scene, self)
        
        # Set up undo stack
        self.undo_stack = QUndoStack(self)
        
        # Canvas controller (set externally)
        self.canvas_controller = None
        
        # Add view to layout
        self.layout.addWidget(self.view)
        
        # Initialize the canvas
        self.initialize()
        
        # Connect signals
        self.connect_signals()
    
    def initialize(self):
        """Initialize the canvas with default settings."""
        # Set scene size (will be able to expand as needed)
        self.scene.setSceneRect(QRectF(0, 0, 3000, 2000))
        
        # Initialize grid
        self.scene.draw_grid()
        
        # Set view settings
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Enable drops
        self.setAcceptDrops(True)
        self.view.setAcceptDrops(True)
    
    def connect_signals(self):
        """Connect signals to slots."""
        # Connect scene selection change
        self.scene.selectionChanged.connect(self.on_selection_changed)
    
    def on_selection_changed(self):
        """Handle selection changes in the scene."""
        selected_items = self.scene.selectedItems()
        
        if not selected_items:
            # No selection
            self.item_selected.emit(None)
        else:
            # Get first selected item
            canvas_item = selected_items[0]
            self.item_selected.emit(canvas_item)
    
    def dragEnterEvent(self, event):
        """
        Handle drag enter events.
        
        Args:
            event: QDragEnterEvent
        """
        # Accept equipment or item drags
        if event.mimeData().hasFormat("application/x-equipment") or \
           event.mimeData().hasFormat("application/x-canvas-item"):
            event.accept()
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """
        Handle drag move events.
        
        Args:
            event: QDragMoveEvent
        """
        # Accept equipment or item drags
        if event.mimeData().hasFormat("application/x-equipment") or \
           event.mimeData().hasFormat("application/x-canvas-item"):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """
        Handle drop events.
        
        Args:
            event: QDropEvent
        """
        # Get drop position in scene coordinates
        pos = self.view.mapToScene(event.pos())
        
        # Handle equipment drops
        if event.mimeData().hasFormat("application/x-equipment"):
            equipment_id = event.mimeData().data("application/x-equipment").data().decode()
            
            # Forward to canvas controller
            if hasattr(self, 'canvas_controller') and self.canvas_controller:
                # The canvas controller will handle creating the appropriate item
                # based on the equipment data
                self.canvas_controller.handle_equipment_drop(equipment_id, pos)
            
            event.acceptProposedAction()
        
        # Handle canvas item drops (for moving items)
        elif event.mimeData().hasFormat("application/x-canvas-item"):
            item_id = event.mimeData().data("application/x-canvas-item").data().decode()
            
            # Find the item in the scene
            for item in self.scene.items():
                if hasattr(item, 'id') and item.id == item_id:
                    # Move the item to the drop position
                    item.setPos(pos)
                    
                    # Emit moved signal
                    self.item_moved.emit(item)
                    break
            
            event.acceptProposedAction()
    
    def clear_scene(self):
        """Clear all items from the scene."""
        self.scene.clear()
        
        # Redraw grid
        self.scene.draw_grid()
    
    def add_command_to_stack(self, command):
        """
        Add a command to the undo stack.
        
        Args:
            command: QUndoCommand to add
        """
        self.undo_stack.push(command)
    
    def undo(self):
        """Undo the last operation."""
        if self.undo_stack.canUndo():
            self.undo_stack.undo()
    
    def redo(self):
        """Redo the last undone operation."""
        if self.undo_stack.canRedo():
            self.undo_stack.redo()
    
    def zoom_in(self):
        """Zoom in on the canvas."""
        self.view.scale(1.25, 1.25)
    
    def zoom_out(self):
        """Zoom out on the canvas."""
        self.view.scale(0.8, 0.8)
    
    def zoom_to_fit(self):
        """Zoom to fit all items in the view."""
        # Get the bounds of all items
        items_rect = self.scene.itemsBoundingRect()
        
        # If there are no items, just use the scene rect
        if items_rect.isEmpty():
            items_rect = self.scene.sceneRect()
        
        # Add some margin
        items_rect.adjust(-50, -50, 50, 50)
        
        # Fit the view to the items
        self.view.fitInView(items_rect, Qt.AspectRatioMode.KeepAspectRatio)
        
    def clear_scene(self):
        """Clear all items from the scene."""
        if hasattr(self, 'scene'):
            # Keep grid lines but remove other items
            for item in self.scene.items():
                if not (isinstance(item, QGraphicsRectItem) and item.data(0) == "grid_line"):
                    self.scene.removeItem(item)
            
            # Redraw grid if needed
            if hasattr(self.scene, 'draw_grid'):
                self.scene.draw_grid()

class LightingScene(QGraphicsScene):
    """
    Custom graphics scene for lighting diagrams.
    Handles grid drawing and item management.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the lighting scene.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.grid_enabled = GRID_ENABLED
        self.grid_size = GRID_SIZE
        self.grid_color = QColor(GRID_COLOR)
        
        # Track active tool
        self.active_tool = "select"
        
        # For custom item creation
        self.current_item = None
        self.creation_in_progress = False
        self.preview_item = None
    
    def draw_grid(self):
        """Draw the grid on the background of the scene."""
        if not self.grid_enabled:
            return
        
        # Clear any existing grid lines
        # (Only remove grid lines, not other items)
        for item in self.items():
            if isinstance(item, QGraphicsRectItem) and item.data(0) == "grid_line":
                self.removeItem(item)
        
        rect = self.sceneRect()
        grid_pen = QPen(self.grid_color)
        grid_pen.setWidth(1)
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        
        # Draw vertical grid lines
        x = int(rect.left()) - (int(rect.left()) % self.grid_size)
        while x < rect.right():
            line = self.addLine(x, rect.top(), x, rect.bottom(), grid_pen)
            line.setData(0, "grid_line")  # Mark as grid line
            line.setZValue(-1000)  # Ensure grid is behind all other items
            x += self.grid_size
        
        # Draw horizontal grid lines
        y = int(rect.top()) - (int(rect.top()) % self.grid_size)
        while y < rect.bottom():
            line = self.addLine(rect.left(), y, rect.right(), y, grid_pen)
            line.setData(0, "grid_line")  # Mark as grid line
            line.setZValue(-1000)  # Ensure grid is behind all other items
            y += self.grid_size
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        # If we're creating an item, start the creation process
        if self.active_tool.startswith("create_"):
            self.start_item_creation(event.scenePos(), self.active_tool.split("_")[1])
            event.accept()
            return
        
        # Otherwise, use default behavior
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        # If we're creating an item, update it
        if self.creation_in_progress and self.current_item:
            self.update_item_creation(event.scenePos())
            event.accept()
            return
        
        # Otherwise, use default behavior
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event: QGraphicsSceneMouseEvent
        """
        # If we're creating an item, finish the creation
        if self.creation_in_progress and self.current_item:
            self.finish_item_creation(event.scenePos())
            event.accept()
            return
            
        # Remove preview item if it exists
        if hasattr(self, 'preview_item') and self.preview_item:
            self.removeItem(self.preview_item)
            self.preview_item = None
        
        # Call parent implementation
        super().mouseReleaseEvent(event)
    
    def set_active_tool(self, tool):
        """
        Set the active tool.
        
        Args:
            tool: Tool identifier
        """
        self.active_tool = tool
    
    def start_item_creation(self, pos, item_type):
        """
        Start creating a new item.
        
        Args:
            pos: Position to create at
            item_type: Type of item to create
        """
        # This method would be implemented to create the appropriate item
        # For now, just set a flag
        self.creation_in_progress = True
        self.current_item = None  # Will be set by the factory
    
    def update_item_creation(self, pos):
        """
        Update item being created.
        
        Args:
            pos: Current mouse position
        """
        # Update the item being created, if any
        pass
    
    def finish_item_creation(self, pos):
        """
        Finish item creation.
        
        Args:
            pos: Final position
        """
        # Finish creating the item
        self.creation_in_progress = False
        self.current_item = None
    
    def update_preview(self, start_pos, current_pos, tool_type):
        """
        Update preview for item being created.
        
        Args:
            start_pos: Starting position of creation
            current_pos: Current mouse position
            tool_type: Type of tool being used
        """
        # If no preview item exists, create one
        if not hasattr(self, 'preview_item'):
            self.preview_item = None
        
        # Create or update preview based on tool type
        if tool_type in ["wall", "door", "window", "flag", "floppy", "scrim", "diffusion"]:
            self._update_rectangle_preview(start_pos, current_pos, tool_type)
        elif tool_type in ["light-spot", "light-flood", "light-led", "camera"]:
            # These items don't need a preview - they're placed directly
            if self.preview_item:
                self.removeItem(self.preview_item)
                self.preview_item = None
    
    def _update_rectangle_preview(self, start_pos, current_pos, tool_type):
        """
        Update preview for rectangular items.
        
        Args:
            start_pos: Starting position of creation
            current_pos: Current mouse position
            tool_type: Type of tool being used
        """
        # Calculate rect from start and current positions
        rect = QRectF(
            min(start_pos.x(), current_pos.x()),
            min(start_pos.y(), current_pos.y()),
            abs(current_pos.x() - start_pos.x()),
            abs(current_pos.y() - start_pos.y())
        )
        
        # If no preview item exists, create one
        if not self.preview_item:
            self.preview_item = self.addRect(rect, 
                                        QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine),
                                        QBrush(Qt.GlobalColor.transparent))
            self.preview_item.setZValue(1000)  # Ensure it's on top
            self.preview_item.setData(0, "preview")  # Mark as preview
        else:
            # Update existing preview
            self.preview_item.setRect(rect)
    
    def snap_to_grid(self, pos):
        """
        Snap a position to the grid.
        
        Args:
            pos: Position to snap
            
        Returns:
            QPointF: Snapped position
        """
        if not self.grid_enabled or self.grid_size <= 1:
            return pos
        
        # Snap to nearest grid point
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        
        return QPointF(x, y)


class LightingView(QGraphicsView):
    """
    Custom graphics view for lighting diagrams.
    Handles zoom, pan, and user interaction with the canvas.
    """
    
    def __init__(self, scene, parent=None):
        """
        Initialize the lighting view.
        
        Args:
            scene: The QGraphicsScene to display
            parent: Parent widget
        """
        super().__init__(scene, parent)
        
        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        
        # Initial zoom level
        self.current_zoom = 1.0
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def wheelEvent(self, event):
        """
        Handle mouse wheel events for zooming.
        
        Args:
            event: QWheelEvent instance
        """
        # Adjust zoom factor based on wheel delta
        zoom_factor = 1.1
        
        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(zoom_factor, zoom_factor)
            self.current_zoom *= zoom_factor
        else:
            # Zoom out
            self.scale(1 / zoom_factor, 1 / zoom_factor)
            self.current_zoom /= zoom_factor
        
        # Don't pass event to parent
        event.accept()
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: QMouseEvent instance
        """
        # Middle button for panning
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            # Create a temporary event to trick QGraphicsView 
            # into starting drag mode
            fake_event = event
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event: QMouseEvent instance
        """
        # Reset drag mode after middle button release
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        super().mouseReleaseEvent(event)
    
    def dragEnterEvent(self, event):
        """
        Handle drag enter events.
        
        Args:
            event: QDragEnterEvent
        """
        # Accept equipment or item drags
        if event.mimeData().hasFormat("application/x-equipment") or \
           event.mimeData().hasFormat("application/x-canvas-item"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """
        Handle drag move events.
        
        Args:
            event: QDragMoveEvent
        """
        # Accept equipment or item drags
        if event.mimeData().hasFormat("application/x-equipment") or \
           event.mimeData().hasFormat("application/x-canvas-item"):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """
        Handle drop events.
        
        Args:
            event: QDropEvent
        """
        # Convert the position to scene coordinates
        pos = self.mapToScene(event.pos())
        
        # Forward the drop to the parent widget (CanvasArea)
        if hasattr(self.parent(), 'dropEvent'):
            # Create a new event with the scene position
            mime_data = QMimeData()
            for format in event.mimeData().formats():
                mime_data.setData(format, event.mimeData().data(format))
            
            # Create a new drop event with the scene position
            drop_event = event
            drop_event.setDropAction(event.dropAction())
            drop_event.setMimeData(mime_data)
            
            # Forward to parent
            self.parent().dropEvent(drop_event)
            event.acceptProposedAction()
