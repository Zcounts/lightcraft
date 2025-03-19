"""
Scene controller for the LightCraft application.
Handles the interaction between the data model and the UI.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from lightcraft.models.project import Project
from lightcraft.models.scene import Scene
from lightcraft.models.equipment import LightingEquipment, SetElement, Camera


class SceneController(QObject):
    """
    Controller for handling scene operations.
    Manages the scene data model and its interaction with the UI.
    """
    
    # Signals for scene changes
    scene_changed = pyqtSignal()
    item_selected = pyqtSignal(object)
    item_added = pyqtSignal(object)
    item_removed = pyqtSignal(str)
    item_modified = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """
        Initialize the scene controller.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Current project and scene
        self.project = None
        self.current_scene = None
        
        # Selected items
        self.selected_items = []
    
    def new_project(self, project_name="New Project"):
        """
        Create a new project with a default scene.
        
        Args:
            project_name: Name for the new project
        """
        self.project = Project(name=project_name)
        
        # Create default scene
        scene = Scene(name="Main Scene")
        self.project.add_scene(scene)
        
        # Set as current scene
        self.current_scene = scene
        
        # Emit scene changed signal
        self.scene_changed.emit()
    
    def load_project(self, file_path):
        """
        Load a project from a file.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            bool: True if project was loaded successfully, False otherwise
        """
        project = Project.load(file_path)
        if not project:
            return False
        
        self.project = project
        
        # Set first scene as current scene
        if self.project.scenes:
            self.current_scene = self.project.scenes[0]
        else:
            # Create a default scene if project has no scenes
            scene = Scene(name="Main Scene")
            self.project.add_scene(scene)
            self.current_scene = scene
        
        # Emit scene changed signal
        self.scene_changed.emit()
        
        return True
    
    def save_project(self, file_path=None):
        """
        Save the current project to a file.
        
        Args:
            file_path: Path to save the project file, or None to use existing path
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.project:
            return False
        
        return self.project.save(file_path)
    
    def set_current_scene(self, scene_id):
        """
        Set the current scene by ID.
        
        Args:
            scene_id: ID of the scene to set as current
        
        Returns:
            bool: True if scene was set, False if scene doesn't exist
        """
        if not self.project:
            return False
        
        scene = self.project.get_scene(scene_id)
        if not scene:
            return False
        
        self.current_scene = scene
        
        # Emit scene changed signal
        self.scene_changed.emit()
        
        return True
    
    def add_item(self, item_type, properties):
        """
        Add a new item to the current scene.
        
        Args:
            item_type: Type of item to add ("light", "set_element", "camera")
            properties: Dictionary of properties for the new item
        
        Returns:
            The created item or None if failed
        """
        if not self.current_scene:
            return None
        
        # Create the item based on type
        if item_type == "light":
            item = LightingEquipment(
                name=properties.get("name", "New Light"),
                equipment_type=properties.get("equipment_type", "Generic")
            )
            category = "lights"
        elif item_type == "set_element":
            item = SetElement(
                name=properties.get("name", "New Set Element"),
                element_type=properties.get("element_type", "Wall")
            )
            category = "set_elements"
        elif item_type == "camera":
            item = Camera(name=properties.get("name", "New Camera"))
            category = "cameras"
        else:
            return None
        
        # Set position
        if "x" in properties and "y" in properties:
            item.x = properties["x"]
            item.y = properties["y"]
        
        # Set other properties
        for key, value in properties.items():
            if hasattr(item, key) and key not in ["id", "created_at", "modified_at"]:
                setattr(item, key, value)
        
        # Add item to scene
        self.current_scene.add_item(item, category)
        
        # Emit item added signal
        self.item_added.emit(item)
        
        return item
    
    def remove_item(self, item_id):
        """
        Remove an item from the current scene.
        
        Args:
            item_id: ID of the item to remove
        
        Returns:
            bool: True if item was removed, False otherwise
        """
        if not self.current_scene:
            return False
        
        result = self.current_scene.remove_item(item_id)
        if result:
            # Emit item removed signal
            self.item_removed.emit(item_id)
            
            # Remove from selection if selected
            self.selected_items = [item for item in self.selected_items if item.id != item_id]
            
            # If selection is empty, emit None selection
            if not self.selected_items:
                self.item_selected.emit(None)
        
        return result
    
    def update_item(self, item_id, properties):
        """
        Update an item's properties.
        
        Args:
            item_id: ID of the item to update
            properties: Dictionary of properties to update
        
        Returns:
            bool: True if item was updated, False otherwise
        """
        if not self.current_scene:
            return False
        
        item = self.current_scene.get_item(item_id)
        if not item:
            return False
        
        # Update properties
        for key, value in properties.items():
            if hasattr(item, key) and key not in ["id", "created_at"]:
                setattr(item, key, value)
        
        # Update modification time
        from datetime import datetime
        item.modified_at = datetime.now()
        
        # Emit item modified signal
        self.item_modified.emit(item)
        
        return True
    
    def select_item(self, item_id=None, clear_selection=True):
        """
        Select an item by ID.
        
        Args:
            item_id: ID of the item to select, or None to clear selection
            clear_selection: Whether to clear existing selection
        
        Returns:
            bool: True if selection was changed, False otherwise
        """
        if not self.current_scene:
            return False
        
        # Clear selection if requested
        if clear_selection:
            self.selected_items = []
        
        # If no item ID was provided, emit cleared selection
        if not item_id:
            self.item_selected.emit(None)
            return True
        
        # Find the item
        item = self.current_scene.get_item(item_id)
        if not item:
            return False
        
        # Add to selection if not already selected
        if item not in self.selected_items:
            self.selected_items.append(item)
        
        # Emit item selected signal
        # For simplicity, just emit the last selected item for now
        # In future prompts, we'll implement multi-selection properly
        self.item_selected.emit(item)
        
        return True
    
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_items = []
        self.item_selected.emit(None)
