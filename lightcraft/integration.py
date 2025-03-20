"""
Integration module for the LightCraft application.
Connects controllers with UI components and sets up signal/slot connections.
"""

from PyQt6.QtCore import Qt, QObject, QTimer

from lightcraft.controllers.scene_controller import SceneController
from lightcraft.controllers.tool_controller import ToolController
from lightcraft.controllers.project_controller import ProjectController
from lightcraft.controllers.canvas_controller import CanvasController
from lightcraft.equipment_integration import setup_equipment_integration


def setup_application_components(main_window):
    """
    Set up application components and establish connections.
    
    Args:
        main_window: The main application window
    """
    # Initialize controllers (order matters!)
    setup_controllers(main_window)
    
    # Connect signals and slots
    connect_signals(main_window)
    
    # Set up equipment library integration
    setup_equipment_integration(main_window, main_window.scene_controller, main_window.canvas_controller)
    
    # Final initialization steps
    finalize_setup(main_window)


def setup_controllers(main_window):
    """
    Initialize all controllers in the correct order.
    
    Args:
        main_window: The main application window
    """
    try:
        # Initialize scene controller first (manages model data)
        main_window.scene_controller = SceneController(main_window)
        
        # Initialize canvas controller next (manages view of model data)
        main_window.canvas_controller = CanvasController(main_window.scene_controller, main_window.canvas_area, main_window)
        
        # Initialize tool controller (interacts with canvas)
        main_window.tool_controller = ToolController(main_window.canvas_area, main_window)
        main_window.tool_controller.canvas_controller = main_window.canvas_controller
        
        # Initialize project controller (depends on scene controller)
        main_window.project_controller = ProjectController(main_window.scene_controller, main_window)
        
        # Connect project controller with project navigator
        if hasattr(main_window, 'project_navigator'):
            main_window.project_controller.set_project_navigator(main_window.project_navigator)
    except Exception as e:
        print(f"Error setting up controllers: {e}")
        import traceback
        traceback.print_exc()


def connect_signals(main_window):
    """
    Connect signals and slots between components.
    
    Args:
        main_window: The main application window
    """
    # Connect tool palette with tool controller
    if hasattr(main_window, 'tool_palette') and hasattr(main_window, 'tool_controller'):
        main_window.tool_palette.tool_selected.connect(main_window.tool_controller.set_active_tool)
    
    # Connect tool controller with canvas controller
    if hasattr(main_window, 'tool_controller') and hasattr(main_window, 'canvas_controller'):
        main_window.tool_controller.tool_action.connect(main_window.canvas_controller.handle_tool_action)
    
    # Connect canvas controller with scene controller
    if hasattr(main_window, 'canvas_controller') and hasattr(main_window, 'scene_controller'):
        main_window.canvas_controller.item_selected.connect(main_window.scene_controller.select_item)
        main_window.canvas_controller.item_added.connect(main_window.scene_controller.add_item)
        main_window.canvas_controller.item_removed.connect(main_window.scene_controller.remove_item)
        main_window.canvas_controller.item_modified.connect(main_window.scene_controller.update_item)
        
        # Connect scene controller back to canvas controller for updates
        main_window.scene_controller.item_modified.connect(main_window.canvas_controller.update_item_on_canvas)
        main_window.scene_controller.scene_changed.connect(main_window.canvas_controller.clear_canvas)
    
    # Connect main window menu actions
    connect_menu_actions(main_window)


def connect_menu_actions(main_window):
    """
    Connect main window menu actions to appropriate handlers.
    
    Args:
        main_window: The main application window
    """
    # File menu
    if hasattr(main_window, 'new_action'):
        main_window.new_action.triggered.connect(main_window.on_new_project)
    
    if hasattr(main_window, 'open_action'):
        main_window.open_action.triggered.connect(main_window.on_open_project)
    
    if hasattr(main_window, 'save_action'):
        main_window.save_action.triggered.connect(main_window.on_save_project)
    
    if hasattr(main_window, 'save_as_action'):
        main_window.save_as_action.triggered.connect(main_window.on_save_project_as)
    
    # Edit menu
    if hasattr(main_window, 'undo_action') and hasattr(main_window, 'canvas_controller'):
        main_window.undo_action.triggered.connect(main_window.canvas_controller.undo)
    
    if hasattr(main_window, 'redo_action') and hasattr(main_window, 'canvas_controller'):
        main_window.redo_action.triggered.connect(main_window.canvas_controller.redo)
    
    # View menu
    if hasattr(main_window, 'zoom_in_action') and hasattr(main_window, 'canvas_area'):
        main_window.zoom_in_action.triggered.connect(main_window.canvas_area.zoom_in)
    
    if hasattr(main_window, 'zoom_out_action') and hasattr(main_window, 'canvas_area'):
        main_window.zoom_out_action.triggered.connect(main_window.canvas_area.zoom_out)
    
    if hasattr(main_window, 'zoom_fit_action') and hasattr(main_window, 'canvas_area'):
        main_window.zoom_fit_action.triggered.connect(main_window.canvas_area.zoom_to_fit)


def finalize_setup(main_window):
    """
    Perform final setup steps after all components are initialized.
    
    Args:
        main_window: The main application window
    """
    # Set default tool
    if hasattr(main_window, 'tool_palette'):
        main_window.tool_palette.select_tool("select")
    
    # Create empty project with default scene
    if hasattr(main_window, 'project_controller'):
        QTimer.singleShot(100, lambda: main_window.project_controller.create_project("New Project", "Default project"))
    
    # Update status bar
    if hasattr(main_window, 'statusBar'):
        main_window.statusBar.showMessage("Ready", 3000)
