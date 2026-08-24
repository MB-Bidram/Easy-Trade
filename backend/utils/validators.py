"""
Input validation functions for Easy-Trade
"""

import re
from typing import Optional, List, Dict, Any
from backend.config import settings
from backend.utils.exceptions import (
    InvalidFileFormatError,
    FileTooLargeError,
    InvalidProjectDataError
)


def validate_project_name(name: str) -> bool:
    """
    Validate project name.
    - Must be 1-255 characters
    - Can contain alphanumeric, spaces, hyphens, underscores
    """
    if not name or len(name) > 255:
        raise InvalidProjectDataError(
            message="Project name must be between 1 and 255 characters",
            details={"provided_length": len(name) if name else 0}
        )
    
    # Allow alphanumeric, spaces, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise InvalidProjectDataError(
            message="Project name can only contain alphanumeric characters, spaces, hyphens, and underscores",
            details={"provided_name": name}
        )
    
    return True


def validate_image_file(filename: str, file_size_bytes: int) -> bool:
    """
    Validate image file.
    - Must have allowed extension
    - Must not exceed size limit
    """
    allowed_formats = settings.allowed_image_formats
    
    # Check file extension
    file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_formats:
        raise InvalidFileFormatError(filename, allowed_formats)
    
    # Check file size
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        raise FileTooLargeError(
            filename,
            file_size_bytes,
            max_size_bytes
        )
    
    return True


def validate_checklist_data(data: Dict[str, Any]) -> bool:
    """
    Validate checklist data structure.
    """
    required_fields = ["title"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise InvalidProjectDataError(
                message=f"Required field '{field}' is missing or empty",
                details={"missing_field": field}
            )
    
    # Validate title length
    if len(data["title"]) > 255:
        raise InvalidProjectDataError(
            message="Checklist title must be less than 255 characters",
            details={"title_length": len(data["title"])}
        )
    
    # Validate items if provided
    if "items" in data and data["items"]:
        if not isinstance(data["items"], list):
            raise InvalidProjectDataError(
                message="Checklist items must be a list",
                details={"items_type": str(type(data["items"]))}
            )
        
        for idx, item in enumerate(data["items"]):
            if not isinstance(item, dict) or "title" not in item:
                raise InvalidProjectDataError(
                    message=f"Checklist item {idx} is missing 'title'",
                    details={"item_index": idx}
                )
    
    return True


def validate_table_structure(table_data: Dict[str, Any]) -> bool:
    """
    Validate table data structure.
    """
    required_fields = ["name", "columns"]
    
    for field in required_fields:
        if field not in table_data:
            raise InvalidProjectDataError(
                message=f"Required table field '{field}' is missing",
                details={"missing_field": field}
            )
    
    # Validate columns
    if not isinstance(table_data["columns"], list):
        raise InvalidProjectDataError(
            message="Table columns must be a list",
            details={"columns_type": str(type(table_data["columns"]))}
        )
    
    if len(table_data["columns"]) == 0:
        raise InvalidProjectDataError(
            message="Table must have at least one column",
            details={"column_count": 0}
        )
    
    # Validate rows if provided
    if "rows" in table_data and table_data["rows"]:
        if not isinstance(table_data["rows"], list):
            raise InvalidProjectDataError(
                message="Table rows must be a list",
                details={"rows_type": str(type(table_data["rows"]))}
            )
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    - Remove special characters
    - Replace spaces with underscores
    - Remove path traversal attempts
    """
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Keep only alphanumeric, dots, hyphens, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    return filename
