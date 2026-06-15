from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.database import get_db
from app.models.response import AnonymousCode, Response, ResponseItem, ResponseOpenAnswer
from app.models.instrument import InstrumentItem, CippSubDimension, CippDimension, OpenQuestion
from app.schemas.response import ResultResponse, CippScoreOut, OpenAnswerOut, CapaianOut
import math

# F-05.3: target capaian (skor Likert dianggap "tercapai" bila >= ambang ini)
CAPAIAN_TARGET = 3.5

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
    capaian = []
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
        # F-05.3: rincian capaian pembelajaran dari dimensi Product (E)
        if dim.kode == "E":
            for sd in dim.sub_dimensions:
                sd_scores = [item_score_map[it.id] for it in sd.items if it.id in item_score_map]
                if sd_scores:
                    rata = round(sum(sd_scores) / len(sd_scores), 2)
                    capaian.append(CapaianOut(
                        kode=sd.kode,
                        nama=sd.nama_id if bahasa == "id" else sd.nama_zh,
                        skor_rata=rata,
                        target=CAPAIAN_TARGET,
                        tercapai=rata >= CAPAIAN_TARGET,
                        jumlah_item=len(sd_scores),
                    ))

    open_rows = (await db.execute(
        select(ResponseOpenAnswer, OpenQuestion)
        .join(OpenQuestion, ResponseOpenAnswer.open_question_id == OpenQuestion.id)
        .where(ResponseOpenAnswer.response_id == response.id)
        .order_by(OpenQuestion.urutan)
    )).all()
    open_answers = [
        OpenAnswerOut(
            pertanyaan=q.pertanyaan_id if bahasa == "id" else q.pertanyaan_zh,
            jawaban=oa.jawaban_teks,
        )
        for oa, q in open_rows
    ]

    return ResultResponse(
        kode=anon.kode,
        course={"nama_id": course.nama_id, "nama_zh": course.nama_zh, "kode_mk": course.kode_mk},
        role=response.role,
        bahasa=response.bahasa,
        submitted_at=response.submitted_at,
        cipp_scores=cipp_scores,
        capaian_pembelajaran=capaian,
        open_answers=open_answers,
    )
