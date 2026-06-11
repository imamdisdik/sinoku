"""Week 2 backend: Admin CRUD Academic + Dashboard"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

files = {}

# ── schemas/academic.py (extended) ──────────────────────────────────────────
files["app/schemas/academic.py"] = '''from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Public ───────────────────────────────────────────────────────────────────
class UniversityPublic(BaseModel):
    id: int
    nama: str
    nama_singkat: str
    kota: str
    provinsi: str
    model_config = {"from_attributes": True}


class ProgramPublic(BaseModel):
    id: int
    nama: str
    nama_singkat: str
    jenjang: str
    model_config = {"from_attributes": True}


class CoursePublic(BaseModel):
    id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    model_config = {"from_attributes": True}


# ── University ────────────────────────────────────────────────────────────────
class UniversityCreate(BaseModel):
    nama: str
    nama_singkat: str
    jenis: str
    kota: str
    provinsi: str
    website: Optional[str] = None
    akreditasi: Optional[str] = None
    tahun_berdiri: Optional[int] = None


class UniversityUpdate(BaseModel):
    nama: Optional[str] = None
    nama_singkat: Optional[str] = None
    jenis: Optional[str] = None
    kota: Optional[str] = None
    provinsi: Optional[str] = None
    website: Optional[str] = None
    akreditasi: Optional[str] = None
    tahun_berdiri: Optional[int] = None
    is_active: Optional[bool] = None


class UniversityOut(BaseModel):
    id: int
    nama: str
    nama_singkat: str
    jenis: str
    kota: str
    provinsi: str
    website: Optional[str]
    akreditasi: Optional[str]
    tahun_berdiri: Optional[int]
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Program ───────────────────────────────────────────────────────────────────
class ProgramCreate(BaseModel):
    university_id: int
    nama: str
    nama_singkat: str
    jenjang: str
    tahun_berdiri: Optional[int] = None
    akreditasi: Optional[str] = None


class ProgramUpdate(BaseModel):
    nama: Optional[str] = None
    nama_singkat: Optional[str] = None
    jenjang: Optional[str] = None
    tahun_berdiri: Optional[int] = None
    akreditasi: Optional[str] = None
    is_active: Optional[bool] = None


class ProgramOut(BaseModel):
    id: int
    university_id: int
    nama: str
    nama_singkat: str
    jenjang: str
    tahun_berdiri: Optional[int]
    akreditasi: Optional[str]
    is_active: bool
    model_config = {"from_attributes": True}


# ── Course ────────────────────────────────────────────────────────────────────
class CourseCreate(BaseModel):
    program_id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    status_mk: str = "wajib"
    deskripsi: Optional[str] = None


class CourseUpdate(BaseModel):
    kode_mk: Optional[str] = None
    nama_id: Optional[str] = None
    nama_zh: Optional[str] = None
    sks: Optional[int] = None
    semester: Optional[int] = None
    status_mk: Optional[str] = None
    deskripsi: Optional[str] = None
    is_active: Optional[bool] = None


class CourseOut(BaseModel):
    id: int
    program_id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    status_mk: str
    deskripsi: Optional[str]
    is_active: bool
    model_config = {"from_attributes": True}


# ── CPL ───────────────────────────────────────────────────────────────────────
class CplCreate(BaseModel):
    program_id: int
    kode_cpl: str
    deskripsi_id: str
    deskripsi_zh: str
    kategori: str  # sikap | pengetahuan | keterampilan


class CplUpdate(BaseModel):
    kode_cpl: Optional[str] = None
    deskripsi_id: Optional[str] = None
    deskripsi_zh: Optional[str] = None
    kategori: Optional[str] = None
    is_active: Optional[bool] = None


class CplOut(BaseModel):
    id: int
    program_id: int
    kode_cpl: str
    deskripsi_id: str
    deskripsi_zh: str
    kategori: str
    is_active: bool
    model_config = {"from_attributes": True}


# ── CPMK ──────────────────────────────────────────────────────────────────────
class CpmkCreate(BaseModel):
    course_id: int
    kode_cpmk: str
    deskripsi_id: str
    deskripsi_zh: str
    bobot_persen: float = Field(ge=0, le=100)


class CpmkUpdate(BaseModel):
    kode_cpmk: Optional[str] = None
    deskripsi_id: Optional[str] = None
    deskripsi_zh: Optional[str] = None
    bobot_persen: Optional[float] = None
    is_active: Optional[bool] = None


class CpmkOut(BaseModel):
    id: int
    course_id: int
    kode_cpmk: str
    deskripsi_id: str
    deskripsi_zh: str
    bobot_persen: float
    is_active: bool
    model_config = {"from_attributes": True}


# ── Mapping ───────────────────────────────────────────────────────────────────
class MappingIds(BaseModel):
    cpl_ids: List[int]


# ── Pagination wrapper ────────────────────────────────────────────────────────
class PagedUniversity(BaseModel):
    data: List[UniversityOut]
    total: int
    page: int
    limit: int


class PagedProgram(BaseModel):
    data: List[ProgramOut]
    total: int
    page: int
    limit: int


class PagedCourse(BaseModel):
    data: List[CourseOut]
    total: int
    page: int
    limit: int
'''

# ── routers/admin/academic.py ────────────────────────────────────────────────
files["app/routers/admin/academic.py"] = '''from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from typing import Optional
from app.database import get_db
from app.dependencies import require_admin, require_superadmin
from app.models.academic import University, Program, Course, Cpl, Cpmk, CourseCplMapping, CpmkCplMapping
from app.schemas.academic import (
    UniversityCreate, UniversityUpdate, UniversityOut, PagedUniversity,
    ProgramCreate, ProgramUpdate, ProgramOut, PagedProgram,
    CourseCreate, CourseUpdate, CourseOut, PagedCourse,
    CplCreate, CplUpdate, CplOut,
    CpmkCreate, CpmkUpdate, CpmkOut,
    MappingIds,
)

router = APIRouter(prefix="/admin", tags=["admin-academic"])


# ══════════════ UNIVERSITY ════════════════════════════════════════════════════

@router.get("/universities", response_model=PagedUniversity)
async def list_universities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q = select(University)
    if search:
        q = q.where(or_(University.nama.ilike(f"%{search}%"), University.nama_singkat.ilike(f"%{search}%")))
    if is_active is not None:
        q = q.where(University.is_active == is_active)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    rows = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": rows, "total": total, "page": page, "limit": limit}


@router.post("/universities", response_model=UniversityOut, status_code=201)
async def create_university(body: UniversityCreate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    u = University(**body.model_dump())
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


@router.get("/universities/{uid}", response_model=UniversityOut)
async def get_university(uid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    u = await db.get(University, uid)
    if not u:
        raise HTTPException(404, "Universitas tidak ditemukan")
    return u


@router.put("/universities/{uid}", response_model=UniversityOut)
async def update_university(uid: int, body: UniversityUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    u = await db.get(University, uid)
    if not u:
        raise HTTPException(404, "Universitas tidak ditemukan")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(u, k, v)
    await db.commit()
    await db.refresh(u)
    return u


@router.delete("/universities/{uid}", status_code=204)
async def delete_university(uid: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    u = await db.get(University, uid)
    if not u:
        raise HTTPException(404, "Universitas tidak ditemukan")
    await db.delete(u)
    await db.commit()


# ══════════════ PROGRAM ═══════════════════════════════════════════════════════

@router.get("/programs", response_model=PagedProgram)
async def list_programs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    university_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q = select(Program)
    if university_id:
        q = q.where(Program.university_id == university_id)
    if search:
        q = q.where(Program.nama.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    rows = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": rows, "total": total, "page": page, "limit": limit}


@router.post("/programs", response_model=ProgramOut, status_code=201)
async def create_program(body: ProgramCreate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    univ = await db.get(University, body.university_id)
    if not univ:
        raise HTTPException(404, "Universitas tidak ditemukan")
    p = Program(**body.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/programs/{pid}", response_model=ProgramOut)
async def get_program(pid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    p = await db.get(Program, pid)
    if not p:
        raise HTTPException(404, "Program tidak ditemukan")
    return p


@router.put("/programs/{pid}", response_model=ProgramOut)
async def update_program(pid: int, body: ProgramUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    p = await db.get(Program, pid)
    if not p:
        raise HTTPException(404, "Program tidak ditemukan")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/programs/{pid}", status_code=204)
async def delete_program(pid: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    p = await db.get(Program, pid)
    if not p:
        raise HTTPException(404, "Program tidak ditemukan")
    await db.delete(p)
    await db.commit()


# ══════════════ COURSE ════════════════════════════════════════════════════════

@router.get("/courses", response_model=PagedCourse)
async def list_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    program_id: Optional[int] = None,
    semester: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q = select(Course)
    if program_id:
        q = q.where(Course.program_id == program_id)
    if semester:
        q = q.where(Course.semester == semester)
    if search:
        q = q.where(or_(Course.nama_id.ilike(f"%{search}%"), Course.kode_mk.ilike(f"%{search}%")))
    if is_active is not None:
        q = q.where(Course.is_active == is_active)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    rows = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": rows, "total": total, "page": page, "limit": limit}


@router.post("/courses", response_model=CourseOut, status_code=201)
async def create_course(body: CourseCreate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    c = Course(**body.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@router.get("/courses/{cid}", response_model=CourseOut)
async def get_course(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    return c


@router.put("/courses/{cid}", response_model=CourseOut)
async def update_course(cid: int, body: CourseUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c


@router.delete("/courses/{cid}", status_code=204)
async def delete_course(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await db.delete(c)
    await db.commit()


@router.post("/courses/{cid}/cpls", status_code=201)
async def map_course_cpls(cid: int, body: MappingIds, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    for cpl_id in body.cpl_ids:
        exists = (await db.execute(
            select(CourseCplMapping).where(CourseCplMapping.course_id == cid, CourseCplMapping.cpl_id == cpl_id)
        )).scalar_one_or_none()
        if not exists:
            db.add(CourseCplMapping(course_id=cid, cpl_id=cpl_id))
    await db.commit()
    return {"mapped": len(body.cpl_ids)}


@router.delete("/courses/{cid}/cpls/{cpl_id}", status_code=204)
async def unmap_course_cpl(cid: int, cpl_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    await db.execute(delete(CourseCplMapping).where(CourseCplMapping.course_id == cid, CourseCplMapping.cpl_id == cpl_id))
    await db.commit()


# ══════════════ CPL ═══════════════════════════════════════════════════════════

@router.get("/cpls", response_model=list[CplOut])
async def list_cpls(
    program_id: Optional[int] = None,
    kategori: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q = select(Cpl)
    if program_id:
        q = q.where(Cpl.program_id == program_id)
    if kategori:
        q = q.where(Cpl.kategori == kategori)
    rows = (await db.execute(q)).scalars().all()
    return rows


@router.post("/cpls", response_model=CplOut, status_code=201)
async def create_cpl(body: CplCreate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    cpl = Cpl(**body.model_dump())
    db.add(cpl)
    await db.commit()
    await db.refresh(cpl)
    return cpl


@router.get("/cpls/{cid}", response_model=CplOut)
async def get_cpl(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    cpl = await db.get(Cpl, cid)
    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan")
    return cpl


@router.put("/cpls/{cid}", response_model=CplOut)
async def update_cpl(cid: int, body: CplUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    cpl = await db.get(Cpl, cid)
    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(cpl, k, v)
    await db.commit()
    await db.refresh(cpl)
    return cpl


@router.delete("/cpls/{cid}", status_code=204)
async def delete_cpl(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    cpl = await db.get(Cpl, cid)
    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan")
    await db.delete(cpl)
    await db.commit()


# ══════════════ CPMK ══════════════════════════════════════════════════════════

@router.get("/cpmks", response_model=list[CpmkOut])
async def list_cpmks(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q = select(Cpmk)
    if course_id:
        q = q.where(Cpmk.course_id == course_id)
    rows = (await db.execute(q)).scalars().all()
    return rows


@router.post("/cpmks", response_model=CpmkOut, status_code=201)
async def create_cpmk(body: CpmkCreate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    cpmk = Cpmk(**body.model_dump())
    db.add(cpmk)
    await db.commit()
    await db.refresh(cpmk)
    return cpmk


@router.get("/cpmks/{cid}", response_model=CpmkOut)
async def get_cpmk(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    cpmk = await db.get(Cpmk, cid)
    if not cpmk:
        raise HTTPException(404, "CPMK tidak ditemukan")
    return cpmk


@router.put("/cpmks/{cid}", response_model=CpmkOut)
async def update_cpmk(cid: int, body: CpmkUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    cpmk = await db.get(Cpmk, cid)
    if not cpmk:
        raise HTTPException(404, "CPMK tidak ditemukan")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(cpmk, k, v)
    await db.commit()
    await db.refresh(cpmk)
    return cpmk


@router.delete("/cpmks/{cid}", status_code=204)
async def delete_cpmk(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    cpmk = await db.get(Cpmk, cid)
    if not cpmk:
        raise HTTPException(404, "CPMK tidak ditemukan")
    await db.delete(cpmk)
    await db.commit()


@router.post("/cpmks/{cid}/cpls", status_code=201)
async def map_cpmk_cpls(cid: int, body: MappingIds, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    for cpl_id in body.cpl_ids:
        exists = (await db.execute(
            select(CpmkCplMapping).where(CpmkCplMapping.cpmk_id == cid, CpmkCplMapping.cpl_id == cpl_id)
        )).scalar_one_or_none()
        if not exists:
            db.add(CpmkCplMapping(cpmk_id=cid, cpl_id=cpl_id))
    await db.commit()
    return {"mapped": len(body.cpl_ids)}


@router.delete("/cpmks/{cid}/cpls/{cpl_id}", status_code=204)
async def unmap_cpmk_cpl(cid: int, cpl_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_superadmin)):
    await db.execute(delete(CpmkCplMapping).where(CpmkCplMapping.cpmk_id == cid, CpmkCplMapping.cpl_id == cpl_id))
    await db.commit()
'''

# ── routers/admin/dashboard.py ───────────────────────────────────────────────
files["app/routers/admin/dashboard.py"] = '''from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import date
from app.database import get_db
from app.dependencies import require_admin
from app.models.response import Response, ResponseItem
from app.models.respondent import Respondent
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem
from app.models.academic import University, Program, Course

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])


@router.get("/kpi")
async def dashboard_kpi(
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
    course_id: Optional[int] = None,
    periode_start: Optional[date] = None,
    periode_end: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q_resp = select(Response).where(Response.status == "submitted")
    if course_id:
        q_resp = q_resp.where(Response.course_id == course_id)
    if periode_start:
        q_resp = q_resp.where(Response.submitted_at >= periode_start)
    if periode_end:
        q_resp = q_resp.where(Response.submitted_at <= periode_end)

    responses = (await db.execute(q_resp)).scalars().all()
    response_ids = [r.id for r in responses]

    total_responses = len(responses)

    q_respondent = select(Respondent)
    if response_ids:
        q_respondent = q_respondent.where(Respondent.id.in_([r.respondent_id for r in responses]))
    respondents = (await db.execute(q_respondent)).scalars().all()
    total_dosen = sum(1 for r in respondents if r.role == "dosen")
    total_mahasiswa = sum(1 for r in respondents if r.role == "mahasiswa")

    dims = (await db.execute(select(CippDimension).order_by(CippDimension.urutan))).scalars().all()
    cipp_by_dimension = []
    all_scores = []

    for dim in dims:
        subdim_ids = (await db.execute(
            select(CippSubDimension.id).where(CippSubDimension.dimension_id == dim.id)
        )).scalars().all()
        item_ids = (await db.execute(
            select(InstrumentItem.id).where(InstrumentItem.sub_dimension_id.in_(subdim_ids))
        )).scalars().all()

        if not item_ids or not response_ids:
            cipp_by_dimension.append({"kode": dim.kode, "nama": dim.nama_dimensi, "rata_rata": 0.0, "std_dev": 0.0})
            continue

        scores = (await db.execute(
            select(ResponseItem.skor).where(
                ResponseItem.response_id.in_(response_ids),
                ResponseItem.item_id.in_(item_ids),
            )
        )).scalars().all()

        if scores:
            avg = sum(scores) / len(scores)
            std = (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5
            all_scores.extend(scores)
        else:
            avg, std = 0.0, 0.0

        cipp_by_dimension.append({
            "kode": dim.kode,
            "nama": dim.nama_dimensi,
            "rata_rata": round(avg, 2),
            "std_dev": round(std, 2),
        })

    avg_cipp = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

    from collections import defaultdict
    trend_map = defaultdict(int)
    for r in responses:
        if r.submitted_at:
            key = r.submitted_at.strftime("%Y-%m")
            trend_map[key] += 1
    response_trend = [{"bulan": k, "jumlah": v} for k, v in sorted(trend_map.items())]

    univ_result = await db.execute(select(func.count()).select_from(University).where(University.is_active == True))
    total_universities = univ_result.scalar()

    return {
        "total_responses": total_responses,
        "total_dosen": total_dosen,
        "total_mahasiswa": total_mahasiswa,
        "total_universities": total_universities,
        "avg_cipp_score": avg_cipp,
        "cipp_by_dimension": cipp_by_dimension,
        "response_trend": response_trend,
    }


@router.get("/problem-heatmap")
async def problem_heatmap(
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
    course_id: Optional[int] = None,
    threshold: float = Query(3.0, ge=1.0, le=5.0),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    q_resp = select(Response.id).where(Response.status == "submitted")
    if course_id:
        q_resp = q_resp.where(Response.course_id == course_id)
    response_ids = (await db.execute(q_resp)).scalars().all()

    if not response_ids:
        return {"items": []}

    items = (await db.execute(
        select(InstrumentItem, CippSubDimension, CippDimension)
        .join(CippSubDimension, InstrumentItem.sub_dimension_id == CippSubDimension.id)
        .join(CippDimension, CippSubDimension.dimension_id == CippDimension.id)
        .where(InstrumentItem.is_active == True)
    )).all()

    result = []
    for item, subdim, dim in items:
        scores_dosen = (await db.execute(
            select(ResponseItem.skor)
            .join(Response, ResponseItem.response_id == Response.id)
            .join(Respondent, Response.respondent_id == Respondent.id)
            .where(
                ResponseItem.item_id == item.id,
                ResponseItem.response_id.in_(response_ids),
                Respondent.role == "dosen",
            )
        )).scalars().all()

        scores_mhs = (await db.execute(
            select(ResponseItem.skor)
            .join(Response, ResponseItem.response_id == Response.id)
            .join(Respondent, Response.respondent_id == Respondent.id)
            .where(
                ResponseItem.item_id == item.id,
                ResponseItem.response_id.in_(response_ids),
                Respondent.role == "mahasiswa",
            )
        )).scalars().all()

        avg_d = round(sum(scores_dosen) / len(scores_dosen), 2) if scores_dosen else None
        avg_m = round(sum(scores_mhs) / len(scores_mhs), 2) if scores_mhs else None

        if (avg_d is not None and avg_d < threshold) or (avg_m is not None and avg_m < threshold):
            gap = round(abs((avg_d or 0) - (avg_m or 0)), 2)
            result.append({
                "item_id": item.id,
                "kode": item.kode,
                "teks_id": item.text_id_dosen,
                "dimensi": dim.kode,
                "sub_dimensi": subdim.kode,
                "skor_dosen": avg_d,
                "skor_mahasiswa": avg_m,
                "gap": gap,
            })

    result.sort(key=lambda x: min(x["skor_dosen"] or 5, x["skor_mahasiswa"] or 5))
    return {"items": result}
'''

# ── routers/admin/__init__.py ────────────────────────────────────────────────
files["app/routers/admin/__init__.py"] = ""

# ── main.py (updated) ────────────────────────────────────────────────────────
files["app/main.py"] = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.core.exceptions import validation_exception_handler, generic_exception_handler
from app.core.middleware import log_request_middleware
from app.routers.auth import router as auth_router
from app.routers.public.landing import router as landing_router
from app.routers.public.survey import router as survey_router
from app.routers.public.result import router as result_router
from app.routers.admin.academic import router as academic_router
from app.routers.admin.dashboard import router as dashboard_router

app = FastAPI(
    title="SINOKU API",
    description="Sistem Evaluasi & Monitoring Mata Kuliah Budaya Tiongkok",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

API_PREFIX = "/api/v1"
app.include_router(auth_router,      prefix=API_PREFIX)
app.include_router(landing_router,   prefix=API_PREFIX)
app.include_router(survey_router,    prefix=API_PREFIX)
app.include_router(result_router,    prefix=API_PREFIX)
app.include_router(academic_router,  prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sinoku-api"}
'''

# ── Write all files ──────────────────────────────────────────────────────────
for rel, content in files.items():
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK {rel}")

print(f"Done - {len(files)} files written.")
