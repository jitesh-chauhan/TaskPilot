from typing import List, Any

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    created_at: str = Field(..., description="UNIX timestamp as string")
    updated_at: str = Field(..., description="UNIX timestamp as string")
    enabled: bool = Field(default=False)



class UserCreateReq(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    created_at: str = Field(..., description="UNIX timestamp as string")
    updated_at: str = Field(..., description="UNIX timestamp as string")
    enabled: bool = Field(default=False)

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