"""
Configuration settings for the LightCraft application.
"""

import os

# Application information
APP_NAME = "LightCraft"
ORGANIZATION_NAME = "LightCraft"
VERSION = "0.1.0"

# Default window size
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# Default panel proportions (percentage of window)
TOOL_PALETTE_WIDTH = 15  # 15% of window width
PROPERTIES_PANEL_WIDTH = 20  # 20% of window width
PROJECT_NAVIGATOR_HEIGHT = 20  # 20% of window height

# Resource paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, 'lightcraft', 'resources')
ICONS_DIR = os.path.join(RESOURCES_DIR, 'icons')
STYLES_DIR = os.path.join(RESOURCES_DIR, 'styles')

# Ensure resource directories exist
if not os.path.exists(RESOURCES_DIR):
    os.makedirs(RESOURCES_DIR, exist_ok=True)
if not os.path.exists(ICONS_DIR):
    os.makedirs(ICONS_DIR, exist_ok=True)
if not os.path.exists(STYLES_DIR):
    os.makedirs(STYLES_DIR, exist_ok=True)

# Application data directory
import os
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".lightcraft")

# Database file
DATABASE_FILE = os.path.join(APP_DATA_DIR, "lightcraft.db")

# Auto-save settings
AUTO_SAVE_ENABLED = True
AUTO_SAVE_INTERVAL = 300  # seconds (5 minutes)

# Default style
DEFAULT_STYLE = os.path.join(STYLES_DIR, 'default.qss')

# Canvas grid settings
GRID_SIZE = 20  # pixels
GRID_COLOR = "#CCCCCC"
GRID_ENABLED = True
