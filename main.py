#!/usr/bin/env python3
"""
LightCraft - Lighting Diagram Designer for Film Shoots
Entry point for the application.
"""

import sys
from lightcraft.app import Application

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle unhandled exceptions by showing an error message."""
    import traceback
    print("An unexpected error occurred:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("\nPlease report this error to the developers.")
    input("Press Enter to exit...")

def main():
    """Main entry point for the LightCraft application."""
    sys.excepthook = handle_exception
    try:
        app = Application(sys.argv)
        exit_code = app.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
