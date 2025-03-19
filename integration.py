"""
Integration module for the LightCraft application.
Connects controllers with UI components and sets up signal/slot connections.
"""

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
    # Initialize controllers
    setup_controllers(main_window)
    
    # Connect signals and slots
    connect_signals(main_window)
    
    # Set up equipment library integration
    setup_equipment_integration(main_window, main_window.scene_controller, main_window.canvas_controller)
    

def setup_controllers(main_window):
    """
    Initialize all controllers.
    
    Args:
        main_window: The main application window
    """
    # Initialize scene controller
    main_window.scene_controller = SceneController(main_window)
    
    # Initialize canvas controller
    main_window.canvas_controller = CanvasController(main_window.scene_controller, main_window.canvas_area)
    
    # Initialize tool controller
    main_window.tool_controller = ToolController(main_window.canvas_area, main_window)
    main_window.tool_controller.set_canvas_controller(main_window.canvas_controller)
    
    # Initialize project controller
    main_window.project_controller = ProjectController(main_window.scene_controller, main_window)
    
    # Set project navigator in project controller
    main_window.project_controller.set_project_navigator(main_window.project_navigator)
    # Inside setup_controllers function in integration.py

    main_window.canvas_controller = CanvasController(
        main_window.scene_controller, 
        main_window.canvas_area, 
        main_window
    )


def connect_signals(main_window):
    """
    Connect signals and slots between components.
    
    Args:
        main_window: The main application window
    """
    # Connect tool palette with tool controller
    main_window.tool_palette.tool_selected.connect(main_window.tool_controller.set_active_tool)
    
    # Connect tool controller with canvas
    main_window.tool_controller.tool_action.connect(main_window.canvas_controller.handle_tool_action)
    
    # Connect canvas controller with scene controller
    main_window.canvas_controller.item_selected.connect(main_window.scene_controller.select_item)
    main_window.canvas_controller.item_added.connect(main_window.scene_controller.add_item)
    main_window.canvas_controller.item_removed.connect(main_window.scene_controller.remove_item)
    main_window.canvas_controller.item_modified.connect(main_window.scene_controller.update_item)
    
    # Connect scene controller with properties panel
    main_window.scene_controller.item_selected.connect(main_window.properties_panel.update_properties)
    
    # Connect properties panel with canvas controller
    main_window.canvas_controller.connect_property_panel(main_window.properties_panel)
    
    # Connect model item modification signal to update canvas
    main_window.scene_controller.item_modified.connect(main_window.canvas_controller.update_item_on_canvas)
    
    # Connect main window menu actions
    connect_menu_actions(main_window)


def connect_menu_actions(main_window):
    """
    Connect main window menu actions to their handlers.
    
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
    if hasattr(main_window, 'undo_action'):
        main_window.undo_action.triggered.connect(main_window.canvas_controller.undo)
    
    if hasattr(main_window, 'redo_action'):
        main_window.redo_action.triggered.connect(main_window.canvas_controller.redo)
    
    # View menu
    if hasattr(main_window, 'zoom_in_action'):
        main_window.zoom_in_action.triggered.connect(
            lambda: main_window.canvas_area.view.scale(1.25, 1.25)
        )
    
    if hasattr(main_window, 'zoom_out_action'):
        main_window.zoom_out_action.triggered.connect(
            lambda: main_window.canvas_area.view.scale(0.8, 0.8)
        )
