"""
Project Navigator for the LightCraft application.
Provides a panel for managing the project structure.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLabel, 
    QPushButton, QFrame, QMenu, QStyledItemDelegate,
    QHeaderView, QSplitter, QListWidget, QListWidgetItem,
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QMessageBox, QInputDialog, QToolButton, QSizePolicy,
    QScrollArea, QGroupBox, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QModelIndex, pyqtSignal, QSize, QVariant,
    QSortFilterProxyModel, QTimer, QMimeData, QPoint
)
from PyQt6.QtGui import (
    QStandardItemModel, QStandardItem, QIcon, QFont, QAction,
    QPixmap, QDrag, QCursor
)

import os
from datetime import datetime
from io import BytesIO
from PIL import Image


class SceneThumbnailItem(QListWidgetItem):
    """
    List widget item representing a scene with thumbnail.
    """
    
    def __init__(self, scene_data, parent=None):
        """
        Initialize the scene thumbnail item.
        
        Args:
            scene_data: Dictionary with scene information
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.scene_id = scene_data['id']
        self.scene_data = scene_data
        
        # Set item text
        self.setText(scene_data['name'])
        
        # Set tooltip with additional information
        created_date = datetime.fromisoformat(scene_data['created_at'])
        updated_date = datetime.fromisoformat(scene_data['updated_at'])
        
        tooltip = (
            f"{scene_data['name']}\n"
            f"Created: {created_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"Updated: {updated_date.strftime('%Y-%m-%d %H:%M')}"
        )
        
        if 'description' in scene_data and scene_data['description']:
            tooltip += f"\n\n{scene_data['description']}"
        
        self.setToolTip(tooltip)
        
        # Set size hint for item
        self.setSizeHint(QSize(120, 120))
        
        # Set default or blank thumbnail
        self.setIcon(QIcon())
    
    def update_thumbnail(self, thumbnail_data):
        """
        Update the thumbnail for this item.
        
        Args:
            thumbnail_data: Thumbnail image data (bytes)
        """
        if thumbnail_data:
            try:
                # Create QPixmap from thumbnail data
                pixmap = QPixmap()
                pixmap.loadFromData(thumbnail_data)
                
                # Resize if needed
                if pixmap.width() > 120 or pixmap.height() > 90:
                    pixmap = pixmap.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio)
                
                # Set as icon
                self.setIcon(QIcon(pixmap))
            except Exception as e:
                print(f"Error setting thumbnail: {e}")
                self.setIcon(QIcon())
        else:
            self.setIcon(QIcon())


class ProjectNavigator(QWidget):
    """
    Project navigator widget for managing project structure.
    Displayed in the main window.
    """
    
    # Signals
    project_selected = pyqtSignal(str)  # Project ID
    scene_selected = pyqtSignal(str)    # Scene ID
    
    scene_created = pyqtSignal(str, str)  # Scene Name, Description
    scene_renamed = pyqtSignal(str, str)  # Scene ID, New Name
    scene_deleted = pyqtSignal(str)       # Scene ID
    scene_duplicated = pyqtSignal(str)    # Scene ID to duplicate
    
    project_created = pyqtSignal(str, str)  # Project Name, Description
    project_opened = pyqtSignal(str)       # Project ID
    project_saved = pyqtSignal()
    project_closed = pyqtSignal()
    
    project_file_opened = pyqtSignal(str)   # File path
    project_file_saved = pyqtSignal(str)    # File path
    
    scenes_reordered = pyqtSignal(list)    # List of scene IDs in new order
    
    def __init__(self, parent=None):
        """
        Initialize the project navigator.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Project manager reference (set externally)
        self.project_manager = None
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        
        # Initialize the navigator
        self.initialize()
        
        # Context menus
        self.scene_menu = None
        self.project_menu = None
        
        # Setup context menus
        self.setup_menus()
        
        # Current project and scene
        self.current_project_id = None
        self.current_scene_id = None
        
        # Drag and drop support
        self.scenes_list.setDragEnabled(True)
        self.scenes_list.setAcceptDrops(True)
        self.scenes_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.scenes_list.dropEvent = self.custom_drop_event
    
    def initialize(self):
        """Initialize the project navigator UI."""
        # Header with title and project buttons
        header_layout = QHBoxLayout()
        
        # Project label
        self.project_label = QLabel("No Project Open")
        font = QFont()
        font.setBold(True)
        self.project_label.setFont(font)
        header_layout.addWidget(self.project_label, 1)
        
        # Project actions button
        self.project_button = QToolButton()
        self.project_button.setText("Project")
        self.project_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        header_layout.addWidget(self.project_button)
        
        self.layout.addLayout(header_layout)
        
        # Scene list header
        scene_header_layout = QHBoxLayout()
        
        # Scenes label
        scenes_label = QLabel("Scenes")
        font = QFont()
        font.setBold(True)
        scenes_label.setFont(font)
        scene_header_layout.addWidget(scenes_label, 1)
        
        # Add scene button
        self.add_scene_btn = QPushButton("+")
        self.add_scene_btn.setToolTip("Add new scene")
        self.add_scene_btn.setFixedSize(24, 24)
        self.add_scene_btn.setEnabled(False)
        self.add_scene_btn.clicked.connect(self.on_add_scene)
        scene_header_layout.addWidget(self.add_scene_btn)
        
        self.layout.addLayout(scene_header_layout)
        
        # Scenes list view
        self.scenes_list = QListWidget()
        self.scenes_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.scenes_list.setIconSize(QSize(120, 90))
        self.scenes_list.setGridSize(QSize(130, 130))
        self.scenes_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.scenes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scenes_list.customContextMenuRequested.connect(self.show_scene_context_menu)
        self.scenes_list.itemDoubleClicked.connect(self.on_scene_double_clicked)
        self.scenes_list.itemClicked.connect(self.on_scene_clicked)
        
        # Add list to layout
        self.layout.addWidget(self.scenes_list, 1)
        
        # Project info section
        self.info_group = QGroupBox("Project Information")
        info_layout = QFormLayout(self.info_group)
        
        # Project name
        self.project_name_label = QLabel("Name:")
        info_layout.addRow("Name:", self.project_name_label)
        
        # Project scenes count
        self.scenes_count_label = QLabel("Scenes: 0")
        info_layout.addRow("Scenes:", self.scenes_count_label)
        
        # Modified status
        self.modified_label = QLabel("Status: Not modified")
        info_layout.addRow("Status:", self.modified_label)
        
        # Add to main layout
        self.layout.addWidget(self.info_group)
    
    def set_project_manager(self, project_manager):
        """
        Set the project manager reference.
        
        Args:
            project_manager: ProjectManager instance
        """
        self.project_manager = project_manager
        
        # Connect signals
        if self.project_manager:
            # Project signals
            self.project_manager.project_created.connect(self.on_project_created)
            self.project_manager.project_loaded.connect(self.on_project_loaded)
            self.project_manager.project_saved.connect(self.on_project_saved)
            self.project_manager.project_closed.connect(self.on_project_closed)
            
            # Scene signals
            self.project_manager.scene_created.connect(self.on_scene_created)
            self.project_manager.scene_loaded.connect(self.on_scene_loaded)
            self.project_manager.scene_saved.connect(self.on_scene_saved)
            self.project_manager.scene_deleted.connect(self.on_scene_deleted)
            
            # Change tracking
            self.project_manager.project_changed.connect(self.on_project_changed)
    
    def setup_menus(self):
        """Set up context menus."""
        # Scene context menu
        self.scene_menu = QMenu(self)
        
        # Scene actions
        self.scene_rename_action = QAction("Rename Scene", self)
        self.scene_rename_action.triggered.connect(self.on_rename_scene)
        self.scene_menu.addAction(self.scene_rename_action)
        
        self.scene_duplicate_action = QAction("Duplicate Scene", self)
        self.scene_duplicate_action.triggered.connect(self.on_duplicate_scene)
        self.scene_menu.addAction(self.scene_duplicate_action)
        
        self.scene_menu.addSeparator()
        
        self.scene_delete_action = QAction("Delete Scene", self)
        self.scene_delete_action.triggered.connect(self.on_delete_scene)
        self.scene_menu.addAction(self.scene_delete_action)
        
        # Project menu for the button
        project_menu = QMenu(self)
        
        # Project actions
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self.on_new_project)
        project_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self.on_open_project)
        project_menu.addAction(open_project_action)
        
        project_menu.addSeparator()
        
        save_project_action = QAction("Save Project", self)
        save_project_action.triggered.connect(self.on_save_project)
        project_menu.addAction(save_project_action)
        
        save_as_action = QAction("Save Project As...", self)
        save_as_action.triggered.connect(self.on_save_project_as)
        project_menu.addAction(save_as_action)
        
        project_menu.addSeparator()
        
        close_project_action = QAction("Close Project", self)
        close_project_action.triggered.connect(self.on_close_project)
        project_menu.addAction(close_project_action)
        
        # Set menu for project button
        self.project_button.setMenu(project_menu)
    
    def show_scene_context_menu(self, position):
        """
        Show context menu for scenes list.
        
        Args:
            position: Position to show the menu
        """
        # Get clicked item
        item = self.scenes_list.itemAt(position)
        if not item:
            return
        
        # Store item for later use in actions
        self.context_menu_item = item
        
        # Show menu
        self.scene_menu.exec(self.scenes_list.mapToGlobal(position))
    
    def update_scenes_list(self):
        """Update the scenes list with current project scenes."""
        self.scenes_list.clear()
        
        if not self.project_manager or not self.current_project_id:
            return
        
        # Get scenes for current project
        scenes = self.project_manager.get_project_scenes()
        
        # Update scenes count label
        self.scenes_count_label.setText(f"Scenes: {len(scenes)}")
        
        # Add scenes to list
        for scene in scenes:
            item = SceneThumbnailItem(scene)
            self.scenes_list.addItem(item)
            
            # Load thumbnail in background
            QTimer.singleShot(100, lambda sid=scene['id'], itm=item: self.load_scene_thumbnail(sid, itm))
    
    def load_scene_thumbnail(self, scene_id, item):
        """
        Load a scene thumbnail in the background.
        
        Args:
            scene_id: ID of the scene
            item: SceneThumbnailItem to update
        """
        if not self.project_manager or not self.project_manager.db:
            return
            
        # Get thumbnail from database
        thumbnail_data = self.project_manager.db.get_scene_thumbnail(scene_id)
        
        # Update item with thumbnail
        item.update_thumbnail(thumbnail_data)
    
    def update_project_info(self):
        """Update project information display."""
        if not self.project_manager or not self.current_project_id:
            # No project open
            self.project_label.setText("No Project Open")
            self.project_name_label.setText("")
            self.scenes_count_label.setText("Scenes: 0")
            self.modified_label.setText("Status: Not modified")
            self.add_scene_btn.setEnabled(False)
            return
        
        # Get project info
        project_info = self.project_manager.get_project_info()
        if not project_info:
            return
        
        # Update labels
        self.project_label.setText(project_info['name'])
        self.project_name_label.setText(project_info['name'])
        
        # Update modified status
        has_changes = self.project_manager.has_unsaved_changes
        self.modified_label.setText(f"Status: {'Modified' if has_changes else 'Saved'}")
        
        # Enable add scene button
        self.add_scene_btn.setEnabled(True)
    
    def on_project_created(self, project_id):
        """
        Handle project creation.
        
        Args:
            project_id: ID of the created project
        """
        self.current_project_id = project_id
        self.update_project_info()
        self.update_scenes_list()
    
    def on_project_loaded(self, project_id):
        """
        Handle project loading.
        
        Args:
            project_id: ID of the loaded project
        """
        self.current_project_id = project_id
        self.update_project_info()
        self.update_scenes_list()
    
    def on_project_saved(self, project_id):
        """
        Handle project saving.
        
        Args:
            project_id: ID of the saved project
        """
        self.update_project_info()
    
    def on_project_closed(self):
        """Handle project closing."""
        self.current_project_id = None
        self.current_scene_id = None
        self.scenes_list.clear()
        self.update_project_info()
    
    def on"""
Project Navigator for the LightCraft application.
Provides a panel for managing scenes and items within the project.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLabel, 
    QPushButton, QFrame, QMenu, QStyledItemDelegate,
    QHeaderView
)
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont, QAction


class ProjectNavigator(QWidget):
    """
    Project navigator widget for managing the project structure.
    Displayed at the bottom of the main window.
    """
    
    # Signal emitted when a scene is selected
    scene_selected = pyqtSignal(str)
    
    # Signal emitted when an item is selected in the tree
    item_selected = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """
        Initialize the project navigator.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        
        # Initialize the navigator
        self.initialize()
    
    def initialize(self):
        """Initialize the project navigator with default content."""
        # Header with title and buttons
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Project Navigator")
        title_font = QFont()
        title_font.setBold(True)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch(1)
        
        # Add Scene button
        add_scene_btn = QPushButton("Add Scene")
        add_scene_btn.setToolTip("Add a new scene to the project")
        header_layout.addWidget(add_scene_btn)
        
        self.layout.addLayout(header_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(separator)
        
        # Tree view for project structure
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.tree_view)
        
        # Set up tree model
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        
        # Create root item
        self.root_item = self.tree_model.invisibleRootItem()
        
        # Add default content
        self.setup_default_content()
        
        # Expand all items by default
        self.tree_view.expandAll()
    
    def setup_default_content(self):
        """Set up default content for the project navigator."""
        # Create a default project item
        project_item = QStandardItem("New Project")
        project_item.setEditable(False)
        font = project_item.font()
        font.setBold(True)
        project_item.setFont(font)
        self.root_item.appendRow(project_item)
        
        # Create a default scene item
        scene_item = QStandardItem("Main Scene")
        scene_item.setData("main_scene", Qt.ItemDataRole.UserRole)
        project_item.appendRow(scene_item)
        
        # Add default categories for the scene
        lights_category = QStandardItem("Lights")
        lights_category.setEditable(False)
        scene_item.appendRow(lights_category)
        
        set_category = QStandardItem("Set Elements")
        set_category.setEditable(False)
        scene_item.appendRow(set_category)
        
        cameras_category = QStandardItem("Cameras")
        cameras_category.setEditable(False)
        scene_item.appendRow(cameras_category)
    
    def show_context_menu(self, position):
        """
        Show context menu for tree items.
        
        Args:
            position: Position where the right-click occurred
        """
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        # Create context menu
        context_menu = QMenu(self)
        
        # Add menu items depending on the type of item
        item = self.tree_model.itemFromIndex(index)
        parent = item.parent()
        
        if parent is None:
            # Project level
            rename_action = QAction("Rename Project", self)
            context_menu.addAction(rename_action)
            
            add_scene_action = QAction("Add Scene", self)
            context_menu.addAction(add_scene_action)
        elif parent.text() == "New Project":
            # Scene level
            rename_action = QAction("Rename Scene", self)
            context_menu.addAction(rename_action)
            
            duplicate_action = QAction("Duplicate Scene", self)
            context_menu.addAction(duplicate_action)
            
            context_menu.addSeparator()
            
            delete_action = QAction("Delete Scene", self)
            context_menu.addAction(delete_action)
        else:
            # Item level or category level
            item_data = item.data(Qt.ItemDataRole.UserRole)
            if item_data is None:
                # Category level
                add_item_action = QAction(f"Add Item to {item.text()}", self)
                context_menu.addAction(add_item_action)
            else:
                # Individual item
                rename_action = QAction("Rename Item", self)
                context_menu.addAction(rename_action)
                
                duplicate_action = QAction("Duplicate Item", self)
                context_menu.addAction(duplicate_action)
                
                context_menu.addSeparator()
                
                delete_action = QAction("Delete Item", self)
                context_menu.addAction(delete_action)
        
        # Show the menu
        context_menu.exec(self.tree_view.mapToGlobal(position))
    
    def update_view(self):
        """Update the project navigator view."""
        # This will be implemented in future prompts when we have
        # the data models defined
        pass
