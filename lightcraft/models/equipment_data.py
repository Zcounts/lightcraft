"""
Equipment data definitions for the LightCraft application.
Contains definitions of industry-standard film lighting equipment.
"""

# Default light colors in hex format
TUNGSTEN_COLOR = "#FF9329"  # 3200K
DAYLIGHT_COLOR = "#FFFFFF"  # 5600K
LED_DAYLIGHT_COLOR = "#F5F5FF"  # LED daylight approximation
LED_BICOLOR_COLOR = "#FFF5E6"  # LED bicolor approximation

# Equipment categories
CATEGORIES = {
    "lights": {
        "name": "Lighting",
        "subcategories": {
            "fresnel": {
                "name": "Fresnel",
                "description": "Traditional tungsten Fresnel lights"
            },
            "hmi": {
                "name": "HMI",
                "description": "Daylight-balanced HMI lights"
            },
            "led": {
                "name": "LED Panels",
                "description": "LED lighting fixtures"
            },
            "practical": {
                "name": "Practicals",
                "description": "Practical lights visible in shot"
            },
            "specialty": {
                "name": "Specialty",
                "description": "Special purpose lights"
            }
        }
    },
    "grip": {
        "name": "Grip Equipment",
        "subcategories": {
            "stands": {
                "name": "Stands",
                "description": "C-stands and light stands"
            },
            "control": {
                "name": "Light Control",
                "description": "Flags, scrims, and other light control"
            },
            "mounts": {
                "name": "Mounts & Clamps",
                "description": "Mounting hardware for lights and modifiers"
            },
            "rigging": {
                "name": "Rigging",
                "description": "Pipes, clamps, and rigging equipment"
            }
        }
    },
    "camera": {
        "name": "Camera",
        "subcategories": {
            "cameras": {
                "name": "Cameras",
                "description": "Camera bodies"
            },
            "lenses": {
                "name": "Lenses",
                "description": "Prime and zoom lenses"
            },
            "support": {
                "name": "Camera Support",
                "description": "Tripods, dollies, and other camera support"
            }
        }
    },
    "set": {
        "name": "Set Pieces",
        "subcategories": {
            "walls": {
                "name": "Walls",
                "description": "Set walls and flats"
            },
            "doors": {
                "name": "Doors & Windows",
                "description": "Doorways and windows"
            },
            "furniture": {
                "name": "Furniture",
                "description": "Set furniture and props"
            }
        }
    }
}

# Equipment library
EQUIPMENT_LIBRARY = {
    # ==== FRESNEL LIGHTS ====
    "fresnel_150w": {
        "name": "150W Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "150 Watt tungsten Fresnel, compact size",
        "properties": {
            "power": 150,  # watts
            "beam_angle_min": 15,  # degrees
            "beam_angle_max": 55,  # degrees
            "beam_angle": 35,  # default degrees
            "color_temperature": 3200,  # Kelvin
            "color": TUNGSTEN_COLOR,
            "weight": 1.5,  # kg
            "size": (15, 15, 20),  # cm (width, height, depth)
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "grip_flag.png"
    },
    "floppy_24x36": {
        "name": "24\"x36\" Floppy",
        "category": "grip",
        "subcategory": "control",
        "description": "24\"x36\" floppy flag with hinged flap",
        "properties": {
            "width": 91.4,  # cm (36 inches)
            "height": 61.0,  # cm (24 inches)
            "weight": 2.2,
            "size": (91.4, 61.0, 2),
            "material": "Fabric",
            "equipment_type": "Floppy"
        },
        "icon": "grip_floppy.png"
    },
    "scrim_24x36": {
        "name": "24\"x36\" Scrim",
        "category": "grip",
        "subcategory": "control",
        "description": "24\"x36\" single scrim for diffusing light",
        "properties": {
            "width": 91.4,  # cm (36 inches)
            "height": 61.0,  # cm (24 inches)
            "weight": 1.8,
            "size": (91.4, 61.0, 1),
            "material": "Scrim",
            "equipment_type": "Scrim"
        },
        "icon": "grip_scrim.png"
    },
    "diffusion_4x4": {
        "name": "4'x4' Diffusion",
        "category": "grip",
        "subcategory": "control",
        "description": "4'x4' diffusion fabric for softening light",
        "properties": {
            "width": 121.9,  # cm (48 inches)
            "height": 121.9,  # cm (48 inches)
            "weight": 0.5,
            "size": (121.9, 121.9, 0.2),
            "material": "Fabric",
            "equipment_type": "Diffusion"
        },
        "icon": "grip_diffusion.png"
    },
    "cardellini_clamp": {
        "name": "Cardellini Clamp",
        "category": "grip",
        "subcategory": "mounts",
        "description": "Versatile end jaw clamp for mounting lights",
        "properties": {
            "weight": 0.8,
            "size": (15, 10, 10),
            "max_load": 10.0,  # kg
            "material": "Aluminum",
            "equipment_type": "Clamp"
        },
        "icon": "grip_cardellini.png"
    },
    "mafer_clamp": {
        "name": "Mafer Clamp",
        "category": "grip",
        "subcategory": "mounts",
        "description": "Heavy-duty clamp for mounting equipment",
        "properties": {
            "weight": 1.2,
            "size": (20, 15, 8),
            "max_load": 15.0,  # kg
            "material": "Aluminum",
            "equipment_type": "Clamp"
        },
        "icon": "grip_mafer.png"
    },
    "pipe_clamp": {
        "name": "Pipe Clamp",
        "category": "grip",
        "subcategory": "rigging",
        "description": "Clamp for attaching equipment to pipes",
        "properties": {
            "weight": 1.0,
            "size": (20, 10, 10),
            "max_load": 20.0,  # kg
            "material": "Steel",
            "equipment_type": "Clamp"
        },
        "icon": "grip_pipe_clamp.png"
    },
    
    # ==== CAMERA EQUIPMENT ====
    "camera_cinema": {
        "name": "Cinema Camera",
        "category": "camera",
        "subcategory": "cameras",
        "description": "Professional cinema camera",
        "properties": {
            "weight": 8.0,
            "size": (25, 20, 40),
            "sensor_size": "Super 35mm",
            "equipment_type": "Camera"
        },
        "icon": "camera_cinema.png"
    },
    "camera_dslr": {
        "name": "DSLR Camera",
        "category": "camera",
        "subcategory": "cameras",
        "description": "Digital SLR camera",
        "properties": {
            "weight": 1.5,
            "size": (15, 10, 12),
            "sensor_size": "APS-C",
            "equipment_type": "Camera"
        },
        "icon": "camera_dslr.png"
    },
    "lens_24_70": {
        "name": "24-70mm Zoom Lens",
        "category": "camera",
        "subcategory": "lenses",
        "description": "Standard zoom lens",
        "properties": {
            "weight": 0.8,
            "size": (8, 8, 12),
            "focal_length_min": 24,
            "focal_length_max": 70,
            "focal_length": 35,  # default mm
            "aperture_min": 2.8,
            "aperture_max": 22,
            "aperture": 5.6,  # default f-stop
            "equipment_type": "Lens"
        },
        "icon": "camera_lens_zoom.png"
    },
    "lens_50mm": {
        "name": "50mm Prime Lens",
        "category": "camera",
        "subcategory": "lenses",
        "description": "Standard prime lens",
        "properties": {
            "weight": 0.5,
            "size": (7, 7, 8),
            "focal_length": 50,  # mm
            "aperture_min": 1.8,
            "aperture_max": 22,
            "aperture": 5.6,  # default f-stop
            "equipment_type": "Lens"
        },
        "icon": "camera_lens_prime.png"
    },
    "tripod_fluid_head": {
        "name": "Fluid Head Tripod",
        "category": "camera",
        "subcategory": "support",
        "description": "Professional fluid head tripod",
        "properties": {
            "height_min": 75,  # cm
            "height_max": 180,  # cm
            "height": 120,  # default cm
            "weight": 5.0,
            "size": (30, 120, 30),
            "max_load": 10.0,  # kg
            "material": "Carbon Fiber",
            "equipment_type": "Tripod"
        },
        "icon": "camera_tripod.png"
    },
    "dolly_track": {
        "name": "Camera Dolly with Track",
        "category": "camera",
        "subcategory": "support",
        "description": "Camera dolly with 12 feet of track",
        "properties": {
            "weight": 95.0,
            "size": (90, 40, 366),  # 12 feet track length
            "max_load": 120.0,  # kg
            "track_length": 366,  # cm (12 feet)
            "material": "Aluminum",
            "equipment_type": "Dolly"
        },
        "icon": "camera_dolly.png"
    },
    
    # ==== SET PIECES ====
    "wall_flat_4x8": {
        "name": "4'x8' Wall Flat",
        "category": "set",
        "subcategory": "walls",
        "description": "Standard 4'x8' wall flat",
        "properties": {
            "width": 244,  # cm (8 feet)
            "height": 122,  # cm (4 feet)
            "thickness": 10,  # cm
            "weight": 20.0,
            "size": (244, 122, 10),
            "material": "Wood",
            "color": "#FFFFFF",  # White
            "equipment_type": "Wall"
        },
        "icon": "set_wall_flat.png"
    },
    "wall_flat_4x4": {
        "name": "4'x4' Wall Flat",
        "category": "set",
        "subcategory": "walls",
        "description": "Standard 4'x4' wall flat",
        "properties": {
            "width": 122,  # cm (4 feet)
            "height": 122,  # cm (4 feet)
            "thickness": 10,  # cm
            "weight": 12.0,
            "size": (122, 122, 10),
            "material": "Wood",
            "color": "#FFFFFF",  # White
            "equipment_type": "Wall"
        },
        "icon": "set_wall_flat.png"
    },
    "door_standard": {
        "name": "Standard Door",
        "category": "set",
        "subcategory": "doors",
        "description": "Standard interior door with frame",
        "properties": {
            "width": 91,  # cm (36 inches)
            "height": 213,  # cm (84 inches / 7 feet)
            "thickness": 10,  # cm
            "weight": 25.0,
            "size": (91, 213, 10),
            "material": "Wood",
            "color": "#F5F5DC",  # Off-white
            "equipment_type": "Door"
        },
        "icon": "set_door.png"
    },
    "window_standard": {
        "name": "Standard Window",
        "category": "set",
        "subcategory": "doors",
        "description": "Standard window with frame",
        "properties": {
            "width": 91,  # cm (36 inches)
            "height": 122,  # cm (48 inches)
            "thickness": 10,  # cm
            "weight": 20.0,
            "size": (91, 122, 10),
            "material": "Wood/Glass",
            "color": "#F5F5DC",  # Off-white
            "equipment_type": "Window"
        },
        "icon": "set_window.png"
    },
    "sofa": {
        "name": "Sofa",
        "category": "set",
        "subcategory": "furniture",
        "description": "Three-seat sofa",
        "properties": {
            "width": 200,  # cm
            "height": 90,  # cm
            "depth": 90,  # cm
            "weight": 50.0,
            "size": (200, 90, 90),
            "material": "Fabric",
            "color": "#C0C0C0",  # Gray
            "equipment_type": "Furniture"
        },
        "icon": "set_sofa.png"
    },
    "dining_table": {
        "name": "Dining Table",
        "category": "set",
        "subcategory": "furniture",
        "description": "Dining table for six",
        "properties": {
            "width": 180,  # cm
            "height": 75,  # cm
            "depth": 90,  # cm
            "weight": 40.0,
            "size": (180, 75, 90),
            "material": "Wood",
            "color": "#8B4513",  # Brown
            "equipment_type": "Furniture"
        },
        "icon": "set_table.png"
    }
}

# Functions for equipment library management

def get_equipment_by_id(equipment_id):
    """
    Get equipment data by ID.
    
    Args:
        equipment_id: ID of the equipment
    
    Returns:
        dict: Equipment data or None if not found
    """
    return EQUIPMENT_LIBRARY.get(equipment_id)

def get_equipment_by_category(category, subcategory=None):
    """
    Get equipment data filtered by category and optional subcategory.
    
    Args:
        category: Category to filter by
        subcategory: Optional subcategory to filter by
    
    Returns:
        list: List of equipment data dictionaries
    """
    if subcategory:
        return [item for item_id, item in EQUIPMENT_LIBRARY.items() 
                if item["category"] == category and item["subcategory"] == subcategory]
    else:
        return [item for item_id, item in EQUIPMENT_LIBRARY.items() 
                if item["category"] == category]

def search_equipment(query):
    """
    Search equipment by name or description.
    
    Args:
        query: Search query string
    
    Returns:
        list: List of matching equipment data dictionaries
    """
    query = query.lower()
    return [item for item_id, item in EQUIPMENT_LIBRARY.items() 
            if query in item["name"].lower() or (
                "description" in item and query in item["description"].lower())]

def get_equipment_icon_path(equipment_id):
    """
    Get the path to the equipment icon.
    
    Args:
        equipment_id: ID of the equipment
    
    Returns:
        str: Path to the icon or None if not found
    """
    from lightcraft.config import ICONS_DIR
    import os
    
    # Try to get the specific icon from equipment data
    equipment = get_equipment_by_id(equipment_id)
    if equipment and "icon" in equipment:
        icon_path = os.path.join(ICONS_DIR, equipment["icon"])
        if os.path.exists(icon_path):
            return icon_path
    
    # If no specific icon, create category-based filename
    if equipment and "category" in equipment and "subcategory" in equipment:
        category = equipment["category"]
        subcategory = equipment["subcategory"]
        icon_name = f"{category}_{subcategory}.svg"
        icon_path = os.path.join(ICONS_DIR, icon_name)
        if os.path.exists(icon_path):
            return icon_path
    
    # Fall back to placeholder
    placeholder_path = os.path.join(ICONS_DIR, "placeholder.svg")
    if os.path.exists(placeholder_path):
        return placeholder_path
    
    # Create placeholder directory and file if needed
    try:
        os.makedirs(ICONS_DIR, exist_ok=True)
        placeholder_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <rect width="48" height="48" fill="#555555" rx="8" ry="8"/>
  <text x="24" y="30" font-family="Arial" font-size="24" fill="white" text-anchor="middle">?</text>
</svg>'''
        with open(placeholder_path, 'w') as f:
            f.write(placeholder_content)
        return placeholder_path
    except:
        return None
    
# Add the remaining equipment items to the library
EQUIPMENT_LIBRARY.update({
    "fresnel_300w": {
        "name": "300W Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "300 Watt tungsten Fresnel",
        "properties": {
            "power": 300,
            "beam_angle_min": 15,
            "beam_angle_max": 55,
            "beam_angle": 35,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 1.8,
            "size": (18, 18, 25),
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "fresnel_small.png"
    },
    "fresnel_650w": {
        "name": "650W Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "650 Watt tungsten Fresnel, industry standard",
        "properties": {
            "power": 650,
            "beam_angle_min": 12,
            "beam_angle_max": 52,
            "beam_angle": 35,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 3.5,
            "size": (25, 25, 30),
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "fresnel_small.png"
    },
    "fresnel_1k": {
        "name": "1K Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "1000 Watt tungsten Fresnel",
        "properties": {
            "power": 1000,
            "beam_angle_min": 10,
            "beam_angle_max": 50,
            "beam_angle": 35,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 5.0,
            "size": (30, 30, 40),
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "fresnel_medium.png"
    },
    "fresnel_2k": {
        "name": "2K Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "2000 Watt tungsten Fresnel",
        "properties": {
            "power": 2000,
            "beam_angle_min": 10,
            "beam_angle_max": 50,
            "beam_angle": 35,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 9.0,
            "size": (40, 40, 55),
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "fresnel_medium.png"
    },
    "fresnel_5k": {
        "name": "5K Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "5000 Watt tungsten Fresnel",
        "properties": {
            "power": 5000,
            "beam_angle_min": 8,
            "beam_angle_max": 45,
            "beam_angle": 30,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 18.0,
            "size": (50, 50, 70),
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "fresnel_large.png"
    },
    "fresnel_10k": {
        "name": "10K Fresnel",
        "category": "lights",
        "subcategory": "fresnel",
        "description": "10000 Watt tungsten Fresnel",
        "properties": {
            "power": 10000,
            "beam_angle_min": 8,
            "beam_angle_max": 45,
            "beam_angle": 30,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 35.0,
            "size": (80, 80, 100),
            "fixture_type": "spotlight",
            "dimmer_compatible": True,
            "equipment_type": "Fresnel"
        },
        "icon": "fresnel_large.png"
    },
    
    # ==== HMI LIGHTS ====
    "hmi_200w": {
        "name": "200W HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "200 Watt HMI light",
        "properties": {
            "power": 200,
            "beam_angle_min": 15,
            "beam_angle_max": 55,
            "beam_angle": 35,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 4.0,
            "size": (20, 20, 30),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_small.png"
    },
    "hmi_575w": {
        "name": "575W HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "575 Watt HMI PAR light",
        "properties": {
            "power": 575,
            "beam_angle_min": 12,
            "beam_angle_max": 45,
            "beam_angle": 30,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 10.0,
            "size": (30, 30, 40),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_small.png"
    },
    "hmi_1.2k": {
        "name": "1.2K HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "1200 Watt HMI fresnel",
        "properties": {
            "power": 1200,
            "beam_angle_min": 10,
            "beam_angle_max": 50,
            "beam_angle": 35,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 15.0,
            "size": (40, 40, 60),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_medium.png"
    },
    "hmi_2.5k": {
        "name": "2.5K HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "2500 Watt HMI fresnel",
        "properties": {
            "power": 2500,
            "beam_angle_min": 10,
            "beam_angle_max": 45,
            "beam_angle": 32,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 25.0,
            "size": (50, 50, 70),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_medium.png"
    },
    "hmi_4k": {
        "name": "4K HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "4000 Watt HMI fresnel",
        "properties": {
            "power": 4000,
            "beam_angle_min": 8,
            "beam_angle_max": 45,
            "beam_angle": 30,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 40.0,
            "size": (60, 60, 80),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_large.png"
    },
    "hmi_6k": {
        "name": "6K HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "6000 Watt HMI fresnel",
        "properties": {
            "power": 6000,
            "beam_angle_min": 8,
            "beam_angle_max": 45,
            "beam_angle": 30,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 60.0,
            "size": (70, 70, 90),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_large.png"
    },
    "hmi_12k": {
        "name": "12K HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "12000 Watt HMI fresnel",
        "properties": {
            "power": 12000,
            "beam_angle_min": 7,
            "beam_angle_max": 40,
            "beam_angle": 25,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 90.0,
            "size": (90, 90, 120),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_large.png"
    },
    "hmi_18k": {
        "name": "18K HMI",
        "category": "lights",
        "subcategory": "hmi",
        "description": "18000 Watt HMI fresnel",
        "properties": {
            "power": 18000,
            "beam_angle_min": 6,
            "beam_angle_max": 40,
            "beam_angle": 25,
            "color_temperature": 5600,
            "color": DAYLIGHT_COLOR,
            "weight": 120.0,
            "size": (100, 100, 130),
            "fixture_type": "spotlight",
            "dimmer_compatible": False,
            "equipment_type": "HMI"
        },
        "icon": "hmi_large.png"
    },
    
    # ==== LED LIGHTS ====
    "led_1x1": {
        "name": "1x1 LED Panel",
        "category": "lights",
        "subcategory": "led",
        "description": "1x1 foot LED panel, daylight balanced",
        "properties": {
            "power": 75,
            "beam_angle_min": 95,
            "beam_angle_max": 95,
            "beam_angle": 95,
            "color_temperature": 5600,
            "color_temperature_min": 5600,
            "color_temperature_max": 5600,
            "color": LED_DAYLIGHT_COLOR,
            "weight": 2.0,
            "size": (30, 30, 8),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Panel"
        },
        "icon": "led_panel_small.png"
    },
    "led_1x1_bicolor": {
        "name": "1x1 Bicolor LED Panel",
        "category": "lights",
        "subcategory": "led",
        "description": "1x1 foot LED panel, variable color temperature",
        "properties": {
            "power": 75,
            "beam_angle_min": 95,
            "beam_angle_max": 95,
            "beam_angle": 95,
            "color_temperature": 4300,
            "color_temperature_min": 3000,
            "color_temperature_max": 5600,
            "color": LED_BICOLOR_COLOR,
            "weight": 2.2,
            "size": (30, 30, 8),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Panel"
        },
        "icon": "led_panel_small.png"
    },
    "led_2x1": {
        "name": "2x1 LED Panel",
        "category": "lights",
        "subcategory": "led",
        "description": "2x1 foot LED panel, daylight balanced",
        "properties": {
            "power": 150,
            "beam_angle_min": 95,
            "beam_angle_max": 95,
            "beam_angle": 95,
            "color_temperature": 5600,
            "color_temperature_min": 5600,
            "color_temperature_max": 5600,
            "color": LED_DAYLIGHT_COLOR,
            "weight": 4.0,
            "size": (60, 30, 8),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Panel"
        },
        "icon": "led_panel_medium.png"
    },
    "led_2x1_bicolor": {
        "name": "2x1 Bicolor LED Panel",
        "category": "lights",
        "subcategory": "led",
        "description": "2x1 foot LED panel, variable color temperature",
        "properties": {
            "power": 150,
            "beam_angle_min": 95,
            "beam_angle_max": 95,
            "beam_angle": 95,
            "color_temperature": 4300,
            "color_temperature_min": 3000,
            "color_temperature_max": 5600,
            "color": LED_BICOLOR_COLOR,
            "weight": 4.2,
            "size": (60, 30, 8),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Panel"
        },
        "icon": "led_panel_medium.png"
    },
    "led_4x4": {
        "name": "4x4 LED Panel",
        "category": "lights",
        "subcategory": "led",
        "description": "4x4 foot LED panel, daylight balanced",
        "properties": {
            "power": 600,
            "beam_angle_min": 90,
            "beam_angle_max": 90,
            "beam_angle": 90,
            "color_temperature": 5600,
            "color_temperature_min": 5600,
            "color_temperature_max": 5600,
            "color": LED_DAYLIGHT_COLOR,
            "weight": 15.0,
            "size": (120, 120, 10),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Panel"
        },
        "icon": "led_panel_large.png"
    },
    "led_tube_4ft": {
        "name": "4ft LED Tube",
        "category": "lights",
        "subcategory": "led",
        "description": "4 foot LED tube light, daylight balanced",
        "properties": {
            "power": 60,
            "beam_angle_min": 180,
            "beam_angle_max": 180,
            "beam_angle": 180,
            "color_temperature": 5600,
            "color_temperature_min": 5600,
            "color_temperature_max": 5600,
            "color": LED_DAYLIGHT_COLOR,
            "weight": 1.5,
            "size": (120, 5, 5),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Tube"
        },
        "icon": "led_tube.png"
    },
    "led_ring_18inch": {
        "name": "18\" LED Ring Light",
        "category": "lights",
        "subcategory": "led",
        "description": "18 inch LED ring light",
        "properties": {
            "power": 90,
            "beam_angle_min": 110,
            "beam_angle_max": 110,
            "beam_angle": 110,
            "color_temperature": 5600,
            "color_temperature_min": 3200,
            "color_temperature_max": 5600,
            "color": LED_BICOLOR_COLOR,
            "weight": 2.5,
            "size": (45, 45, 5),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "LED Ring"
        },
        "icon": "led_ring.png"
    },
    
    # ==== PRACTICAL LIGHTS ====
    "practical_table_lamp": {
        "name": "Table Lamp",
        "category": "lights",
        "subcategory": "practical",
        "description": "Standard table lamp for set",
        "properties": {
            "power": 60,
            "beam_angle_min": 180,
            "beam_angle_max": 180,
            "beam_angle": 180,
            "color_temperature": 2700,
            "color": "#FFE2B7",  # Warm white
            "weight": 1.0,
            "size": (30, 60, 30),
            "fixture_type": "practical",
            "dimmer_compatible": True,
            "equipment_type": "Table Lamp"
        },
        "icon": "practical_table_lamp.png"
    },
    "practical_floor_lamp": {
        "name": "Floor Lamp",
        "category": "lights",
        "subcategory": "practical",
        "description": "Standard floor lamp for set",
        "properties": {
            "power": 100,
            "beam_angle_min": 180,
            "beam_angle_max": 180,
            "beam_angle": 180,
            "color_temperature": 2700,
            "color": "#FFE2B7",  # Warm white
            "weight": 3.0,
            "size": (40, 150, 40),
            "fixture_type": "practical",
            "dimmer_compatible": True,
            "equipment_type": "Floor Lamp"
        },
        "icon": "practical_floor_lamp.png"
    },
    "practical_wall_sconce": {
        "name": "Wall Sconce",
        "category": "lights",
        "subcategory": "practical",
        "description": "Wall-mounted light sconce for set",
        "properties": {
            "power": 40,
            "beam_angle_min": 180,
            "beam_angle_max": 180,
            "beam_angle": 180,
            "color_temperature": 2700,
            "color": "#FFE2B7",  # Warm white
            "weight": 0.8,
            "size": (20, 30, 15),
            "fixture_type": "practical",
            "dimmer_compatible": True,
            "equipment_type": "Wall Sconce"
        },
        "icon": "practical_sconce.png"
    },
    "practical_candle": {
        "name": "Candle",
        "category": "lights",
        "subcategory": "practical",
        "description": "Electric candle with flicker effect",
        "properties": {
            "power": 2,
            "beam_angle_min": 360,
            "beam_angle_max": 360,
            "beam_angle": 360,
            "color_temperature": 1800,
            "color": "#FFBB77",  # Candle flame color
            "weight": 0.1,
            "size": (5, 15, 5),
            "fixture_type": "practical",
            "dimmer_compatible": True,
            "equipment_type": "Candle"
        },
        "icon": "practical_candle.png"
    },
    
    # ==== SPECIALTY LIGHTS ====
    "china_ball_18inch": {
        "name": "18\" China Ball",
        "category": "lights",
        "subcategory": "specialty",
        "description": "18 inch paper lantern with socket",
        "properties": {
            "power": 150,
            "beam_angle_min": 360,
            "beam_angle_max": 360,
            "beam_angle": 360,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 0.5,
            "size": (45, 45, 45),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "China Ball"
        },
        "icon": "specialty_china_ball.png"
    },
    "book_light": {
        "name": "Book Light",
        "category": "lights",
        "subcategory": "specialty",
        "description": "Bounce light with diffusion setup",
        "properties": {
            "power": 0,  # Depends on source light
            "beam_angle_min": 80,
            "beam_angle_max": 80,
            "beam_angle": 80,
            "color_temperature": 0,  # Depends on source light
            "color": "#FFFFFF",
            "weight": 1.0,
            "size": (100, 70, 70),
            "fixture_type": "floodlight",
            "dimmer_compatible": False,
            "equipment_type": "Book Light"
        },
        "icon": "specialty_book_light.png"
    },
    "kino_flo_4ft_4bank": {
        "name": "Kino Flo 4ft 4Bank",
        "category": "lights",
        "subcategory": "specialty",
        "description": "4ft 4-bank fluorescent fixture",
        "properties": {
            "power": 500,
            "beam_angle_min": 160,
            "beam_angle_max": 160,
            "beam_angle": 160,
            "color_temperature": 5500,
            "color": DAYLIGHT_COLOR,
            "weight": 7.5,
            "size": (120, 60, 15),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "Kino Flo"
        },
        "icon": "specialty_kino_flo.png"
    },
    "space_light": {
        "name": "Space Light",
        "category": "lights",
        "subcategory": "specialty",
        "description": "Overhead soft light for area illumination",
        "properties": {
            "power": 6000,
            "beam_angle_min": 270,
            "beam_angle_max": 270,
            "beam_angle": 270,
            "color_temperature": 3200,
            "color": TUNGSTEN_COLOR,
            "weight": 15.0,
            "size": (90, 60, 90),
            "fixture_type": "floodlight",
            "dimmer_compatible": True,
            "equipment_type": "Space Light"
        },
        "icon": "specialty_space_light.png"
    },
    
    # ==== GRIP EQUIPMENT ====
    "c_stand": {
        "name": "C-Stand",
        "category": "grip",
        "subcategory": "stands",
        "description": "Industry standard C-stand with arm and knuckle",
        "properties": {
            "height_min": 75,  # cm
            "height_max": 250,  # cm
            "height": 150,  # default cm
            "weight": 7.0,
            "size": (50, 150, 50),
            "base_diameter": 110,  # cm
            "max_load": 10.0,  # kg
            "material": "Steel",
            "equipment_type": "C-Stand"
        },
        "icon": "grip_c_stand.png"
    },
    "light_stand": {
        "name": "Light Stand",
        "category": "grip",
        "subcategory": "stands",
        "description": "Standard light stand",
        "properties": {
            "height_min": 90,  # cm
            "height_max": 300,  # cm
            "height": 200,  # default cm
            "weight": 4.0,
            "size": (40, 200, 40),
            "base_diameter": 90,  # cm
            "max_load": 8.0,  # kg
            "material": "Aluminum",
            "equipment_type": "Light Stand"
        },
        "icon": "grip_light_stand.png"
    },
    "sandbag_15lb": {
        "name": "15lb Sandbag",
        "category": "grip",
        "subcategory": "stands",
        "description": "15lb sandbag for stand stabilization",
        "properties": {
            "weight": 6.8,  # kg (15lb)
            "size": (30, 10, 20),
            "material": "Fabric/Sand",
            "equipment_type": "Sandbag"
        },
        "icon": "grip_sandbag.png"
    },
    "apple_box_full": {
        "name": "Apple Box (Full)",
        "category": "grip",
        "subcategory": "stands",
        "description": "Full-size apple box for grip needs",
        "properties": {
            "height": 20.3,  # cm (8 inches)
            "weight": 5.0,
            "size": (50.8, 20.3, 30.5),  # cm (20" x 8" x 12")
            "material": "Wood",
            "equipment_type": "Apple Box"
        },
        "icon": "grip_apple_box.png"
    },
    "flag_24x36": {
        "name": "24\"x36\" Flag",
        "category": "grip",
        "subcategory": "control",
        "description": "24\"x36\" solid flag for blocking light",
        "properties": {
            "width": 91.4,  # cm (36 inches)
            "height": 61.0,  # cm (24 inches)
            "weight": 2.0,
            "size": (91.4, 61.0, 2),
            "material": "Fabric",
            "equipment_type": "Flag"
        },
        "icon": "grip_flag.png"
    }
})  # Close both the dictionary and the update() method
