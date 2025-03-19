"""
Canvas Area for the LightCraft application.
Provides the main drawing area where lighting diagrams are created and manipulated.
"""

from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor

from lightcraft.config import GRID_SIZE, GRID_COLOR, GRID_ENABLED


class CanvasArea(QWidget):
    """
    Canvas area widget for creating and editing lighting diagrams.
    Contains a QGraphicsView and QGraphicsScene for diagram items.
    """
    
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
        
        # Create scene and view
        self.scene = LightingScene(self)
        self.view = LightingView(self.scene, self)
        
        # Add view to layout
        self.layout.addWidget(self.view)
        
        # Initialize the canvas
        self.initialize()
    
    def initialize(self):
        """Initialize the canvas with default settings."""
        # Set scene size (will be able to expand as needed)
        self.scene.setSceneRect(QRectF(0, 0, 3000, 2000))
        
        # Initialize grid
        self.scene.draw_grid()
        
        # Set view settings
        self.view.setRenderHint(self.view.renderHints().RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)


class LightingScene(QGraphicsScene):
    """
    Custom graphics scene for lighting diagrams.
    Handles grid drawing and will handle item management.
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
    
    def draw_grid(self):
        """Draw the grid on the background of the scene."""
        if not self.grid_enabled:
            return
        
        # Clear any existing grid lines
        # (In full implementation, we'd use a more efficient approach)
        
        rect = self.sceneRect()
        grid_pen = QPen(self.grid_color)
        grid_pen.setWidth(1)
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        
        # Draw vertical grid lines
        x = int(rect.left()) - (int(rect.left()) % self.grid_size)
        while x < rect.right():
            self.addLine(x, rect.top(), x, rect.bottom(), grid_pen)
            x += self.grid_size
        
        # Draw horizontal grid lines
        y = int(rect.top()) - (int(rect.top()) % self.grid_size)
        while y < rect.bottom():
            self.addLine(rect.left(), y, rect.right(), y, grid_pen)
            y += self.grid_size


class LightingView(QGraphicsView):
    """
    Custom graphics view for lighting diagrams.
    Handles zoom, pan, and will handle user interaction with the canvas.
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
        self.setRenderHint(self.renderHints().RenderHint.Antialiasing)
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
