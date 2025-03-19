#!/usr/bin/env python3
"""
LightCraft - Lighting Diagram Designer for Film Shoots
Entry point for the application.
"""

import sys
from lightcraft.app import Application


def main():
    """Main entry point for the LightCraft application."""
    app = Application(sys.argv)
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
