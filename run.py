#!/usr/bin/env python3
"""
Simple starter script for LightCraft
"""

import sys
import os
import importlib.util

# Add the parent directory to the path so we can import lightcraft
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the main function
from main import main

if __name__ == "__main__":
    main()
