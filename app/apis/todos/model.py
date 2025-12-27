from typing import List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


class TodoModel(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Primary identifier"
    )
    user_id: Optional[str] = Field(default=None, description="User ID")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default=3, ge=1, le=5)
    due_date: Optional[str] = Field(
        default=None, description="UNIX timestamp as string in milliseconds"
    )
    created_at: str = Field(..., description="UNIX timestamp as string")
    updated_at: str = Field(..., description="UNIX timestamp as string")
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[str] = Field(
        default=None, description="UNIX timestamp as string"
    )

    @field_validator(
        "created_at", "updated_at", "due_date", "deleted_at", mode="before"
    )
    @classmethod
    def validate_unix_timestamp(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("Timestamp must be a string")
        return v


class TodoCreate(BaseModel):
    title: str
    description: str
    priority: str
    due_date: str
    email: EmailStr

class TodoDeleteResponse(BaseModel):
    data : List[Any] = []
    status: str = "success"
    message: str = "Success Message"

class TodoCreateResponse(BaseModel):
    data: List[Any] = []
    status: str = "success"
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "message": "Todo Created",
                "status": "success"
            }
        }

class TodoResponse(BaseModel):
    status: str
    message: str
    data: List[TodoModel]



class ErrorResponse(BaseModel):
    data: List[Any] = []
    status: str = "failed"
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "message": "Detailed error message here",
                "status": "failed"
            }
        }
