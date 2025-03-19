"""
Tool controller for the LightCraft application.
Handles the interaction between tools and the canvas.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt


class ToolController(QObject):
    """
    Controller for handling tool operations in the canvas.
    Manages the active tool and its interactions.
    """
    
    # Signal emitted when a tool action is performed
    tool_action = pyqtSignal(str, object)
    
    def __init__(self, canvas=None, parent=None):
        """
        Initialize the tool controller.
        
        Args:
            canvas: The canvas area to control
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.canvas = canvas
        self.active_tool = None
        self.tools = {}  # Dictionary of available tools
        
        # Initialize tools
        self.initialize_tools()
    
    def initialize_tools(self):
        """Initialize the available tools."""
        # This is a placeholder for now - will be implemented in future prompts
        self.tools = {
            "select": {"cursor": Qt.CursorShape.ArrowCursor, "mode": "select"},
            "select-area": {"cursor": Qt.CursorShape.CrossCursor, "mode": "select-area"},
            "rotate": {"cursor": Qt.CursorShape.SizeAllCursor, "mode": "rotate"},
            "room": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "room"},
            "wall": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "wall"},
            "door": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "door"},
            "window": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "window"},
            "light-spot": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "light-spot"},
            "light-flood": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "light-flood"},
            "light-led": {"cursor": Qt.CursorShape.CrossCursor, "mode": "create", "item_type": "light-led"}
        }
    
    def set_active_tool(self, tool_id):
        """
        Set the active tool.
        
        Args:
            tool_id: Identifier for the tool to activate
        
        Returns:
            bool: True if tool was set, False if tool doesn't exist
        """
        if tool_id not in self.tools:
            return False
        
        self.active_tool = tool_id
        
        # Apply tool-specific settings to canvas
        if self.canvas:
            tool_info = self.tools[tool_id]
            self.canvas.view.setCursor(tool_info["cursor"])
            
            # Set canvas mode based on tool
            # This will be implemented in future prompts
        
        # Emit tool action signal
        self.tool_action.emit("select", {"tool": tool_id})
        
        return True
    
    def handle_canvas_press(self, event, pos):
        """
        Handle mouse press events on the canvas.
        
        Args:
            event: The mouse event
            pos: The position in scene coordinates
        """
        if not self.active_tool:
            return
        
        tool_info = self.tools[self.active_tool]
        
        # Handle based on tool mode
        if tool_info["mode"] == "select":
            self.tool_action.emit("select_at", {"pos": pos})
        
        elif tool_info["mode"] == "select-area":
            self.tool_action.emit("start_area_select", {"pos": pos})
        
        elif tool_info["mode"] == "rotate":
            self.tool_action.emit("start_rotate", {"pos": pos})
        
        elif tool_info["mode"] == "create":
            self.tool_action.emit("create", {
                "type": tool_info["item_type"],
                "pos": pos
            })
    
    def handle_canvas_move(self, event, pos):
        """
        Handle mouse move events on the canvas.
        
        Args:
            event: The mouse event
            pos: The position in scene coordinates
        """
        if not self.active_tool:
            return
        
        tool_info = self.tools[self.active_tool]
        
        # Handle based on tool mode
        if tool_info["mode"] == "select" and event.buttons() & Qt.MouseButton.LeftButton:
            self.tool_action.emit("move_selection", {"pos": pos})
        
        elif tool_info["mode"] == "select-area" and event.buttons() & Qt.MouseButton.LeftButton:
            self.tool_action.emit("update_area_select", {"pos": pos})
        
        elif tool_info["mode"] == "rotate" and event.buttons() & Qt.MouseButton.LeftButton:
            self.tool_action.emit("update_rotate", {"pos": pos})
        
        elif tool_info["mode"] == "create" and event.buttons() & Qt.MouseButton.LeftButton:
            self.tool_action.emit("update_create", {
                "type": tool_info["item_type"],
                "pos": pos
            })
    
    def handle_canvas_release(self, event, pos):
        """
        Handle mouse release events on the canvas.
        
        Args:
            event: The mouse event
            pos: The position in scene coordinates
        """
        if not self.active_tool:
            return
        
        tool_info = self.tools[self.active_tool]
        
        # Handle based on tool mode
        if tool_info["mode"] == "select":
            self.tool_action.emit("end_select", {"pos": pos})
        
        elif tool_info["mode"] == "select-area":
            self.tool_action.emit("end_area_select", {"pos": pos})
        
        elif tool_info["mode"] == "rotate":
            self.tool_action.emit("end_rotate", {"pos": pos})
        
        elif tool_info["mode"] == "create":
            self.tool_action.emit("end_create", {
                "type": tool_info["item_type"],
                "pos": pos
            })
