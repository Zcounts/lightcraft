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
        
        # Set up application settings
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        
        # Initialize main window
        self.main_window = MainWindow(self.settings)
    
    def run(self):
        """
        Start the application event loop.
        
        Returns:
            int: The exit code from the application
        """
        self.main_window.show()
        return self.app.exec()
