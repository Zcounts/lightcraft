# LightCraft

LightCraft is a desktop application for designing lighting diagrams for film shoots. It provides an intuitive interface for film crew members to plan and visualize lighting setups.

## Features

- Create and manage lighting diagrams for film productions
- Place and configure various lighting equipment
- Design set elements like walls, doors, and windows
- Position cameras and visualize shot angles
- Export diagrams as PDF for sharing with crew members

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6
- Pillow (Python Imaging Library)
- reportlab (for PDF export)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/lightcraft.git
   cd lightcraft
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package and dependencies:
   ```
   pip install -e .
   ```

4. Run the application:
   ```
   lightcraft
   ```

   Alternatively, you can run it directly:
   ```
   python -m lightcraft.main
   ```

## Project Structure

```
lightcraft/
│
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── setup.py                # Installation script
├── README.md               # Documentation
│
├── lightcraft/             # Main package
│   ├── __init__.py
│   ├── app.py              # Application class
│   ├── config.py           # Configuration settings
│   │
│   ├── ui/                 # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py  # Main application window
│   │   ├── canvas_area.py  # Canvas for lighting diagram
│   │   ├── tool_palette.py # Tool selection panel
│   │   ├── properties_panel.py # Item properties panel
│   │   └── project_navigator.py # Scene/project navigator
│   │
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── project.py      # Project data model
│   │   ├── scene.py        # Scene data model
│   │   └── equipment.py    # Equipment data model
│   │
│   ├── controllers/        # Business logic
│   │   ├── __init__.py
│   │   ├── tool_controller.py # Handles tool operations
│   │   └── scene_controller.py # Manages scene operations
│   │
│   └── resources/          # Application resources
│       ├── icons/          # UI icons
│       └── styles/         # CSS styles
│
└── tests/                  # Unit tests
    ├── __init__.py
    ├── test_models.py
    └── test_controllers.py
```

## Development

This application follows a Model-View-Controller (MVC) architecture:

- **Models**: Data structures for projects, scenes, and equipment
- **Views**: UI components implemented with PyQt6
- **Controllers**: Business logic connecting models and views

## Future Development

- Canvas & Interaction: Implement drag-drop functionality and visual elements
- Equipment Library: Add a comprehensive database of lighting equipment
- Project Management: Implement save/load functionality
- Export: Add PDF export functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.
