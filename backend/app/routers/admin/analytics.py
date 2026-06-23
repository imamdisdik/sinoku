from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Sequence
from datetime import date
from app.database import get_db
from app.dependencies import require_admin, is_scoped, program_scope_condition
from app.models.auth import User
from app.models.response import Response, ResponseItem
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem
from app.models.academic import Course, Program, Cpl, Cpmk, CpmkCplMapping

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


def _base_response_ids_query(
    role: str,
    course_id: Optional[int],
    current_user: User,
    periode_start: Optional[date] = None,
    periode_end: Optional[date] = None,
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
):
    q = select(Response.id).where(
        Response.is_complete == True,
        Response.role == role,
    )
    if course_id:
        q = q.where(Response.course_id == course_id)
    # UC-17f: filter periode (inklusif, berdasarkan tanggal submit)
    if periode_start:
        q = q.where(func.date(Response.submitted_at) >= periode_start)
    if periode_end:
        q = q.where(func.date(Response.submitted_at) <= periode_end)

    # F-07.3: filter global univ/prodi (untuk superadmin) + scoping per peran.
    scoped = is_scoped(current_user)
    if scoped or university_id or program_id:
        q = q.join(Course, Response.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        )
        if scoped:
            q = q.where(program_scope_condition(current_user))
        if university_id:
            q = q.where(Program.university_id == university_id)
        if program_id:
            q = q.where(Course.program_id == program_id)
    return q


async def _avg_scores_for(
    db: AsyncSession,
    response_ids: Sequence,
    item_ids: Sequence,
):
    if not response_ids or not item_ids:
        return None, 0
    scores = (await db.execute(
        select(ResponseItem.skor).where(
            ResponseItem.response_id.in_(response_ids),
            ResponseItem.item_id.in_(item_ids),
        )
    )).scalars().all()
    if not scores:
        return None, 0
    return round(sum(scores) / len(scores), 2), len(scores)


async def _distribution_for(
    db: AsyncSession,
    response_ids: Sequence,
    item_ids: Sequence,
):
    dist: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    if not response_ids or not item_ids:
        return dist, 0, 0.0
    rows = (await db.execute(
        select(ResponseItem.skor).where(
            ResponseItem.response_id.in_(response_ids),
            ResponseItem.item_id.in_(item_ids),
        )
    )).scalars().all()
    for s in rows:
        if s in dist:
            dist[s] += 1
    total = sum(dist.values())
    mean = round(sum(k * v for k, v in dist.items()) / total, 2) if total else 0.0
    return dist, total, mean


async def _get_item_ids_for_dim(db: AsyncSession, dim_id: int) -> list[int]:
    subdim_ids = (await db.execute(
        select(CippSubDimension.id).where(CippSubDimension.dimension_id == dim_id)
    )).scalars().all()
    if not subdim_ids:
        return []
    return list((await db.execute(
        select(InstrumentItem.id).where(
            InstrumentItem.sub_dimension_id.in_(subdim_ids),
            InstrumentItem.is_active == True,
        )
    )).scalars().all())


@router.get("/comparison")
async def comparison(
    course_id: Optional[int] = None,
    periode_start: Optional[date] = None,
    periode_end: Optional[date] = None,
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Skor rata-rata per dimensi CIPP, dipisah antara dosen dan mahasiswa."""
    ids_dosen = (await db.execute(
        _base_response_ids_query("dosen", course_id, current_user, periode_start, periode_end, university_id, program_id)
    )).scalars().all()
    ids_mhs = (await db.execute(
        _base_response_ids_query("mahasiswa", course_id, current_user, periode_start, periode_end, university_id, program_id)
    )).scalars().all()

    dims = (await db.execute(
        select(CippDimension).order_by(CippDimension.urutan)
    )).scalars().all()

    result = []
    for dim in dims:
        item_ids = await _get_item_ids_for_dim(db, dim.id)
        avg_d, n_d = await _avg_scores_for(db, ids_dosen, item_ids)
        avg_m, n_m = await _avg_scores_for(db, ids_mhs, item_ids)
        result.append({
            "kode": dim.kode,
            "nama": dim.nama_id,
            "warna_hex": dim.warna_hex,
            "skor_dosen": avg_d,
            "skor_mahasiswa": avg_m,
            "n_dosen": n_d,
            "n_mahasiswa": n_m,
        })

    return {
        "total_dosen": len(ids_dosen),
        "total_mahasiswa": len(ids_mhs),
        "dimensions": result,
    }


@router.get("/distribution")
async def distribution(
    course_id: Optional[int] = None,
    dimensi: Optional[str] = None,
    periode_start: Optional[date] = None,
    periode_end: Optional[date] = None,
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Distribusi frekuensi skor Likert 1–5 per dimensi, dipisah dosen vs mahasiswa."""
    ids_dosen = (await db.execute(
        _base_response_ids_query("dosen", course_id, current_user, periode_start, periode_end, university_id, program_id)
    )).scalars().all()
    ids_mhs = (await db.execute(
        _base_response_ids_query("mahasiswa", course_id, current_user, periode_start, periode_end, university_id, program_id)
    )).scalars().all()

    if dimensi:
        dim_obj = (await db.execute(
            select(CippDimension).where(CippDimension.kode == dimensi.upper())
        )).scalar_one_or_none()
        dims = [dim_obj] if dim_obj else []
    else:
        dims = (await db.execute(
            select(CippDimension).order_by(CippDimension.urutan)
        )).scalars().all()

    result = []
    for dim in dims:
        item_ids = await _get_item_ids_for_dim(db, dim.id)
        dist_d, n_d, mean_d = await _distribution_for(db, ids_dosen, item_ids)
        dist_m, n_m, mean_m = await _distribution_for(db, ids_mhs, item_ids)
        result.append({
            "kode": dim.kode,
            "nama": dim.nama_id,
            "warna_hex": dim.warna_hex,
            "dosen": {"distribution": dist_d, "n": n_d, "mean": mean_d},
            "mahasiswa": {"distribution": dist_m, "n": n_m, "mean": mean_m},
        })

    return {"dimensions": result}


# ══════════════ UC-17b: PERBANDINGAN UNIV / PRODI / MK ════════════════════════

@router.get("/comparison-groups")
async def comparison_groups(
    group_by: str = Query("university", pattern="^(university|program|course)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Perbandingan skor CIPP antar Universitas / Program Studi / Mata Kuliah.

    Admin/dosen hanya melihat grup di universitasnya sendiri.
    """
    from app.models.academic import University

    # Peta dimensi → item_ids (sekali saja)
    dims = (await db.execute(
        select(CippDimension).order_by(CippDimension.urutan)
    )).scalars().all()
    dim_items: dict[str, list[int]] = {}
    for dim in dims:
        dim_items[dim.kode] = await _get_item_ids_for_dim(db, dim.id)

    # Tentukan daftar grup sesuai scoping per peran
    scoped = is_scoped(current_user)

    if group_by == "university":
        q = select(University)
        if scoped and current_user.university_id:
            q = q.where(University.id == current_user.university_id)
        elif scoped and current_user.program_id:
            q = q.where(University.id == select(Program.university_id).where(Program.id == current_user.program_id).scalar_subquery())
        elif scoped:
            q = q.where(University.id == -1)
        groups = [(u.id, u.nama_singkat or u.nama) for u in (await db.execute(q.order_by(University.nama))).scalars().all()]
    elif group_by == "program":
        q = select(Program)
        if scoped:
            q = q.where(program_scope_condition(current_user))
        groups = [(p.id, p.nama_singkat or p.nama) for p in (await db.execute(q.order_by(Program.nama))).scalars().all()]
    else:  # course
        q = select(Course)
        if scoped:
            q = q.join(Program, Course.program_id == Program.id).where(program_scope_condition(current_user))
        groups = [(c.id, c.kode_mk) for c in (await db.execute(q.order_by(Course.kode_mk))).scalars().all()]

    def _group_response_ids_query(group_id: int):
        base = select(Response.id).where(Response.is_complete == True)
        if group_by == "course":
            return base.where(Response.course_id == group_id)
        # university / program butuh join ke course→program
        base = base.join(Course, Response.course_id == Course.id)
        if group_by == "program":
            return base.where(Course.program_id == group_id)
        return base.join(Program, Course.program_id == Program.id).where(Program.university_id == group_id)

    result = []
    for gid, gname in groups:
        resp_ids = (await db.execute(_group_response_ids_query(gid))).scalars().all()
        cipp: dict[str, float | None] = {}
        for dim in dims:
            avg, _ = await _avg_scores_for(db, resp_ids, dim_items[dim.kode])
            cipp[dim.kode] = avg
        # hanya tampilkan grup yang punya respons
        if resp_ids:
            result.append({
                "group_id": gid,
                "group_nama": gname,
                "n_responses": len(resp_ids),
                "cipp": cipp,
            })

    return {
        "group_by": group_by,
        "dimensions": [{"kode": d.kode, "nama": d.nama_id, "warna_hex": d.warna_hex} for d in dims],
        "data": result,
    }


# ══════════════ UC-17a: SKOR CIPP PER DIMENSI + SUB-DIMENSI ══════════════════

@router.get("/cipp-scores")
async def cipp_scores(
    course_id: Optional[int] = None,
    role: Optional[str] = Query(None, pattern="^(dosen|mahasiswa)$"),
    periode_start: Optional[date] = None,
    periode_end: Optional[date] = None,
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Skor rata-rata CIPP per dimensi beserta breakdown per sub-dimensi."""
    ids_dosen = (await db.execute(
        _base_response_ids_query("dosen", course_id, current_user, periode_start, periode_end, university_id, program_id)
    )).scalars().all()
    ids_mhs = (await db.execute(
        _base_response_ids_query("mahasiswa", course_id, current_user, periode_start, periode_end, university_id, program_id)
    )).scalars().all()

    if role == "dosen":
        active_ids = ids_dosen
    elif role == "mahasiswa":
        active_ids = ids_mhs
    else:
        active_ids = list(ids_dosen) + list(ids_mhs)

    dims = (await db.execute(
        select(CippDimension).order_by(CippDimension.urutan)
    )).scalars().all()

    result = []
    for dim in dims:
        subdims = (await db.execute(
            select(CippSubDimension)
            .where(CippSubDimension.dimension_id == dim.id)
            .order_by(CippSubDimension.urutan)
        )).scalars().all()

        subdim_out = []
        dim_scores: list[float] = []

        for sd in subdims:
            item_ids = (await db.execute(
                select(InstrumentItem.id).where(
                    InstrumentItem.sub_dimension_id == sd.id,
                    InstrumentItem.is_active == True,
                )
            )).scalars().all()

            if item_ids and active_ids:
                scores = (await db.execute(
                    select(ResponseItem.skor).where(
                        ResponseItem.response_id.in_(active_ids),
                        ResponseItem.item_id.in_(item_ids),
                    )
                )).scalars().all()
                n = len(scores)
                avg = round(sum(scores) / n, 2) if n else None
                std = round((sum((s - (avg or 0)) ** 2 for s in scores) / n) ** 0.5, 2) if n > 1 else 0.0
            else:
                scores, n, avg, std = [], 0, None, 0.0

            if scores:
                dim_scores.extend(scores)

            subdim_out.append({
                "kode": sd.kode,
                "nama": sd.nama_id,
                "rata_rata": avg,
                "std_dev": std,
                "n": n,
            })

        n_dim = len(dim_scores)
        avg_dim = round(sum(dim_scores) / n_dim, 2) if n_dim else None
        std_dim = round((sum((s - (avg_dim or 0)) ** 2 for s in dim_scores) / n_dim) ** 0.5, 2) if n_dim > 1 else 0.0

        result.append({
            "kode": dim.kode,
            "nama": dim.nama_id,
            "warna_hex": dim.warna_hex,
            "rata_rata": avg_dim,
            "std_dev": std_dim,
            "n": n_dim,
            "sub_dimensions": subdim_out,
        })

    return {
        "total_responses": len(active_ids),
        "total_dosen": len(ids_dosen),
        "total_mahasiswa": len(ids_mhs),
        "dimensions": result,
    }


# ══════════════ UC-17c: MATRIKS CPL-CPMK ═════════════════════════════════════

@router.get("/cpl-cpmk-matrix")
async def cpl_cpmk_matrix(
    course_id: int = Query(..., description="ID mata kuliah (wajib)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Matriks pemetaan CPL-CPMK untuk satu mata kuliah, dilengkapi rata-rata skor."""
    course = await db.get(Course, course_id)
    if not course:
        from fastapi import HTTPException
        raise HTTPException(404, "Mata kuliah tidak ditemukan")

    # CPL terkait mata kuliah (via CourseCplMapping)
    from app.models.academic import CourseCplMapping
    cpl_ids = (await db.execute(
        select(CourseCplMapping.cpl_id).where(CourseCplMapping.course_id == course_id)
    )).scalars().all()

    cpls = []
    if cpl_ids:
        cpls = (await db.execute(
            select(Cpl).where(Cpl.id.in_(cpl_ids)).order_by(Cpl.kode_cpl)
        )).scalars().all()

    # CPMK mata kuliah
    cpmks = (await db.execute(
        select(Cpmk).where(Cpmk.course_id == course_id, Cpmk.is_active == True).order_by(Cpmk.kode_cpmk)
    )).scalars().all()

    cpmk_ids = [c.id for c in cpmks]

    # Mapping yang ada
    mappings = set()
    if cpmk_ids and cpl_ids:
        rows = (await db.execute(
            select(CpmkCplMapping.cpmk_id, CpmkCplMapping.cpl_id).where(
                CpmkCplMapping.cpmk_id.in_(cpmk_ids),
                CpmkCplMapping.cpl_id.in_(cpl_ids),
            )
        )).all()
        mappings = {(r.cpmk_id, r.cpl_id) for r in rows}

    # Skor rata-rata per CPMK (dari rubrik assessment → respons)
    # Gunakan skor dari ResponseItem berdasarkan item instrumen yang terkait kode CPMK
    # Simplified: avg skor semua respons di MK ini
    resp_ids = (await db.execute(
        select(Response.id).where(Response.course_id == course_id, Response.is_complete == True)
    )).scalars().all()

    cpmk_avg: dict[int, tuple[float | None, int]] = {}
    for cpmk in cpmks:
        # Cari rubrik terkait CPMK ini untuk mendapatkan rata-rata skor rubrik
        from app.models.assessment import AssessmentRubric, AssessmentScheme
        rubric_rows = (await db.execute(
            select(AssessmentRubric.skor_min, AssessmentRubric.skor_max)
            .join(AssessmentScheme, AssessmentRubric.assessment_scheme_id == AssessmentScheme.id)
            .where(
                AssessmentScheme.course_id == course_id,
                AssessmentRubric.cpmk_id == cpmk.id,
            )
        )).all()

        if rubric_rows:
            midpoints = [(r.skor_min + r.skor_max) / 2 for r in rubric_rows]
            avg = round(sum(midpoints) / len(midpoints), 2)
            cpmk_avg[cpmk.id] = (avg, len(rubric_rows))
        else:
            cpmk_avg[cpmk.id] = (None, 0)

    matrix = [
        {
            "cpmk_id": cpmk.id,
            "cpl_id": cpl.id,
            "has_mapping": (cpmk.id, cpl.id) in mappings,
            "avg_score": cpmk_avg.get(cpmk.id, (None, 0))[0],
            "n": cpmk_avg.get(cpmk.id, (None, 0))[1],
        }
        for cpmk in cpmks
        for cpl in cpls
    ]

    return {
        "course": {"id": course.id, "nama": course.nama_id, "kode_mk": course.kode_mk},
        "cpls": [{"id": c.id, "kode": c.kode_cpl, "deskripsi": c.deskripsi_id} for c in cpls],
        "cpmks": [{"id": c.id, "kode": c.kode_cpmk, "deskripsi": c.deskripsi_id, "bobot": float(c.bobot_persen)} for c in cpmks],
        "matrix": matrix,
    }
