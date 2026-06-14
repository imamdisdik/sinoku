from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel, Field
from app.database import get_db
from app.dependencies import require_admin, require_superadmin_or_admin
from app.models.auth import User
from app.models.assessment import AssessmentScheme, AssessmentRubric, MbkmIntegration
from app.models.academic import Course, Program

router = APIRouter(prefix="/admin/assessment", tags=["admin-assessment"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SchemeOut(BaseModel):
    id: int
    course_id: int
    rps_version_id: Optional[int] = None
    nama_komponen: str
    tipe: str
    bobot_persen: float
    deskripsi: Optional[str] = None
    model_config = {"from_attributes": True}


class SchemeCreate(BaseModel):
    course_id: int
    rps_version_id: Optional[int] = None
    nama_komponen: str
    tipe: str
    bobot_persen: float = Field(ge=0, le=100)
    deskripsi: Optional[str] = None


class SchemeUpdate(BaseModel):
    nama_komponen: Optional[str] = None
    tipe: Optional[str] = None
    bobot_persen: Optional[float] = Field(default=None, ge=0, le=100)
    deskripsi: Optional[str] = None
    rps_version_id: Optional[int] = None


class RubricOut(BaseModel):
    id: int
    assessment_scheme_id: int
    cpmk_id: int
    level: str
    skor_min: float
    skor_max: float
    deskriptor: str
    model_config = {"from_attributes": True}


class RubricCreate(BaseModel):
    cpmk_id: int
    level: str
    skor_min: float = Field(ge=0, le=100)
    skor_max: float = Field(ge=0, le=100)
    deskriptor: str


class RubricUpdate(BaseModel):
    cpmk_id: Optional[int] = None
    level: Optional[str] = None
    skor_min: Optional[float] = Field(default=None, ge=0, le=100)
    skor_max: Optional[float] = Field(default=None, ge=0, le=100)
    deskriptor: Optional[str] = None


class MbkmOut(BaseModel):
    id: int
    course_id: int
    jenis_program: str
    nama_mitra: str
    deskripsi: Optional[str] = None
    sks_diakui: int
    tahun_akademik: str
    is_active: bool
    model_config = {"from_attributes": True}


class MbkmCreate(BaseModel):
    course_id: int
    jenis_program: str
    nama_mitra: str
    deskripsi: Optional[str] = None
    sks_diakui: int = Field(ge=1, le=24)
    tahun_akademik: str


class MbkmUpdate(BaseModel):
    jenis_program: Optional[str] = None
    nama_mitra: Optional[str] = None
    deskripsi: Optional[str] = None
    sks_diakui: Optional[int] = Field(default=None, ge=1, le=24)
    tahun_akademik: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _check_course_access(course_id: int, current_user: User, db: AsyncSession) -> Course:
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        program = await db.get(Program, course.program_id)
        if not program or program.university_id != current_user.university_id:
            raise HTTPException(403, "Akses ditolak")
    return course


async def _check_scheme_access(scheme_id: int, current_user: User, db: AsyncSession) -> AssessmentScheme:
    scheme = await db.get(AssessmentScheme, scheme_id)
    if not scheme:
        raise HTTPException(404, "Skema penilaian tidak ditemukan")
    await _check_course_access(scheme.course_id, current_user, db)
    return scheme


def _scope_scheme(q, current_user: User):
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        q = q.join(Course, AssessmentScheme.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(Program.university_id == current_user.university_id)
    return q


def _scope_mbkm(q, current_user: User):
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        q = q.join(Course, MbkmIntegration.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(Program.university_id == current_user.university_id)
    return q


# ══════════════ ASSESSMENT SCHEME (UC-14j) ════════════════════════════════════

@router.get("/schemes", response_model=list[SchemeOut])
async def list_schemes(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q = select(AssessmentScheme)
    q = _scope_scheme(q, current_user)
    if course_id:
        q = q.where(AssessmentScheme.course_id == course_id)
    rows = (await db.execute(q.order_by(AssessmentScheme.tipe, AssessmentScheme.nama_komponen))).scalars().all()
    return rows


@router.post("/schemes", response_model=SchemeOut, status_code=201)
async def create_scheme(
    body: SchemeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    await _check_course_access(body.course_id, current_user, db)
    scheme = AssessmentScheme(**body.model_dump())
    db.add(scheme)
    await db.commit()
    await db.refresh(scheme)
    return scheme


@router.get("/schemes/{scheme_id}", response_model=SchemeOut)
async def get_scheme(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await _check_scheme_access(scheme_id, current_user, db)


@router.put("/schemes/{scheme_id}", response_model=SchemeOut)
async def update_scheme(
    scheme_id: int,
    body: SchemeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    scheme = await _check_scheme_access(scheme_id, current_user, db)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(scheme, k, v)
    await db.commit()
    await db.refresh(scheme)
    return scheme


@router.delete("/schemes/{scheme_id}", status_code=204)
async def delete_scheme(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    scheme = await _check_scheme_access(scheme_id, current_user, db)
    await db.delete(scheme)
    await db.commit()


# ══════════════ RUBRIK (UC-14k) ═══════════════════════════════════════════════

@router.get("/schemes/{scheme_id}/rubrics", response_model=list[RubricOut])
async def list_rubrics(
    scheme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await _check_scheme_access(scheme_id, current_user, db)
    rows = (await db.execute(
        select(AssessmentRubric)
        .where(AssessmentRubric.assessment_scheme_id == scheme_id)
        .order_by(AssessmentRubric.cpmk_id, AssessmentRubric.skor_max.desc())
    )).scalars().all()
    return rows


@router.post("/schemes/{scheme_id}/rubrics", response_model=RubricOut, status_code=201)
async def create_rubric(
    scheme_id: int,
    body: RubricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    await _check_scheme_access(scheme_id, current_user, db)
    if body.skor_min >= body.skor_max:
        raise HTTPException(400, "skor_min harus lebih kecil dari skor_max")
    rubric = AssessmentRubric(assessment_scheme_id=scheme_id, **body.model_dump())
    db.add(rubric)
    await db.commit()
    await db.refresh(rubric)
    return rubric


@router.put("/rubrics/{rubric_id}", response_model=RubricOut)
async def update_rubric(
    rubric_id: int,
    body: RubricUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    rubric = await db.get(AssessmentRubric, rubric_id)
    if not rubric:
        raise HTTPException(404, "Rubrik tidak ditemukan")
    await _check_scheme_access(rubric.assessment_scheme_id, current_user, db)
    data = body.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(rubric, k, v)
    skor_min = data.get("skor_min", float(rubric.skor_min))
    skor_max = data.get("skor_max", float(rubric.skor_max))
    if skor_min >= skor_max:
        raise HTTPException(400, "skor_min harus lebih kecil dari skor_max")
    await db.commit()
    await db.refresh(rubric)
    return rubric


@router.delete("/rubrics/{rubric_id}", status_code=204)
async def delete_rubric(
    rubric_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    rubric = await db.get(AssessmentRubric, rubric_id)
    if not rubric:
        raise HTTPException(404, "Rubrik tidak ditemukan")
    await _check_scheme_access(rubric.assessment_scheme_id, current_user, db)
    await db.delete(rubric)
    await db.commit()


# ══════════════ MBKM INTEGRATION (UC-14l) ═════════════════════════════════════

@router.get("/mbkm", response_model=list[MbkmOut])
async def list_mbkm(
    course_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q = select(MbkmIntegration)
    q = _scope_mbkm(q, current_user)
    if course_id:
        q = q.where(MbkmIntegration.course_id == course_id)
    if is_active is not None:
        q = q.where(MbkmIntegration.is_active == is_active)
    rows = (await db.execute(q.order_by(MbkmIntegration.tahun_akademik.desc()))).scalars().all()
    return rows


@router.post("/mbkm", response_model=MbkmOut, status_code=201)
async def create_mbkm(
    body: MbkmCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    await _check_course_access(body.course_id, current_user, db)
    mbkm = MbkmIntegration(**body.model_dump())
    db.add(mbkm)
    await db.commit()
    await db.refresh(mbkm)
    return mbkm


@router.get("/mbkm/{mbkm_id}", response_model=MbkmOut)
async def get_mbkm(
    mbkm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    mbkm = await db.get(MbkmIntegration, mbkm_id)
    if not mbkm:
        raise HTTPException(404, "Data MBKM tidak ditemukan")
    await _check_course_access(mbkm.course_id, current_user, db)
    return mbkm


@router.put("/mbkm/{mbkm_id}", response_model=MbkmOut)
async def update_mbkm(
    mbkm_id: int,
    body: MbkmUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    mbkm = await db.get(MbkmIntegration, mbkm_id)
    if not mbkm:
        raise HTTPException(404, "Data MBKM tidak ditemukan")
    await _check_course_access(mbkm.course_id, current_user, db)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(mbkm, k, v)
    await db.commit()
    await db.refresh(mbkm)
    return mbkm


@router.delete("/mbkm/{mbkm_id}", status_code=204)
async def delete_mbkm(
    mbkm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    mbkm = await db.get(MbkmIntegration, mbkm_id)
    if not mbkm:
        raise HTTPException(404, "Data MBKM tidak ditemukan")
    await _check_course_access(mbkm.course_id, current_user, db)
    await db.delete(mbkm)
    await db.commit()


@router.patch("/mbkm/{mbkm_id}/toggle", response_model=MbkmOut)
async def toggle_mbkm(
    mbkm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    mbkm = await db.get(MbkmIntegration, mbkm_id)
    if not mbkm:
        raise HTTPException(404, "Data MBKM tidak ditemukan")
    await _check_course_access(mbkm.course_id, current_user, db)
    mbkm.is_active = not mbkm.is_active
    await db.commit()
    await db.refresh(mbkm)
    return mbkm
