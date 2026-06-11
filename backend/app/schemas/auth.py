from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class UserInfo(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    university_id: Optional[int] = None
    program_id: Optional[int] = None

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
