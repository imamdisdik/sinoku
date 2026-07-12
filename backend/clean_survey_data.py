"""
Bersihkan DATA KUISIONER (respons uji coba) — TIDAK menyentuh struktur/akun.

Yang DIHAPUS (bila --delete):
  - responses (+ response_items, response_open_answers, anonymous_codes via CASCADE)
  - respondents (profil mahasiswa) (+ sub-tabelnya via CASCADE)
  - diagnostic_reports (laporan hasil dari respons uji coba)

Yang TIDAK disentuh: universitas, fakultas, prodi, mata kuliah, CPL/CPMK, RPS,
skema/rubrik/MBKM, instrumen, dan SEMUA akun pengguna.

PEMAKAIAN (di VPS):
  # 1) LIHAT DULU (default, tidak menghapus apa pun) — pastikan memang uji coba:
  docker compose exec -T backend python clean_survey_data.py

  # 2) Hapus SEMUA respons:
  docker compose exec -T backend python clean_survey_data.py --delete

  # (opsional) batasi ke tanggal submit tertentu, mis. kemarin:
  docker compose exec -T backend python clean_survey_data.py --date 2026-07-11
  docker compose exec -T backend python clean_survey_data.py --date 2026-07-11 --delete

  # (opsional) batasi ke peran tertentu: dosen SAJA atau mahasiswa SAJA
  docker compose exec -T backend python clean_survey_data.py --role dosen
  docker compose exec -T backend python clean_survey_data.py --role dosen --delete

SARAN: backup dulu sebelum menghapus:
  docker compose exec -T db pg_dump -U sinoku sinoku_db > backup_sebelum_hapus.sql
"""
import asyncio
import sys
from datetime import date
sys.path.insert(0, '/app')

from sqlalchemy import select, delete, func
from app.database import AsyncSessionLocal
from app.models.response import Response
from app.models.respondent import Respondent
from app.models.report import DiagnosticReport
from app.models.academic import Course, Program, University


def parse_args():
    do_delete = "--delete" in sys.argv
    only_date = None
    only_role = None
    if "--date" in sys.argv:
        i = sys.argv.index("--date")
        try:
            y, m, d = map(int, sys.argv[i + 1].split("-"))
            only_date = date(y, m, d)
        except Exception:
            print("Format --date salah. Pakai: --date YYYY-MM-DD")
            sys.exit(1)
    if "--role" in sys.argv:
        i = sys.argv.index("--role")
        val = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        if val not in ("dosen", "mahasiswa"):
            print("Nilai --role harus 'dosen' atau 'mahasiswa'.")
            sys.exit(1)
        only_role = val
    return do_delete, only_date, only_role


async def main():
    do_delete, only_date, only_role = parse_args()

    async with AsyncSessionLocal() as db:
        # Query respons + konteks untuk ditampilkan
        q = (
            select(Response, Course, University, Respondent)
            .join(Course, Response.course_id == Course.id)
            .join(Program, Course.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .outerjoin(Respondent, Response.respondent_id == Respondent.id)
        )
        if only_date:
            q = q.where(func.date(Response.submitted_at) == only_date)
        if only_role:
            q = q.where(Response.role == only_role)
        q = q.order_by(Response.submitted_at)
        rows = (await db.execute(q)).all()

        print("\n=== DATA KUISIONER (RESPONS) ===")
        if only_date:
            print(f"Filter tanggal submit: {only_date}")
        if not rows:
            print("Tidak ada respons yang cocok. Tidak ada yang dihapus.")
            return

        print(f"{'Tanggal':<12} {'Peran':<10} {'Universitas':<14} {'MK':<12} {'Responden'}")
        print("-" * 74)
        for resp, course, univ, respondent in rows:
            tgl = resp.submitted_at.strftime("%Y-%m-%d") if resp.submitted_at else "(draft)"
            nama = (respondent.full_name if respondent else "(dosen/akun)") or "(anonim)"
            print(f"{tgl:<12} {resp.role:<10} {(univ.nama_singkat or '')[:13]:<14} {(course.kode_mk or '')[:11]:<12} {nama}")

        n_resp = len(rows)
        response_ids = [r[0].id for r in rows]
        respondent_ids = [r[3].id for r in rows if r[3] is not None]

        # Laporan diagnostik terkait (opsional dibersihkan)
        rep_q = select(func.count()).select_from(DiagnosticReport)
        if only_date or only_role:
            # laporan tak difilter per tanggal/peran → TIDAK disentuh saat pakai filter
            n_rep = 0
        else:
            n_rep = (await db.execute(rep_q)).scalar()

        print("-" * 74)
        print(f"Total respons: {n_resp} | profil responden: {len(set(respondent_ids))} | "
              f"laporan diagnostik yang akan dihapus: {n_rep}")

        if not do_delete:
            print("\n[MODE LIHAT SAJA] Belum ada yang dihapus.")
            print("Kalau daftar di atas memang UJI COBA semua, jalankan lagi dengan menambahkan --delete")
            return

        # ── EKSEKUSI HAPUS ──────────────────────────────────────────
        # 1) Laporan diagnostik (hanya bila tanpa filter tanggal/peran)
        if not only_date and not only_role:
            await db.execute(delete(DiagnosticReport))
        # 2) Respons (cascade ke item/jawaban/kode anonim)
        await db.execute(delete(Response).where(Response.id.in_(response_ids)))
        # 3) Profil responden (cascade ke sub-tabel)
        if respondent_ids:
            await db.execute(delete(Respondent).where(Respondent.id.in_(respondent_ids)))
        await db.commit()

        print(f"\n=== SELESAI DIHAPUS ===")
        print(f"Respons: {n_resp} | Profil responden: {len(set(respondent_ids))} | Laporan: {n_rep}")
        print("Struktur (universitas/prodi/MK/instrumen) & akun TIDAK diubah.")


if __name__ == "__main__":
    asyncio.run(main())
