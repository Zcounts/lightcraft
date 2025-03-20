"""
Canvas controller for the LightCraft application.
Manages interactions between tools and the canvas area.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QPointF, QMimeData
from PyQt6.QtWidgets import QApplication, QGraphicsItem
from PyQt6.QtGui import QUndoCommand
from PyQt6.QtGui import QTransform, QDrag

from lightcraft.models.equipment import LightingEquipment, Camera, SetElement
from lightcraft.ui.canvas_items import LightItem, CameraItem, WallItem, ModifierItem
from lightcraft.ui.canvas_factory import CanvasItemFactory


class ItemCreateCommand(QUndoCommand):
    """Undo command for item creation."""
    
    def __init__(self, canvas_controller, item, description="Create item"):
        """
        Initialize the command.
        
        Args:
            canvas_controller: The canvas controller
            item: Item that was created
            description: Command description
        """
        super().__init__(description)
        self.canvas_controller = canvas_controller
        self.item = item
        self.scene = item.scene()
        self.canvas_item_id = item.model_item.id if hasattr(item, 'model_item') and hasattr(item.model_item, 'id') else None
        
    def undo(self):
        """Undo the item creation."""
        if self.scene and self.item.scene() == self.scene:
            self.scene.removeItem(self.item)
            if self.canvas_item_id:
                self.canvas_controller.item_removed.emit(self.canvas_item_id)
    
    def redo(self):
        """Redo the item creation."""
        if self.scene and self.item.scene() != self.scene:
            self.scene.addItem(self.item)
            if hasattr(self.item, 'model_item'):
                self.canvas_controller.item_added.emit(self.item.model_item)


class ItemDeleteCommand(QUndoCommand):
    """Undo command for item deletion."""
    
    def __init__(self, canvas_controller, item, description="Delete item"):
        """
        Initialize the command.
        
        Args:
            canvas_controller: The canvas controller
            item: Item to delete
            description: Command description
        """
        super().__init__(description)
        self.canvas_controller = canvas_controller
        self.item = item
        self.scene = item.scene()
        self.pos = item.pos()
        self.canvas_item_id = item.model_item.id if hasattr(item, 'model_item') and hasattr(item.model_item, 'id') else None
        
    def undo(self):
        """Undo the item deletion."""
        if self.scene:
            self.scene.addItem(self.item)
            self.item.setPos(self.pos)
            if hasattr(self.item, 'model_item'):
                self.canvas_controller.item_added.emit(self.item.model_item)
    
    def redo(self):
        """Redo the item deletion."""
        if self.scene and self.item.scene() == self.scene:
            self.scene.removeItem(self.item)
            if self.canvas_item_id:
                self.canvas_controller.item_removed.emit(self.canvas_item_id)


class ItemMoveCommand(QUndoCommand):
    """Undo command for item movement."""
    
    def __init__(self, item, old_pos, new_pos, description="Move item"):
        """
        Initialize the command.
        
        Args:
            item: Item that was moved
            old_pos: Original position
            new_pos: New position
            description: Command description
        """
        super().__init__(description)
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        
    def undo(self):
        """Undo the item movement."""
        self.item.setPos(self.old_pos)
        if hasattr(self.item, 'model_item'):
            self.item.update_model_from_item()
    
    def redo(self):
        """Redo the item movement."""
        self.item.setPos(self.new_pos)
        if hasattr(self.item, 'model_item'):
            self.item.update_model_from_item()


class CanvasController(QObject):
    """
    Controller for managing canvas operations.
    Connects tools and canvas area, handling creation and modification of items.
    """
    
    # Signals
    item_selected = pyqtSignal(object)  # Model item selected
    item_added = pyqtSignal(object)     # Model item added
    item_removed = pyqtSignal(str)      # Model item ID removed
    item_modified = pyqtSignal(object)  # Model item modified
    
    def __init__(self, scene_controller, canvas_area, parent=None):
        """
        Initialize the canvas controller.
        
        Args:
            scene_controller: The scene controller
            canvas_area: The canvas area widget
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.scene_controller = scene_controller
        self.canvas_area = canvas_area
        
        # Set this controller in the canvas area
        if hasattr(self.canvas_area, 'canvas_controller'):
            self.canvas_area.canvas_controller = self
        
        # Create item factory
        self.item_factory = CanvasItemFactory()
        
        # Track currently selected items
        self.selected_items = []
        
        # Connect signals from canvas area
        self.connect_canvas_signals()
        
        # Properties panel reference (set externally)
        self.properties_panel = None
        
        # Current drawing operation
        self.drawing_in_progress = False
        self.drawing_start_pos = None
        self.preview_item = None
        self.current_tool = None
    
    def connect_canvas_signals(self):
        """Connect to canvas area signals."""
        if hasattr(self.canvas_area, 'item_selected'):
            self.canvas_area.item_selected.connect(self.on_canvas_item_selected)
        
        if hasattr(self.canvas_area, 'item_moved'):
            self.canvas_area.item_moved.connect(self.on_canvas_item_moved)
        
        if hasattr(self.canvas_area, 'item_resized'):
            self.canvas_area.item_resized.connect(self.on_canvas_item_resized)
        
        if hasattr(self.canvas_area, 'item_rotated'):
            self.canvas_area.item_rotated.connect(self.on_canvas_item_rotated)
    
    def connect_property_panel(self, properties_panel):
        """
        Connect to a properties panel.
        
        Args:
            properties_panel: PropertiesPanel instance
        """
        self.properties_panel = properties_panel
        
        # Connect property changed signal
        if hasattr(properties_panel, 'property_changed'):
            properties_panel.property_changed.connect(self.on_property_changed)
    
    def handle_tool_action(self, action, data):
        """
        Handle actions from the tool controller.
        
        Args:
            action: Action name
            data: Action data
        """
        # Store the current tool
        if action == "select" and "tool" in data:
            self.current_tool = data["tool"]
            
            # Set active tool in scene
            if hasattr(self.canvas_area, 'scene') and hasattr(self.canvas_area.scene, 'set_active_tool'):
                self.canvas_area.scene.set_active_tool(self.current_tool)
        
        # Handle create action
        elif action == "create":
            self.start_create_item(data.get("type"), data.get("pos"))
        
        # Handle update create action
        elif action == "update_create":
            self.update_create_item(data.get("type"), data.get("pos"))
        
        # Handle end create action
        elif action == "end_create":
            self.finish_create_item(data.get("type"), data.get("pos"))

        # Handle update create action
        elif action == "update_create":
            self.update_create_item(data.get("type"), data.get("pos"))
        
        # Handle end create action
        elif action == "end_create":
            self.finish_create_item(data.get("type"), data.get("pos"))
        
        # Handle select at position
        elif action == "select_at":
            self.select_at_position(data.get("pos"))
        
        # Handle start area select
        elif action == "start_area_select":
            if hasattr(self.canvas_area, 'view'):
                self.canvas_area.view.setDragMode(self.canvas_area.view.DragMode.RubberBandDrag)
            self.start_area_select(data.get("pos"))
        
        # Handle update area select
        elif action == "update_area_select":
            self.update_area_select(data.get("pos"))
        
        # Handle end area select
        elif action == "end_area_select":
            if hasattr(self.canvas_area, 'view'):
                self.canvas_area.view.setDragMode(self.canvas_area.view.DragMode.NoDrag)
            self.finish_area_select(data.get("pos"))
        
        # Handle start rotation
        elif action == "start_rotate":
            self.start_rotate_items(data.get("pos"))
        
        # Handle update rotation
        elif action == "update_rotate":
            self.update_rotate_items(data.get("pos"))
        
        # Handle end rotation
        elif action == "end_rotate":
            self.finish_rotate_items(data.get("pos"))
        
        # Handle delete
        elif action == "delete":
            self.delete_selected_items()
        
        # Handle movement
        elif action == "move_selection":
            self.move_selection(data.get("pos"))
    
    def create_new_item(self, item_type, position, properties=None):
        """
        Create a new item on the canvas.
        
        Args:
            item_type: Type of item to create
            position: Position to create at
            properties: Optional properties for the item
            
        Returns:
            The created canvas item or None if failed
        """
        if not self.canvas_area or not self.canvas_area.scene:
            return None
        
        # Extract position coordinates
        x = position.x() if hasattr(position, 'x') else 0
        y = position.y() if hasattr(position, 'y') else 0
        
        # Convert item type to match factory expectations
        factory_type = item_type
        if item_type == "light-spot":
            factory_type = "spot_light"
        elif item_type == "light-flood":
            factory_type = "flood_light"
        elif item_type == "light-led":
            factory_type = "led_panel"
        
        # Define default properties if not provided
        if properties is None:
            properties = {}
        
        # Add position to properties
        properties["x"] = x
        properties["y"] = y
        
        # Create model item based on type
        model_item = None
        if item_type.startswith("light"):
            # Create light equipment
            model_item = LightingEquipment(name=properties.get("name", "New Light"))
            for key, value in properties.items():
                if hasattr(model_item, key):
                    setattr(model_item, key, value)
            
            # Set default values if not provided
            if not hasattr(model_item, 'equipment_type') or not model_item.equipment_type:
                if factory_type == "spot_light":
                    model_item.equipment_type = "Fresnel"
                elif factory_type == "flood_light":
                    model_item.equipment_type = "Floodlight"
                elif factory_type == "led_panel":
                    model_item.equipment_type = "LED Panel"
                else:
                    model_item.equipment_type = "Generic"
            
            if not hasattr(model_item, 'power') or not model_item.power:
                model_item.power = 650
            
            if not hasattr(model_item, 'color_temperature') or not model_item.color_temperature:
                model_item.color_temperature = 5600
                
            if not hasattr(model_item, 'beam_angle') or not model_item.beam_angle:
                if factory_type == "spot_light":
                    model_item.beam_angle = 35
                elif factory_type == "flood_light":
                    model_item.beam_angle = 90
                elif factory_type == "led_panel":
                    model_item.beam_angle = 120
                else:
                    model_item.beam_angle = 45
                    
            if not hasattr(model_item, 'color') or not model_item.color:
                if model_item.color_temperature <= 3500:
                    model_item.color = "#FF9329"  # Tungsten color
                else:
                    model_item.color = "#FFFFFF"  # Daylight color
            
            if not hasattr(model_item, 'fixture_type') or not model_item.fixture_type:
                if factory_type == "spot_light":
                    model_item.fixture_type = "spotlight"
                elif factory_type == "flood_light" or factory_type == "led_panel":
                    model_item.fixture_type = "floodlight"
                else:
                    model_item.fixture_type = "spotlight"
        
        elif item_type == "camera":
            # Create camera
            model_item = Camera(name=properties.get("name", "New Camera"))
            for key, value in properties.items():
                if hasattr(model_item, key):
                    setattr(model_item, key, value)
            
            # Set default values if not provided
            if not hasattr(model_item, 'lens_mm') or not model_item.lens_mm:
                model_item.lens_mm = 35
        
        elif item_type in ["wall", "door", "window", "flag", "floppy", "scrim", "diffusion"]:
            # Create set element
            model_item = SetElement(name=properties.get("name", f"New {item_type.capitalize()}"))
            model_item.element_type = item_type.capitalize()
            
            for key, value in properties.items():
                if hasattr(model_item, key):
                    setattr(model_item, key, value)
            
            # Set default values if not provided
            if not hasattr(model_item, 'width') or not model_item.width:
                if item_type in ["wall", "door", "window"]:
                    model_item.width = 200  # Default wall/door/window width
                else:
                    model_item.width = 60   # Default flag/modifier width
            
            if not hasattr(model_item, 'height') or not model_item.height:
                if item_type == "wall":
                    model_item.height = 10  # Default wall height/thickness
                elif item_type in ["door", "window"]:
                    model_item.height = 10  # Default door/window height/thickness
                else:
                    model_item.height = 30   # Default flag/modifier height
            
            if (not hasattr(model_item, 'thickness') or not model_item.thickness) and item_type in ["wall", "door", "window"]:
                model_item.thickness = 10   # Default wall thickness
            
            if not hasattr(model_item, 'color') or not model_item.color:
                if item_type == "wall":
                    model_item.color = "#AAAAAA"  # Default wall color
                elif item_type == "door":
                    model_item.color = "#8B4513"  # Default door color
                elif item_type == "window":
                    model_item.color = "#B0C4DE"  # Default window color
                elif item_type == "flag":
                    model_item.color = "#111111"  # Default flag color
                elif item_type == "floppy":
                    model_item.color = "#222222"  # Default floppy color
                elif item_type == "scrim":
                    model_item.color = "#444444"  # Default scrim color
                elif item_type == "diffusion":
                    model_item.color = "#DDDDDD"  # Default diffusion color
        
        if not model_item:
            return None
        
        # Create canvas item from model item
        canvas_item = self.item_factory.create_item(model_item)
        if not canvas_item:
            return None
        
        # Add item to scene
        self.canvas_area.scene.addItem(canvas_item)
        
        # Set proper position
        canvas_item.setPos(position)
        
        # Update model
        canvas_item.update_model_from_item()
        
        # Add create command to undo stack
        if hasattr(self.canvas_area, 'add_command_to_stack'):
            self.canvas_area.add_command_to_stack(
                ItemCreateCommand(self, canvas_item, f"Create {item_type}")
            )
        
        # Emit item added signal
        self.item_added.emit(model_item)

        # Show status message
        if hasattr(self.parent(), 'statusBar'):
            self.parent().statusBar.showMessage(f"Created {item_type} at ({position.x():.0f}, {position.y():.0f})", 3000)
        
        # Select the new item
        if self.canvas_area.scene:
            self.canvas_area.scene.clearSelection()
            canvas_item.setSelected(True)
            self.on_canvas_item_selected(canvas_item)
        
        return canvas_item
    
    def handle_equipment_drop(self, equipment_id, position):
        """
        Handle equipment item dropped onto the canvas.
        
        Args:
            equipment_id: ID of the equipment from the library
            position: Position for the item
            
        Returns:
            The created canvas item or None if failed
        """
        try:
            # Import equipment data
            from lightcraft.models.equipment_data import get_equipment_by_id
            
            # Get equipment data
            equipment_data = get_equipment_by_id(equipment_id)
            if not equipment_data:
                print(f"Could not find equipment with ID: {equipment_id}")
                return None
                
            # Create appropriate model item based on category
            model_item = None
            category = equipment_data.get('category', '')
            
            if category == 'lights':
                model_item = LightingEquipment(name=equipment_data.get('name', 'New Light'))
                # Set light properties
                if 'properties' in equipment_data:
                    props = equipment_data['properties']
                    for key, value in props.items():
                        if hasattr(model_item, key):
                            setattr(model_item, key, value)
            elif category == 'camera':
                model_item = Camera(name=equipment_data.get('name', 'New Camera'))
                # Set camera properties
                if 'properties' in equipment_data:
                    props = equipment_data['properties']
                    for key, value in props.items():
                        if hasattr(model_item, key):
                            setattr(model_item, key, value)
            elif category in ['set', 'grip']:
                element_type = 'Wall'
                if equipment_data.get('subcategory') == 'control':
                    element_type = equipment_data.get('name', 'Flag').split(' ')[0]
                model_item = SetElement(name=equipment_data.get('name', 'New Element'), element_type=element_type)
                # Set element properties
                if 'properties' in equipment_data:
                    props = equipment_data['properties']
                    for key, value in props.items():
                        if hasattr(model_item, key):
                            setattr(model_item, key, value)
            
            if not model_item:
                print(f"Could not create model item for equipment type: {category}")
                return None
                
            # Set position
            model_item.x = position.x()
            model_item.y = position.y()
            
            # Create canvas item from model item
            canvas_item = self.item_factory.create_item(model_item)
            if not canvas_item:
                print(f"Could not create canvas item from model item")
                return None
            
            # Add item to scene
            self.canvas_area.scene.addItem(canvas_item)
            
            # Set proper position
            canvas_item.setPos(position)
            
            # Update model
            canvas_item.update_model_from_item()
            
            # Add create command to undo stack
            if hasattr(self.canvas_area, 'add_command_to_stack'):
                from lightcraft.controllers.canvas_controller import ItemCreateCommand
                self.canvas_area.add_command_to_stack(
                    ItemCreateCommand(self, canvas_item, f"Add equipment {model_item.name}")
                )
            
            # Emit item added signal
            self.item_added.emit(model_item)
            
            # Select the new item
            if self.canvas_area.scene:
                self.canvas_area.scene.clearSelection()
                canvas_item.setSelected(True)
                self.on_canvas_item_selected(canvas_item)
            
            return canvas_item
        except Exception as e:
            print(f"Error handling equipment drop: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def start_create_item(self, item_type, position):
        """
        Start creating a new item.
        
        Args:
            item_type: Type of item to create
            position: Starting position
        """
        if not self.canvas_area or not self.canvas_area.scene:
            return
        
        self.drawing_in_progress = True
        self.drawing_start_pos = position
        
        # Snap to grid if enabled
        if hasattr(self.canvas_area.scene, 'snap_to_grid'):
            position = self.canvas_area.scene.snap_to_grid(position)
            self.drawing_start_pos = position
        
        # For items that are placed directly (not drawn)
        if item_type in ["light-spot", "light-flood", "light-led", "camera"]:
            self.create_new_item(item_type, position)
            self.drawing_in_progress = False
            self.drawing_start_pos = None
        else:
            # For items that need to be drawn (walls, doors, etc.)
            if hasattr(self.canvas_area.scene, 'update_preview'):
                self.canvas_area.scene.update_preview(position, position, item_type)
    
    def update_create_item(self, item_type, position):
        """
        Update item being created.
        
        Args:
            item_type: Type of item being created
            position: Current position
        """
        if not self.drawing_in_progress or not self.drawing_start_pos:
            return
        
        # Snap to grid if enabled
        if hasattr(self.canvas_area.scene, 'snap_to_grid'):
            position = self.canvas_area.scene.snap_to_grid(position)
        
        # Update preview
        if hasattr(self.canvas_area.scene, 'update_preview'):
            self.canvas_area.scene.update_preview(self.drawing_start_pos, position, item_type)
    
    def finish_create_item(self, item_type, position):
        """
        Finish creating an item.
        
        Args:
            item_type: Type of item being created
            position: Final position
        """
        if not self.drawing_in_progress or not self.drawing_start_pos:
            return
        
        # Snap to grid if enabled
        if hasattr(self.canvas_area.scene, 'snap_to_grid'):
            position = self.canvas_area.scene.snap_to_grid(position)
        
        # Check if this was just a click (not a drag)
        start_x = self.drawing_start_pos.x()
        start_y = self.drawing_start_pos.y()
        end_x = position.x()
        end_y = position.y()
        
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        
        if distance < 5:
            # Treat as a single click - create default size item
            if item_type in ["wall", "door", "window"]:
                # Default horizontal wall
                properties = {
                    "name": f"New {item_type.capitalize()}",
                    "width": 200,
                    "height": 10 if item_type == "wall" else 150
                }
                self.create_new_item(item_type, position, properties)
            elif item_type in ["flag", "floppy", "scrim", "diffusion"]:
                # Default modifier
                properties = {
                    "name": f"New {item_type.capitalize()}", 
                    "width": 60, 
                    "height": 30
                }
                self.create_new_item(item_type, position, properties)
        else:
            # Create item with size based on drag distance
            width = abs(end_x - start_x)
            height = abs(end_y - start_y)
            
            if width < 10:
                width = 10
            if height < 10:
                height = 10
            
            # Calculate center position
            center_x = (start_x + end_x) / 2
            center_y = (start_y + end_y) / 2
            center_pos = QPointF(center_x, center_y)
            
            if item_type in ["wall", "door", "window"]:
                properties = {
                    "name": f"New {item_type.capitalize()}",
                    "width": width,
                    "height": height if item_type != "wall" else 10
                }
                self.create_new_item(item_type, center_pos, properties)
            elif item_type in ["flag", "floppy", "scrim", "diffusion"]:
                properties = {
                    "name": f"New {item_type.capitalize()}", 
                    "width": width, 
                    "height": height
                }
                self.create_new_item(item_type, center_pos, properties)
        
        # Reset drawing state
        self.drawing_in_progress = False
        self.drawing_start_pos = None
        
        # Remove preview if it exists
        if hasattr(self.canvas_area.scene, 'preview_item') and self.canvas_area.scene.preview_item:
            self.canvas_area.scene.removeItem(self.canvas_area.scene.preview_item)
            self.canvas_area.scene.preview_item = None
    
    def select_at_position(self, position):
        """
        Select an item at the given position.
        
        Args:
            position: Position to select at
        """
        if not self.canvas_area or not self.canvas_area.scene:
            return
        
        # Clear current selection
        self.canvas_area.scene.clearSelection()
        
        # Find items at position
        items = self.canvas_area.scene.items(position)
        
        # Select the first valid item
        for item in items:
            if isinstance(item, (LightItem, CameraItem, WallItem, ModifierItem)):
                item.setSelected(True)
                self.on_canvas_item_selected(item)
                break
    
    def start_area_select(self, position):
        """
        Start area selection.
        
        Args:
            position: Starting position
        """
        # This is handled by QGraphicsView's rubber band drag mode
        pass
    
    def update_area_select(self, position):
        """
        Update area selection.
        
        Args:
            position: Current position
        """
        # This is handled by QGraphicsView's rubber band drag mode
        pass
    
    def finish_area_select(self, position):
        """
        Finish area selection.
        
        Args:
            position: Final position
        """
        # Get selected items from scene
        if self.canvas_area and self.canvas_area.scene:
            selected_items = self.canvas_area.scene.selectedItems()
            if selected_items:
                # Use the first selected item for now
                self.on_canvas_item_selected(selected_items[0])
    
    def start_rotate_items(self, position):
        """
        Start rotating selected items.
        
        Args:
            position: Starting position
        """
        # This will be expanded in the future
        pass
    
    def update_rotate_items(self, position):
        """
        Update rotation of selected items.
        
        Args:
            position: Current position
        """
        # This will be expanded in the future
        pass
    
    def finish_rotate_items(self, position):
        """
        Finish rotating selected items.
        
        Args:
            position: Final position
        """
        # This will be expanded in the future
        pass
    
    def delete_selected_items(self):
        """Delete all selected items on the canvas."""
        if not self.canvas_area or not self.canvas_area.scene:
            return
        
        # Get selected items
        selected_items = self.canvas_area.scene.selectedItems()
        
        for item in selected_items:
            # Check if it's a canvas item
            if hasattr(item, 'model_item') and item.model_item:
                # Create delete command for undo stack
                if hasattr(self.canvas_area, 'add_command_to_stack'):
                    self.canvas_area.add_command_to_stack(
                        ItemDeleteCommand(self, item, f"Delete {item.model_item.name}")
                    )
                
                # Remove from scene
                self.canvas_area.scene.removeItem(item)
                
                # Emit item removed signal
                self.item_removed.emit(item.model_item.id)
        
        # Clear selection tracking
        self.selected_items = []
        
        # Update properties panel
        self.item_selected.emit(None)
    
    def move_selection(self, position):
        """
        Move selected items.
        
        Args:
            position: New position
        """
        # This is handled by the QGraphicsItem's default dragging behavior
        pass
    
    def on_canvas_item_selected(self, item):
        """
        Handle canvas item selection.
        
        Args:
            item: Selected canvas item or None if no selection
        """
        if not item:
            self.selected_items = []
            self.item_selected.emit(None)
            return
        
        # Check if it's a canvas item with a model
        if hasattr(item, 'model_item') and item.model_item:
            self.selected_items = [item]
            self.item_selected.emit(item.model_item)
    
    def on_canvas_item_moved(self, item):
        """
        Handle canvas item movement.
        
        Args:
            item: Moved canvas item
        """
        if hasattr(item, 'model_item') and item.model_item:
            # Update model item with new position
            item.update_model_from_item()
            
            # Emit item modified signal
            self.item_modified.emit(item.model_item)
            
            # Add move command to undo stack
            if hasattr(self.canvas_area, 'add_command_to_stack') and hasattr(item, 'last_pos'):
                self.canvas_area.add_command_to_stack(
                    ItemMoveCommand(item, item.last_pos, item.pos(),
                                   f"Move {item.model_item.name}")
                )
                
                # Update last position
                item.last_pos = item.pos()
    
    def on_canvas_item_resized(self, item):
        """
        Handle canvas item resizing.
        
        Args:
            item: Resized canvas item
        """
        if hasattr(item, 'model_item') and item.model_item:
            # Update model item with new size
            item.update_model_from_item()
            
            # Emit item modified signal
            self.item_modified.emit(item.model_item)
    
    def on_canvas_item_rotated(self, item):
        """
        Handle canvas item rotation.
        
        Args:
            item: Rotated canvas item
        """
        if hasattr(item, 'model_item') and item.model_item:
            # Update model item with new rotation
            item.update_model_from_item()
            
            # Emit item modified signal
            self.item_modified.emit(item.model_item)
    
    def on_property_changed(self, property_name, value):
        """
        Handle property changes from the properties panel.
        
        Args:
            property_name: Name of the property that changed
            value: New property value
        """
        if not self.selected_items:
            return
        
        # Apply change to all selected canvas items
        for item in self.selected_items:
            if hasattr(item, 'model_item') and item.model_item:
                # Update the model item
                if hasattr(item.model_item, property_name):
                    setattr(item.model_item, property_name, value)
                
                # Update the canvas item from model
                item.update_from_model()
                
                # Emit item modified signal
                self.item_modified.emit(item.model_item)
    
    def update_item_on_canvas(self, model_item):
        """
        Update a canvas item based on model item changes.
        
        Args:
            model_item: The updated model item
        """
        if not self.canvas_area or not self.canvas_area.scene:
            return
        
        # Find canvas item for this model item
        for item in self.canvas_area.scene.items():
            if (hasattr(item, 'model_item') and item.model_item and 
                hasattr(item.model_item, 'id') and hasattr(model_item, 'id') and
                item.model_item.id == model_item.id):
                
                # Update canvas item from model
                item.update_from_model()
                break
    
    def undo(self):
        """Undo the last operation."""
        if hasattr(self.canvas_area, 'undo'):
            self.canvas_area.undo()
    
    def redo(self):
        """Redo the last undone operation."""
        if hasattr(self.canvas_area, 'redo'):
            self.canvas_area.redo()
    
    def clear_canvas(self):
        """Clear all items from the canvas."""
        if hasattr(self.canvas_area, 'clear_scene'):
            self.canvas_area.clear_scene()
