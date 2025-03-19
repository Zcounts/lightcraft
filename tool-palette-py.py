"""
Tool Palette for the LightCraft application.
Provides a panel with tools for creating and manipulating lighting equipment.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QLabel, 
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont


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
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Initialize tools
        self.initialize()
    
    def initialize(self):
        """Initialize the tool palette with tool categories and buttons."""
        # Selection Tools Header
        self.add_category_header("Selection Tools")
        
        # Selection tools
        self.add_tool_button("select", "Select", "Select and move items")
        self.add_tool_button("select-area", "Select Area", "Select multiple items")
        self.add_tool_button("rotate", "Rotate", "Rotate selected items")
        
        # Drawing Tools Header
        self.add_category_header("Drawing Tools")
        
        # Drawing tools
        self.add_tool_button("room", "Room", "Create room boundaries")
        self.add_tool_button("wall", "Wall", "Draw walls")
        self.add_tool_button("door", "Door", "Add doors")
        self.add_tool_button("window", "Window", "Add windows")
        
        # Lighting Tools Header
        self.add_category_header("Lighting Tools")
        
        # Lighting tools 
        # (These are placeholders - will be filled with actual equipment in future prompts)
        self.add_tool_button("light-spot", "Spot Light", "Add spot light")
        self.add_tool_button("light-flood", "Flood Light", "Add flood light")
        self.add_tool_button("light-led", "LED Panel", "Add LED panel")
        
        # Add stretcher to push all content to the top
        self.layout.addStretch(1)
    
    def add_category_header(self, title):
        """
        Add a category header label to the tool palette.
        
        Args:
            title: The header title text
        """
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Style the header
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet(
            "QLabel { background-color: #e0e0e0; padding: 4px; border-radius: 2px; }"
        )
        
        self.layout.addWidget(label)
    
    def add_tool_button(self, tool_id, name, tooltip):
        """
        Add a tool button to the palette.
        
        Args:
            tool_id: Unique identifier for the tool
            name: Display name for the tool
            tooltip: Tooltip text
        """
        button = QToolButton()
        button.setText(name)
        button.setToolTip(tooltip)
        button.setCheckable(True)
        button.setMinimumWidth(80)
        button.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Preferred
        )
        
        # In the future, we'll add icons for each tool
        # button.setIcon(QIcon(f":/icons/{tool_id}.png"))
        # button.setIconSize(QSize(24, 24))
        # button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Set ID property for identification
        button.setProperty("tool_id", tool_id)
        
        # Connect clicked signal
        button.clicked.connect(lambda checked, tid=tool_id: self.on_tool_selected(tid, checked))
        
        self.layout.addWidget(button)
    
    def on_tool_selected(self, tool_id, checked):
        """
        Handle tool selection.
        
        Args:
            tool_id: ID of the selected tool
            checked: Whether the button is checked
        """
        if checked:
            # Uncheck all other tools
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QToolButton) and widget.property("tool_id") != tool_id:
                        widget.setChecked(False)
            
            # Emit signal with selected tool ID
            self.tool_selected.emit(tool_id)
