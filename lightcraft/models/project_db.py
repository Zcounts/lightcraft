"""
Database management for LightCraft application.
Provides SQLite storage for projects, scenes, and version history.
"""

import os
import sqlite3
import json
import time
import uuid
import shutil
from datetime import datetime
from PIL import Image
from io import BytesIO

from lightcraft.config import APP_DATA_DIR, DATABASE_FILE


class ProjectDatabase:
    """
    Database manager for LightCraft projects.
    Handles persistence of project data using SQLite.
    """
    
    def __init__(self):
        """Initialize the project database."""
        # Ensure the data directory exists
        if not os.path.exists(APP_DATA_DIR):
            os.makedirs(APP_DATA_DIR)
        
        # Database file path
        self.db_file = DATABASE_FILE
        
        # Initialize database connection
        self.conn = None
        self.cursor = None
        
        # Connect to database
        self.connect()
        
        # Initialize database schema if needed
        self._init_db()
    
    def connect(self):
        """Connect to the SQLite database."""
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        try:
            # Create projects table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_opened_at TEXT,
                data TEXT,
                thumbnail BLOB,
                file_path TEXT
            )
            ''')
            
            # Create scenes table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scenes (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                data TEXT,
                thumbnail BLOB,
                order_index INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
            ''')
            
            # Create versions table for history
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS versions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                scene_id TEXT,
                version_number INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT,
                thumbnail BLOB,
                description TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (scene_id) REFERENCES scenes (id) ON DELETE CASCADE
            )
            ''')
            
            # Create settings table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            ''')
            
            # Create auto_save table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS auto_save (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                scene_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (scene_id) REFERENCES scenes (id) ON DELETE CASCADE
            )
            ''')
            
            # Insert default settings if not exists
            self.cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('auto_save_interval', '300'),
                   ('max_version_history', '10'),
                   ('recent_projects_limit', '5')
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
    
    def create_project(self, project_data):
        """
        Create a new project in the database.
        
        Args:
            project_data: Dictionary with project data
        
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            # Generate UUID if not provided
            if 'id' not in project_data:
                project_data['id'] = str(uuid.uuid4())
            
            # Set timestamps if not provided
            current_time = datetime.now().isoformat()
            if 'created_at' not in project_data:
                project_data['created_at'] = current_time
            if 'updated_at' not in project_data:
                project_data['updated_at'] = current_time
            
            # Extract data for JSON storage
            data_json = {}
            for key in list(project_data.keys()):
                if key not in ['id', 'name', 'description', 'created_at', 
                               'updated_at', 'last_opened_at', 'thumbnail', 'file_path']:
                    data_json[key] = project_data.pop(key)
            
            project_data['data'] = json.dumps(data_json)
            
            # Set last_opened_at if not provided
            if 'last_opened_at' not in project_data:
                project_data['last_opened_at'] = current_time
            
            # Create default scene if needed
            if 'create_default_scene' in project_data and project_data['create_default_scene']:
                scene_data = {
                    'project_id': project_data['id'],
                    'name': 'Main Scene',
                    'description': 'Default scene',
                    'order_index': 0
                }
                self.create_scene(scene_data)
            
            self.conn.commit()
            return project_data['id']
        except sqlite3.Error as e:
            print(f"Error creating project: {e}")
            self.conn.rollback()
            return None
    
    def update_project(self, project_id, project_data):
        """
        Update an existing project.
        
        Args:
            project_id: ID of the project to update
            project_data: Dictionary with updated project data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update timestamp
            project_data['updated_at'] = datetime.now().isoformat()
            
            # Get existing project data
            self.cursor.execute('''
            SELECT data FROM projects WHERE id = ?
            ''', (project_id,))
            
            existing_data = {}
            row = self.cursor.fetchone()
            if row and row['data']:
                existing_data = json.loads(row['data'])
            
            # Extract data for JSON storage
            data_json = existing_data
            for key in list(project_data.keys()):
                if key not in ['id', 'name', 'description', 'created_at', 
                               'updated_at', 'last_opened_at', 'thumbnail', 'file_path']:
                    data_json[key] = project_data.pop(key)
            
            project_data['data'] = json.dumps(data_json)
            
            # Build update query
            update_fields = []
            params = {}
            
            for key, value in project_data.items():
                update_fields.append(f"{key} = :{key}")
                params[key] = value
            
            params['id'] = project_id
            
            query = f'''
            UPDATE projects SET {', '.join(update_fields)}
            WHERE id = :id
            '''
            
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating project: {e}")
            self.conn.rollback()
            return False
    
    def get_project(self, project_id):
        """
        Get a project by ID.
        
        Args:
            project_id: ID of the project to retrieve
        
        Returns:
            Dictionary with project data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT * FROM projects WHERE id = ?
            ''', (project_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dictionary
            project = dict(row)
            
            # Parse JSON data field
            if project['data']:
                data_json = json.loads(project['data'])
                # Add data fields to project dictionary
                for key, value in data_json.items():
                    project[key] = value
            
            # Remove JSON data field from result
            project.pop('data')
            
            return project
        except sqlite3.Error as e:
            print(f"Error retrieving project: {e}")
            return None
    
    def delete_project(self, project_id):
        """
        Delete a project and all its scenes.
        
        Args:
            project_id: ID of the project to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete project (cascade will delete scenes and versions)
            self.cursor.execute('''
            DELETE FROM projects WHERE id = ?
            ''', (project_id,))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting project: {e}")
            self.conn.rollback()
            return False
    
    def get_all_projects(self):
        """
        Get all projects.
        
        Returns:
            List of project dictionaries
        """
        try:
            self.cursor.execute('''
            SELECT id, name, description, created_at, updated_at, 
                   last_opened_at, file_path
            FROM projects
            ORDER BY updated_at DESC
            ''')
            
            projects = []
            for row in self.cursor.fetchall():
                project = dict(row)
                projects.append(project)
            
            return projects
        except sqlite3.Error as e:
            print(f"Error retrieving projects: {e}")
            return []
    
    def get_recent_projects(self, limit=5):
        """
        Get recent projects.
        
        Args:
            limit: Maximum number of projects to return
        
        Returns:
            List of project dictionaries
        """
        try:
            self.cursor.execute('''
            SELECT id, name, description, created_at, updated_at, 
                   last_opened_at, file_path
            FROM projects
            ORDER BY last_opened_at DESC
            LIMIT ?
            ''', (limit,))
            
            projects = []
            for row in self.cursor.fetchall():
                project = dict(row)
                projects.append(project)
            
            return projects
        except sqlite3.Error as e:
            print(f"Error retrieving recent projects: {e}")
            return []
    
    def update_project_thumbnail(self, project_id, thumbnail_data):
        """
        Update a project's thumbnail.
        
        Args:
            project_id: ID of the project
            thumbnail_data: Thumbnail image data (bytes)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute('''
            UPDATE projects
            SET thumbnail = ?, updated_at = ?
            WHERE id = ?
            ''', (thumbnail_data, datetime.now().isoformat(), project_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating project thumbnail: {e}")
            self.conn.rollback()
            return False
    
    def get_project_thumbnail(self, project_id):
        """
        Get a project's thumbnail.
        
        Args:
            project_id: ID of the project
        
        Returns:
            Thumbnail data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT thumbnail FROM projects WHERE id = ?
            ''', (project_id,))
            
            row = self.cursor.fetchone()
            if row:
                return row['thumbnail']
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving project thumbnail: {e}")
            return None
    
    def create_scene(self, scene_data):
        """
        Create a new scene.
        
        Args:
            scene_data: Dictionary with scene data
        
        Returns:
            Scene ID if successful, None otherwise
        """
        try:
            # Generate UUID if not provided
            if 'id' not in scene_data:
                scene_data['id'] = str(uuid.uuid4())
            
            # Set timestamps if not provided
            current_time = datetime.now().isoformat()
            if 'created_at' not in scene_data:
                scene_data['created_at'] = current_time
            if 'updated_at' not in scene_data:
                scene_data['updated_at'] = current_time
            
            # Get next order index if not provided
            if 'order_index' not in scene_data:
                self.cursor.execute('''
                SELECT MAX(order_index) as max_index
                FROM scenes
                WHERE project_id = ?
                ''', (scene_data['project_id'],))
                
                row = self.cursor.fetchone()
                max_index = row['max_index'] if row and row['max_index'] is not None else -1
                scene_data['order_index'] = max_index + 1
            
            # Extract data for JSON storage
            data_json = {}
            for key in list(scene_data.keys()):
                if key not in ['id', 'project_id', 'name', 'description', 
                               'created_at', 'updated_at', 'thumbnail', 'order_index']:
                    data_json[key] = scene_data.pop(key)
            
            scene_data['data'] = json.dumps(data_json)
            
            # Insert scene
            self.cursor.execute('''
            INSERT INTO scenes (id, project_id, name, description, created_at, 
                               updated_at, data, thumbnail, order_index)
            VALUES (:id, :project_id, :name, :description, :created_at, 
                    :updated_at, :data, :thumbnail, :order_index)
            ''', scene_data)
            
            # Update project updated_at timestamp
            self.cursor.execute('''
            UPDATE projects
            SET updated_at = ?
            WHERE id = ?
            ''', (current_time, scene_data['project_id']))
            
            self.conn.commit()
            return scene_data['id']
        except sqlite3.Error as e:
            print(f"Error creating scene: {e}")
            self.conn.rollback()
            return None
    
    def update_scene(self, scene_id, scene_data):
        """
        Update an existing scene.
        
        Args:
            scene_id: ID of the scene to update
            scene_data: Dictionary with updated scene data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update timestamp
            current_time = datetime.now().isoformat()
            scene_data['updated_at'] = current_time
            
            # Get existing scene data
            self.cursor.execute('''
            SELECT data, project_id FROM scenes WHERE id = ?
            ''', (scene_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return False
            
            existing_data = {}
            if row['data']:
                existing_data = json.loads(row['data'])
            
            project_id = row['project_id']
            
            # Extract data for JSON storage
            data_json = existing_data
            for key in list(scene_data.keys()):
                if key not in ['id', 'project_id', 'name', 'description', 
                              'created_at', 'updated_at', 'thumbnail', 'order_index']:
                    data_json[key] = scene_data.pop(key)
            
            scene_data['data'] = json.dumps(data_json)
            
            # Build update query
            update_fields = []
            params = {}
            
            for key, value in scene_data.items():
                update_fields.append(f"{key} = :{key}")
                params[key] = value
            
            params['id'] = scene_id
            
            query = f'''
            UPDATE scenes SET {', '.join(update_fields)}
            WHERE id = :id
            '''
            
            self.cursor.execute(query, params)
            
            # Update project updated_at timestamp
            self.cursor.execute('''
            UPDATE projects
            SET updated_at = ?
            WHERE id = ?
            ''', (current_time, project_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating scene: {e}")
            self.conn.rollback()
            return False
    
    def get_scene(self, scene_id):
        """
        Get a scene by ID.
        
        Args:
            scene_id: ID of the scene to retrieve
        
        Returns:
            Dictionary with scene data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT * FROM scenes WHERE id = ?
            ''', (scene_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dictionary
            scene = dict(row)
            
            # Parse JSON data field
            if scene['data']:
                data_json = json.loads(scene['data'])
                # Add data fields to scene dictionary
                for key, value in data_json.items():
                    scene[key] = value
            
            # Remove JSON data field from result
            scene.pop('data')
            
            return scene
        except sqlite3.Error as e:
            print(f"Error retrieving scene: {e}")
            return None
    
    def delete_scene(self, scene_id):
        """
        Delete a scene.
        
        Args:
            scene_id: ID of the scene to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get project ID for the scene
            self.cursor.execute('''
            SELECT project_id FROM scenes WHERE id = ?
            ''', (scene_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return False
            
            project_id = row['project_id']
            
            # Get the order index of the scene to delete
            self.cursor.execute('''
            SELECT order_index FROM scenes WHERE id = ?
            ''', (scene_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return False
            
            deleted_index = row['order_index']
            
            # Delete the scene
            self.cursor.execute('''
            DELETE FROM scenes WHERE id = ?
            ''', (scene_id,))
            
            # Update order_index of scenes with higher order_index
            self.cursor.execute('''
            UPDATE scenes 
            SET order_index = order_index - 1
            WHERE project_id = ? AND order_index > ?
            ''', (project_id, deleted_index))
            
            # Update project updated_at timestamp
            self.cursor.execute('''
            UPDATE projects
            SET updated_at = ?
            WHERE id = ?
            ''', (datetime.now().isoformat(), project_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting scene: {e}")
            self.conn.rollback()
            return False
    
    def get_project_scenes(self, project_id):
        """
        Get all scenes for a project.
        
        Args:
            project_id: ID of the project
        
        Returns:
            List of scene dictionaries
        """
        try:
            self.cursor.execute('''
            SELECT id, name, description, created_at, updated_at, order_index
            FROM scenes
            WHERE project_id = ?
            ORDER BY order_index
            ''', (project_id,))
            
            scenes = []
            for row in self.cursor.fetchall():
                scene = dict(row)
                scenes.append(scene)
            
            return scenes
        except sqlite3.Error as e:
            print(f"Error retrieving project scenes: {e}")
            return []
    
    def update_scene_thumbnail(self, scene_id, thumbnail_data):
        """
        Update a scene's thumbnail.
        
        Args:
            scene_id: ID of the scene
            thumbnail_data: Thumbnail image data (bytes)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute('''
            UPDATE scenes
            SET thumbnail = ?, updated_at = ?
            WHERE id = ?
            ''', (thumbnail_data, datetime.now().isoformat(), scene_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating scene thumbnail: {e}")
            self.conn.rollback()
            return False
    
    def get_scene_thumbnail(self, scene_id):
        """
        Get a scene's thumbnail.
        
        Args:
            scene_id: ID of the scene
        
        Returns:
            Thumbnail data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT thumbnail FROM scenes WHERE id = ?
            ''', (scene_id,))
            
            row = self.cursor.fetchone()
            if row:
                return row['thumbnail']
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving scene thumbnail: {e}")
            return None
    
    def reorder_scenes(self, project_id, scene_order):
        """
        Update the order of scenes in a project.
        
        Args:
            project_id: ID of the project
            scene_order: List of scene IDs in the new order
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for index, scene_id in enumerate(scene_order):
                self.cursor.execute('''
                UPDATE scenes
                SET order_index = ?
                WHERE id = ? AND project_id = ?
                ''', (index, scene_id, project_id))
            
            # Update project updated_at timestamp
            self.cursor.execute('''
            UPDATE projects
            SET updated_at = ?
            WHERE id = ?
            ''', (datetime.now().isoformat(), project_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error reordering scenes: {e}")
            self.conn.rollback()
            return False
    
    def duplicate_scene(self, scene_id, new_name=None):
        """
        Duplicate a scene.
        
        Args:
            scene_id: ID of the scene to duplicate
            new_name: Optional name for the new scene
        
        Returns:
            ID of the new scene if successful, None otherwise
        """
        try:
            # Get the scene to duplicate
            original_scene = self.get_scene(scene_id)
            if not original_scene:
                return None
            
            # Create new scene data
            new_scene = original_scene.copy()
            new_scene.pop('id')
            
            if new_name:
                new_scene['name'] = new_name
            else:
                new_scene['name'] = f"Copy of {original_scene['name']}"
            
            # Create the new scene
            return self.create_scene(new_scene)
        except Exception as e:
            print(f"Error duplicating scene: {e}")
            self.conn.rollback()
            return None
    
    def create_version(self, project_id, scene_id, data, description=None):
        """
        Create a version entry for a project or scene.
        
        Args:
            project_id: ID of the project
            scene_id: ID of the scene (can be None for project version)
            data: Version data (JSON serializable)
            description: Optional description for the version
        
        Returns:
            Version ID if successful, None otherwise
        """
        try:
            # Get next version number
            if scene_id:
                self.cursor.execute('''
                SELECT MAX(version_number) as max_version
                FROM versions
                WHERE project_id = ? AND scene_id = ?
                ''', (project_id, scene_id))
            else:
                self.cursor.execute('''
                SELECT MAX(version_number) as max_version
                FROM versions
                WHERE project_id = ? AND scene_id IS NULL
                ''', (project_id,))
            
            row = self.cursor.fetchone()
            max_version = row['max_version'] if row and row['max_version'] is not None else 0
            version_number = max_version + 1
            
            # Create version entry
            version_id = str(uuid.uuid4())
            version_data = {
                "id": version_id,
                "project_id": project_id,
                "scene_id": scene_id,
                "version_number": version_number,
                "created_at": datetime.now().isoformat(),
                "data": json.dumps(data),
                "description": description
            }
            
            self.cursor.execute('''
            INSERT INTO versions (id, project_id, scene_id, version_number, 
                                 created_at, data, thumbnail, description)
            VALUES (:id, :project_id, :scene_id, :version_number, 
                    :created_at, :data, :thumbnail, :description)
            ''', version_data)
            
            # Clean up old versions if needed
            self._cleanup_old_versions(project_id, scene_id)
            
            self.conn.commit()
            return version_id
        except sqlite3.Error as e:
            print(f"Error creating version: {e}")
            self.conn.rollback()
            return None
    
    def _cleanup_old_versions(self, project_id, scene_id):
        """
        Clean up old versions exceeding the limit.
        
        Args:
            project_id: ID of the project
            scene_id: ID of the scene (can be None)
        """
        try:
            # Get max version history setting
            self.cursor.execute('''
            SELECT value FROM settings WHERE key = 'max_version_history'
            ''')
            
            row = self.cursor.fetchone()
            max_versions = int(row['value']) if row else 10
            
            # Get current version count
            if scene_id:
                self.cursor.execute('''
                SELECT COUNT(*) as version_count
                FROM versions
                WHERE project_id = ? AND scene_id = ?
                ''', (project_id, scene_id))
            else:
                self.cursor.execute('''
                SELECT COUNT(*) as version_count
                FROM versions
                WHERE project_id = ? AND scene_id IS NULL
                ''', (project_id,))
            
            row = self.cursor.fetchone()
            version_count = row['version_count'] if row else 0
            
            # Delete oldest versions if needed
            if version_count > max_versions:
                to_delete = version_count - max_versions
                
                if scene_id:
                    self.cursor.execute('''
                    DELETE FROM versions
                    WHERE id IN (
                        SELECT id FROM versions
                        WHERE project_id = ? AND scene_id = ?
                        ORDER BY version_number ASC
                        LIMIT ?
                    )
                    ''', (project_id, scene_id, to_delete))
                else:
                    self.cursor.execute('''
                    DELETE FROM versions
                    WHERE id IN (
                        SELECT id FROM versions
                        WHERE project_id = ? AND scene_id IS NULL
                        ORDER BY version_number ASC
                        LIMIT ?
                    )
                    ''', (project_id, to_delete))
        except sqlite3.Error as e:
            print(f"Error cleaning up old versions: {e}")
    
    def get_versions(self, project_id, scene_id=None):
        """
        Get versions for a project or scene.
        
        Args:
            project_id: ID of the project
            scene_id: Optional ID of the scene
        
        Returns:
            List of version dictionaries
        """
        try:
            if scene_id:
                self.cursor.execute('''
                SELECT id, version_number, created_at, description
                FROM versions
                WHERE project_id = ? AND scene_id = ?
                ORDER BY version_number DESC
                ''', (project_id, scene_id))
            else:
                self.cursor.execute('''
                SELECT id, version_number, created_at, description
                FROM versions
                WHERE project_id = ? AND scene_id IS NULL
                ORDER BY version_number DESC
                ''', (project_id,))
            
            versions = []
            for row in self.cursor.fetchall():
                version = dict(row)
                versions.append(version)
            
            return versions
        except sqlite3.Error as e:
            print(f"Error retrieving versions: {e}")
            return []
    
    def get_version_data(self, version_id):
        """
        Get data for a specific version.
        
        Args:
            version_id: ID of the version
        
        Returns:
            Version data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT data FROM versions WHERE id = ?
            ''', (version_id,))
            
            row = self.cursor.fetchone()
            if row and row['data']:
                return json.loads(row['data'])
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving version data: {e}")
            return None
    
    def create_auto_save(self, project_id, scene_id, data):
        """
        Create or update an auto-save entry.
        
        Args:
            project_id: ID of the project
            scene_id: ID of the scene
            data: Auto-save data (JSON serializable)
        
        Returns:
            Auto-save ID if successful, None otherwise
        """
        try:
            # Check if auto-save already exists
            self.cursor.execute('''
            SELECT id FROM auto_save
            WHERE project_id = ? AND scene_id = ?
            ''', (project_id, scene_id))
            
            row = self.cursor.fetchone()
            auto_save_id = row['id'] if row else str(uuid.uuid4())
            
            # Create or update auto-save
            if row:
                self.cursor.execute('''
                UPDATE auto_save
                SET data = ?, created_at = ?
                WHERE id = ?
                ''', (json.dumps(data), datetime.now().isoformat(), auto_save_id))
            else:
                self.cursor.execute('''
                INSERT INTO auto_save (id, project_id, scene_id, created_at, data)
                VALUES (?, ?, ?, ?, ?)
                ''', (auto_save_id, project_id, scene_id, datetime.now().isoformat(), json.dumps(data)))
            
            self.conn.commit()
            return auto_save_id
        except sqlite3.Error as e:
            print(f"Error creating auto-save: {e}")
            self.conn.rollback()
            return None
    
    def get_auto_save(self, project_id, scene_id):
        """
        Get auto-save data for a scene.
        
        Args:
            project_id: ID of the project
            scene_id: ID of the scene
        
        Returns:
            Auto-save data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT data, created_at FROM auto_save
            WHERE project_id = ? AND scene_id = ?
            ''', (project_id, scene_id))
            
            row = self.cursor.fetchone()
            if row and row['data']:
                return {
                    'data': json.loads(row['data']),
                    'created_at': row['created_at']
                }
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving auto-save: {e}")
            return None
    
    def clear_auto_save(self, project_id, scene_id):
        """
        Delete auto-save data for a scene.
        
        Args:
            project_id: ID of the project
            scene_id: ID of the scene
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute('''
            DELETE FROM auto_save
            WHERE project_id = ? AND scene_id = ?
            ''', (project_id, scene_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing auto-save: {e}")
            self.conn.rollback()
            return False
    
    def get_setting(self, key, default=None):
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if setting not found
        
        Returns:
            Setting value or default
        """
        try:
            self.cursor.execute('''
            SELECT value FROM settings WHERE key = ?
            ''', (key,))
            
            row = self.cursor.fetchone()
            if row:
                return row['value']
            return default
        except sqlite3.Error as e:
            print(f"Error retrieving setting: {e}")
            return default
    
    def set_setting(self, key, value):
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
            ''', (key, value))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving setting: {e}")
            self.conn.rollback()
            return False
    
    def backup_database(self, backup_path=None):
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional path for the backup file
        
        Returns:
            Path to the backup file if successful, None otherwise
        """
        try:
            # Disconnect from current database to ensure it's flushed
            self.disconnect()
            
            # Generate backup path if not provided
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(APP_DATA_DIR, f"lightcraft_backup_{timestamp}.db")
            
            # Copy database file
            shutil.copy2(self.db_file, backup_path)
            
            # Reconnect to database
            self.connect()
            
            return backup_path
        except Exception as e:
            print(f"Error backing up database: {e}")
            # Make sure we're reconnected
            self.connect()
            return None
    
    def export_project(self, project_id, export_path):
        """
        Export a project to a standalone file.
        
        Args:
            project_id: ID of the project to export
            export_path: Path to the export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get project data
            project = self.get_project(project_id)
            if not project:
                return False
            
            # Get all scenes for the project
            scenes = self.get_project_scenes(project_id)
            
            # Get full scene data
            full_scenes = []
            for scene in scenes:
                scene_data = self.get_scene(scene['id'])
                scene_data['thumbnail'] = self.get_scene_thumbnail(scene['id'])
                full_scenes.append(scene_data)
            
            # Create export data
            export_data = {
                'project': project,
                'scenes': full_scenes,
                'format_version': '1.0',
                'export_date': datetime.now().isoformat()
            }
            
            # Add project thumbnail
            export_data['project']['thumbnail'] = self.get_project_thumbnail(project_id)
            
            # Write to file
            with open(export_path, 'w') as f:
                json.dump(export_data, f)
            
            return True
        except Exception as e:
            print(f"Error exporting project: {e}")
            return False
    
    def import_project(self, import_path):
        """
        Import a project from a file.
        
        Args:
            import_path: Path to the import file
        
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            # Read import file
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            # Check format version
            if 'format_version' not in import_data:
                print("Invalid import file format")
                return None
            
            # Extract project and scenes
            project_data = import_data['project']
            scenes_data = import_data['scenes']
            
            # Generate new IDs to avoid conflicts
            old_project_id = project_data['id']
            new_project_id = str(uuid.uuid4())
            id_mapping = {old_project_id: new_project_id}
            
            # Update project ID and other fields
            project_data['id'] = new_project_id
            project_data['imported_at'] = datetime.now().isoformat()
            project_data['file_path'] = None
            
            # Create project
            self.create_project(project_data)
            
            # Create scenes
            for scene_data in scenes_data:
                old_scene_id = scene_data['id']
                new_scene_id = str(uuid.uuid4())
                id_mapping[old_scene_id] = new_scene_id
                
                scene_data['id'] = new_scene_id
                scene_data['project_id'] = new_project_id
                
                self.create_scene(scene_data)
            
            return new_project_id
        except Exception as e:
            print(f"Error importing project: {e}")
            return None
    
    def generate_thumbnail_from_scene(self, scene_id, width=200, height=150):
        """
        Generate a thumbnail image from scene data.
        This is a placeholder that would be implemented based on the rendering system.
        
        Args:
            scene_id: ID of the scene
            width: Width of the thumbnail
            height: Height of the thumbnail
        
        Returns:
            Thumbnail image data (bytes) or None if generation failed
        """
        # This would use the scene rendering system to create a thumbnail
        # For now, we'll create a simple placeholder
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a blank image
            image = Image.new('RGB', (width, height), color=(240, 240, 240))
            draw = ImageDraw.Draw(image)
            
            # Get scene data
            scene = self.get_scene(scene_id)
            if not scene:
                return None
            
            # Draw scene name
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            draw.text((10, 10), scene['name'], fill=(0, 0, 0), font=font)
            
            # Draw project ID and scene ID
            draw.text((10, 30), f"Scene: {scene_id[:8]}...", fill=(100, 100, 100), font=font)
            
            # Draw border
            draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200))
            
            # Save to bytes
            byte_arr = BytesIO()
            image.save(byte_arr, format='PNG')
            return byte_arr.getvalue()
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
