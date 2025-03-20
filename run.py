#!/usr/bin/env python3
"""
Simple starter script for LightCraft
"""

import sys
import os
import traceback

# Add the parent directory to the path so we can import lightcraft
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def handle_exception(exc_type, exc_value, exc_tb):
    """Handle unhandled exceptions by showing an error message."""
    print("An unexpected error occurred:")
    traceback.print_exception(exc_type, exc_value, exc_tb)
    print("\nPlease report this error to the developers.")
    input("Press Enter to exit...")

try:
    # Import and run the main function
    from main import main
    sys.excepthook = handle_exception
    main()
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required packages are installed.")
    print("Run setup_packages.bat to install the required packages.")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
