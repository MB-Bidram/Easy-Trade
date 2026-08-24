"""
File handling and image processing utilities
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from PIL import Image
import io

from backend.config import settings
from backend.utils.helpers import (
    ensure_directory_exists,
    generate_unique_id,
    sanitize_filename,
    get_file_size
)
from backend.utils.exceptions import ImageProcessingError


async def save_upload_image(
    file: UploadFile,
    project_id: str,
    compress: bool = True
) -> Tuple[str, int]:
    """
    Save uploaded image file with compression.
    
    Args:
        file: Uploaded file object
        project_id: Project ID for directory structure
        compress: Whether to compress image
    
    Returns:
        Tuple of (file_path, file_size_bytes)
    """
    try:
        # Create project images directory
        images_dir = ensure_directory_exists(
            f"{settings.projects_dir}/{project_id}/images"
        )
        
        # Generate unique filename
        original_filename = sanitize_filename(file.filename)
        unique_filename = f"{generate_unique_id()}_{original_filename}"
        file_path = images_dir / unique_filename
        
        # Read file content
        content = await file.read()
        
        # Process image
        if compress:
            content = compress_image_data(content)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        file_size = get_file_size(str(file_path))
        
        return str(file_path), file_size
        
    except Exception as e:
        raise ImageProcessingError(
            filename=file.filename,
            reason=str(e)
        )


def compress_image_data(image_data: bytes, quality: int = 85) -> bytes:
    """
    Compress image data using PIL.
    
    Args:
        image_data: Raw image bytes
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed image bytes
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Compress image
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        raise ImageProcessingError(
            filename="unknown",
            reason=f"Failed to compress image: {str(e)}"
        )


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Get image dimensions (width, height).
    
    Returns:
        Tuple of (width, height)
    """
    try:
        image = Image.open(image_path)
        return image.size
    except Exception:
        return (0, 0)


def delete_image(image_path: str) -> bool:
    """
    Delete image file.
    """
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            return True
        return False
    except (OSError, IOError):
        return False


def cleanup_project_directory(project_dir: str) -> bool:
    """
    Safely delete entire project directory.
    """
    try:
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
            return True
        return False
    except (OSError, IOError):
        return False


def read_image_file(image_path: str) -> Optional[bytes]:
    """
    Read image file as bytes.
    """
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except (OSError, IOError):
        return None
