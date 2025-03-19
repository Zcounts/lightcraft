"""
Build script to create a standalone executable for LightCraft.
Run this script to generate a clickable .exe file.
"""
import PyInstaller.__main__
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Run PyInstaller
PyInstaller.__main__.run([
    'main.py',                           # Your main script
    '--name=LightCraft',                 # Name of the application
    '--onefile',                         # Create a single file
    '--windowed',                        # Don't open a console window
    '--icon=lightcraft/resources/icons/app_icon.ico',  # Application icon
    '--add-data=lightcraft/resources;lightcraft/resources',  # Include resources
    '--distpath=' + os.path.join(script_dir, 'dist'),  # Output directory
    '--workpath=' + os.path.join(script_dir, 'build'),  # Working directory
    '--clean',                           # Clean PyInstaller cache
])

print("\nBuild complete! Your executable is in the 'dist' folder.")
print("Just double-click 'LightCraft.exe' to run the application.")
