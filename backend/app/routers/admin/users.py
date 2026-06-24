from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update
from typing import Optional
from app.database import get_db
from app.dependencies import require_admin, require_superadmin_or_admin
from app.models.auth import User
from app.models.report import DiagnosticReport
from app.schemas.auth import UserOut, UserCreate, UserUpdate, PagedUsers
from app.core.security import hash_password

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

# Peran yang boleh dibuat tiap pengelola (hierarki turun)
CREATABLE_BY = {
    "superadmin": {"admin_universitas", "admin_fakultas", "admin_prodi", "dosen"},
    "admin_universitas": {"admin_fakultas", "admin_prodi", "dosen"},
    "admin_fakultas": {"admin_prodi", "dosen"},
    "admin_prodi": {"dosen"},
}
ALLOWED_ROLES = {"admin_universitas", "admin_fakultas", "admin_prodi", "dosen"}


def _scope(q, current_user: User):
    """Batasi daftar akun sesuai cakupan peran pengelola."""
    if current_user.role == "superadmin":
        return q
    if current_user.role == "admin_universitas" and current_user.university_id:
        return q.where(User.university_id == current_user.university_id)
    if current_user.role == "admin_fakultas" and current_user.faculty_id:
        return q.where(User.faculty_id == current_user.faculty_id)
    if current_user.role == "admin_prodi" and current_user.program_id:
        return q.where(User.program_id == current_user.program_id)
    # dosen / tanpa cakupan valid: tidak mengelola akun
    return q.where(User.id == current_user.id)


def _user_in_scope(current_user: User, user: User) -> bool:
    if current_user.role == "superadmin":
        return True
    if current_user.role == "admin_universitas":
        return user.university_id == current_user.university_id
    if current_user.role == "admin_fakultas":
        return user.faculty_id == current_user.faculty_id
    if current_user.role == "admin_prodi":
        return user.program_id == current_user.program_id
    return False


@router.get("", response_model=PagedUsers)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q = select(User).where(User.role != "superadmin")
    q = _scope(q, current_user)

    if role:
        q = q.where(User.role == role)
    if is_active is not None:
        q = q.where(User.is_active == is_active)
    if search:
        q = q.where(or_(User.full_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    rows = (await db.execute(q.order_by(User.full_name).offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": rows, "total": total, "page": page, "limit": limit}


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    # Validasi role yang boleh dibuat oleh peran pengelola ini
    if body.role not in ALLOWED_ROLES:
        raise HTTPException(400, "Role tidak valid")
    if body.role not in CREATABLE_BY.get(current_user.role, set()):
        raise HTTPException(403, f"Peran Anda tidak dapat membuat akun '{body.role}'")

    # Admin tingkat bawah: paksa cakupan akun baru ke cakupan pengelola
    university_id = body.university_id
    faculty_id = body.faculty_id
    program_id = body.program_id
    if current_user.role == "admin_universitas":
        if university_id and university_id != current_user.university_id:
            raise HTTPException(403, "Tidak bisa membuat akun di universitas lain")
        university_id = current_user.university_id
    elif current_user.role == "admin_fakultas":
        university_id = current_user.university_id
        faculty_id = current_user.faculty_id
    elif current_user.role == "admin_prodi":
        university_id = current_user.university_id
        faculty_id = current_user.faculty_id
        program_id = current_user.program_id

    # Cek email duplikat
    existing = (await db.execute(select(User).where(User.email == body.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(400, "Email sudah terdaftar")

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=body.role,
        university_id=university_id,
        faculty_id=faculty_id,
        program_id=program_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{uid}", response_model=UserOut)
async def get_user(
    uid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await db.get(User, uid)
    if not user or user.role == "superadmin":
        raise HTTPException(404, "User tidak ditemukan")
    if not _user_in_scope(current_user, user):
        raise HTTPException(403, "Akses ditolak")
    return user


@router.put("/{uid}", response_model=UserOut)
async def update_user(
    uid: str,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    user = await db.get(User, uid)
    if not user or user.role == "superadmin":
        raise HTTPException(404, "User tidak ditemukan")
    if not _user_in_scope(current_user, user):
        raise HTTPException(403, "Akses ditolak")

    data = body.model_dump(exclude_none=True)
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))

    for k, v in data.items():
        setattr(user, k, v)

    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{uid}/toggle", response_model=UserOut)
async def toggle_user_active(
    uid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    user = await db.get(User, uid)
    if not user or user.role == "superadmin":
        raise HTTPException(404, "User tidak ditemukan")
    if not _user_in_scope(current_user, user):
        raise HTTPException(403, "Akses ditolak")

    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{uid}", status_code=204)
async def delete_user(
    uid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    user = await db.get(User, uid)
    if not user or user.role == "superadmin":
        raise HTTPException(404, "User tidak ditemukan")
    if not _user_in_scope(current_user, user):
        raise HTTPException(403, "Akses ditolak")
    if str(user.id) == str(current_user.id):
        raise HTTPException(400, "Tidak bisa menghapus akun sendiri")
    # Laporan diagnostik ber-FK RESTRICT pada generated_by → alihkan ke admin penghapus
    # agar laporan tetap utuh. Relasi lain (sesi, dosen pengampu) cascade; RPS/respons SET NULL.
    await db.execute(
        update(DiagnosticReport)
        .where(DiagnosticReport.generated_by == user.id)
        .values(generated_by=current_user.id)
    )
    await db.delete(user)
    await db.commit()
