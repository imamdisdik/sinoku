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


# ── Kelompok peran (5 aktor) ─────────────────────────────────────────────────
# superadmin | admin_universitas | admin_fakultas | admin_prodi | dosen
ADMIN_ROLES = ("admin_universitas", "admin_fakultas", "admin_prodi")
MANAGER_ROLES = ("superadmin",) + ADMIN_ROLES          # boleh mengelola (tanpa dosen)
STAFF_ROLES = MANAGER_ROLES + ("dosen",)               # semua peran login


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Semua peran login (lihat/baca + RPS)."""
    if user.role not in STAFF_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    if user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user


def require_superadmin_or_admin(user: User = Depends(get_current_user)) -> User:
    """Peran pengelola: superadmin + semua tingkat admin (tanpa dosen)."""
    if user.role not in MANAGER_ROLES:
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


def is_scoped(user: User) -> bool:
    """True jika peran dibatasi cakupan (semua kecuali superadmin)."""
    return user.role != "superadmin"


def program_scope_condition(user: User):
    """
    Kondisi SQLAlchemy pada tabel Program sesuai cakupan peran. Pakai pada query
    yang sudah/akan men-join Program:
      - superadmin       → semua
      - admin_universitas→ Program.university_id == user.university_id
      - admin_fakultas   → Program.faculty_id   == user.faculty_id
      - admin_prodi/dosen→ Program.id           == user.program_id
    Tanpa scope yang valid → tidak ada akses (false()).
    """
    from app.models.academic import Program
    from sqlalchemy import true, false
    if user.role == "superadmin":
        return true()
    if user.role == "admin_universitas":
        return Program.university_id == user.university_id if user.university_id else false()
    if user.role == "admin_fakultas":
        return Program.faculty_id == user.faculty_id if user.faculty_id else false()
    if user.role in ("admin_prodi", "dosen"):
        return Program.id == user.program_id if user.program_id else false()
    return false()


def program_in_scope(user: User, program) -> bool:
    """Cek apakah objek Program berada dalam cakupan user (untuk validasi tulis)."""
    if user.role == "superadmin":
        return True
    if user.role == "admin_universitas":
        return bool(user.university_id) and program.university_id == user.university_id
    if user.role == "admin_fakultas":
        return bool(user.faculty_id) and program.faculty_id == user.faculty_id
    if user.role in ("admin_prodi", "dosen"):
        return bool(user.program_id) and program.id == user.program_id
    return False


async def assert_program_in_scope(db, user: User, program_id: int):
    """Pastikan user boleh menulis pada program_id; jika tidak → 403/404."""
    if user.role == "superadmin":
        return
    from app.models.academic import Program
    program = await db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program tidak ditemukan")
    if not program_in_scope(user, program):
        raise HTTPException(status_code=403, detail="Di luar cakupan Anda")
