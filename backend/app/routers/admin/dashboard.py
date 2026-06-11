from fastapi import APIRouter, Depends, Query
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
