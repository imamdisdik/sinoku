from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    limit: int = Query(20, ge=1, le=500),
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
    limit: int = Query(20, ge=1, le=500),
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
    limit: int = Query(20, ge=1, le=500),
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


@router.get("/courses/{cid}/cpls", response_model=list[int])
async def get_course_cpls(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    rows = (await db.execute(
        select(CourseCplMapping.cpl_id).where(CourseCplMapping.course_id == cid)
    )).scalars().all()
    return rows


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


@router.get("/cpmks/{cid}/cpls", response_model=list[int])
async def get_cpmk_cpls(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    rows = (await db.execute(
        select(CpmkCplMapping.cpl_id).where(CpmkCplMapping.cpmk_id == cid)
    )).scalars().all()
    return rows


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
