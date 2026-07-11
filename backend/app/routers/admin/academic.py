from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from typing import Optional
from app.database import get_db
from app.dependencies import (
    require_admin, require_superadmin, require_superadmin_or_admin,
    is_scoped, program_scope_condition, program_in_scope, assert_program_in_scope,
)
from app.models.academic import University, Faculty, Program, Course, Cpl, Cpmk, CourseCplMapping, CpmkCplMapping, CourseLecturer
from app.models.auth import User
from app.models.response import Response
from app.models.report import DiagnosticReport
from app.schemas.academic import (
    UniversityCreate, UniversityUpdate, UniversityOut, PagedUniversity, LogoUpdate,
    FacultyCreate, FacultyUpdate, FacultyOut, PagedFaculty,
    ProgramCreate, ProgramUpdate, ProgramOut, PagedProgram,
    CourseCreate, CourseUpdate, CourseOut, PagedCourse,
    CplCreate, CplUpdate, CplOut,
    CpmkCreate, CpmkUpdate, CpmkOut,
    MappingIds, AssignLecturers,
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
    current_user=Depends(require_admin),
):
    q = select(University)
    # Scoping: non-superadmin hanya melihat universitasnya sendiri
    if current_user.role != "superadmin" and current_user.university_id:
        q = q.where(University.id == current_user.university_id)
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


@router.put("/universities/{uid}/logo", response_model=UniversityOut)
async def update_university_logo(uid: int, body: LogoUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    """Set/hapus logo universitas. Superadmin: univ mana pun; Admin Universitas: miliknya."""
    u = await db.get(University, uid)
    if not u:
        raise HTTPException(404, "Universitas tidak ditemukan")
    if current_user.role != "superadmin":
        if not (current_user.role == "admin_universitas" and current_user.university_id == uid):
            raise HTTPException(403, "Di luar cakupan Anda")
    u.logo_url = body.logo_url
    await db.commit()
    await db.refresh(u)
    return u


# ══════════════ FACULTY ═══════════════════════════════════════════════════════

def _faculty_scope(q, user):
    """Batasi daftar fakultas sesuai cakupan peran."""
    if user.role == "superadmin":
        return q
    if user.role == "admin_fakultas" and user.faculty_id:
        return q.where(Faculty.id == user.faculty_id)
    if user.university_id:
        return q.where(Faculty.university_id == user.university_id)
    if user.program_id:
        return q.where(Faculty.id == select(Program.faculty_id).where(Program.id == user.program_id).scalar_subquery())
    return q.where(Faculty.id == -1)


@router.get("/faculties", response_model=PagedFaculty)
async def list_faculties(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=500),
    university_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    q = select(Faculty)
    q = _faculty_scope(q, current_user)
    if current_user.role == "superadmin" and university_id:
        q = q.where(Faculty.university_id == university_id)
    if search:
        q = q.where(or_(Faculty.nama.ilike(f"%{search}%"), Faculty.nama_singkat.ilike(f"%{search}%")))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    rows = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": rows, "total": total, "page": page, "limit": limit}


def _can_manage_faculty_univ(user, university_id: int) -> bool:
    if user.role == "superadmin":
        return True
    if user.role == "admin_universitas":
        return bool(user.university_id) and university_id == user.university_id
    return False


@router.post("/faculties", response_model=FacultyOut, status_code=201)
async def create_faculty(body: FacultyCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    univ = await db.get(University, body.university_id)
    if not univ:
        raise HTTPException(404, "Universitas tidak ditemukan")
    if not _can_manage_faculty_univ(current_user, body.university_id):
        raise HTTPException(403, "Di luar cakupan Anda")
    f = Faculty(**body.model_dump())
    db.add(f)
    await db.commit()
    await db.refresh(f)
    return f


@router.get("/faculties/{fid}", response_model=FacultyOut)
async def get_faculty(fid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    f = await db.get(Faculty, fid)
    if not f:
        raise HTTPException(404, "Fakultas tidak ditemukan")
    return f


@router.put("/faculties/{fid}", response_model=FacultyOut)
async def update_faculty(fid: int, body: FacultyUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    f = await db.get(Faculty, fid)
    if not f:
        raise HTTPException(404, "Fakultas tidak ditemukan")
    if not _can_manage_faculty_univ(current_user, f.university_id):
        raise HTTPException(403, "Di luar cakupan Anda")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(f, k, v)
    await db.commit()
    await db.refresh(f)
    return f


@router.delete("/faculties/{fid}", status_code=204)
async def delete_faculty(fid: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    f = await db.get(Faculty, fid)
    if not f:
        raise HTTPException(404, "Fakultas tidak ditemukan")
    if not _can_manage_faculty_univ(current_user, f.university_id):
        raise HTTPException(403, "Di luar cakupan Anda")
    await db.delete(f)
    await db.commit()


# ══════════════ PROGRAM ═══════════════════════════════════════════════════════

@router.get("/programs", response_model=PagedProgram)
async def list_programs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=500),
    university_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    q = select(Program)
    # Scoping: tiap peran hanya lihat prodi dalam cakupannya
    if is_scoped(current_user):
        q = q.where(program_scope_condition(current_user))
    elif university_id:
        q = q.where(Program.university_id == university_id)
    if faculty_id:
        q = q.where(Program.faculty_id == faculty_id)
    if search:
        q = q.where(Program.nama.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    rows = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": rows, "total": total, "page": page, "limit": limit}


@router.post("/programs", response_model=ProgramOut, status_code=201)
async def create_program(body: ProgramCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    univ = await db.get(University, body.university_id)
    if not univ:
        raise HTTPException(404, "Universitas tidak ditemukan")
    # Scope tulis: hanya superadmin/admin_universitas (univ sendiri) & admin_fakultas (fakultas sendiri)
    if current_user.role == "admin_universitas" and body.university_id != current_user.university_id:
        raise HTTPException(403, "Di luar cakupan Anda")
    if current_user.role == "admin_fakultas" and body.faculty_id != current_user.faculty_id:
        raise HTTPException(403, "Prodi harus di fakultas Anda")
    if current_user.role == "admin_prodi":
        raise HTTPException(403, "Admin Prodi tidak dapat membuat program studi")
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
async def update_program(pid: int, body: ProgramUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    p = await db.get(Program, pid)
    if not p:
        raise HTTPException(404, "Program tidak ditemukan")
    if current_user.role == "admin_prodi" or not program_in_scope(current_user, p):
        raise HTTPException(403, "Di luar cakupan Anda")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/programs/{pid}", status_code=204)
async def delete_program(pid: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    p = await db.get(Program, pid)
    if not p:
        raise HTTPException(404, "Program tidak ditemukan")
    if current_user.role == "admin_prodi" or not program_in_scope(current_user, p):
        raise HTTPException(403, "Di luar cakupan Anda")
    await db.delete(p)
    await db.commit()


# ══════════════ COURSE ════════════════════════════════════════════════════════

@router.get("/courses", response_model=PagedCourse)
async def list_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=500),
    program_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    university_id: Optional[int] = None,
    semester: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    q = select(Course)
    joined_program = False
    # Scoping: tiap peran hanya lihat MK dalam cakupannya (via join program)
    if is_scoped(current_user):
        q = q.join(Program, Course.program_id == Program.id).where(program_scope_condition(current_user))
        joined_program = True
    if faculty_id or university_id:
        if not joined_program:
            q = q.join(Program, Course.program_id == Program.id)
            joined_program = True
        if faculty_id:
            q = q.where(Program.faculty_id == faculty_id)
        if university_id:
            q = q.where(Program.university_id == university_id)
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
async def create_course(body: CourseCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    await assert_program_in_scope(db, current_user, body.program_id)
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
async def update_course(cid: int, body: CourseUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await assert_program_in_scope(db, current_user, c.program_id)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c


@router.delete("/courses/{cid}", status_code=204)
async def delete_course(cid: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await assert_program_in_scope(db, current_user, c.program_id)
    # Hapus dependensi ber-FK RESTRICT secara manual agar MK bisa dihapus.
    # Laporan diagnostik & respons evaluasi (respons cascade ke response_items,
    # response_open_answers, anonymous_codes lewat ON DELETE CASCADE di DB).
    await db.execute(delete(DiagnosticReport).where(DiagnosticReport.course_id == cid))
    await db.execute(delete(Response).where(Response.course_id == cid))
    # MK dihapus → cpmks, rps, assessment_schemes, mbkm, mapping ikut via CASCADE.
    await db.delete(c)
    await db.commit()


@router.get("/courses/{cid}/cpls", response_model=list[int])
async def get_course_cpls(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    rows = (await db.execute(
        select(CourseCplMapping.cpl_id).where(CourseCplMapping.course_id == cid)
    )).scalars().all()
    return rows


@router.post("/courses/{cid}/cpls", status_code=201)
async def map_course_cpls(cid: int, body: MappingIds, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    c = await db.get(Course, cid)
    if not c:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await assert_program_in_scope(db, current_user, c.program_id)
    existing_ids = set((await db.execute(
        select(CourseCplMapping.cpl_id).where(
            CourseCplMapping.course_id == cid,
            CourseCplMapping.cpl_id.in_(body.cpl_ids),
        )
    )).scalars().all())
    for cpl_id in body.cpl_ids:
        if cpl_id not in existing_ids:
            db.add(CourseCplMapping(course_id=cid, cpl_id=cpl_id))
    await db.commit()
    return {"mapped": len(body.cpl_ids)}


@router.delete("/courses/{cid}/cpls/{cpl_id}", status_code=204)
async def unmap_course_cpl(cid: int, cpl_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    c = await db.get(Course, cid)
    if c:
        await assert_program_in_scope(db, current_user, c.program_id)
    await db.execute(delete(CourseCplMapping).where(CourseCplMapping.course_id == cid, CourseCplMapping.cpl_id == cpl_id))
    await db.commit()


# ── Dosen Pengampu MK (course_lecturers) ──────────────────────────────────────

@router.get("/courses/{cid}/lecturers")
async def get_course_lecturers(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    rows = (await db.execute(
        select(User.id, User.full_name, User.email)
        .join(CourseLecturer, CourseLecturer.user_id == User.id)
        .where(CourseLecturer.course_id == cid)
        .order_by(User.full_name)
    )).all()
    return [{"id": str(r.id), "full_name": r.full_name, "email": r.email} for r in rows]


@router.get("/courses/{cid}/available-lecturers")
async def available_lecturers(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    """Dosen yang boleh diampukan ke MK ini: dosen aktif di prodi MK."""
    course = await db.get(Course, cid)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    rows = (await db.execute(
        select(User.id, User.full_name, User.email)
        .where(User.role == "dosen", User.program_id == course.program_id, User.is_active == True)
        .order_by(User.full_name)
    )).all()
    return [{"id": str(r.id), "full_name": r.full_name, "email": r.email} for r in rows]


@router.post("/courses/{cid}/lecturers", status_code=201)
async def assign_course_lecturers(cid: int, body: AssignLecturers, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    course = await db.get(Course, cid)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await assert_program_in_scope(db, current_user, course.program_id)
    existing = set(str(x) for x in (await db.execute(
        select(CourseLecturer.user_id).where(CourseLecturer.course_id == cid)
    )).scalars().all())
    added = 0
    for uid in body.user_ids:
        if uid in existing:
            continue
        u = await db.get(User, uid)
        if not u or u.role != "dosen" or u.program_id != course.program_id:
            raise HTTPException(400, "Dosen tidak valid untuk prodi mata kuliah ini")
        db.add(CourseLecturer(course_id=cid, user_id=uid))
        added += 1
    await db.commit()
    return {"assigned": added}


@router.delete("/courses/{cid}/lecturers/{user_id}", status_code=204)
async def unassign_course_lecturer(cid: int, user_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    course = await db.get(Course, cid)
    if course:
        await assert_program_in_scope(db, current_user, course.program_id)
    await db.execute(delete(CourseLecturer).where(CourseLecturer.course_id == cid, CourseLecturer.user_id == user_id))
    await db.commit()


@router.get("/my-courses", response_model=list[CourseOut])
async def my_taught_courses(db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    """MK yang diampu oleh dosen yang sedang login (untuk evaluasi dosen)."""
    rows = (await db.execute(
        select(Course)
        .join(CourseLecturer, CourseLecturer.course_id == Course.id)
        .where(CourseLecturer.user_id == current_user.id, Course.is_active == True)
        .order_by(Course.kode_mk)
    )).scalars().all()
    return rows


# ══════════════ CPL ═══════════════════════════════════════════════════════════

@router.get("/cpls", response_model=list[CplOut])
async def list_cpls(
    program_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    university_id: Optional[int] = None,
    kategori: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    q = select(Cpl)
    joined_program = False
    # Scoping: tiap peran hanya lihat CPL dalam cakupannya (via join program)
    if is_scoped(current_user):
        q = q.join(Program, Cpl.program_id == Program.id).where(program_scope_condition(current_user))
        joined_program = True
    if faculty_id or university_id:
        if not joined_program:
            q = q.join(Program, Cpl.program_id == Program.id)
            joined_program = True
        if faculty_id:
            q = q.where(Program.faculty_id == faculty_id)
        if university_id:
            q = q.where(Program.university_id == university_id)
    if program_id:
        q = q.where(Cpl.program_id == program_id)
    if kategori:
        q = q.where(Cpl.kategori == kategori)
    rows = (await db.execute(q)).scalars().all()
    return rows


@router.post("/cpls", response_model=CplOut, status_code=201)
async def create_cpl(body: CplCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    await assert_program_in_scope(db, current_user, body.program_id)
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
async def update_cpl(cid: int, body: CplUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    cpl = await db.get(Cpl, cid)
    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan")
    await assert_program_in_scope(db, current_user, cpl.program_id)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(cpl, k, v)
    await db.commit()
    await db.refresh(cpl)
    return cpl


@router.delete("/cpls/{cid}", status_code=204)
async def delete_cpl(cid: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    cpl = await db.get(Cpl, cid)
    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan")
    await assert_program_in_scope(db, current_user, cpl.program_id)
    await db.delete(cpl)
    await db.commit()


# ══════════════ CPMK ══════════════════════════════════════════════════════════

@router.get("/cpmks", response_model=list[CpmkOut])
async def list_cpmks(
    course_id: Optional[int] = None,
    program_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    university_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    q = select(Cpmk)
    joined = False
    # Scoping: tiap peran hanya lihat CPMK dalam cakupannya (via join course→program)
    if is_scoped(current_user):
        q = q.join(Course, Cpmk.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(program_scope_condition(current_user))
        joined = True
    if program_id or faculty_id or university_id:
        if not joined:
            q = q.join(Course, Cpmk.course_id == Course.id).join(Program, Course.program_id == Program.id)
            joined = True
        if program_id:
            q = q.where(Course.program_id == program_id)
        if faculty_id:
            q = q.where(Program.faculty_id == faculty_id)
        if university_id:
            q = q.where(Program.university_id == university_id)
    if course_id:
        q = q.where(Cpmk.course_id == course_id)
    rows = (await db.execute(q)).scalars().all()
    return rows


async def _assert_cpmk_scope(db, current_user, course_id: int):
    """Validasi cakupan tulis CPMK lewat course → program."""
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    await assert_program_in_scope(db, current_user, course.program_id)


@router.post("/cpmks", response_model=CpmkOut, status_code=201)
async def create_cpmk(body: CpmkCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    await _assert_cpmk_scope(db, current_user, body.course_id)
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
async def update_cpmk(cid: int, body: CpmkUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    cpmk = await db.get(Cpmk, cid)
    if not cpmk:
        raise HTTPException(404, "CPMK tidak ditemukan")
    await _assert_cpmk_scope(db, current_user, cpmk.course_id)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(cpmk, k, v)
    await db.commit()
    await db.refresh(cpmk)
    return cpmk


@router.delete("/cpmks/{cid}", status_code=204)
async def delete_cpmk(cid: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    cpmk = await db.get(Cpmk, cid)
    if not cpmk:
        raise HTTPException(404, "CPMK tidak ditemukan")
    await _assert_cpmk_scope(db, current_user, cpmk.course_id)
    await db.delete(cpmk)
    await db.commit()


@router.get("/cpmks/{cid}/cpls", response_model=list[int])
async def get_cpmk_cpls(cid: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    rows = (await db.execute(
        select(CpmkCplMapping.cpl_id).where(CpmkCplMapping.cpmk_id == cid)
    )).scalars().all()
    return rows


@router.post("/cpmks/{cid}/cpls", status_code=201)
async def map_cpmk_cpls(cid: int, body: MappingIds, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    cpmk = await db.get(Cpmk, cid)
    if cpmk:
        await _assert_cpmk_scope(db, current_user, cpmk.course_id)
    existing_ids = set((await db.execute(
        select(CpmkCplMapping.cpl_id).where(
            CpmkCplMapping.cpmk_id == cid,
            CpmkCplMapping.cpl_id.in_(body.cpl_ids),
        )
    )).scalars().all())
    for cpl_id in body.cpl_ids:
        if cpl_id not in existing_ids:
            db.add(CpmkCplMapping(cpmk_id=cid, cpl_id=cpl_id))
    await db.commit()
    return {"mapped": len(body.cpl_ids)}


@router.delete("/cpmks/{cid}/cpls/{cpl_id}", status_code=204)
async def unmap_cpmk_cpl(cid: int, cpl_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_superadmin_or_admin)):
    cpmk = await db.get(Cpmk, cid)
    if cpmk:
        await _assert_cpmk_scope(db, current_user, cpmk.course_id)
    await db.execute(delete(CpmkCplMapping).where(CpmkCplMapping.cpmk_id == cid, CpmkCplMapping.cpl_id == cpl_id))
    await db.commit()
