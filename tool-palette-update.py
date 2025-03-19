"""
This code shows the updates needed for the tool palette to work 
with the enhanced canvas functionality.
These modifications should be added to the existing tool_palette.py file.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy, QButtonGroup
)

# Update the initialize method in ToolPalette class

def initialize(self):
    """Initialize the tool palette with tool categories and buttons."""
    # Selection Tools Header
    self.add_category_header("Selection Tools")
    
    # Create a button group for selection tools to make them mutually exclusive
    self.selection_group = QButtonGroup(self)
    
    # Selection tools
    select_btn = self.add_tool_button("select", "Select", "Select and move items")
    select_area_btn = self.add_tool_button("select-area", "Area Select", "Select multiple items")
    rotate_btn = self.add_tool_button("rotate", "Rotate", "Rotate selected items")
    
    # Add the buttons to the selection group
    self.selection_group.addButton(select_btn)
    self.selection_group.addButton(select_area_btn)
    self.selection_group.addButton(rotate_btn)
    
    # Drawing Tools Header
    self.add_category_header("Set Elements")
    
    # Create a button group for drawing tools
    self.drawing_group = QButtonGroup(self)
    
    # Drawing tools
    room_btn = self.add_tool_button("room", "Room", "Create room boundaries")
    wall_btn = self.add_tool_button("wall", "Wall", "Draw walls")
    door_btn = self.add_tool_button("door", "Door", "Add doors")
    window_btn = self.add_tool_button("window", "Window", "Add windows")
    
    # Add the buttons to the drawing group
    self.drawing_group.addButton(room_btn)
    self.drawing_group.addButton(wall_btn)
    self.drawing_group.addButton(door_btn)
    self.drawing_group.addButton(window_btn)
    
    # Lighting Tools Header
    self.add_category_header("Lighting Tools")
    
    # Create a button group for lighting tools
    self.lighting_group = QButtonGroup(self)
    
    # Lighting tools
    spot_btn = self.add_tool_button("light-spot", "Spot Light", "Add spot light")
    flood_btn = self.add_tool_button("light-flood", "Flood Light", "Add flood light")
    led_btn = self.add_tool_button("light-led", "LED Panel", "Add LED panel")
    
    # Add the buttons to the lighting group
    self.lighting_group.addButton(spot_btn)
    self.lighting_group.addButton(flood_btn)
    self.lighting_group.addButton(led_btn)
    
    # Camera Header
    self.add_category_header("Camera Tools")
    
    # Create a button group for camera tools
    self.camera_group = QButtonGroup(self)
    
    # Camera tools
    camera_btn = self.add_tool_button("camera", "Camera", "Add camera position")
    self.camera_group.addButton(camera_btn)
    
    # Modifiers Header
    self.add_category_header("Light Modifiers")
    
    # Create a button group for modifiers
    self.modifier_group = QButtonGroup(self)
    
    # Modifier tools
    flag_btn = self.add_tool_button("flag", "Flag", "Add flag (blocks light)")
    floppy_btn = self.add_tool_button("floppy", "Floppy", "Add floppy (blocks and redirects light)")
    scrim_btn = self.add_tool_button("scrim", "Scrim", "Add scrim (diffuses light)")
    
    # Add the buttons to the modifiers group
    self.modifier_group.addButton(flag_btn)
    self.modifier_group.addButton(floppy_btn)
    self.modifier_group.addButton(scrim_btn)
    
    # Group all tools together in a master group
    self.all_tools_group = QButtonGroup(self)
    self.all_tools_group.setExclusive(True)
    
    # Add all tools to the master group
    for btn in self.selection_group.buttons():
        self.all_tools_group.addButton(btn)
    
    for btn in self.drawing_group.buttons():
        self.all_tools_group.addButton(btn)
    
    for btn in self.lighting_group.buttons():
        self.all_tools_group.addButton(btn)
    
    for btn in self.camera_group.buttons():
        self.all_tools_group.addButton(btn)
    
    for btn in self.modifier_group.buttons():
        self.all_tools_group.addButton(btn)
    
    # Select the default tool (select tool)
    select_btn.setChecked(True)
    
    # Add stretcher to push all content to the top
    self.layout.addStretch(1)

# Add a new method to the ToolPalette class for programmatic tool selection

def select_tool(self, tool_id):
    """
    Programmatically select a tool.
    
    Args:
        tool_id: ID of the tool to select
    
    Returns:
        bool: True if tool was selected, False if not found
    """
    # Find the button with this tool_id and check it
    for button in self.all_tools_group.buttons():
        if button.property("tool_id") == tool_id:
            button.setChecked(True)
            self.on_tool_selected(tool_id, True)
            return True
    
    return False
