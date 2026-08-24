"""
Custom exception classes for Easy-Trade application
"""

from fastapi import status
from typing import Optional, Dict, Any


class EasyTradeException(Exception):
    """Base exception for Easy-Trade"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ProjectNotFoundError(EasyTradeException):
    """Raised when project is not found"""
    def __init__(self, project_id: str):
        super().__init__(
            message=f"Project '{project_id}' not found",
            code="PROJECT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"project_id": project_id}
        )


class ProjectAlreadyExistsError(EasyTradeException):
    """Raised when trying to create duplicate project"""
    def __init__(self, project_name: str):
        super().__init__(
            message=f"Project '{project_name}' already exists",
            code="PROJECT_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
            details={"project_name": project_name}
        )


class InvalidFileFormatError(EasyTradeException):
    """Raised when file format is invalid"""
    def __init__(self, filename: str, allowed_formats: list):
        super().__init__(
            message=f"File '{filename}' has invalid format. Allowed: {', '.join(allowed_formats)}",
            code="INVALID_FILE_FORMAT",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"filename": filename, "allowed_formats": allowed_formats}
        )


class FileTooLargeError(EasyTradeException):
    """Raised when file size exceeds limit"""
    def __init__(self, filename: str, file_size: int, max_size: int):
        super().__init__(
            message=f"File '{filename}' ({file_size} bytes) exceeds max size ({max_size} bytes)",
            code="FILE_TOO_LARGE",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details={"filename": filename, "file_size": file_size, "max_size": max_size}
        )


class ChecklistNotFoundError(EasyTradeException):
    """Raised when checklist is not found"""
    def __init__(self, checklist_id: str):
        super().__init__(
            message=f"Checklist '{checklist_id}' not found",
            code="CHECKLIST_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"checklist_id": checklist_id}
        )


class ChecklistItemNotFoundError(EasyTradeException):
    """Raised when checklist item is not found"""
    def __init__(self, item_id: str):
        super().__init__(
            message=f"Checklist item '{item_id}' not found",
            code="CHECKLIST_ITEM_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"item_id": item_id}
        )


class InvalidProjectDataError(EasyTradeException):
    """Raised when project data is invalid"""
    def __init__(self, message: str, details: dict):
        super().__init__(
            message=message,
            code="INVALID_PROJECT_DATA",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class CompressionError(EasyTradeException):
    """Raised when project compression fails"""
    def __init__(self, project_id: str, reason: str):
        super().__init__(
            message=f"Failed to compress project '{project_id}': {reason}",
            code="COMPRESSION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"project_id": project_id, "reason": reason}
        )


class DecompressionError(EasyTradeException):
    """Raised when project decompression fails"""
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            message=f"Failed to decompress file '{file_path}': {reason}",
            code="DECOMPRESSION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"file_path": file_path, "reason": reason}
        )


class DatabaseError(EasyTradeException):
    """Raised when database operation fails"""
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database error during {operation}: {reason}",
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation, "reason": reason}
        )


class ImageProcessingError(EasyTradeException):
    """Raised when image processing fails"""
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"Failed to process image '{filename}': {reason}",
            code="IMAGE_PROCESSING_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"filename": filename, "reason": reason}
        )
