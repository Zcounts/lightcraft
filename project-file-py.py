"""
Project file format for the LightCraft application.
Handles serialization and deserialization of project files.
"""

import os
import json
import zipfile
import tempfile
from datetime import datetime
from io import BytesIO


class ProjectFile:
    """
    Project file manager for LightCraft.
    Handles saving and loading project files (.lightcraft).
    """
    
    # File format version
    FORMAT_VERSION = "1.0"
    
    # File signature
    FILE_SIGNATURE = "LIGHTCRAFT_PROJECT"
    
    @staticmethod
    def save_project(file_path, project_data, scenes_data, thumbnails=None):
        """
        Save a project to a file.
        
        Args:
            file_path: Path to save to
            project_data: Dictionary with project data
            scenes_data: List of dictionaries with scene data
            thumbnails: Dictionary mapping scene IDs to thumbnail data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a temporary directory for project files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create project.json with project and scenes data
                metadata = {
                    "signature": ProjectFile.FILE_SIGNATURE,
                    "format_version": ProjectFile.FORMAT_VERSION,
                    "export_date": datetime.now().isoformat(),
                    "project": project_data,
                    "scenes": scenes_data
                }
                
                with open(os.path.join(temp_dir, "project.json"), "w") as f:
                    json.dump(metadata, f, indent=2)
                
                # Save thumbnails if provided
                if thumbnails:
                    thumbnails_dir = os.path.join(temp_dir, "thumbnails")
                    os.makedirs(thumbnails_dir, exist_ok=True)
                    
                    for scene_id, thumbnail_data in thumbnails.items():
                        if thumbnail_data:
                            with open(os.path.join(thumbnails_dir, f"{scene_id}.png"), "wb") as f:
                                f.write(thumbnail_data)
                
                # Create zip file
                with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    # Add project.json
                    zf.write(os.path.join(temp_dir, "project.json"), "project.json")
                    
                    # Add thumbnails if available
                    if thumbnails and os.path.exists(thumbnails_dir):
                        for filename in os.listdir(thumbnails_dir):
                            zf.write(os.path.join(thumbnails_dir, filename), 
                                    os.path.join("thumbnails", filename))
            
            return True
        except Exception as e:
            print(f"Error saving project file: {e}")
            return False
    
    @staticmethod
    def load_project(file_path):
        """
        Load a project from a file.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            Tuple containing (project_data, scenes_data, thumbnails) or (None, None, None) if failed
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Project file not found: {file_path}")
            
            # Create a temporary directory for extracting files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract zip file
                with zipfile.ZipFile(file_path, "r") as zf:
                    zf.extractall(temp_dir)
                
                # Load project.json
                with open(os.path.join(temp_dir, "project.json"), "r") as f:
                    metadata = json.load(f)
                
                # Validate file signature and format version
                if "signature" not in metadata or metadata["signature"] != ProjectFile.FILE_SIGNATURE:
                    raise ValueError("Invalid project file signature")
                
                if "format_version" not in metadata:
                    raise ValueError("Missing format version")
                
                # Extract project and scenes data
                project_data = metadata.get("project")
                scenes_data = metadata.get("scenes", [])
                
                # Load thumbnails
                thumbnails = {}
                thumbnails_dir = os.path.join(temp_dir, "thumbnails")
                if os.path.exists(thumbnails_dir):
                    for filename in os.listdir(thumbnails_dir):
                        if filename.endswith(".png"):
                            scene_id = os.path.splitext(filename)[0]
                            with open(os.path.join(thumbnails_dir, filename), "rb") as f:
                                thumbnails[scene_id] = f.read()
                
                return project_data, scenes_data, thumbnails
        except Exception as e:
            print(f"Error loading project file: {e}")
            return None, None, None
    
    @staticmethod
    def extract_project_info(file_path):
        """
        Extract basic information from a project file without fully loading it.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            Dictionary with basic project information or None if failed
        """
        try:
            # Open zip file
            with zipfile.ZipFile(file_path, "r") as zf:
                # Check if project.json exists
                if "project.json" not in zf.namelist():
                    raise ValueError("Invalid project file format")
                
                # Read project.json
                with zf.open("project.json") as f:
                    metadata = json.load(f)
                
                # Validate file signature
                if "signature" not in metadata or metadata["signature"] != ProjectFile.FILE_SIGNATURE:
                    raise ValueError("Invalid project file signature")
                
                # Extract basic project info
                project_info = {}
                if "project" in metadata:
                    project = metadata["project"]
                    project_info["name"] = project.get("name", "Unnamed Project")
                    project_info["description"] = project.get("description", "")
                    project_info["created_at"] = project.get("created_at", "")
                    project_info["updated_at"] = project.get("updated_at", "")
                
                # Count scenes
                project_info["scene_count"] = len(metadata.get("scenes", []))
                
                # Get format version
                project_info["format_version"] = metadata.get("format_version", "")
                
                # Get export date
                project_info["export_date"] = metadata.get("export_date", "")
                
                return project_info
        except Exception as e:
            print(f"Error extracting project info: {e}")
            return None
    
    @staticmethod
    def extract_thumbnail(file_path):
        """
        Extract the first scene thumbnail from a project file.
        
        Args:
            file_path: Path to the project file
        
        Returns:
            Thumbnail data or None if failed
        """
        try:
            # Open zip file
            with zipfile.ZipFile(file_path, "r") as zf:
                # Check if thumbnails directory exists
                thumbnail_files = [name for name in zf.namelist() 
                                 if name.startswith("thumbnails/") and name.endswith(".png")]
                
                if not thumbnail_files:
                    return None
                
                # Get first thumbnail
                with zf.open(thumbnail_files[0]) as f:
                    return f.read()
        except Exception as e:
            print(f"Error extracting thumbnail: {e}")
            return None
