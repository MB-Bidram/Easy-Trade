"""
Project compression and serialization utilities
"""

import zipfile
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from backend.config import settings
from backend.utils.helpers import (
    generate_unique_id,
    get_timestamp_str,
    ensure_directory_exists,
    write_json_file,
    read_json_file,
    calculate_file_hash,
    get_file_size
)
from backend.utils.exceptions import CompressionError, DecompressionError


class ProjectManager:
    """Manager for project compression, decompression, and serialization"""

    @staticmethod
    def serialize_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize project to dictionary format.
        
        Args:
            project_data: Project data dictionary
        
        Returns:
            Serialized project dictionary
        """
        return {
            "id": project_data.get("id"),
            "name": project_data.get("name"),
            "description": project_data.get("description"),
            "type": project_data.get("project_type", "checklist"),
            "created_at": project_data.get("created_at"),
            "updated_at": project_data.get("updated_at"),
            "version": project_data.get("version", 1),
            "is_archived": project_data.get("is_archived", False),
            "metadata": project_data.get("metadata", {})
        }

    @staticmethod
    def deserialize_project(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize project from dictionary format.
        
        Args:
            data: Serialized project dictionary
        
        Returns:
            Project data dictionary
        """
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "description": data.get("description"),
            "project_type": data.get("type", "checklist"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "version": data.get("version", 1),
            "is_archived": data.get("is_archived", False),
            "metadata": data.get("metadata", {})
        }

    @staticmethod
    def compress_project(
        project_id: str,
        project_data: Dict[str, Any],
        checklists: list = None,
        notes: list = None,
        images_dir: str = None,
        tables: list = None,
        output_dir: str = None
    ) -> str:
        """
        Compress project to ZIP file.
        
        Args:
            project_id: Project UUID
            project_data: Project metadata
            checklists: List of checklist data
            notes: List of note data
            images_dir: Directory containing images
            tables: List of table data
            output_dir: Output directory for ZIP file
        
        Returns:
            Path to created ZIP file
        """
        try:
            if output_dir is None:
                output_dir = f"{settings.projects_dir}/{project_id}"
            
            ensure_directory_exists(output_dir)
            
            zip_path = os.path.join(output_dir, f"{project_id}_project.zip")
            file_list = []
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                # Add project metadata
                project_json = ProjectManager.serialize_project(project_data)
                project_json["compression_date"] = get_timestamp_str()
                zipf.writestr("project.json", json.dumps(project_json, indent=2))
                file_list.append({"name": "project.json", "size": len(json.dumps(project_json))})
                
                # Add checklists
                if checklists:
                    for idx, checklist in enumerate(checklists):
                        checklist_json = json.dumps(checklist, default=str, indent=2)
                        checklist_path = f"checklists/checklist_{idx}.json"
                        zipf.writestr(checklist_path, checklist_json)
                        file_list.append({"name": checklist_path, "size": len(checklist_json)})
                
                # Add notes
                if notes:
                    for idx, note in enumerate(notes):
                        note_content = note.get("content", "")
                        note_path = f"notes/note_{note.get('id', idx)}.txt"
                        zipf.writestr(note_path, note_content)
                        file_list.append({"name": note_path, "size": len(note_content)})
                
                # Add images
                if images_dir and os.path.exists(images_dir):
                    for filename in os.listdir(images_dir):
                        file_path = os.path.join(images_dir, filename)
                        if os.path.isfile(file_path):
                            arcname = f"images/{filename}"
                            zipf.write(file_path, arcname)
                            file_list.append({
                                "name": arcname,
                                "size": get_file_size(file_path)
                            })
                
                # Add tables
                if tables:
                    for idx, table in enumerate(tables):
                        table_json = json.dumps(table, default=str, indent=2)
                        table_path = f"tables/table_{idx}.json"
                        zipf.writestr(table_path, table_json)
                        file_list.append({"name": table_path, "size": len(table_json)})
                
                # Add metadata file
                metadata = {
                    "compression_date": get_timestamp_str(),
                    "project_id": project_id,
                    "file_size_bytes": 0,  # Will be updated
                    "total_files": len(file_list),
                    "total_checklists": len(checklists) if checklists else 0,
                    "total_notes": len(notes) if notes else 0,
                    "total_tables": len(tables) if tables else 0,
                    "file_list": file_list
                }
                metadata_json = json.dumps(metadata, indent=2)
                zipf.writestr("metadata.json", metadata_json)
            
            return zip_path
            
        except Exception as e:
            raise CompressionError(project_id, str(e))

    @staticmethod
    def decompress_project(zip_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Decompress project from ZIP file.
        
        Args:
            zip_path: Path to ZIP file
            output_dir: Output directory for extracted files
        
        Returns:
            Dictionary with extracted project data
        """
        try:
            if not os.path.exists(zip_path):
                raise FileNotFoundError(f"ZIP file not found: {zip_path}")
            
            if output_dir is None:
                output_dir = os.path.dirname(zip_path)
            
            ensure_directory_exists(output_dir)
            extract_dir = os.path.join(output_dir, f"extracted_{generate_unique_id()}")
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Load project metadata
            project_json_path = os.path.join(extract_dir, "project.json")
            project_data = read_json_file(project_json_path)
            
            # Load checklists
            checklists_dir = os.path.join(extract_dir, "checklists")
            checklists = []
            if os.path.exists(checklists_dir):
                for filename in sorted(os.listdir(checklists_dir)):
                    if filename.endswith(".json"):
                        checklist_path = os.path.join(checklists_dir, filename)
                        checklist = read_json_file(checklist_path)
                        checklists.append(checklist)
            
            # Load notes
            notes_dir = os.path.join(extract_dir, "notes")
            notes = []
            if os.path.exists(notes_dir):
                for filename in sorted(os.listdir(notes_dir)):
                    if filename.endswith(".txt"):
                        note_path = os.path.join(notes_dir, filename)
                        try:
                            with open(note_path, 'r', encoding='utf-8') as f:
                                notes.append({"content": f.read()})
                        except (IOError, OSError):
                            pass
            
            # Load tables
            tables_dir = os.path.join(extract_dir, "tables")
            tables = []
            if os.path.exists(tables_dir):
                for filename in sorted(os.listdir(tables_dir)):
                    if filename.endswith(".json"):
                        table_path = os.path.join(tables_dir, filename)
                        table = read_json_file(table_path)
                        tables.append(table)
            
            # Images directory path
            images_dir = os.path.join(extract_dir, "images")
            
            return {
                "project": project_data,
                "checklists": checklists,
                "notes": notes,
                "tables": tables,
                "images_dir": images_dir if os.path.exists(images_dir) else None,
                "extract_dir": extract_dir
            }
            
        except Exception as e:
            raise DecompressionError(zip_path, str(e))

    @staticmethod
    def backup_project(
        project_id: str,
        project_data: Dict[str, Any],
        checklists: list = None,
        notes: list = None,
        images_dir: str = None,
        tables: list = None
    ) -> str:
        """
        Create a backup of the project.
        
        Args:
            project_id: Project UUID
            project_data: Project metadata
            checklists: List of checklist data
            notes: List of note data
            images_dir: Directory containing images
            tables: List of table data
        
        Returns:
            Path to backup ZIP file
        """
        backup_dir = f"{settings.projects_dir}/{project_id}/backups"
        ensure_directory_exists(backup_dir)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        return ProjectManager.compress_project(
            project_id=project_id,
            project_data=project_data,
            checklists=checklists,
            notes=notes,
            images_dir=images_dir,
            tables=tables,
            output_dir=backup_dir
        )

    @staticmethod
    def cleanup_old_backups(project_id: str, keep_count: int = 5) -> int:
        """
        Clean up old backup files, keeping only the most recent.
        
        Args:
            project_id: Project UUID
            keep_count: Number of backups to keep
        
        Returns:
            Number of backups deleted
        """
        backup_dir = f"{settings.projects_dir}/{project_id}/backups"
        
        if not os.path.exists(backup_dir):
            return 0
        
        # Get all zip files sorted by modification time
        files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.zip')],
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
            reverse=True
        )
        
        deleted_count = 0
        for backup_file in files[keep_count:]:
            try:
                os.remove(os.path.join(backup_dir, backup_file))
                deleted_count += 1
            except (OSError, IOError):
                pass
        
        return deleted_count
