"""
Application class for LightCraft.
Initializes the PyQt application and main window.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
import sys
import os

from lightcraft.ui.main_window import MainWindow
from lightcraft.config import APP_NAME, ORGANIZATION_NAME, VERSION
from lightcraft.integration import setup_application_components


class Application:
    """
    Main application class for LightCraft.
    Handles initialization of the QApplication and MainWindow.
    """
    
    def __init__(self, argv):
        """
        Initialize the Application with command line arguments.
        
        Args:
            argv: Command line arguments passed to the application
        """
        self.app = QApplication(argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setOrganizationName(ORGANIZATION_NAME)
        self.app.setApplicationVersion(VERSION)

        # Ensure necessary directories exist
        import os
        from lightcraft.config import APP_DATA_DIR, RESOURCES_DIR, ICONS_DIR, STYLES_DIR
        
        for directory in [APP_DATA_DIR, RESOURCES_DIR, ICONS_DIR, STYLES_DIR]:
            os.makedirs(directory, exist_ok=True)

        # Ensure project manager database exists and is initialized
        from lightcraft.models.project_db import ProjectDatabase
        db = ProjectDatabase()
        
        # Set up application settings
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        
        # Initialize main window
        self.main_window = MainWindow(self.settings)
        
        # Set up application components and connections
        setup_application_components(self.main_window)
    
    def run(self):
        """
        Start the application event loop.
        
        Returns:
            int: The exit code from the application
        """
        self.main_window.show()
        return self.app.exec()
