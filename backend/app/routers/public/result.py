from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.database import get_db
from app.models.response import AnonymousCode, Response, ResponseItem, ResponseOpenAnswer
from app.models.instrument import InstrumentItem, CippSubDimension, CippDimension, OpenQuestion
from app.schemas.response import ResultResponse, CippScoreOut, OpenAnswerOut
import math

router = APIRouter(prefix="/public", tags=["public-result"])


@router.get("/result/{kode}", response_model=ResultResponse)
async def get_result(kode: str, db: AsyncSession = Depends(get_db)):
    anon_result = await db.execute(
        select(AnonymousCode).where(AnonymousCode.kode == kode)
    )
    anon = anon_result.scalar_one_or_none()
    if not anon:
        raise HTTPException(status_code=404, detail="Kode tidak ditemukan")
    if not anon.is_accessible:
        raise HTTPException(status_code=403, detail="Akses kode anonim tidak aktif")

    anon.last_accessed = datetime.now(timezone.utc)

    response = await db.get(Response, anon.response_id)
    from app.models.academic import Course
    course = await db.get(Course, response.course_id)

    items_result = await db.execute(
        select(ResponseItem).where(ResponseItem.response_id == response.id)
    )
    response_items = items_result.scalars().all()

    dims_result = await db.execute(
        select(CippDimension).options(
            selectinload(CippDimension.sub_dimensions).selectinload(CippSubDimension.items)
        ).order_by(CippDimension.urutan)
    )
    dimensions = dims_result.scalars().all()

    item_score_map = {ri.item_id: ri.skor for ri in response_items}
    bahasa = response.bahasa

    cipp_scores = []
    for dim in dimensions:
        scores = []
        for sd in dim.sub_dimensions:
            for item in sd.items:
                if item.id in item_score_map:
                    scores.append(item_score_map[item.id])
        if scores:
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            cipp_scores.append(CippScoreOut(
                dimensi=dim.nama_id if bahasa == "id" else dim.nama_zh,
                kode=dim.kode,
                skor_rata=round(mean, 2),
                std_dev=round(math.sqrt(variance), 2),
                jumlah_item=len(scores),
            ))

    open_result = await db.execute(
        select(ResponseOpenAnswer).where(ResponseOpenAnswer.response_id == response.id)
    )
    open_answers_db = open_result.scalars().all()
    open_answers = []
    for oa in open_answers_db:
        q = await db.get(OpenQuestion, oa.open_question_id)
        if q:
            open_answers.append(OpenAnswerOut(
                pertanyaan=q.pertanyaan_id if bahasa == "id" else q.pertanyaan_zh,
                jawaban=oa.jawaban_teks,
            ))

    return ResultResponse(
        kode=anon.kode,
        course={"nama_id": course.nama_id, "nama_zh": course.nama_zh, "kode_mk": course.kode_mk},
        role=response.role,
        bahasa=response.bahasa,
        submitted_at=response.submitted_at,
        cipp_scores=cipp_scores,
        open_answers=open_answers,
    )
