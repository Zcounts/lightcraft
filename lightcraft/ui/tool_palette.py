"""
Tool Palette for the LightCraft application.
Provides a panel with tools for creating and manipulating lighting equipment.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QLabel, 
    QScrollArea, QFrame, QSizePolicy, QButtonGroup,
    QGridLayout, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QCursor
from PyQt6.QtWidgets import QButtonGroup

class ToolButton(QToolButton):
    """Custom tool button with improved styling and feedback."""
    
    def __init__(self, tool_id, name, tooltip="", parent=None):
        """
        Initialize the tool button.
        
        Args:
            tool_id: Unique identifier for the tool
            name: Display name for the tool
            tooltip: Tooltip text
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store tool id
        self.tool_id = tool_id
        self.setProperty("tool_id", tool_id)
        
        # Set button text and tooltip
        self.setText(name)
        self.setToolTip(tooltip)
        
        # Make button checkable
        self.setCheckable(True)
        
        # Set size and policies
        self.setMinimumWidth(80)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Preferred
        )
        
        # Set style properties
        self.setStyleSheet("""
            QToolButton {
                padding: 4px;
                border-radius: 4px;
                margin: 2px;
            }
            QToolButton:checked {
                background-color: #c0d6e4;
                border: 1px solid #6c8eaf;
            }
            QToolButton:hover:!checked {
                background-color: #e0e0e0;
            }
        """)
        
        # Future: Set icon for the button
        # self.setIcon(QIcon(f":/icons/{tool_id}.png"))
        # self.setIconSize(QSize(24, 24))
        # self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)


class ToolCategory(QWidget):
    """Widget for a category of tools."""
    
    def __init__(self, title, parent=None):
        """
        Initialize the tool category.
        
        Args:
            title: Category title
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 4)
        self.layout.setSpacing(2)
        
        # Add header
        self.header = QLabel(title)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Style the header
        font = QFont()
        font.setBold(True)
        self.header.setFont(font)
        self.header.setStyleSheet(
            "QLabel { background-color: #e0e0e0; padding: 4px; border-radius: 2px; }"
        )
        
        self.layout.addWidget(self.header)
        
        # Create button grid for tools
        self.button_grid = QGridLayout()
        self.button_grid.setSpacing(2)
        self.layout.addLayout(self.button_grid)
        
        # Track number of tools
        self.tool_count = 0
        
        # Track the button group
        self.button_group = None
    
    def add_tool(self, tool_button):
        """
        Add a tool button to the category.
        
        Args:
            tool_button: ToolButton to add
            
        Returns:
            The added button
        """
        # Add to grid layout - 2 buttons per row
        row = self.tool_count // 2
        col = self.tool_count % 2
        
        self.button_grid.addWidget(tool_button, row, col)
        self.tool_count += 1
        
        return tool_button
    
    def set_button_group(self, group):
        """
        Set the button group for this category.
        
        Args:
            group: QButtonGroup to use
        """
        self.button_group = group


class ToolPalette(QScrollArea):
    """
    Tool palette widget providing access to editing tools.
    Displayed on the left side of the main window.
    """
    
    # Signal emitted when a tool is selected
    tool_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Initialize the tool palette.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create widget to hold tools
        self.tool_widget = QWidget()
        self.setWidget(self.tool_widget)
        
        # Create layout
        self.layout = QVBoxLayout(self.tool_widget)
        self.layout.setContentsMargins(4, 8, 4, 8)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Create title
        title = QLabel("Tools")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        title.setFont(font)
        title.setStyleSheet("QLabel { margin-bottom: 8px; }")
        self.layout.addWidget(title)
        
        # Create tool categories
        self.categories = {}
        self.button_groups = {}
        
        # Master button group to ensure only one tool is selected
        self.master_button_group = QButtonGroup(self)
        self.master_button_group.setExclusive(True)
        
        # Initialize tools
        self.initialize()
        
        # Connect the master button group
        self.master_button_group.buttonClicked.connect(self.on_tool_selected)
        
        # Set default tool
        self.select_tool("select")
    
    def initialize(self):
        """Initialize the tool palette with tool categories and buttons."""
        # Selection Tools
        self.add_category("Selection Tools")
        self.add_tool("select", "Select", "Select and move items", "Selection Tools")
        self.add_tool("select-area", "Multi-Select", "Select multiple items", "Selection Tools")
        self.add_tool("rotate", "Rotate", "Rotate selected items", "Selection Tools")
        
        # Set Elements
        self.add_category("Set Elements")
        self.add_tool("wall", "Wall", "Create walls", "Set Elements")
        self.add_tool("door", "Door", "Add doors", "Set Elements")
        self.add_tool("window", "Window", "Add windows", "Set Elements")
        
        # Lighting Tools
        self.add_category("Lighting Tools")
        self.add_tool("light-spot", "Spot Light", "Add spot light", "Lighting Tools")
        self.add_tool("light-flood", "Flood Light", "Add flood light", "Lighting Tools")
        self.add_tool("light-led", "LED Panel", "Add LED panel", "Lighting Tools")
        
        # Camera Tools
        self.add_category("Camera Tools")
        self.add_tool("camera", "Camera", "Add camera position", "Camera Tools")
        
        # Modifier Tools
        self.add_category("Light Modifiers")
        self.add_tool("flag", "Flag", "Add flag (blocks light)", "Light Modifiers")
        self.add_tool("floppy", "Floppy", "Add floppy (blocks and redirects light)", "Light Modifiers")
        self.add_tool("scrim", "Scrim", "Add scrim (diffuses light)", "Light Modifiers")
        self.add_tool("diffusion", "Diffusion", "Add diffusion (softens light)", "Light Modifiers")
        
        # Add stretcher to push all content to the top
        self.layout.addStretch(1)
    
    def add_category(self, title):
        """
        Add a tool category.
        
        Args:
            title: Category title
        """
        category = ToolCategory(title)
        self.layout.addWidget(category)
        self.categories[title] = category
        
        # Create button group for this category
        group = QButtonGroup(self)
        group.setExclusive(True)
        self.button_groups[title] = group
        category.set_button_group(group)
    
    def add_tool(self, tool_id, name, tooltip, category):
        """
        Add a tool button to a category.
        
        Args:
            tool_id: Unique identifier for the tool
            name: Display name for the tool
            tooltip: Tooltip text
            category: Category to add the tool to
            
        Returns:
            The created tool button
        """
        if category not in self.categories:
            return None
        
        # Create tool button
        button = ToolButton(tool_id, name, tooltip)
        
        # Add to category
        self.categories[category].add_tool(button)
        
        # Add to category button group
        if category in self.button_groups:
            self.button_groups[category].addButton(button)
        
        # Add to master button group
        self.master_button_group.addButton(button)
        
        return button
    
    def on_tool_selected(self, button):
        """
        Handle tool selection.
        
        Args:
            button: The selected button
        """
        tool_id = button.property("tool_id")
        
        if tool_id:
            # Update cursor based on tool
            cursor = self.get_tool_cursor(tool_id)
            if cursor:
                # Set cursor on the application
                QApplication.setOverrideCursor(cursor)
            else:
                # Reset to default
                QApplication.restoreOverrideCursor()
            
            # Emit signal with selected tool ID
            self.tool_selected.emit(tool_id)
    
    def get_tool_cursor(self, tool_id):
        """
        Get the appropriate cursor for a tool.
        
        Args:
            tool_id: Tool identifier
        
        Returns:
            QCursor for the tool or None for default
        """
        # Define cursors for different tools
        cursor_map = {
            "select": Qt.CursorShape.ArrowCursor,
            "select-area": Qt.CursorShape.CrossCursor,
            "rotate": Qt.CursorShape.SizeAllCursor,
            "wall": Qt.CursorShape.CrossCursor,
            "door": Qt.CursorShape.CrossCursor,
            "window": Qt.CursorShape.CrossCursor,
            "light-spot": Qt.CursorShape.CrossCursor,
            "light-flood": Qt.CursorShape.CrossCursor,
            "light-led": Qt.CursorShape.CrossCursor,
            "camera": Qt.CursorShape.CrossCursor,
            "flag": Qt.CursorShape.CrossCursor,
            "floppy": Qt.CursorShape.CrossCursor,
            "scrim": Qt.CursorShape.CrossCursor,
            "diffusion": Qt.CursorShape.CrossCursor
        }
        
        if tool_id in cursor_map:
            return QCursor(cursor_map[tool_id])
        
        return None
    
    def select_tool(self, tool_id):
        """
        Programmatically select a tool.
        
        Args:
            tool_id: ID of the tool to select
        
        Returns:
            bool: True if tool was selected, False if not found
        """
        # Find the button with this tool_id and check it
        for button in self.master_button_group.buttons():
            if button.property("tool_id") == tool_id:
                button.setChecked(True)
                self.on_tool_selected(button)
                return True
        
        return False
