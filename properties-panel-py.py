"""
Properties Panel for the LightCraft application.
Displays and allows editing of properties for selected items.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, 
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
    QComboBox, QColorDialog, QPushButton, QHBoxLayout,
    QSizePolicy, QGroupBox, QSlider, QCheckBox, QListWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QColor, QFont, QPalette

import math
from lightcraft.ui.canvas_items import LightItem, CameraItem, WallItem, ModifierItem


class ColorButton(QPushButton):
    """
    Button for selecting colors.
    """
    
    # Signal emitted when a color is selected
    color_selected = pyqtSignal(str)
    
    def __init__(self, color="#FFFFFF", parent=None):
        """
        Initialize the color button.
        
        Args:
            color: Initial color in hex format
            parent: Parent widget
        """
        super().__init__(parent)
        self.color = QColor(color)
        self.setMinimumWidth(30)
        self.update_background()
        
        # Connect clicked signal
        self.clicked.connect(self.show_color_dialog)
    
    def update_background(self):
        """Update button background to reflect current color."""
        self.setStyleSheet(f"background-color: {self.color.name()}; min-height: 20px;")
    
    def show_color_dialog(self):
        """Show color selection dialog."""
        color = QColorDialog.getColor(self.color, self.parent(), "Select Color")
        if color.isValid():
            self.color = color
            self.update_background()
            self.color_selected.emit(color.name())
    
    def set_color(self, color):
        """
        Set the button color.
        
        Args:
            color: Color in hex format
        """
        self.color = QColor(color)
        self.update_background()


class PropertiesPanel(QScrollArea):
    """
    Properties panel widget for viewing and editing item properties.
    Displayed on the right side of the main window.
    """
    
    # Signal emitted when a property value is changed
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        """
        Initialize the properties panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create widget to hold properties
        self.properties_widget = QWidget()
        self.setWidget(self.properties_widget)
        
        # Create layout
        self.layout = QVBoxLayout(self.properties_widget)
        self.layout.setContentsMargins(8, 12, 8, 12)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Current selected item (None if no selection)
        self.current_item = None
        
        # Forms for different property sections
        self.common_form = QFormLayout()
        self.specific_form = QFormLayout()
        
        # Property widgets (for updating)
        self.property_widgets = {}
        
        # Initialize panel
        self.initialize()
    
    def initialize(self):
        """Initialize the properties panel with default content."""
        # Title
        title_label = QLabel("Properties")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("QLabel { margin-bottom: 8px; }")
        self.layout.addWidget(title_label)
        
        # No selection label
        self.no_selection_label = QLabel("No item selected")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setStyleSheet(
            "QLabel { color: #777; margin: 20px; }"
        )
        self.layout.addWidget(self.no_selection_label)
        
        # Property container widget (hidden when no selection)
        self.property_container = QWidget()
        self.property_layout = QVBoxLayout(self.property_container)
        self.property_layout.setContentsMargins(0, 0, 0, 0)
        self.property_layout.setSpacing(8)
        self.layout.addWidget(self.property_container)
        self.property_container.hide()
        
        # Add property groups
        self.create_common_properties_group()
        self.create_specific_properties_group()
        
        # Add stretcher to push all content to the top
        self.layout.addStretch(1)
    
    def create_common_properties_group(self):
        """Create the group for common properties (position, rotation, etc.)."""
        group = QGroupBox("Common Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        self.common_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.common_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # Name field
        self.property_widgets["name"] = QLineEdit()
        self.property_widgets["name"].textChanged.connect(
            lambda text: self.on_property_changed("name", text)
        )
        self.common_form.addRow("Name:", self.property_widgets["name"])
        
        # Position X
        self.property_widgets["x"] = QDoubleSpinBox()
        self.property_widgets["x"].setRange(-10000, 10000)
        self.property_widgets["x"].valueChanged.connect(
            lambda value: self.on_property_changed("x", value)
        )
        self.common_form.addRow("Position X:", self.property_widgets["x"])
        
        # Position Y
        self.property_widgets["y"] = QDoubleSpinBox()
        self.property_widgets["y"].setRange(-10000, 10000)
        self.property_widgets["y"].valueChanged.connect(
            lambda value: self.on_property_changed("y", value)
        )
        self.common_form.addRow("Position Y:", self.property_widgets["y"])
        
        # Rotation
        self.property_widgets["rotation"] = QDoubleSpinBox()
        self.property_widgets["rotation"].setRange(0, 360)
        self.property_widgets["rotation"].valueChanged.connect(
            lambda value: self.on_property_changed("rotation", value)
        )
        self.common_form.addRow("Rotation:", self.property_widgets["rotation"])
        
        # Visibility
        self.property_widgets["visible"] = QCheckBox("Visible")
        self.property_widgets["visible"].stateChanged.connect(
            lambda state: self.on_property_changed("visible", state == Qt.CheckState.Checked)
        )
        self.common_form.addRow("", self.property_widgets["visible"])
        
        group.setLayout(self.common_form)
        self.property_layout.addWidget(group)
    
    def create_specific_properties_group(self):
        """
        Create the group for item-specific properties.
        These will change based on the selected item type.
        """
        group = QGroupBox("Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        self.specific_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.specific_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # This will be populated dynamically when an item is selected
        group.setLayout(self.specific_form)
        self.property_layout.addWidget(group)
    
    def clear_specific_properties(self):
        """Clear the specific properties form."""
        # Remove all widgets from the form
        while self.specific_form.rowCount() > 0:
            self.specific_form.removeRow(0)
        
        # Remove specific property widgets from the dictionary
        keys_to_remove = [key for key in self.property_widgets if key not in ["name", "x", "y", "rotation", "visible"]]
        for key in keys_to_remove:
            del self.property_widgets[key]
    
    def update_properties(self, item=None):
        """
        Update the panel to display properties for the selected item.
        
        Args:
            item: The selected item or None if no selection
        """
        self.current_item = item
        
        if item is None:
            # No selection
            self.no_selection_label.show()
            self.property_container.hide()
            return
        
        # Show properties container and hide no selection label
        self.no_selection_label.hide()
        self.property_container.show()
        
        # Update common properties
        self._updating = True  # Flag to prevent property signal feedback
        
        # Set common properties
        if hasattr(item, 'name'):
            self.property_widgets["name"].setText(item.name)
        else:
            self.property_widgets["name"].setText("Item")
        
        self.property_widgets["x"].setValue(item.x)
        self.property_widgets["y"].setValue(item.y)
        self.property_widgets["rotation"].setValue(item.rotation)
        
        if hasattr(item, 'visible'):
            self.property_widgets["visible"].setChecked(item.visible)
        else:
            self.property_widgets["visible"].setChecked(True)
        
        # Clear and update specific properties based on item type
        self.clear_specific_properties()
        
        if isinstance(item, LightingEquipment):
            self.setup_light_properties(item)
        elif isinstance(item, Camera):
            self.setup_camera_properties(item)
        elif isinstance(item, SetElement):
            if hasattr(item, 'element_type'):
                if item.element_type.lower() in ['wall', 'door', 'window']:
                    self.setup_wall_properties(item)
                elif item.element_type.lower() in ['flag', 'floppy', 'scrim', 'diffusion']:
                    self.setup_modifier_properties(item)
                else:
                    self.setup_set_element_properties(item)
            else:
                self.setup_set_element_properties(item)
        
        self._updating = False
    
    def setup_light_properties(self, item):
        """
        Set up properties for a light item.
        
        Args:
            item: LightingEquipment instance
        """
        # Equipment type
        if hasattr(item, 'equipment_type'):
            type_label = QLabel(item.equipment_type)
            type_label.setStyleSheet("font-weight: bold;")
            self.specific_form.addRow("Type:", type_label)
        
        # Power
        if hasattr(item, 'power'):
            power_spin = QSpinBox()
            power_spin.setRange(0, 20000)
            power_spin.setSuffix(" W")
            power_spin.setValue(item.power)
            power_spin.valueChanged.connect(
                lambda value: self.on_property_changed("power", value)
            )
            self.property_widgets["power"] = power_spin
            self.specific_form.addRow("Power:", power_spin)
        
        # Intensity / Dimmer
        intensity_slider = QSlider(Qt.Orientation.Horizontal)
        intensity_slider.setRange(0, 100)
        intensity_slider.setValue(item.intensity if hasattr(item, 'intensity') else 100)
        intensity_label = QLabel(f"{intensity_slider.value()}%")
        
        # Update label when slider changes
        def update_intensity_label(value):
            intensity_label.setText(f"{value}%")
            if not self._updating:
                self.on_property_changed("intensity", value)
        
        intensity_slider.valueChanged.connect(update_intensity_label)
        self.property_widgets["intensity"] = intensity_slider
        
        # Layout for slider and label
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(intensity_slider)
        intensity_layout.addWidget(intensity_label)
        
        self.specific_form.addRow("Intensity:", intensity_layout)
        
        # Beam angle
        if hasattr(item, 'beam_angle'):
            beam_spin = QSpinBox()
            beam_spin.setRange(1, 180)
            beam_spin.setSuffix("°")
            beam_spin.setValue(item.beam_angle)
            beam_spin.valueChanged.connect(
                lambda value: self.on_property_changed("beam_angle", value)
            )
            self.property_widgets["beam_angle"] = beam_spin
            self.specific_form.addRow("Beam Angle:", beam_spin)
        
        # Color temperature
        if hasattr(item, 'color_temperature'):
            temp_spin = QSpinBox()
            temp_spin.setRange(1000, 10000)
            temp_spin.setSuffix(" K")
            temp_spin.setSingleStep(100)
            temp_spin.setValue(item.color_temperature)
            temp_spin.valueChanged.connect(
                lambda value: self.on_property_changed("color_temperature", value)
            )
            self.property_widgets["color_temperature"] = temp_spin
            self.specific_form.addRow("Color Temp:", temp_spin)
        
        # Color
        if hasattr(item, 'color'):
            color_button = ColorButton(item.color)
            color_button.color_selected.connect(
                lambda color: self.on_property_changed("color", color)
            )
            self.property_widgets["color"] = color_button
            self.specific_form.addRow("Color:", color_button)
        
        # Fixture type
        if hasattr(item, 'fixture_type'):
            fixture_combo = QComboBox()
            fixture_combo.addItems(["spotlight", "floodlight", "practical"])
            fixture_combo.setCurrentText(item.fixture_type)
            fixture_combo.currentTextChanged.connect(
                lambda text: self.on_property_changed("fixture_type", text)
            )
            self.property_widgets["fixture_type"] = fixture_combo
            self.specific_form.addRow("Fixture Type:", fixture_combo)
    
    def setup_camera_properties(self, item):
        """
        Set up properties for a camera item.
        
        Args:
            item: Camera instance
        """
        # Camera type
        if hasattr(item, 'camera_type'):
            type_combo = QComboBox()
            type_combo.addItems(["Main", "Secondary", "POV", "VFX"])
            type_combo.setCurrentText(item.camera_type)
            type_combo.currentTextChanged.connect(
                lambda text: self.on_property_changed("camera_type", text)
            )
            self.property_widgets["camera_type"] = type_combo
            self.specific_form.addRow("Type:", type_combo)
        
        # Lens focal length
        if hasattr(item, 'lens_mm'):
            lens_spin = QSpinBox()
            lens_spin.setRange(8, 300)
            lens_spin.setSuffix(" mm")
            lens_spin.setValue(item.lens_mm)
            lens_spin.valueChanged.connect(
                lambda value: self.on_property_changed("lens_mm", value)
            )
            self.property_widgets["lens_mm"] = lens_spin
            self.specific_form.addRow("Focal Length:", lens_spin)
        
        # Height
        if hasattr(item, 'height'):
            height_spin = QDoubleSpinBox()
            height_spin.setRange(0, 300)
            height_spin.setSuffix(" cm")
            height_spin.setValue(item.height)
            height_spin.valueChanged.connect(
                lambda value: self.on_property_changed("height", value)
            )
            self.property_widgets["height"] = height_spin
            self.specific_form.addRow("Height:", height_spin)
        
        # Shot type
        if hasattr(item, 'shot_type'):
            shot_combo = QComboBox()
            shot_combo.addItems(["Wide", "Medium", "Close-up", "Insert", "POV"])
            shot_combo.setCurrentText(item.shot_type)
            shot_combo.currentTextChanged.connect(
                lambda text: self.on_property_changed("shot_type", text)
            )
            self.property_widgets["shot_type"] = shot_combo
            self.specific_form.addRow("Shot Type:", shot_combo)
        
        """
Properties Panel for the LightCraft application.
Displays and allows editing of properties for selected items.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, 
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
    QComboBox, QColorDialog, QPushButton, QHBoxLayout,
    QSizePolicy, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QColor, QFont


class PropertiesPanel(QScrollArea):
    """
    Properties panel widget for viewing and editing item properties.
    Displayed on the right side of the main window.
    """
    
    # Signal emitted when a property value is changed
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        """
        Initialize the properties panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create widget to hold properties
        self.properties_widget = QWidget()
        self.setWidget(self.properties_widget)
        
        # Create layout
        self.layout = QVBoxLayout(self.properties_widget)
        self.layout.setContentsMargins(8, 12, 8, 12)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Current selected item (None if no selection)
        self.current_item = None
        
        # Initialize panel
        self.initialize()
    
    def initialize(self):
        """Initialize the properties panel with default content."""
        # Title
        title_label = QLabel("Properties")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("QLabel { margin-bottom: 8px; }")
        self.layout.addWidget(title_label)
        
        # No selection label
        self.no_selection_label = QLabel("No item selected")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setStyleSheet(
            "QLabel { color: #777; margin: 20px; }"
        )
        self.layout.addWidget(self.no_selection_label)
        
        # Property container widget (hidden when no selection)
        self.property_container = QWidget()
        self.property_layout = QVBoxLayout(self.property_container)
        self.property_layout.setContentsMargins(0, 0, 0, 0)
        self.property_layout.setSpacing(8)
        self.layout.addWidget(self.property_container)
        self.property_container.hide()
        
        # Add placeholder property groups
        # These will be populated dynamically based on the selected item
        self.create_common_properties_group()
        self.create_specific_properties_group()
        
        # Add stretcher to push all content to the top
        self.layout.addStretch(1)
    
    def create_common_properties_group(self):
        """Create the group for common properties (position, rotation, etc.)."""
        group = QGroupBox("Common Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # Position X
        self.pos_x = QDoubleSpinBox()
        self.pos_x.setRange(-10000, 10000)
        form_layout.addRow("Position X:", self.pos_x)
        
        # Position Y
        self.pos_y = QDoubleSpinBox()
        self.pos_y.setRange(-10000, 10000)
        form_layout.addRow("Position Y:", self.pos_y)
        
        # Rotation
        self.rotation = QDoubleSpinBox()
        self.rotation.setRange(0, 360)
        form_layout.addRow("Rotation:", self.rotation)
        
        # Name field
        self.name_field = QLineEdit()
        form_layout.addRow("Name:", self.name_field)
        
        group.setLayout(form_layout)
        self.property_layout.addWidget(group)
    
    def create_specific_properties_group(self):
        """
        Create the group for item-specific properties.
        These will change based on the selected item type.
        """
        group = QGroupBox("Specific Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        # This will be populated dynamically when an item is selected
        self.specific_layout = QFormLayout()
        self.specific_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.specific_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # Add placeholder text
        placeholder = QLabel("Select an item to view properties")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("QLabel { color: #777; margin: 10px; }")
        self.specific_layout.addWidget(placeholder)
        
        group.setLayout(self.specific_layout)
        self.property_layout.addWidget(group)
    
    def update_properties(self, item=None):
        """
        Update the panel to display properties for the selected item.
        
        Args:
            item: The selected item or None if no selection
        """
        self.current_item = item
        
        if item is None:
            # No selection
            self.no_selection_label.show()
            self.property_container.hide()
            return
        
        # Show properties container and hide no selection label
        self.no_selection_label.hide()
        self.property_container.show()
        
        # Set common properties (in future prompts, we'll link this to actual item data)
        self.pos_x.setValue(0)
        self.pos_y.setValue(0)
        self.rotation.setValue(0)
        self.name_field.setText("Item")
        
        # Clear and update specific properties 
        # This will be implemented in future prompts when we have the item types defined
        
        # Connect signals for property changes
        # This will be implemented in future prompts
    
    def clear_selection(self):
        """Clear the current selection and reset the panel."""
        self.current_item = None
        self.update_properties(None)
