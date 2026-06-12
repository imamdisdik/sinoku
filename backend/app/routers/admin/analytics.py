from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.database import get_db
from app.dependencies import require_admin
from app.models.auth import User
from app.models.response import Response, ResponseItem
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem
from app.models.academic import Course, Program

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


def _scope_responses(q, current_user: User):
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        q = q.join(Course, Response.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(Program.university_id == current_user.university_id)
        if current_user.role == "dosen" and current_user.program_id:
            q = q.where(Course.program_id == current_user.program_id)
    return q


@router.get("/comparison")
async def comparison(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Skor rata-rata per dimensi CIPP, dipisah antara dosen dan mahasiswa."""
    # Ambil response IDs per role
    def base_q(role: str):
        q = select(Response.id).where(Response.is_complete == True, Response.role == role)
        q = _scope_responses(q, current_user)
        if course_id:
            q = q.where(Response.course_id == course_id)
        return q

    ids_dosen = (await db.execute(base_q("dosen"))).scalars().all()
    ids_mhs = (await db.execute(base_q("mahasiswa"))).scalars().all()

    dims = (await db.execute(
        select(CippDimension).order_by(CippDimension.urutan)
    )).scalars().all()

    result = []
    for dim in dims:
        subdim_ids = (await db.execute(
            select(CippSubDimension.id).where(CippSubDimension.dimension_id == dim.id)
        )).scalars().all()
        item_ids = (await db.execute(
            select(InstrumentItem.id).where(InstrumentItem.sub_dimension_id.in_(subdim_ids), InstrumentItem.is_active == True)
        )).scalars().all()

        async def avg_scores(response_ids, item_ids):
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

        avg_d, n_d = await avg_scores(ids_dosen, item_ids)
        avg_m, n_m = await avg_scores(ids_mhs, item_ids)

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
    def base_q(role: str):
        q = select(Response.id).where(Response.is_complete == True, Response.role == role)
        q = _scope_responses(q, current_user)
        if course_id:
            q = q.where(Response.course_id == course_id)
        return q

    ids_dosen = (await db.execute(base_q("dosen"))).scalars().all()
    ids_mhs = (await db.execute(base_q("mahasiswa"))).scalars().all()

    # Filter dimensi
    dim_filter = []
    if dimensi:
        dim_obj = (await db.execute(
            select(CippDimension).where(CippDimension.kode == dimensi.upper())
        )).scalar_one_or_none()
        if dim_obj:
            dim_filter = [dim_obj]
    else:
        dim_filter = (await db.execute(
            select(CippDimension).order_by(CippDimension.urutan)
        )).scalars().all()

    result = []
    for dim in dim_filter:
        subdim_ids = (await db.execute(
            select(CippSubDimension.id).where(CippSubDimension.dimension_id == dim.id)
        )).scalars().all()
        item_ids = (await db.execute(
            select(InstrumentItem.id).where(
                InstrumentItem.sub_dimension_id.in_(subdim_ids),
                InstrumentItem.is_active == True,
            )
        )).scalars().all()

        async def get_dist(response_ids):
            dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
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

        dist_d, n_d, mean_d = await get_dist(ids_dosen)
        dist_m, n_m, mean_m = await get_dist(ids_mhs)

        result.append({
            "kode": dim.kode,
            "nama": dim.nama_id,
            "warna_hex": dim.warna_hex,
            "dosen": {
                "distribution": dist_d,
                "n": n_d,
                "mean": mean_d,
            },
            "mahasiswa": {
                "distribution": dist_m,
                "n": n_m,
                "mean": mean_m,
            },
        })

    return {"dimensions": result}
