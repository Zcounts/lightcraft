"""
Equipment library panel for the LightCraft application.
Provides a UI for browsing and selecting equipment.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QSplitter, QMenu, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QSpinBox, QDoubleSpinBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QDrag, QCursor, QColor

import os
from lightcraft.models.equipment_data import (
    CATEGORIES, EQUIPMENT_LIBRARY, 
    get_equipment_by_id, get_equipment_by_category, 
    search_equipment, get_equipment_icon_path
)


class EquipmentItem(QListWidgetItem):
    """
    Custom list widget item for equipment display.
    """
    
    def __init__(self, equipment_id, equipment_data, parent=None):
        """
        Initialize the equipment item.
        
        Args:
            equipment_id: ID of the equipment
            equipment_data: Equipment data dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        self.equipment_id = equipment_id
        self.equipment_data = equipment_data
        
        # Set item text and icon
        self.setText(equipment_data["name"])
        
        # Load icon if available
        icon_path = get_equipment_icon_path(equipment_id)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        
        # Set tooltip with description
        if "description" in equipment_data:
            self.setToolTip(equipment_data["description"])
        
        # Set size hint for item
        self.setSizeHint(QSize(120, 80))


class EquipmentLibraryPanel(QWidget):
    """
    Equipment library panel for browsing and selecting equipment.
    """
    
    # Signal emitted when equipment is selected
    equipment_selected = pyqtSignal(str, dict)
    
    # Signal emitted when equipment is drag-dropped onto canvas
    equipment_dropped = pyqtSignal(str, dict, object)  # equipment_id, data, position
    
    def __init__(self, parent=None):
        """
        Initialize the equipment library panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        
        # Header with search
        self.setup_header()
        
        # Splitter for category tree and equipment list
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter, 1)
        
        # Left side: Category tree
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.setMinimumWidth(150)
        self.category_tree.setMaximumWidth(250)
        self.splitter.addWidget(self.category_tree)
        
        # Right side: Equipment list
        self.equipment_list = QListWidget()
        self.equipment_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.equipment_list.setIconSize(QSize(48, 48))
        self.equipment_list.setGridSize(QSize(100, 90))
        self.equipment_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.equipment_list.setMovement(QListWidget.Movement.Static)
        self.equipment_list.setDragEnabled(True)
        self.splitter.addWidget(self.equipment_list)
        
        # Bottom section: Favorite/Recent items
        self.setup_favorites()
        
        # Initialize all components
        self.initialize()
        
        # Set up connections
        self.setup_connections()
        
        # User's favorite equipment (equipment_id list)
        self.favorites = []
        
        # Recent equipment (equipment_id list)
        self.recent_equipment = []
    
    def setup_header(self):
        """Set up the header with search controls."""
        header_layout = QHBoxLayout()
        
        # Search box
        self.search_label = QLabel("Search:")
        header_layout.addWidget(self.search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter search term...")
        header_layout.addWidget(self.search_box, 1)
        
        # Add to main layout
        self.layout.addLayout(header_layout)
    
    def setup_favorites(self):
        """Set up the favorites/recent items section."""
        # Tabs for Favorites and Recent
        self.favorites_tabs = QTabWidget()
        self.favorites_tabs.setMaximumHeight(120)
        
        # Favorites tab
        self.favorites_list = QListWidget()
        self.favorites_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.favorites_list.setIconSize(QSize(32, 32))
        self.favorites_list.setGridSize(QSize(80, 70))
        self.favorites_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.favorites_list.setMovement(QListWidget.Movement.Static)
        self.favorites_list.setDragEnabled(True)
        self.favorites_tabs.addTab(self.favorites_list, "Favorites")
        
        # Recent tab
        self.recent_list = QListWidget()
        self.recent_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.recent_list.setIconSize(QSize(32, 32))
        self.recent_list.setGridSize(QSize(80, 70))
        self.recent_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.recent_list.setMovement(QListWidget.Movement.Static)
        self.recent_list.setDragEnabled(True)
        self.favorites_tabs.addTab(self.recent_list, "Recent")
        
        # Add to main layout
        self.layout.addWidget(self.favorites_tabs)
    
    def initialize(self):
        """Initialize the equipment library panel."""
        # Populate category tree
        self.populate_category_tree()
        
        # Populate equipment list with first category
        self.populate_equipment_list("lights")
    
    def setup_connections(self):
        """Set up signal connections."""
        # Connect search box
        self.search_box.textChanged.connect(self.on_search)
        
        # Connect category tree selection
        self.category_tree.itemClicked.connect(self.on_category_selected)
        
        # Connect equipment list selection
        self.equipment_list.itemClicked.connect(self.on_equipment_selected)
        self.equipment_list.itemDoubleClicked.connect(self.on_equipment_double_clicked)
        
        # Connect favorites and recent lists
        self.favorites_list.itemClicked.connect(self.on_favorite_selected)
        self.recent_list.itemClicked.connect(self.on_recent_selected)
        
        # Context menu for equipment list
        self.equipment_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.equipment_list.customContextMenuRequested.connect(self.show_equipment_context_menu)
        
        # Context menu for favorites list
        self.favorites_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.favorites_list.customContextMenuRequested.connect(self.show_favorites_context_menu)
    
    def populate_category_tree(self):
        """Populate the category tree with all categories and subcategories."""
        self.category_tree.clear()
        
        # Create "All Equipment" root item
        all_item = QTreeWidgetItem(["All Equipment"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, "all")
        self.category_tree.addTopLevelItem(all_item)
        
        # Add main categories
        for category_id, category_data in CATEGORIES.items():
            category_item = QTreeWidgetItem([category_data["name"]])
            category_item.setData(0, Qt.ItemDataRole.UserRole, category_id)
            self.category_tree.addTopLevelItem(category_item)
            
            # Add subcategories
            if "subcategories" in category_data:
                for subcategory_id, subcategory_data in category_data["subcategories"].items():
                    subcategory_item = QTreeWidgetItem([subcategory_data["name"]])
                    subcategory_item.setData(0, Qt.ItemDataRole.UserRole, category_id + "/" + subcategory_id)
                    category_item.addChild(subcategory_item)
            
            # Expand main categories
            category_item.setExpanded(True)
        
        # Add "Custom Equipment" item
        custom_item = QTreeWidgetItem(["Custom Equipment"])
        custom_item.setData(0, Qt.ItemDataRole.UserRole, "custom")
        self.category_tree.addTopLevelItem(custom_item)
        
        # Select first item
        self.category_tree.setCurrentItem(all_item)
    
    def populate_equipment_list(self, category_id, subcategory_id=None):
        """
        Populate the equipment list with items from the specified category.
        
        Args:
            category_id: Category ID to display
            subcategory_id: Optional subcategory ID to filter by
        """
        self.equipment_list.clear()
        
        if category_id == "all":
            # Show all equipment
            for equip_id, equip_data in EQUIPMENT_LIBRARY.items():
                self.add_equipment_to_list(equip_id, equip_data)
        elif category_id == "custom":
            # Show custom equipment (not implemented yet)
            pass
        else:
            # Show category-specific equipment
            if subcategory_id:
                # Filter by subcategory
                for equip_id, equip_data in EQUIPMENT_LIBRARY.items():
                    if equip_data["category"] == category_id and equip_data["subcategory"] == subcategory_id:
                        self.add_equipment_to_list(equip_id, equip_data)
            else:
                # Show all in category
                for equip_id, equip_data in EQUIPMENT_LIBRARY.items():
                    if equip_data["category"] == category_id:
                        self.add_equipment_to_list(equip_id, equip_data)
    
    def add_equipment_to_list(self, equipment_id, equipment_data):
        """
        Add equipment to the equipment list.
        
        Args:
            equipment_id: ID of the equipment
            equipment_data: Equipment data dictionary
        """
        item = EquipmentItem(equipment_id, equipment_data)
        self.equipment_list.addItem(item)
    
    def update_favorites_list(self):
        """Update the favorites list with current favorites."""
        self.favorites_list.clear()
        
        for equipment_id in self.favorites:
            equipment_data = get_equipment_by_id(equipment_id)
            if equipment_data:
                item = EquipmentItem(equipment_id, equipment_data)
                self.favorites_list.addItem(item)
    
    def update_recent_list(self):
        """Update the recent equipment list."""
        self.recent_list.clear()
        
        for equipment_id in self.recent_equipment:
            equipment_data = get_equipment_by_id(equipment_id)
            if equipment_data:
                item = EquipmentItem(equipment_id, equipment_data)
                self.recent_list.addItem(item)
    
    def add_to_favorites(self, equipment_id):
        """
        Add equipment to favorites.
        
        Args:
            equipment_id: ID of the equipment to add
        """
        if equipment_id not in self.favorites:
            self.favorites.append(equipment_id)
            self.update_favorites_list()
    
    def remove_from_favorites(self, equipment_id):
        """
        Remove equipment from favorites.
        
        Args:
            equipment_id: ID of the equipment to remove
        """
        if equipment_id in self.favorites:
            self.favorites.remove(equipment_id)
            self.update_favorites_list()
    
    def add_to_recent(self, equipment_id):
        """
        Add equipment to recent list.
        
        Args:
            equipment_id: ID of the equipment to add
        """
        # Remove if already in list (to move to front)
        if equipment_id in self.recent_equipment:
            self.recent_equipment.remove(equipment_id)
        
        # Add to front of list
        self.recent_equipment.insert(0, equipment_id)
        
        # Limit size of recent list
        if len(self.recent_equipment) > 10:
            self.recent_equipment = self.recent_equipment[:10]
        
        # Update display
        self.update_recent_list()
    
    def on_search(self, text):
        """
        Handle search box text changes.
        
        Args:
            text: Current search text
        """
        if not text:
            # If search is empty, show current category
            category_item = self.category_tree.currentItem()
            if category_item:
                category_id = category_item.data(0, Qt.ItemDataRole.UserRole)
                if "/" in category_id:
                    parts = category_id.split("/")
                    self.populate_equipment_list(parts[0], parts[1])
                else:
                    self.populate_equipment_list(category_id)
        else:
            # Search for equipment
            self.equipment_list.clear()
            results = search_equipment(text)
            
            for item in results:
                self.add_equipment_to_list(
                    [eq_id for eq_id, eq_data in EQUIPMENT_LIBRARY.items() if eq_data == item][0], 
                    item
                )
    
    def on_category_selected(self, item, column):
        """
        Handle category tree item selection.
        
        Args:
            item: Selected tree item
            column: Selected column
        """
        category_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        if "/" in category_id:
            # Subcategory selected
            parts = category_id.split("/")
            self.populate_equipment_list(parts[0], parts[1])
        else:
            # Main category selected
            self.populate_equipment_list(category_id)
    
    def on_equipment_selected(self, item):
        """
        Handle equipment item selection.
        
        Args:
            item: Selected equipment item
        """
        if isinstance(item, EquipmentItem):
            # Emit signal with equipment data
            self.equipment_selected.emit(item.equipment_id, item.equipment_data)
            
            # Add to recent list
            self.add_to_recent(item.equipment_id)
    
    def on_equipment_double_clicked(self, item):
        """
        Handle equipment item double click.
        
        Args:
            item: Double-clicked equipment item
        """
        if isinstance(item, EquipmentItem):
            # Emit signal for adding to canvas (will be handled by controller)
            self.equipment_selected.emit(item.equipment_id, item.equipment_data)
            
            # Add to recent list
            self.add_to_recent(item.equipment_id)
    
    def on_favorite_selected(self, item):
        """
        Handle favorite item selection.
        
        Args:
            item: Selected favorite item
        """
        if isinstance(item, EquipmentItem):
            # Emit signal with equipment data
            self.equipment_selected.emit(item.equipment_id, item.equipment_data)
            
            # Add to recent list
            self.add_to_recent(item.equipment_id)
    
    def on_recent_selected(self, item):
        """
        Handle recent item selection.
        
        Args:
            item: Selected recent item
        """
        if isinstance(item, EquipmentItem):
            # Emit signal with equipment data
            self.equipment_selected.emit(item.equipment_id, item.equipment_data)
    
    def show_equipment_context_menu(self, position):
        """
        Show context menu for equipment list.
        
        Args:
            position: Position of the right-click
        """
        item = self.equipment_list.itemAt(position)
        if not item or not isinstance(item, EquipmentItem):
            return
        
        menu = QMenu(self)
        
        # Add to canvas action
        add_action = menu.addAction("Add to Canvas")
        add_action.triggered.connect(lambda: self.on_equipment_double_clicked(item))
        
        # Add to favorites action
        if item.equipment_id in self.favorites:
            fav_action = menu.addAction("Remove from Favorites")
            fav_action.triggered.connect(lambda: self.remove_from_favorites(item.equipment_id))
        else:
            fav_action = menu.addAction("Add to Favorites")
            fav_action.triggered.connect(lambda: self.add_to_favorites(item.equipment_id))
        
        # Show properties action
        prop_action = menu.addAction("Show Properties")
        prop_action.triggered.connect(lambda: self.show_equipment_properties(item.equipment_id, item.equipment_data))
        
        # Execute menu
        menu.exec(self.equipment_list.mapToGlobal(position))
    
    def show_favorites_context_menu(self, position):
        """
        Show context menu for favorites list.
        
        Args:
            position: Position of the right-click
        """
        item = self.favorites_list.itemAt(position)
        if not item or not isinstance(item, EquipmentItem):
            return
        
        menu = QMenu(self)
        
        # Add to canvas action
        add_action = menu.addAction("Add to Canvas")
        add_action.triggered.connect(lambda: self.on_favorite_selected(item))
        
        # Remove from favorites action
        remove_action = menu.addAction("Remove from Favorites")
        remove_action.triggered.connect(lambda: self.remove_from_favorites(item.equipment_id))
        
        # Show properties action
        prop_action = menu.addAction("Show Properties")
        prop_action.triggered.connect(lambda: self.show_equipment_properties(item.equipment_id, item.equipment_data))
        
        # Execute menu
        menu.exec(self.favorites_list.mapToGlobal(position))
    
    def show_equipment_properties(self, equipment_id, equipment_data):
        """
        Show details dialog for equipment.
        
        Args:
            equipment_id: ID of the equipment
            equipment_data: Equipment data dictionary
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Equipment Details: {equipment_data['name']}")
        dialog.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Equipment name and icon
        header_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel()
        icon_path = get_equipment_icon_path(equipment_id)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(pixmap)
        header_layout.addWidget(icon_label)
        
        # Name and category
        info_layout = QVBoxLayout()
        name_label = QLabel(f"<b>{equipment_data['name']}</b>")
        category_name = CATEGORIES[equipment_data['category']]['name']
        subcategory_name = CATEGORIES[equipment_data['category']]['subcategories'][equipment_data['subcategory']]['name']
        category_label = QLabel(f"{category_name} - {subcategory_name}")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(category_label)
        header_layout.addLayout(info_layout, 1)
        
        layout.addLayout(header_layout)
        
        # Description
        if "description" in equipment_data:
            desc_label = QLabel(equipment_data["description"])
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Properties
        if "properties" in equipment_data:
            props_form = QFormLayout()
            
            for prop_name, prop_value in equipment_data["properties"].items():
                # Skip internal properties (those starting with _)
                if prop_name.startswith("_"):
                    continue
                
                # Format property name
                display_name = prop_name.replace("_", " ").title()
                
                # Format property value based on type
                if isinstance(prop_value, (int, float)):
                    # Add units for known properties
                    if "angle" in prop_name:
                        value_str = f"{prop_value}°"
                    elif "temperature" in prop_name:
                        value_str = f"{prop_value}K"
                    elif "power" in prop_name:
                        value_str = f"{prop_value}W"
                    elif "height" in prop_name or "width" in prop_name or "depth" in prop_name:
                        value_str = f"{prop_value} cm"
                    elif "weight" in prop_name:
                        value_str = f"{prop_value} kg"
                    else:
                        value_str = str(prop_value)
                elif isinstance(prop_value, bool):
                    value_str = "Yes" if prop_value else "No"
                elif isinstance(prop_value, (list, tuple)) and len(prop_value) == 3:
                    # Assume it's a size tuple (width, height, depth)
                    value_str = f"W: {prop_value[0]} cm, H: {prop_value[1]} cm, D: {prop_value[2]} cm"
                else:
                    value_str = str(prop_value)
                
                props_form.addRow(f"{display_name}:", QLabel(value_str))
            
            layout.addLayout(props_form)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog
        dialog.exec()
    
    def create_custom_equipment(self):
        """Show dialog for creating custom equipment."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Custom Equipment")
        dialog.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Form layout for properties
        form = QFormLayout()
        
        # Basic properties
        name_edit = QLineEdit()
        form.addRow("Name:", name_edit)
        
        category_combo = QComboBox()
        for category_id, category_data in CATEGORIES.items():
            category_combo.addItem(category_data["name"], category_id)
        form.addRow("Category:", category_combo)
        
        subcategory_combo = QComboBox()
        # Will be populated when category is selected
        form.addRow("Subcategory:", subcategory_combo)
        
        description_edit = QLineEdit()
        form.addRow("Description:", description_edit)
        
        # Connect category selection to update subcategories
        def update_subcategories(index):
            subcategory_combo.clear()
            category_id = category_combo.currentData()
            if category_id in CATEGORIES and "subcategories" in CATEGORIES[category_id]:
                for subcat_id, subcat_data in CATEGORIES[category_id]["subcategories"].items():
                    subcategory_combo.addItem(subcat_data["name"], subcat_id)
        
        category_combo.currentIndexChanged.connect(update_subcategories)
        # Initialize subcategories for first category
        update_subcategories(0)
        
        # Physical properties
        power_spin = QSpinBox()
        power_spin.setRange(0, 50000)
        power_spin.setSuffix(" W")
        form.addRow("Power:", power_spin)
        
        beam_angle_spin = QSpinBox()
        beam_angle_spin.setRange(1, 360)
        beam_angle_spin.setSuffix("°")
        form.addRow("Beam Angle:", beam_angle_spin)
        
        color_temp_spin = QSpinBox()
        color_temp_spin.setRange(1000, 10000)
        color_temp_spin.setSuffix(" K")
        color_temp_spin.setSingleStep(100)
        color_temp_spin.setValue(5600)
        form.addRow("Color Temperature:", color_temp_spin)
        
        # Color button
        color_button = QPushButton("Select Color")
        self.custom_color = QColor("#FFFFFF")
        
        def choose_color():
            color = QColorDialog.getColor(self.custom_color, dialog, "Select Equipment Color")
            if color.isValid():
                self.custom_color = color
                color_button.setStyleSheet(f"background-color: {color.name()};")
        
        color_button.clicked.connect(choose_color)
        form.addRow("Color:", color_button)
        
        # Add form to layout
        layout.addLayout(form)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Create custom equipment
            equipment_id = f"custom_{name_edit.text().lower().replace(' ', '_')}"
            category_id = category_combo.currentData()
            subcategory_id = subcategory_combo.currentData()
            
            equipment_data = {
                "name": name_edit.text(),
                "category": category_id,
                "subcategory": subcategory_id,
                "description": description_edit.text(),
                "properties": {
                    "power": power_spin.value(),
                    "beam_angle": beam_angle_spin.value(),
                    "color_temperature": color_temp_spin.value(),
                    "color": self.custom_color.name(),
                    "equipment_type": "Custom"
                },
                "icon": "custom_equipment.png",
                "custom": True
            }
            
            # Add to equipment library
            # In a real implementation, this would store the custom equipment in user settings
            EQUIPMENT_LIBRARY[equipment_id] = equipment_data
            
            # Refresh the display
            category_item = self.category_tree.currentItem()
            if category_item:
                category_id = category_item.data(0, Qt.ItemDataRole.UserRole)
                if "/" in category_id:
                    parts = category_id.split("/")
                    self.populate_equipment_list(parts[0], parts[1])
                else:
                    self.populate_equipment_list(category_id)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: QMouseEvent instance
        """
        super().mousePressEvent(event)
        
        # Get item under mouse cursor for drag operation
        if event.button() == Qt.MouseButton.LeftButton:
            if self.equipment_list.underMouse():
                item = self.equipment_list.itemAt(self.equipment_list.mapFromGlobal(QCursor.pos()))
                if item and isinstance(item, EquipmentItem):
                    self.start_drag(item)
            elif self.favorites_list.underMouse():
                item = self.favorites_list.itemAt(self.favorites_list.mapFromGlobal(QCursor.pos()))
                if item and isinstance(item, EquipmentItem):
                    self.start_drag(item)
            elif self.recent_list.underMouse():
                item = self.recent_list.itemAt(self.recent_list.mapFromGlobal(QCursor.pos()))
                if item and isinstance(item, EquipmentItem):
                    self.start_drag(item)
    
    def start_drag(self, item):
        """
        Start drag operation for an equipment item.
        
        Args:
            item: EquipmentItem to drag
        """
        # Create drag object
        drag = QDrag(self)
        
        # Create mime data with equipment info
        mime_data = QMimeData()
        mime_data.setData("application/x-equipment", item.equipment_id.encode())
        drag.setMimeData(mime_data)
        
        # Set drag icon
        icon_path = get_equipment_icon_path(item.equipment_id)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        # Execute drag
        result = drag.exec(Qt.DropAction.CopyAction)
        
        # Emit signal for equipment dropped
        if result == Qt.DropAction.CopyAction:
            self.equipment_dropped.emit(
                item.equipment_id, 
                item.equipment_data, 
                QCursor.pos()
            )
            
            # Add to recent
            self.add_to_recent(item.equipment_id)
