from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from typing import Optional
from datetime import date
from app.database import get_db
from app.dependencies import require_admin, is_scoped, program_scope_condition
from app.models.auth import User
from app.models.response import Response, ResponseItem
from app.models.respondent import Respondent
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem
from app.models.academic import University, Program, Course

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])


def _scope_responses(q, current_user: User, university_id=None, program_id=None, faculty_id=None, lecturer_id=None):
    """Filter response berdasarkan scope role + filter eksplisit univ/prodi/fakultas/dosen (F-07.3)."""
    if lecturer_id:
        q = q.where(Response.evaluated_lecturer_id == lecturer_id)
    scoped = is_scoped(current_user)
    if scoped or university_id or program_id or faculty_id:
        q = q.join(Course, Response.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        )
        if scoped:
            q = q.where(program_scope_condition(current_user))
        if university_id:
            q = q.where(Program.university_id == university_id)
        if program_id:
            q = q.where(Course.program_id == program_id)
        if faculty_id:
            q = q.where(Program.faculty_id == faculty_id)
    return q


@router.get("/kpi")
async def dashboard_kpi(
    course_id: Optional[int] = None,
    periode_start: Optional[date] = None,
    periode_end: Optional[date] = None,
    university_id: Optional[int] = None,
    program_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    lecturer_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q_resp = select(Response).where(Response.is_complete == True)
    q_resp = _scope_responses(q_resp, current_user, university_id, program_id, faculty_id, lecturer_id)

    if course_id:
        q_resp = q_resp.where(Response.course_id == course_id)
    if periode_start:
        q_resp = q_resp.where(Response.submitted_at >= periode_start)
    if periode_end:
        q_resp = q_resp.where(Response.submitted_at <= periode_end)

    responses = (await db.execute(q_resp)).scalars().all()
    response_ids = [r.id for r in responses]

    total_responses = len(responses)
    total_dosen = sum(1 for r in responses if r.role == "dosen")
    total_mahasiswa = sum(1 for r in responses if r.role == "mahasiswa")

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
            cipp_by_dimension.append({"kode": dim.kode, "nama": dim.nama_id, "rata_rata": 0.0, "std_dev": 0.0})
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
            "nama": dim.nama_id,
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

    # Total universitas: superadmin lihat semua, admin lihat 1
    if current_user.role == "superadmin":
        total_universities = (await db.execute(
            select(func.count()).select_from(University).where(University.is_active == True)
        )).scalar()
    else:
        total_universities = 1

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
    course_id: Optional[int] = None,
    threshold: float = Query(3.0, ge=1.0, le=5.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q_resp = select(Response.id).where(Response.is_complete == True)
    q_resp = _scope_responses(q_resp, current_user)
    if course_id:
        q_resp = q_resp.where(Response.course_id == course_id)
    response_ids = (await db.execute(q_resp)).scalars().all()

    if not response_ids:
        return {"items": []}

    # Satu query: avg per item split dosen/mahasiswa menggunakan conditional aggregation
    agg_rows = (await db.execute(
        select(
            InstrumentItem.id,
            InstrumentItem.kode,
            InstrumentItem.text_id_dosen,
            CippSubDimension.kode.label("sub_kode"),
            CippDimension.kode.label("dim_kode"),
            func.avg(case((Response.role == "dosen", ResponseItem.skor), else_=None)).label("avg_dosen"),
            func.avg(case((Response.role == "mahasiswa", ResponseItem.skor), else_=None)).label("avg_mhs"),
        )
        .join(ResponseItem, ResponseItem.item_id == InstrumentItem.id)
        .join(Response, ResponseItem.response_id == Response.id)
        .join(CippSubDimension, InstrumentItem.sub_dimension_id == CippSubDimension.id)
        .join(CippDimension, CippSubDimension.dimension_id == CippDimension.id)
        .where(
            InstrumentItem.is_active == True,
            ResponseItem.response_id.in_(response_ids),
        )
        .group_by(
            InstrumentItem.id, InstrumentItem.kode, InstrumentItem.text_id_dosen,
            CippSubDimension.kode, CippDimension.kode,
        )
    )).all()

    result = []
    for row in agg_rows:
        avg_d = round(float(row.avg_dosen), 2) if row.avg_dosen is not None else None
        avg_m = round(float(row.avg_mhs), 2) if row.avg_mhs is not None else None
        if (avg_d is not None and avg_d < threshold) or (avg_m is not None and avg_m < threshold):
            gap = round(abs((avg_d or 0) - (avg_m or 0)), 2)
            result.append({
                "item_id": row.id,
                "kode": row.kode,
                "teks_id": row.text_id_dosen,
                "dimensi": row.dim_kode,
                "sub_dimensi": row.sub_kode,
                "skor_dosen": avg_d,
                "skor_mahasiswa": avg_m,
                "gap": gap,
            })

    result.sort(key=lambda x: min(x["skor_dosen"] or 5, x["skor_mahasiswa"] or 5))
    return {"items": result}
