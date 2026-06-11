from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from typing import Optional
from app.database import get_db
from app.core.security import decode_token
from app.models.auth import User, Session
from datetime import datetime, timezone

bearer = HTTPBearer()
bearer_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid atau kadaluarsa")

    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("superadmin", "admin", "dosen"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    if user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user


def require_superadmin_or_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("superadmin", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Coba ambil user dari JWT, kembalikan None jika tidak ada/invalid."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
        return result.scalar_one_or_none()
    except Exception:
        return None


def apply_university_scope(query, user: User):
    """Terapkan filter university_id berdasarkan role."""
    from app.models.academic import Program, Course
    if user.role in ("admin", "dosen") and user.university_id:
        return query, user.university_id
    return query, None
