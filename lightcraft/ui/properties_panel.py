"""
Properties Panel for the LightCraft application.
Displays and allows editing of properties for selected items.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, 
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
    QComboBox, QColorDialog, QPushButton, QHBoxLayout,
    QSizePolicy, QGroupBox, QSlider, QCheckBox, QTabWidget,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QColor, QFont, QPalette, QPixmap

from lightcraft.models.equipment import LightingEquipment, Camera, SetElement


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
        self.setMinimumHeight(20)
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


class LabeledSlider(QWidget):
    """
    Slider with a label showing the current value.
    """
    
    # Signal emitted when value changes
    value_changed = pyqtSignal(int)
    
    def __init__(self, min_value=0, max_value=100, value=50, suffix="", parent=None):
        """
        Initialize the labeled slider.
        
        Args:
            min_value: Minimum value
            max_value: Maximum value
            value: Initial value
            suffix: Suffix to display after the value
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.suffix = suffix
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_value, max_value)
        self.slider.setValue(value)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval((max_value - min_value) // 5)
        self.layout.addWidget(self.slider, 3)
        
        # Create label
        self.label = QLabel(f"{value}{suffix}")
        self.label.setMinimumWidth(40)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.label, 1)
        
        # Connect signals
        self.slider.valueChanged.connect(self.on_slider_value_changed)
    
    def on_slider_value_changed(self, value):
        """
        Handle slider value changes.
        
        Args:
            value: New slider value
        """
        # Update label
        self.label.setText(f"{value}{self.suffix}")
        
        # Emit signal
        self.value_changed.emit(value)
    
    def value(self):
        """
        Get the current slider value.
        
        Returns:
            Current value
        """
        return self.slider.value()
    
    def setValue(self, value):
        """
        Set the slider value.
        
        Args:
            value: New value
        """
        self.slider.setValue(value)


class PropertyEditor(QWidget):
    """Base class for property editors."""
    
    # Signal emitted when property value changes
    value_changed = pyqtSignal(object)
    
    def __init__(self, property_name, parent=None):
        """
        Initialize the property editor.
        
        Args:
            property_name: Name of the property being edited
            parent: Parent widget
        """
        super().__init__(parent)
        self.property_name = property_name
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        pass
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return None


class TextPropertyEditor(PropertyEditor):
    """Editor for text properties."""
    
    def __init__(self, property_name, parent=None):
        """
        Initialize the text property editor.
        
        Args:
            property_name: Name of the property being edited
            parent: Parent widget
        """
        super().__init__(property_name, parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create text field
        self.text_field = QLineEdit()
        self.layout.addWidget(self.text_field)
        
        # Connect signals
        self.text_field.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self, text):
        """
        Handle text changes.
        
        Args:
            text: New text
        """
        self.value_changed.emit(text)
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        if value is not None:
            self.text_field.setText(str(value))
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return self.text_field.text()


class NumericPropertyEditor(PropertyEditor):
    """Editor for numeric properties."""
    
    def __init__(self, property_name, min_value=0, max_value=1000, 
                 decimals=0, step=1, suffix="", parent=None):
        """
        Initialize the numeric property editor.
        
        Args:
            property_name: Name of the property being edited
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            decimals: Number of decimal places
            step: Step size
            suffix: Suffix to display
            parent: Parent widget
        """
        super().__init__(property_name, parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create spin box (int or double based on decimals)
        if decimals > 0:
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setDecimals(decimals)
            self.spin_box.setSingleStep(step)
        else:
            self.spin_box = QSpinBox()
            self.spin_box.setSingleStep(int(step))
        
        self.spin_box.setRange(min_value, max_value)
        if suffix:
            self.spin_box.setSuffix(f" {suffix}")
        
        self.layout.addWidget(self.spin_box)
        
        # Connect signals
        self.spin_box.valueChanged.connect(self.on_value_changed)
    
    def on_value_changed(self, value):
        """
        Handle value changes.
        
        Args:
            value: New value
        """
        self.value_changed.emit(value)
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        if value is not None:
            self.spin_box.setValue(value)
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return self.spin_box.value()


class ColorPropertyEditor(PropertyEditor):
    """Editor for color properties."""
    
    def __init__(self, property_name, parent=None):
        """
        Initialize the color property editor.
        
        Args:
            property_name: Name of the property being edited
            parent: Parent widget
        """
        super().__init__(property_name, parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create color button
        self.color_button = ColorButton()
        self.layout.addWidget(self.color_button)
        
        # Connect signals
        self.color_button.color_selected.connect(self.on_color_selected)
    
    def on_color_selected(self, color):
        """
        Handle color selection.
        
        Args:
            color: New color (hex string)
        """
        self.value_changed.emit(color)
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        if value is not None:
            self.color_button.set_color(value)
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return self.color_button.color.name()


class ChoicePropertyEditor(PropertyEditor):
    """Editor for choice properties (dropdown)."""
    
    def __init__(self, property_name, choices=None, parent=None):
        """
        Initialize the choice property editor.
        
        Args:
            property_name: Name of the property being edited
            choices: List of available choices
            parent: Parent widget
        """
        super().__init__(property_name, parent)
        
        if choices is None:
            choices = []
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create combo box
        self.combo_box = QComboBox()
        self.combo_box.addItems(choices)
        self.layout.addWidget(self.combo_box)
        
        # Connect signals
        self.combo_box.currentTextChanged.connect(self.on_choice_changed)
    
    def on_choice_changed(self, text):
        """
        Handle choice changes.
        
        Args:
            text: New choice
        """
        self.value_changed.emit(text)
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        if value is not None:
            index = self.combo_box.findText(str(value))
            if index >= 0:
                self.combo_box.setCurrentIndex(index)
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return self.combo_box.currentText()


class SliderPropertyEditor(PropertyEditor):
    """Editor for slider properties (percentage, intensity)."""
    
    def __init__(self, property_name, min_value=0, max_value=100, 
                 suffix="%", parent=None):
        """
        Initialize the slider property editor.
        
        Args:
            property_name: Name of the property being edited
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            suffix: Suffix to display
            parent: Parent widget
        """
        super().__init__(property_name, parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create slider
        self.slider = LabeledSlider(min_value, max_value, min_value, suffix)
        self.layout.addWidget(self.slider)
        
        # Connect signals
        self.slider.value_changed.connect(self.on_value_changed)
    
    def on_value_changed(self, value):
        """
        Handle value changes.
        
        Args:
            value: New value
        """
        self.value_changed.emit(value)
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        if value is not None:
            self.slider.setValue(int(value))
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return self.slider.value()


class BooleanPropertyEditor(PropertyEditor):
    """Editor for boolean properties (checkboxes)."""
    
    def __init__(self, property_name, label="", parent=None):
        """
        Initialize the boolean property editor.
        
        Args:
            property_name: Name of the property being edited
            label: Label text
            parent: Parent widget
        """
        super().__init__(property_name, parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create checkbox
        self.checkbox = QCheckBox(label)
        self.layout.addWidget(self.checkbox)
        
        # Connect signals
        self.checkbox.toggled.connect(self.on_toggled)
    
    def on_toggled(self, checked):
        """
        Handle toggle changes.
        
        Args:
            checked: New state
        """
        self.value_changed.emit(checked)
    
    def set_value(self, value):
        """
        Set the editor value.
        
        Args:
            value: Value to set
        """
        if value is not None:
            self.checkbox.setChecked(bool(value))
    
    def get_value(self):
        """
        Get the current editor value.
        
        Returns:
            Current value
        """
        return self.checkbox.isChecked()


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
        
        # Flag to prevent signal feedback loops
        self._updating = False
        
        # Property editors
        self.property_editors = {}
        
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
        
        # Add stretcher to push all content to the top
        self.layout.addStretch(1)
    
    def clear_properties(self):
        """Clear all property editors."""
        # Remove all widgets from the property layout
        while self.property_layout.count():
            item = self.property_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Clear property editors dictionary
        self.property_editors.clear()
    
    def update_properties(self, item=None):
        """
        Update the panel to display properties for the selected item.
        
        Args:
            item: The selected item or None if no selection
        """
        self.current_item = item
        
        # Set updating flag to prevent signal loops
        self._updating = True
        
        # Clear existing properties
        self.clear_properties()
        
        if item is None:
            # No selection
            self.no_selection_label.show()
            self.property_container.hide()
            self._updating = False
            return
        
        # Show properties container and hide no selection label
        self.no_selection_label.hide()
        self.property_container.show()
        
        # Determine item type and set up appropriate property editors
        if isinstance(item, LightingEquipment):
            self.setup_common_properties(item)
            self.setup_light_properties(item)
        elif isinstance(item, Camera):
            self.setup_common_properties(item)
            self.setup_camera_properties(item)
        elif isinstance(item, SetElement):
            self.setup_common_properties(item)
            
            # Different setup based on element type
            if hasattr(item, 'element_type'):
                if item.element_type.lower() in ['wall', 'door', 'window']:
                    self.setup_wall_properties(item)
                elif item.element_type.lower() in ['flag', 'floppy', 'neg', 'scrim', 'cutter', 'diffusion']:
                    self.setup_modifier_properties(item)
                else:
                    self.setup_set_element_properties(item)
            else:
                self.setup_set_element_properties(item)
        
        # Reset updating flag
        self._updating = False
    
    def setup_common_properties(self, item):
        """
        Set up common property editors for all items.
        
        Args:
            item: Item to edit
        """
        # Create common properties group
        group = QGroupBox("Common Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Name
        name_editor = TextPropertyEditor("name")
        name_editor.set_value(item.name if hasattr(item, 'name') else "")
        name_editor.value_changed.connect(self.on_property_changed)
        form.addRow("Name:", name_editor)
        self.property_editors["name"] = name_editor
        
        # Position X
        pos_x_editor = NumericPropertyEditor("x", -10000, 10000, 1, 1)
        pos_x_editor.set_value(item.x if hasattr(item, 'x') else 0)
        pos_x_editor.value_changed.connect(self.on_property_changed)
        form.addRow("Position X:", pos_x_editor)
        self.property_editors["x"] = pos_x_editor
        
        # Position Y
        pos_y_editor = NumericPropertyEditor("y", -10000, 10000, 1, 1)
        pos_y_editor.set_value(item.y if hasattr(item, 'y') else 0)
        pos_y_editor.value_changed.connect(self.on_property_changed)
        form.addRow("Position Y:", pos_y_editor)
        self.property_editors["y"] = pos_y_editor
        
        # Rotation
        rotation_editor = NumericPropertyEditor("rotation", 0, 360, 1, 1, "°")
        rotation_editor.set_value(item.rotation if hasattr(item, 'rotation') else 0)
        rotation_editor.value_changed.connect(self.on_property_changed)
        form.addRow("Rotation:", rotation_editor)
        self.property_editors["rotation"] = rotation_editor
        
        # Visibility
        visible_editor = BooleanPropertyEditor("visible", "Visible")
        visible_editor.set_value(item.visible if hasattr(item, 'visible') else True)
        visible_editor.value_changed.connect(self.on_property_changed)
        form.addRow("", visible_editor)
        self.property_editors["visible"] = visible_editor
        
        group.setLayout(form)
        self.property_layout.addWidget(group)
    
    def setup_light_properties(self, item):
        """
        Set up property editors for light items.
        
        Args:
            item: Light item to edit
        """
        # Create light properties group
        group = QGroupBox("Light Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Equipment type
        if hasattr(item, 'equipment_type'):
            type_editor = ChoicePropertyEditor("equipment_type", 
                                             ["Fresnel", "HMI", "LED Panel", "Practical", "China Ball"])
            type_editor.set_value(item.equipment_type)
            type_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Type:", type_editor)
            self.property_editors["equipment_type"] = type_editor
        
        # Power
        if hasattr(item, 'power'):
            power_editor = NumericPropertyEditor("power", 0, 20000, 0, 10, "W")
            power_editor.set_value(item.power)
            power_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Power:", power_editor)
            self.property_editors["power"] = power_editor
        
        # Intensity
        intensity_editor = SliderPropertyEditor("intensity", 0, 100, "%")
        intensity_editor.set_value(item.intensity if hasattr(item, 'intensity') else 100)
        intensity_editor.value_changed.connect(self.on_property_changed)
        form.addRow("Intensity:", intensity_editor)
        self.property_editors["intensity"] = intensity_editor
        
        # Beam angle
        if hasattr(item, 'beam_angle'):
            angle_editor = NumericPropertyEditor("beam_angle", 1, 180, 0, 1, "°")
            angle_editor.set_value(item.beam_angle)
            angle_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Beam Angle:", angle_editor)
            self.property_editors["beam_angle"] = angle_editor
        
        # Color temperature
        if hasattr(item, 'color_temperature'):
            temp_editor = NumericPropertyEditor("color_temperature", 1000, 10000, 0, 100, "K")
            temp_editor.set_value(item.color_temperature)
            temp_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Color Temp:", temp_editor)
            self.property_editors["color_temperature"] = temp_editor
        
        # Color
        if hasattr(item, 'color'):
            color_editor = ColorPropertyEditor("color")
            color_editor.set_value(item.color)
            color_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Color:", color_editor)
            self.property_editors["color"] = color_editor
        
        # Fixture type
        if hasattr(item, 'fixture_type'):
            fixture_editor = ChoicePropertyEditor("fixture_type", 
                                               ["spotlight", "floodlight", "practical"])
            fixture_editor.set_value(item.fixture_type)
            fixture_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Fixture Type:", fixture_editor)
            self.property_editors["fixture_type"] = fixture_editor
        
        group.setLayout(form)
        self.property_layout.addWidget(group)
    
    def setup_camera_properties(self, item):
        """
        Set up property editors for camera items.
        
        Args:
            item: Camera item to edit
        """
        # Create camera properties group
        group = QGroupBox("Camera Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Camera type
        if hasattr(item, 'camera_type'):
            type_editor = ChoicePropertyEditor("camera_type", 
                                             ["Main", "Secondary", "POV", "VFX"])
            type_editor.set_value(item.camera_type)
            type_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Camera Type:", type_editor)
            self.property_editors["camera_type"] = type_editor
        
        # Lens focal length
        if hasattr(item, 'lens_mm'):
            lens_editor = NumericPropertyEditor("lens_mm", 8, 300, 0, 1, "mm")
            lens_editor.set_value(item.lens_mm)
            lens_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Focal Length:", lens_editor)
            self.property_editors["lens_mm"] = lens_editor
        
        # Height
        if hasattr(item, 'height'):
            height_editor = NumericPropertyEditor("height", 0, 300, 1, 5, "cm")
            height_editor.set_value(item.height)
            height_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Height:", height_editor)
            self.property_editors["height"] = height_editor
        
        # Shot type
        if hasattr(item, 'shot_type'):
            shot_editor = ChoicePropertyEditor("shot_type", 
                                            ["Wide", "Medium", "Close-up", "Insert", "POV"])
            shot_editor.set_value(item.shot_type)
            shot_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Shot Type:", shot_editor)
            self.property_editors["shot_type"] = shot_editor
        
        group.setLayout(form)
        self.property_layout.addWidget(group)
    
    def setup_wall_properties(self, item):
        """
        Set up property editors for wall items.
        
        Args:
            item: Wall item to edit
        """
        # Create wall properties group
        group = QGroupBox("Wall Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Wall type 
        if hasattr(item, 'element_type'):
            type_editor = ChoicePropertyEditor("element_type", 
                                             ["Wall", "Door", "Window"])
            type_editor.set_value(item.element_type)
            type_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Type:", type_editor)
            self.property_editors["element_type"] = type_editor
        
        # Width
        if hasattr(item, 'width'):
            width_editor = NumericPropertyEditor("width", 10, 1000, 1, 10, "cm")
            width_editor.set_value(item.width)
            width_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Width:", width_editor)
            self.property_editors["width"] = width_editor
        
        # Thickness
        if hasattr(item, 'thickness'):
            thickness_editor = NumericPropertyEditor("thickness", 1, 100, 1, 1, "cm")
            thickness_editor.set_value(item.thickness)
            thickness_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Thickness:", thickness_editor)
            self.property_editors["thickness"] = thickness_editor
        
        # Color
        if hasattr(item, 'color'):
            color_editor = ColorPropertyEditor("color")
            color_editor.set_value(item.color)
            color_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Color:", color_editor)
            self.property_editors["color"] = color_editor
        
        # Material
        if hasattr(item, 'material'):
            material_editor = ChoicePropertyEditor("material", 
                                                ["Wood", "Concrete", "Brick", "Glass", "Fabric"])
            material_editor.set_value(item.material)
            material_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Material:", material_editor)
            self.property_editors["material"] = material_editor
        
        group.setLayout(form)
        self.property_layout.addWidget(group)
    
    def setup_modifier_properties(self, item):
        """
        Set up property editors for light modifier items.
        
        Args:
            item: Modifier item to edit
        """
        # Create modifier properties group
        group = QGroupBox("Modifier Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Modifier type
        if hasattr(item, 'element_type'):
            type_editor = ChoicePropertyEditor("element_type", 
                                             ["Flag", "Floppy", "Scrim", "Diffusion", "Cutter", "Neg"])
            type_editor.set_value(item.element_type)
            type_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Type:", type_editor)
            self.property_editors["element_type"] = type_editor
        
        # Width
        if hasattr(item, 'width'):
            width_editor = NumericPropertyEditor("width", 10, 1000, 1, 10, "cm")
            width_editor.set_value(item.width)
            width_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Width:", width_editor)
            self.property_editors["width"] = width_editor
        
        # Height
        if hasattr(item, 'height'):
            height_editor = NumericPropertyEditor("height", 10, 1000, 1, 10, "cm")
            height_editor.set_value(item.height)
            height_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Height:", height_editor)
            self.property_editors["height"] = height_editor
        
        # Material
        if hasattr(item, 'material'):
            material_editor = ChoicePropertyEditor("material", 
                                                ["Fabric", "Metal", "Paper", "Silk"])
            material_editor.set_value(item.material if item.material else "Fabric")
            material_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Material:", material_editor)
            self.property_editors["material"] = material_editor
        
        group.setLayout(form)
        self.property_layout.addWidget(group)
    
    def setup_set_element_properties(self, item):
        """
        Set up property editors for generic set elements.
        
        Args:
            item: Set element to edit
        """
        # Create set element properties group
        group = QGroupBox("Set Element Properties")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Element type
        if hasattr(item, 'element_type'):
            type_editor = ChoicePropertyEditor("element_type", 
                                             ["Wall", "Door", "Window", "Furniture", "Prop"])
            type_editor.set_value(item.element_type)
            type_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Type:", type_editor)
            self.property_editors["element_type"] = type_editor
        
        # Width
        if hasattr(item, 'width'):
            width_editor = NumericPropertyEditor("width", 10, 1000, 1, 10, "cm")
            width_editor.set_value(item.width)
            width_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Width:", width_editor)
            self.property_editors["width"] = width_editor
        
        # Height 
        if hasattr(item, 'height'):
            height_editor = NumericPropertyEditor("height", 10, 1000, 1, 10, "cm")
            height_editor.set_value(item.height)
            height_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Height:", height_editor)
            self.property_editors["height"] = height_editor
        
        # Color
        if hasattr(item, 'color'):
            color_editor = ColorPropertyEditor("color")
            color_editor.set_value(item.color if item.color else "#AAAAAA")
            color_editor.value_changed.connect(self.on_property_changed)
            form.addRow("Color:", color_editor)
            self.property_editors["color"] = color_editor
        
        group.setLayout(form)
        self.property_layout.addWidget(group)
    
    def on_property_changed(self, value):
        """
        Handle property value changes.
        
        Args:
            value: New property value
        """
        # If we're updating the UI, don't emit signals
        if self._updating:
            return
        
        # Get the sender and its property name
        sender = self.sender()
        if not isinstance(sender, PropertyEditor):
            return
            
        property_name = sender.property_name
        
        # Emit signal with property name and value
        self.property_changed.emit(property_name, value)
