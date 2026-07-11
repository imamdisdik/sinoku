from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from app.database import get_db
from app.dependencies import (
    require_admin, is_scoped, program_scope_condition, program_in_scope,
    assert_program_in_scope, dosen_course_ids_subquery, dosen_can_access_course,
)
from app.models.auth import User
from app.models.rps import RpsVersion, RpsChecklistItem, RpsChecklistResponse
from app.models.academic import Course, Program

router = APIRouter(prefix="/admin/rps", tags=["admin-rps"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class RpsOut(BaseModel):
    id: int
    course_id: int
    tahun_akademik: str
    semester: str
    status: str
    file_url: Optional[str] = None
    catatan: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class RpsCreate(BaseModel):
    course_id: int
    tahun_akademik: str
    semester: str
    status: str = "draft"
    file_url: Optional[str] = None
    catatan: Optional[str] = None


class RpsUpdate(BaseModel):
    tahun_akademik: Optional[str] = None
    semester: Optional[str] = None
    status: Optional[str] = None
    file_url: Optional[str] = None
    catatan: Optional[str] = None


class ChecklistItemOut(BaseModel):
    id: int
    kode: str
    nama_komponen: str
    deskripsi: Optional[str] = None
    is_mandatory: bool
    urutan: int
    model_config = {"from_attributes": True}


class ChecklistResponseOut(BaseModel):
    id: int
    rps_version_id: int
    checklist_item_id: int
    is_fulfilled: bool
    catatan: Optional[str] = None
    checked_at: Optional[datetime] = None
    checklist_item: ChecklistItemOut  # cocok dgn relasi model & frontend (item.checklist_item.kode)
    model_config = {"from_attributes": True}


class ChecklistUpdate(BaseModel):
    is_fulfilled: bool
    catatan: Optional[str] = None


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _check_rps_university(rps: RpsVersion, current_user: User, db: AsyncSession):
    """Pastikan RPS yang diakses milik universitas user (admin/dosen)."""
    if is_scoped(current_user):
        course = await db.get(Course, rps.course_id)
        if not course:
            raise HTTPException(403, "Akses ditolak")
        program = await db.get(Program, course.program_id)
        if not program or not program_in_scope(current_user, program):
            raise HTTPException(403, "Akses ditolak")
        if not await dosen_can_access_course(db, current_user, rps.course_id):
            raise HTTPException(403, "Anda tidak mengampu mata kuliah ini")


def _scope_course(q, current_user: User):
    if is_scoped(current_user):
        q = q.join(Course, RpsVersion.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(program_scope_condition(current_user))
        # Dosen: hanya RPS untuk MK yang ia ampu
        if current_user.role == "dosen":
            q = q.where(Course.id.in_(dosen_course_ids_subquery(current_user)))
    return q


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[RpsOut])
async def list_rps(
    course_id: Optional[int] = None,
    program_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    university_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q = select(RpsVersion)
    q = _scope_course(q, current_user)
    if program_id or faculty_id or university_id:
        sub = select(Course.id)
        if faculty_id or university_id:
            sub = sub.join(Program, Course.program_id == Program.id)
        if program_id:
            sub = sub.where(Course.program_id == program_id)
        if faculty_id:
            sub = sub.where(Program.faculty_id == faculty_id)
        if university_id:
            sub = sub.where(Program.university_id == university_id)
        q = q.where(RpsVersion.course_id.in_(sub))
    if course_id:
        q = q.where(RpsVersion.course_id == course_id)
    if status:
        q = q.where(RpsVersion.status == status)
    rows = (await db.execute(q.order_by(RpsVersion.created_at.desc()))).scalars().all()
    return rows


@router.post("", response_model=RpsOut, status_code=201)
async def create_rps(
    body: RpsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    course = await db.get(Course, body.course_id)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await assert_program_in_scope(db, current_user, course.program_id)
    if not await dosen_can_access_course(db, current_user, body.course_id):
        raise HTTPException(403, "Anda tidak mengampu mata kuliah ini")
    rps = RpsVersion(
        course_id=body.course_id,
        tahun_akademik=body.tahun_akademik,
        semester=body.semester,
        status=body.status,
        file_url=body.file_url,
        catatan=body.catatan,
        created_by=current_user.id,
    )
    db.add(rps)
    await db.commit()
    await db.refresh(rps)
    return rps


@router.get("/{rps_id}", response_model=RpsOut)
async def get_rps(
    rps_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rps = await db.get(RpsVersion, rps_id)
    if not rps:
        raise HTTPException(404, "RPS tidak ditemukan")
    await _check_rps_university(rps, current_user, db)
    return rps


@router.put("/{rps_id}", response_model=RpsOut)
async def update_rps(
    rps_id: int,
    body: RpsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rps = await db.get(RpsVersion, rps_id)
    if not rps:
        raise HTTPException(404, "RPS tidak ditemukan")
    await _check_rps_university(rps, current_user, db)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(rps, k, v)
    await db.commit()
    await db.refresh(rps)
    return rps


@router.delete("/{rps_id}", status_code=204)
async def delete_rps(
    rps_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rps = await db.get(RpsVersion, rps_id)
    if not rps:
        raise HTTPException(404, "RPS tidak ditemukan")
    await _check_rps_university(rps, current_user, db)
    await db.delete(rps)
    await db.commit()


# ── Checklist ─────────────────────────────────────────────────────────────────

@router.get("/{rps_id}/checklist", response_model=list[ChecklistResponseOut])
async def get_checklist(
    rps_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rps = await db.get(RpsVersion, rps_id)
    if not rps:
        raise HTTPException(404, "RPS tidak ditemukan")

    # Ambil semua checklist items
    all_items = (await db.execute(
        select(RpsChecklistItem).order_by(RpsChecklistItem.urutan)
    )).scalars().all()

    # Ambil responses yang sudah ada
    existing = (await db.execute(
        select(RpsChecklistResponse).where(RpsChecklistResponse.rps_version_id == rps_id)
    )).scalars().all()
    existing_map = {r.checklist_item_id: r for r in existing}

    # Auto-create yang belum ada
    result = []
    for item in all_items:
        if item.id not in existing_map:
            resp = RpsChecklistResponse(
                rps_version_id=rps_id,
                checklist_item_id=item.id,
                is_fulfilled=False,
            )
            db.add(resp)
            await db.flush()
            resp.checklist_item = item
            result.append(resp)
        else:
            existing_map[item.id].checklist_item = item
            result.append(existing_map[item.id])

    await db.commit()
    return result


@router.patch("/{rps_id}/checklist/{item_id}", response_model=ChecklistResponseOut)
async def update_checklist_item(
    rps_id: int,
    item_id: int,
    body: ChecklistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    resp = (await db.execute(
        select(RpsChecklistResponse).where(
            RpsChecklistResponse.rps_version_id == rps_id,
            RpsChecklistResponse.checklist_item_id == item_id,
        )
    )).scalar_one_or_none()

    if not resp:
        raise HTTPException(404, "Checklist item tidak ditemukan")

    resp.is_fulfilled = body.is_fulfilled
    resp.catatan = body.catatan
    resp.checked_by = current_user.id
    resp.checked_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(resp)

    checklist_item = await db.get(RpsChecklistItem, item_id)
    resp.checklist_item = checklist_item
    return resp
