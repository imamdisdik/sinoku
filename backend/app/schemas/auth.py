from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime


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
    faculty_id: Optional[int] = None
    program_id: Optional[int] = None

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


# ── User Management ────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    university_id: Optional[int] = None
    faculty_id: Optional[int] = None
    program_id: Optional[int] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str               # admin_universitas | admin_fakultas | admin_prodi | dosen
    university_id: Optional[int] = None
    faculty_id: Optional[int] = None
    program_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    university_id: Optional[int] = None
    faculty_id: Optional[int] = None
    program_id: Optional[int] = None
    is_active: Optional[bool] = None


class PagedUsers(BaseModel):
    data: list[UserOut]
    total: int
    page: int
    limit: int
