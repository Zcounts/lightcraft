"""
Application class for LightCraft.
Initializes the PyQt application and main window.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QPalette, QColor
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
    
    def __init__(self, argv, existing_app=None):
        """
        Initialize the Application with command line arguments.
        
        Args:
            argv: Command line arguments passed to the application
            existing_app: Optional existing QApplication instance
        """
        if existing_app:
            self.app = existing_app
        else:
            self.app = QApplication(argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setOrganizationName(ORGANIZATION_NAME)
        self.app.setApplicationVersion(VERSION)

        # Ensure necessary directories exist
        import os
        from lightcraft.config import APP_DATA_DIR, RESOURCES_DIR, ICONS_DIR, STYLES_DIR
        
        for directory in [APP_DATA_DIR, RESOURCES_DIR, ICONS_DIR, STYLES_DIR]:
            os.makedirs(directory, exist_ok=True)

        # Set application style
        self.apply_dark_theme()
        
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

    def apply_dark_theme(self):
        """Apply a dark theme to the application."""
        self.app.setStyle("Fusion")
        
        # Dark palette
        dark_palette = QPalette()
        dark_color = QColor(45, 45, 45)
        disabled_color = QColor(70, 70, 70)
        text_color = QColor(220, 220, 220)
        highlight_color = QColor(42, 130, 218)
        bright_text = QColor(255, 255, 255)
        
        # Set colors
        dark_palette.setColor(QPalette.ColorRole.Window, dark_color)
        dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, dark_color)
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, dark_color)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Text, text_color)
        dark_palette.setColor(QPalette.ColorRole.Button, dark_color)
        dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        dark_palette.setColor(QPalette.ColorRole.BrightText, bright_text)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, bright_text)
        
        # Disabled colors
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_color)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_color)
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_color)
        
        # Apply the palette
        self.app.setPalette(dark_palette)
        
        # Additional stylesheet for specific controls
        self.app.setStyleSheet("""
            QToolTip { 
                color: #ffffff; 
                background-color: #2a2a2a; 
                border: 1px solid #767676; 
                border-radius: 2px;
            }
            
            QMenuBar {
                background-color: #2d2d2d;
                color: #eeeeee;
            }
            
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            
            QMenu {
                background-color: #2d2d2d;
                color: #eeeeee;
                border: 1px solid #767676;
            }
            
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
            
            QPushButton {
                background-color: #424242;
                color: #eeeeee;
                border: 1px solid #767676;
                border-radius: 4px;
                padding: 4px 12px;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            
            QPushButton:pressed {
                background-color: #2a82da;
            }
            
            QToolButton {
                background-color: #424242;
                color: #eeeeee;
                border: 1px solid #767676;
                border-radius: 2px;
            }
            
            QToolButton:checked {
                background-color: #2a82da;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                margin: 12px 0px 12px 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #5d5d5d;
                min-height: 20px;
                border-radius: 4px;
                margin: 2px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
