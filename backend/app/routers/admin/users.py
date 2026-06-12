from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from app.database import get_db
from app.dependencies import require_admin, require_superadmin_or_admin
from app.models.auth import User
from app.schemas.auth import UserOut, UserCreate, UserUpdate, PagedUsers
from app.core.security import hash_password

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

ALLOWED_ROLES = {"admin", "dosen"}


def _scope(q, current_user: User):
    """Terapkan scoping: admin hanya lihat user di univ sendiri."""
    if current_user.role == "admin" and current_user.university_id:
        q = q.where(User.university_id == current_user.university_id)
    return q


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
    # Validasi role yang boleh dibuat
    if body.role not in ALLOWED_ROLES:
        raise HTTPException(400, "Role hanya boleh: admin atau dosen")

    # Admin hanya bisa buat akun dosen (bukan admin lain)
    if current_user.role == "admin" and body.role != "dosen":
        raise HTTPException(403, "Admin universitas hanya bisa membuat akun dosen")

    # Admin wajib assign ke univ sendiri
    if current_user.role == "admin":
        if body.university_id and body.university_id != current_user.university_id:
            raise HTTPException(403, "Tidak bisa membuat akun di universitas lain")
        body = body.model_copy(update={"university_id": current_user.university_id})

    # Cek email duplikat
    existing = (await db.execute(select(User).where(User.email == body.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(400, "Email sudah terdaftar")

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=body.role,
        university_id=body.university_id,
        program_id=body.program_id,
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
    # Admin hanya bisa lihat user di univ sendiri
    if current_user.role == "admin" and user.university_id != current_user.university_id:
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
    if current_user.role == "admin" and user.university_id != current_user.university_id:
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
    if current_user.role == "admin" and user.university_id != current_user.university_id:
        raise HTTPException(403, "Akses ditolak")

    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    return user
