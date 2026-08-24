"""
Helper utility functions for Easy-Trade
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import json


def generate_unique_id() -> str:
    """
    Generate a unique UUID string for resources.
    """
    return str(uuid.uuid4())


def get_timestamp() -> datetime:
    """
    Get current UTC timestamp.
    """
    return datetime.utcnow()


def get_timestamp_str() -> str:
    """
    Get current UTC timestamp as ISO format string.
    """
    return datetime.utcnow().isoformat() + "Z"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    """
    import re
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Keep only safe characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable file size.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_month_string(date: datetime) -> str:
    """
    Format datetime as month string (e.g., "2026-08")
    """
    return date.strftime("%Y-%m")


def calculate_average(values: List[float]) -> float:
    """
    Calculate average of a list of values.
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def round_to_decimals(value: float, decimals: int = 2) -> float:
    """
    Round float to specified decimal places.
    """
    return round(value, decimals)


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, IOError):
        return 0


def ensure_directory_exists(directory_path: str) -> Path:
    """
    Ensure directory exists, create if not.
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def delete_file(file_path: str) -> bool:
    """
    Delete a file safely.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except (OSError, IOError):
        return False


def read_json_file(file_path: str) -> dict:
    """
    Read and parse JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        return {}


def write_json_file(file_path: str, data: dict) -> bool:
    """
    Write data to JSON file.
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError):
        return False


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[-1].lower()
    return ''


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file.
    """
    import hashlib
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (IOError, OSError):
        return ""


def cleanup_temp_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Clean up temporary files older than specified hours.
    Returns number of files deleted.
    """
    import time
    deleted_count = 0
    
    if not os.path.exists(directory):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except (OSError, IOError):
                        pass
    except (OSError, IOError):
        pass
    
    return deleted_count
