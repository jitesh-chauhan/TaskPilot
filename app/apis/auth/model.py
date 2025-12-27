from typing import List, Any

from pydantic import BaseModel, EmailStr


class AuthModel(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    data: List[dict[str, str]]
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "data": [{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}],
                "status": "success",
                "message": "Login successful"
            }
        }


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