"""
Pydantic models (schemas) for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class ProjectType(str, Enum):
    """Project type enumeration"""
    CHECKLIST = "checklist"
    MARKET_OVERVIEW = "market_overview"
    JOURNAL = "journal"


class PriorityLevel(str, Enum):
    """Priority level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ==================== BASE RESPONSE MODEL ====================

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class PaginatedResponse(BaseModel):
    """Paginated API response"""
    success: bool = True
    data: List[Any] = []
    pagination: Dict[str, int] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# ==================== PROJECT MODELS ====================

class ProjectCreate(BaseModel):
    """Project creation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: ProjectType = ProjectType.CHECKLIST
    metadata: Optional[Dict[str, Any]] = None

    @validator('name')
    def name_alphanumeric(cls, v):
        """Validate project name contains only safe characters"""
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Project name can only contain alphanumeric, spaces, hyphens, underscores')
        return v


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_archived: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectRead(BaseModel):
    """Project read/response schema"""
    id: str
    name: str
    description: Optional[str]
    project_type: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    file_size_bytes: int
    version: int
    checklists_count: Optional[int] = 0
    notes_count: Optional[int] = 0
    images_count: Optional[int] = 0
    tables_count: Optional[int] = 0

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# ==================== CHECKLIST MODELS ====================

class ChecklistItemCreate(BaseModel):
    """Checklist item creation schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    order: int = 0
    notes: Optional[str] = None


class ChecklistItemUpdate(BaseModel):
    """Checklist item update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    notes: Optional[str] = None


class ChecklistItemRead(BaseModel):
    """Checklist item read/response schema"""
    id: str
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    order: int
    priority: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z" if v else None
        }


class ChecklistCreate(BaseModel):
    """Checklist creation schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    items: Optional[List[ChecklistItemCreate]] = None
    is_template: Optional[bool] = False


class ChecklistUpdate(BaseModel):
    """Checklist update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_template: Optional[bool] = None


class ChecklistRead(BaseModel):
    """Checklist read/response schema"""
    id: str
    project_id: str
    title: str
    description: Optional[str]
    is_template: bool
    completion_percentage: float
    total_items: int
    completed_items: int
    items: Optional[List[ChecklistItemRead]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# ==================== NOTE MODELS ====================

class NoteCreate(BaseModel):
    """Note creation schema"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = None


class NoteUpdate(BaseModel):
    """Note update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None


class NoteRead(BaseModel):
    """Note read/response schema"""
    id: str
    project_id: str
    title: str
    content: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# ==================== IMAGE MODELS ====================

class ImageCreate(BaseModel):
    """Image creation schema"""
    description: Optional[str] = None


class ImageRead(BaseModel):
    """Image read/response schema"""
    id: str
    project_id: str
    filename: str
    file_size_bytes: int
    width: Optional[int]
    height: Optional[int]
    description: Optional[str]
    uploaded_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# ==================== TABLE MODELS ====================

class TableColumnDefinition(BaseModel):
    """Table column definition"""
    name: str = Field(..., min_length=1)
    type: str = "string"  # string, number, boolean, date
    required: Optional[bool] = False
    width: Optional[int] = None


class TableRowData(BaseModel):
    """Table row data"""
    id: Optional[str] = None
    data: Dict[str, Any]


class TableCreate(BaseModel):
    """Table creation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    columns: List[TableColumnDefinition] = Field(..., min_length=1)
    rows: Optional[List[TableRowData]] = None

    @validator('columns')
    def validate_columns(cls, v):
        """Ensure at least one column"""
        if len(v) == 0:
            raise ValueError('Table must have at least one column')
        return v


class TableUpdate(BaseModel):
    """Table update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    columns: Optional[List[TableColumnDefinition]] = None


class TableRead(BaseModel):
    """Table read/response schema"""
    id: str
    project_id: str
    name: str
    description: Optional[str]
    columns: List[TableColumnDefinition]
    rows: Optional[List[TableRowData]]
    row_count: int
    column_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# ==================== TRADE MODELS ====================

class TradeCreate(BaseModel):
    """Trade creation schema"""
    ticker: str = Field(..., min_length=1, max_length=10)
    entry_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    notes: Optional[str] = None
    project_id: Optional[str] = None


class TradeUpdate(BaseModel):
    """Trade update schema"""
    exit_price: Optional[float] = None
    notes: Optional[str] = None


class TradeRead(BaseModel):
    """Trade read/response schema"""
    id: int
    ticker: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_date: datetime
    exit_date: Optional[datetime]
    is_closed: bool
    notes: Optional[str]
    pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None
    project_id: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z" if v else None
        }
