from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence
from app.database import get_db
from app.dependencies import require_admin
from app.models.auth import User
from app.models.response import Response, ResponseItem
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem
from app.models.academic import Course, Program

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


def _base_response_ids_query(role: str, course_id: Optional[int], current_user: User):
    q = select(Response.id).where(
        Response.is_complete == True,
        Response.role == role,
    )
    if course_id:
        q = q.where(Response.course_id == course_id)
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        q = q.join(Course, Response.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(Program.university_id == current_user.university_id)
        if current_user.role == "dosen" and current_user.program_id:
            q = q.where(Course.program_id == current_user.program_id)
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Skor rata-rata per dimensi CIPP, dipisah antara dosen dan mahasiswa."""
    ids_dosen = (await db.execute(
        _base_response_ids_query("dosen", course_id, current_user)
    )).scalars().all()
    ids_mhs = (await db.execute(
        _base_response_ids_query("mahasiswa", course_id, current_user)
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Distribusi frekuensi skor Likert 1–5 per dimensi, dipisah dosen vs mahasiswa."""
    ids_dosen = (await db.execute(
        _base_response_ids_query("dosen", course_id, current_user)
    )).scalars().all()
    ids_mhs = (await db.execute(
        _base_response_ids_query("mahasiswa", course_id, current_user)
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
