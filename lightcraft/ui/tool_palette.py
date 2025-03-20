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
        
    # Generate SVG icon based on tool type
        self.setIcon(self.create_icon_for_tool(tool_id))
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    def create_icon_for_tool(self, tool_id):
            """Create a simple SVG icon based on the tool type."""
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtGui import QPixmap, QPainter
            
            # Create a blank pixmap
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Get SVG content based on tool ID
            svg_content = self.get_svg_for_tool(tool_id)
            
            if svg_content:
                # Create painter and render SVG
                painter = QPainter(pixmap)
                renderer = QSvgRenderer(svg_content.encode('utf-8'))
                renderer.render(painter)
                painter.end()
            
            return QIcon(pixmap)
        
        def get_svg_for_tool(self, tool_id):
            """Get SVG content for a specific tool."""
            # Simple SVG icons for different tools
            svg_icons = {
                "select": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M7,2l12,11.2l-5.8,0.5l3.3,7.3l-2.2,1l-3.2-7.4L7,18.5V2"/></svg>',
                "select-area": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M3,3v18h18V3H3z M19,19H5V5h14V19z"/><path fill="#ffffff" d="M7,7h4v4H7V7z M13,7h4v4h-4V7z M7,13h4v4H7V13z M13,13h4v4h-4V13z"/></svg>',
                "rotate": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M12,5V3l4,4l-4,4V9c-3.3,0-6,2.7-6,6c0,1,0.2,1.9,0.7,2.7l-1.7,1.7C3.4,18.1,3,16.6,3,15C3,9.5,7.5,5,12,5 M12,19c3.3,0,6-2.7,6-6c0-1-0.2-1.9-0.7-2.7l1.7-1.7c0.6,1.3,1,2.8,1,4.4c0,5.5-4.5,10-10,10l-4-4l4-4V19z"/></svg>',
                "wall": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M3,6h18v12H3V6z M7,10h2v4H7V10z M11,10h2v4h-2V10z M15,10h2v4h-2V10z"/></svg>',
                "door": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M19,3h-9C8.3,3,7,4.3,7,6v12c0,1.7,1.3,3,3,3h9V3z M13,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S13.6,15,13,15z"/></svg>',
                "window": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M3,3h18v18H3V3z M17,17V7H7v10H17z M5,5h2v2H5V5z M5,17h2v2H5V17z M17,5h2v2h-2V5z M17,17h2v2h-2V17z"/></svg>',
                "light-spot": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M6.4,6.4L2,5l1.4,4.4L6.4,6.4z M17.6,6.4L20.6,5l-1.4,4.4L17.6,6.4z M12,4c-5,0-9,4-9,9c0,3.9,2.5,7.2,6,8.4V22h6v-0.6c3.5-1.2,6-4.5,6-8.4C21,8,17,4,12,4z M12,19c-3.3,0-6-2.7-6-6c0-3.3,2.7-6,6-6s6,2.7,6,6C18,16.3,15.3,19,12,19z M12,9c-2.2,0-4,1.8-4,4c0,2.2,1.8,4,4,4s4-1.8,4-4C16,10.8,14.2,9,12,9z"/></svg>',
                "light-flood": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M10,2v2h4V2H10z M10,20v2h4v-2H10z M4,10h2v4H4V10z M18,10h2v4h-2V10z M17,8l1.4-1.4L17,5.2L15.6,6.6L17,8z M7,8L5.6,6.6L7,5.2L8.4,6.6L7,8z M17,16l1.4,1.4L17,18.8l-1.4-1.4L17,16z M7,16l1.4,1.4L7,18.8l-1.4-1.4L7,16z M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,16c-2.2,0-4-1.8-4-4c0-2.2,1.8-4,4-4s4,1.8,4,4C16,14.2,14.2,16,12,16z"/></svg>',
                "light-led": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M3,3h18v18H3V3z M5,5v14h14V5H5z M7,7h10v10H7V7z M9,9h6v6H9V9z"/></svg>',
                "camera": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M9,3L7.2,5H4C2.9,5,2,5.9,2,7v12c0,1.1,0.9,2,2,2h16c1.1,0,2-0.9,2-2V7c0-1.1-0.9-2-2-2h-3.2L15,3H9z M12,18c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,18,12,18z M12,10c-1.7,0-3,1.3-3,3s1.3,3,3,3s3-1.3,3-3S13.7,10,12,10z"/></svg>',
                "flag": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M12.4,2l-0.2,6.6L14,8l1.2-6H12.4z M19,8l-7.8-2.6L11,11.4L18.8,14L19,8z M7,2v20h2V2H7z"/></svg>',
                "floppy": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M5,3h14c1.1,0,2,0.9,2,2v14c0,1.1-0.9,2-2,2H5c-1.1,0-2-0.9-2-2V5C3,3.9,3.9,3,5,3z M12,17c1.7,0,3-1.3,3-3s-1.3-3-3-3s-3,1.3-3,3S10.3,17,12,17z M6,6h9v4H6V6z"/></svg>',
                "scrim": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M3,3h4v4H3V3z M9,3h4v4H9V3z M15,3h4v4h-4V3z M3,9h4v4H3V9z M9,9h4v4H9V9z M15,9h4v4h-4V9z M3,15h4v4H3V15z M9,15h4v4H9V15z M15,15h4v4h-4V15z"/></svg>',
                "diffusion": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffffff" d="M2,4h20v16H2V4z M4,6v12h16V6H4z M8,8h8v2H8V8z M8,12h8v2H8V12z M8,16h8v2H8V16z"/></svg>'
            }
            
            return svg_icons.get(tool_id, None)

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
