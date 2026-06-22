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
from app.models.academic import University, Program, Course, Cpmk, CourseCplMapping, CpmkCplMapping
from app.models.rps import RpsVersion, RpsChecklistItem, RpsChecklistResponse
from app.models.assessment import AssessmentScheme

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

    # UC-19c/d/f: keselarasan RPS-asesmen, analisis CPL-CPMK, saran revisi
    rps_alignment = await _build_rps_alignment(course_id, db)
    cpl_cpmk = await _build_cpl_cpmk_analysis(course_id, db)
    rps_suggestions = _build_rps_suggestions(dimensions_data, rps_alignment, cpl_cpmk)

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
        "rps_alignment": rps_alignment,       # UC-19c
        "cpl_cpmk_analysis": cpl_cpmk,        # UC-19d
        "rps_suggestions": rps_suggestions,   # UC-19f
    }


async def _build_rps_alignment(course_id: int, db: AsyncSession) -> dict:
    """UC-19c: Keselarasan RPS & Asesmen — status RPS aktif, % kelengkapan checklist, skema asesmen."""
    rps = (await db.execute(
        select(RpsVersion)
        .where(RpsVersion.course_id == course_id)
        .order_by(RpsVersion.status == "aktif", RpsVersion.created_at.desc())
    )).scalars().first()

    checklist_pct = None
    checklist_total = checklist_fulfilled = 0
    unmet_components: list[str] = []
    if rps:
        rows = (await db.execute(
            select(RpsChecklistResponse, RpsChecklistItem)
            .join(RpsChecklistItem, RpsChecklistResponse.checklist_item_id == RpsChecklistItem.id)
            .where(RpsChecklistResponse.rps_version_id == rps.id)
        )).all()
        checklist_total = len(rows)
        checklist_fulfilled = sum(1 for r, _ in rows if r.is_fulfilled)
        unmet_components = [item.nama_komponen for r, item in rows if not r.is_fulfilled and item.is_mandatory]
        if checklist_total:
            checklist_pct = round(checklist_fulfilled / checklist_total * 100, 1)

    schemes = (await db.execute(
        select(AssessmentScheme).where(AssessmentScheme.course_id == course_id)
    )).scalars().all()
    total_bobot = round(sum(float(s.bobot_persen) for s in schemes), 2)

    return {
        "has_rps": rps is not None,
        "rps_status": rps.status if rps else None,
        "rps_tahun_akademik": rps.tahun_akademik if rps else None,
        "checklist_pct": checklist_pct,
        "checklist_fulfilled": checklist_fulfilled,
        "checklist_total": checklist_total,
        "unmet_mandatory": unmet_components,
        "scheme_count": len(schemes),
        "total_bobot_asesmen": total_bobot,
        "bobot_lengkap": abs(total_bobot - 100.0) < 0.01,
    }


async def _build_cpl_cpmk_analysis(course_id: int, db: AsyncSession) -> dict:
    """UC-19d: Analisis CPL-CPMK — jumlah CPMK, CPL terpetakan, dan cakupan pemetaan."""
    cpmks = (await db.execute(
        select(Cpmk).where(Cpmk.course_id == course_id, Cpmk.is_active == True)
    )).scalars().all()
    cpmk_ids = [c.id for c in cpmks]

    cpl_ids = (await db.execute(
        select(CourseCplMapping.cpl_id).where(CourseCplMapping.course_id == course_id)
    )).scalars().all()

    mapped_cpmk_ids: set[int] = set()
    if cpmk_ids:
        rows = (await db.execute(
            select(CpmkCplMapping.cpmk_id).where(CpmkCplMapping.cpmk_id.in_(cpmk_ids))
        )).scalars().all()
        mapped_cpmk_ids = set(rows)

    unmapped = [c.kode_cpmk for c in cpmks if c.id not in mapped_cpmk_ids]
    total_bobot_cpmk = round(sum(float(c.bobot_persen) for c in cpmks), 2)
    coverage = round(len(mapped_cpmk_ids) / len(cpmks) * 100, 1) if cpmks else None

    return {
        "total_cpmk": len(cpmks),
        "total_cpl_terpetakan": len(cpl_ids),
        "cpmk_termapping": len(mapped_cpmk_ids),
        "cpmk_belum_termapping": unmapped,
        "coverage_pct": coverage,
        "total_bobot_cpmk": total_bobot_cpmk,
        "bobot_cpmk_lengkap": abs(total_bobot_cpmk - 100.0) < 0.01,
    }


def _build_rps_suggestions(dimensions_data: list, rps_alignment: dict, cpl_cpmk: dict) -> list[str]:
    """UC-19f: Saran revisi RPS otomatis berdasarkan gap checklist, asesmen, dan skor CIPP rendah."""
    saran: list[str] = []

    if not rps_alignment["has_rps"]:
        saran.append("Belum ada dokumen RPS untuk mata kuliah ini. Susun RPS sesuai standar BAN-PT sebelum perkuliahan berikutnya.")
    else:
        if rps_alignment["checklist_pct"] is not None and rps_alignment["checklist_pct"] < 100:
            unmet = rps_alignment["unmet_mandatory"]
            if unmet:
                saran.append(f"Lengkapi komponen RPS wajib yang belum terpenuhi: {', '.join(unmet[:5])}.")
        if not rps_alignment["bobot_lengkap"]:
            saran.append(f"Total bobot skema asesmen = {rps_alignment['total_bobot_asesmen']}%, idealnya 100%. Tinjau ulang distribusi bobot penilaian.")
        if rps_alignment["scheme_count"] == 0:
            saran.append("Belum ada skema asesmen terdaftar. Definisikan komponen penilaian (UTS/UAS/Tugas) beserta bobotnya.")

    if cpl_cpmk["cpmk_belum_termapping"]:
        saran.append(f"CPMK belum dipetakan ke CPL: {', '.join(cpl_cpmk['cpmk_belum_termapping'][:5])}. Lengkapi pemetaan untuk menjaga keterlacakan capaian.")
    if not cpl_cpmk["bobot_cpmk_lengkap"] and cpl_cpmk["total_cpmk"] > 0:
        saran.append(f"Total bobot CPMK = {cpl_cpmk['total_bobot_cpmk']}%, idealnya 100%. Seimbangkan bobot antar CPMK.")

    # Saran berdasarkan dimensi CIPP terlemah
    scored = [d for d in dimensions_data if d["avg_dosen"] is not None or d["avg_mahasiswa"] is not None]
    if scored:
        def dim_avg(d):
            vals = [v for v in [d["avg_dosen"], d["avg_mahasiswa"]] if v is not None]
            return sum(vals) / len(vals) if vals else 5.0
        weakest = min(scored, key=dim_avg)
        if dim_avg(weakest) < 3.5:
            label = {"B": "Konteks", "C": "Input", "D": "Proses", "E": "Produk"}.get(weakest["kode"], weakest["kode"])
            saran.append(f"Dimensi {label} ({weakest['nama']}) memperoleh skor terendah ({round(dim_avg(weakest), 2)}). Prioritaskan revisi RPS pada aspek terkait dimensi ini.")

    if not saran:
        saran.append("Tidak ada isu kritis terdeteksi. RPS, asesmen, dan pemetaan CPL-CPMK sudah lengkap dan skor CIPP memadai.")
    return saran


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


@router.get("/template-data")
async def template_report_data(
    course_id: int,
    periode_start: date,
    periode_end: date,
    role: str = "semua",  # mahasiswa | dosen | semua
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Data laporan format Template CIPP (A. Identitas, B. 15 subdimensi, C. indikator detail,
    D. interpretasi) untuk satu MK + periode + peran. Skor Likert dikonversi ke persen."""
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    program = await db.get(Program, course.program_id)
    university = await db.get(University, program.university_id) if program else None
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        if not program or program.university_id != current_user.university_id:
            raise HTTPException(403, "Akses ditolak")

    # Respons selesai dalam periode, difilter peran
    q = select(Response).where(
        Response.course_id == course_id,
        Response.is_complete == True,
        Response.submitted_at >= datetime.combine(periode_start, datetime.min.time()),
        Response.submitted_at <= datetime.combine(periode_end, datetime.max.time()),
    )
    if role in ("mahasiswa", "dosen"):
        q = q.where(Response.role == role)
    responses = (await db.execute(q)).scalars().all()
    resp_ids = [r.id for r in responses]

    # Index skor item
    score_index: dict = {}
    if resp_ids:
        for item_id, skor in (await db.execute(
            select(ResponseItem.item_id, ResponseItem.skor).where(ResponseItem.response_id.in_(resp_ids))
        )).all():
            score_index.setdefault(item_id, []).append(skor)

    def pct(item_ids):
        vals = [s for iid in item_ids for s in score_index.get(iid, [])]
        return (round(sum(vals) / len(vals) / 5 * 100, 1), len(vals)) if vals else (None, 0)

    # Dimensi → subdimensi → item
    dims = (await db.execute(select(CippDimension).order_by(CippDimension.urutan))).scalars().all()
    subdimensi, indikator = [], []
    for dim in dims:
        subs = (await db.execute(
            select(CippSubDimension).where(CippSubDimension.dimension_id == dim.id).order_by(CippSubDimension.urutan)
        )).scalars().all()
        for sd in subs:
            items = (await db.execute(
                select(InstrumentItem).where(
                    InstrumentItem.sub_dimension_id == sd.id, InstrumentItem.is_active == True
                ).order_by(InstrumentItem.nomor_urut)
            )).scalars().all()
            sd_pct, sd_n = pct([it.id for it in items])
            subdimensi.append({
                "kode": sd.kode, "dimensi": dim.nama_id, "dimensi_kode": dim.kode,
                "nama": sd.nama_id, "persen": sd_pct, "n": sd_n,
            })
            for it in items:
                it_pct, it_n = pct([it.id])
                indikator.append({
                    "kode": it.kode, "subdim_kode": sd.kode,
                    "indikator": it.indikator or it.text_id_dosen[:50],
                    "persen": it_pct, "n": it_n,
                })

    # D. Interpretasi otomatis
    scored = [s for s in subdimensi if s["persen"] is not None]
    kekuatan = [f"{s['nama']} ({s['persen']}%)" for s in sorted(scored, key=lambda x: -x["persen"])[:3]]
    kelemahan = [f"{s['nama']} ({s['persen']}%)" for s in sorted(scored, key=lambda x: x["persen"])[:3]]
    rekomendasi = [
        f"Tingkatkan aspek '{s['nama']}' yang masih {s['persen']}% melalui evaluasi dan perbaikan terarah."
        for s in sorted(scored, key=lambda x: x["persen"])[:3] if s["persen"] < 75
    ] or ["Pertahankan kualitas seluruh aspek yang sudah baik dan lakukan monitoring berkala."]

    role_label = {"mahasiswa": "Mahasiswa", "dosen": "Dosen", "semua": "Mahasiswa & Dosen"}.get(role, "Semua")
    return {
        "identitas": {
            "universitas": university.nama if university else "-",
            "program_studi": program.nama if program else "-",
            "mata_kuliah": f"{course.kode_mk} — {course.nama_id}",
            "semester": course.semester,
            "jumlah_sks": course.sks,
            "periode": f"{periode_start.isoformat()} s/d {periode_end.isoformat()}",
            "peran_responden": role_label,
            "jumlah_responden": len(responses),
        },
        "subdimensi": subdimensi,
        "indikator": indikator,
        "interpretasi": {"kekuatan": kekuatan, "kelemahan": kelemahan, "rekomendasi": rekomendasi},
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
