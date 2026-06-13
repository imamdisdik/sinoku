from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime
import uuid
from app.database import get_db
from app.dependencies import require_admin
from app.models.auth import User
from app.models.report import DiagnosticReport
from app.models.response import Response, ResponseItem
from app.models.respondent import Respondent
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem
from app.models.academic import University, Program, Course

router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ReportCreate(BaseModel):
    course_id: int
    periode_start: date
    periode_end: date
    title: str


class ReportOut(BaseModel):
    id: str
    title: str
    course_id: int
    university_id: int
    program_id: int
    periode_start: date
    periode_end: date
    generated_at: datetime
    snapshot_json: dict
    model_config = {"from_attributes": True}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _scope_responses(q, current_user: User):
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        q = q.join(Course, Response.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(Program.university_id == current_user.university_id)
        if current_user.role == "dosen" and current_user.program_id:
            q = q.where(Course.program_id == current_user.program_id)
    return q


async def _build_snapshot(course_id: int, periode_start: date, periode_end: date, db: AsyncSession) -> dict:
    """Bangun snapshot data CIPP lengkap untuk satu mata kuliah dan periode."""

    # Ambil semua respons selesai dalam periode
    q = select(Response).where(
        Response.course_id == course_id,
        Response.is_complete == True,
        Response.submitted_at >= datetime.combine(periode_start, datetime.min.time()),
        Response.submitted_at <= datetime.combine(periode_end, datetime.max.time()),
    )
    responses = (await db.execute(q)).scalars().all()
    ids_dosen = [r.id for r in responses if r.role == "dosen"]
    ids_mhs = [r.id for r in responses if r.role == "mahasiswa"]
    all_ids = ids_dosen + ids_mhs

    # Skor semua item
    if all_ids:
        score_rows = (await db.execute(
            select(ResponseItem.item_id, ResponseItem.response_id, ResponseItem.skor)
            .where(ResponseItem.response_id.in_(all_ids))
        )).all()
    else:
        score_rows = []

    score_index: dict = {}
    for item_id, resp_id, skor in score_rows:
        score_index.setdefault(item_id, {})[resp_id] = skor

    def mean_for(item_id, resp_ids):
        s = [score_index.get(item_id, {}).get(r) for r in resp_ids]
        s = [x for x in s if x is not None]
        return round(sum(s) / len(s), 2) if s else None

    # Dimensi & item
    dims = (await db.execute(
        select(CippDimension).order_by(CippDimension.urutan)
    )).scalars().all()

    dimensions_data = []
    overall_scores_d, overall_scores_m = [], []

    for dim in dims:
        subdim_ids = (await db.execute(
            select(CippSubDimension.id).where(CippSubDimension.dimension_id == dim.id)
        )).scalars().all()
        item_ids = (await db.execute(
            select(InstrumentItem.id).where(
                InstrumentItem.sub_dimension_id.in_(subdim_ids),
                InstrumentItem.is_active == True,
            )
        )).scalars().all()

        scores_d = [score_index.get(iid, {}).get(r) for iid in item_ids for r in ids_dosen]
        scores_d = [x for x in scores_d if x is not None]
        scores_m = [score_index.get(iid, {}).get(r) for iid in item_ids for r in ids_mhs]
        scores_m = [x for x in scores_m if x is not None]

        avg_d = round(sum(scores_d) / len(scores_d), 2) if scores_d else None
        avg_m = round(sum(scores_m) / len(scores_m), 2) if scores_m else None

        overall_scores_d.extend(scores_d)
        overall_scores_m.extend(scores_m)

        # Rekomendasi otomatis berdasarkan skor
        recommendation = _generate_recommendation(dim.kode, avg_d, avg_m)

        dimensions_data.append({
            "kode": dim.kode,
            "nama": dim.nama_id,
            "warna_hex": dim.warna_hex,
            "avg_dosen": avg_d,
            "avg_mahasiswa": avg_m,
            "n_dosen": len(scores_d),
            "n_mahasiswa": len(scores_m),
            "recommendation": recommendation,
        })

    # Skor keseluruhan CIPP
    overall_d = round(sum(overall_scores_d) / len(overall_scores_d), 2) if overall_scores_d else None
    overall_m = round(sum(overall_scores_m) / len(overall_scores_m), 2) if overall_scores_m else None

    # Profil responden
    respondent_ids = [r.respondent_id for r in responses if r.respondent_id]
    gender_dist: dict = {}
    semester_dist: dict = {}
    hsk_dist: dict = {}
    if respondent_ids:
        respondents = (await db.execute(
            select(Respondent).where(Respondent.id.in_(respondent_ids))
        )).scalars().all()
        for r in respondents:
            if r.gender:
                gender_dist[r.gender] = gender_dist.get(r.gender, 0) + 1
            if r.current_semester:
                k = f"Semester {r.current_semester}"
                semester_dist[k] = semester_dist.get(k, 0) + 1
            if r.hsk_level_mahasiswa:
                hsk_dist[r.hsk_level_mahasiswa] = hsk_dist.get(r.hsk_level_mahasiswa, 0) + 1

    return {
        "total_respons": len(responses),
        "total_dosen": len(ids_dosen),
        "total_mahasiswa": len(ids_mhs),
        "overall_avg_dosen": overall_d,
        "overall_avg_mahasiswa": overall_m,
        "dimensions": dimensions_data,
        "profil_responden": {
            "gender": gender_dist,
            "semester": semester_dist,
            "hsk": hsk_dist,
        },
    }


def _generate_recommendation(kode: str, avg_d, avg_m) -> str:
    """Hasilkan rekomendasi singkat berdasarkan skor dimensi."""
    label = {"B": "Konteks", "C": "Input", "D": "Proses", "E": "Produk"}.get(kode, kode)
    scores = [s for s in [avg_d, avg_m] if s is not None]
    if not scores:
        return f"Data {label} belum tersedia untuk dianalisis."
    avg = sum(scores) / len(scores)
    if avg >= 4.5:
        return f"Dimensi {label} menunjukkan performa sangat baik. Pertahankan dan jadikan best practice."
    elif avg >= 3.5:
        return f"Dimensi {label} baik. Identifikasi sub-aspek yang masih di bawah rata-rata untuk ditingkatkan."
    elif avg >= 2.5:
        return f"Dimensi {label} cukup. Diperlukan evaluasi dan perbaikan pada aspek-aspek yang lemah."
    else:
        return f"Dimensi {label} perlu perhatian serius. Rekomendasikan revisi menyeluruh pada komponen ini."


# ══════════════ ENDPOINTS ═════════════════════════════════════════════════════

@router.get("")
async def list_reports(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if current_user.role == "superadmin":
        q = select(DiagnosticReport)
    elif current_user.university_id:
        q = select(DiagnosticReport).where(
            DiagnosticReport.university_id == current_user.university_id
        )
    else:
        q = select(DiagnosticReport).where(
            DiagnosticReport.generated_by == current_user.id
        )
    if course_id:
        q = q.where(DiagnosticReport.course_id == course_id)
    q = q.order_by(DiagnosticReport.generated_at.desc())
    rows = (await db.execute(q)).scalars().all()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "course_id": r.course_id,
            "university_id": r.university_id,
            "program_id": r.program_id,
            "periode_start": r.periode_start.isoformat(),
            "periode_end": r.periode_end.isoformat(),
            "generated_at": r.generated_at.isoformat(),
        }
        for r in rows
    ]


@router.post("", status_code=201)
async def generate_report(
    body: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Generate snapshot laporan diagnostik untuk MK + periode tertentu."""
    course = await db.get(Course, body.course_id)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")

    # Validasi akses universitas
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        program = await db.get(Program, course.program_id)
        if not program or program.university_id != current_user.university_id:
            raise HTTPException(403, "Akses ditolak")
        university_id = current_user.university_id
        program_id = course.program_id
    else:
        program = await db.get(Program, course.program_id)
        university_id = program.university_id if program else 0
        program_id = course.program_id

    snapshot = await _build_snapshot(body.course_id, body.periode_start, body.periode_end, db)

    report = DiagnosticReport(
        generated_by=current_user.id,
        university_id=university_id,
        program_id=program_id,
        course_id=body.course_id,
        periode_start=body.periode_start,
        periode_end=body.periode_end,
        title=body.title,
        snapshot_json=snapshot,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return {
        "id": str(report.id),
        "title": report.title,
        "course_id": report.course_id,
        "generated_at": report.generated_at.isoformat(),
        "snapshot_json": report.snapshot_json,
    }


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    report = await db.get(DiagnosticReport, uuid.UUID(report_id))
    if not report:
        raise HTTPException(404, "Laporan tidak ditemukan")
    if current_user.role not in ("superadmin",) and report.university_id != current_user.university_id:
        raise HTTPException(403, "Akses ditolak")
    return {
        "id": str(report.id),
        "title": report.title,
        "course_id": report.course_id,
        "university_id": report.university_id,
        "program_id": report.program_id,
        "periode_start": report.periode_start.isoformat(),
        "periode_end": report.periode_end.isoformat(),
        "generated_at": report.generated_at.isoformat(),
        "snapshot_json": report.snapshot_json,
    }


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    report = await db.get(DiagnosticReport, uuid.UUID(report_id))
    if not report:
        raise HTTPException(404, "Laporan tidak ditemukan")
    if current_user.role not in ("superadmin",) and report.generated_by != current_user.id:
        raise HTTPException(403, "Hanya pembuat laporan yang dapat menghapus")
    await db.delete(report)
    await db.commit()
