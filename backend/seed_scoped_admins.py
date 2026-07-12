"""
Seed akun admin berjenjang untuk SETIAP universitas/fakultas/prodi yang ada:
  - 1x admin_universitas per Universitas
  - 1x admin_fakultas    per Fakultas
  - 1x admin_prodi       per Program Studi

Idempotent: melewati akun yang email-nya sudah ada. Aman dijalankan berulang.
Setelah seed, menulis LAPORAN LENGKAP siap-cetak → 'akun_sinoku_report.html'.

Jalankan di VPS:
  docker compose exec -T backend python seed_scoped_admins.py
Lalu ambil laporannya keluar container & cetak jadi PDF:
  docker compose cp backend:/app/akun_sinoku_report.html ./akun_sinoku_report.html
  (buka file itu di browser → Ctrl+P → Save as PDF)

Ubah DEFAULT_PASSWORD di bawah bila ingin kata sandi awal berbeda.
"""
import asyncio
import html
import re
import sys
from datetime import datetime
sys.path.insert(0, '/app')

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.auth import User
from app.models.academic import University, Faculty, Program
from app.core.security import hash_password

DEFAULT_PASSWORD = "sinoku123"
EMAIL_DOMAIN = "sinoku.id"
REPORT_FILE = "/app/akun_sinoku_report.html"

ROLE_LABEL = {
    "admin_universitas": "Admin Universitas",
    "admin_fakultas": "Admin Fakultas",
    "admin_prodi": "Admin Prodi",
}
ROLE_ORDER = {"admin_universitas": 0, "admin_fakultas": 1, "admin_prodi": 2}


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "", (text or "").lower())
    return s or "x"


async def main():
    created_emails = set()
    skipped = 0

    async with AsyncSessionLocal() as db:
        univs = (await db.execute(select(University))).scalars().all()
        faks = (await db.execute(select(Faculty))).scalars().all()
        progs = (await db.execute(select(Program))).scalars().all()

        univ_by_id = {u.id: u for u in univs}
        fak_by_id = {f.id: f for f in faks}
        prog_by_id = {p.id: p for p in progs}

        existing_emails = set(
            e.lower() for e in (await db.execute(select(User.email))).scalars().all()
        )

        def make(email, full_name, role, university_id=None, faculty_id=None, program_id=None):
            nonlocal skipped
            email = email.lower()
            if email in existing_emails:
                skipped += 1
                return
            db.add(User(
                email=email, full_name=full_name,
                hashed_password=hash_password(DEFAULT_PASSWORD), role=role,
                university_id=university_id, faculty_id=faculty_id, program_id=program_id,
                is_active=True,
            ))
            existing_emails.add(email)
            created_emails.add(email)

        for u in univs:
            make(f"admin.univ.{slug(u.nama_singkat)}.{u.id}@{EMAIL_DOMAIN}",
                 f"Admin Universitas — {u.nama}", "admin_universitas", university_id=u.id)
        for f in faks:
            make(f"admin.fak.{slug(f.nama_singkat)}.{f.id}@{EMAIL_DOMAIN}",
                 f"Admin Fakultas — {f.nama}", "admin_fakultas",
                 university_id=f.university_id, faculty_id=f.id)
        for p in progs:
            make(f"admin.prodi.{slug(p.nama_singkat)}.{p.id}@{EMAIL_DOMAIN}",
                 f"Admin Prodi — {p.nama}", "admin_prodi",
                 university_id=p.university_id, faculty_id=p.faculty_id, program_id=p.id)

        await db.commit()

        # ── Ambil SEMUA akun admin berjenjang untuk laporan lengkap ──
        rows = (await db.execute(
            select(User).where(User.role.in_(list(ROLE_LABEL.keys())))
        )).scalars().all()

    def scope_text(u: User) -> str:
        if u.role == "admin_universitas":
            e = univ_by_id.get(u.university_id)
            return e.nama if e else "-"
        if u.role == "admin_fakultas":
            e = fak_by_id.get(u.faculty_id)
            unv = univ_by_id.get(u.university_id)
            return f"{e.nama if e else '-'} ({unv.nama_singkat if unv else '-'})"
        e = prog_by_id.get(u.program_id)
        unv = univ_by_id.get(u.university_id)
        return f"{e.nama if e else '-'} ({unv.nama_singkat if unv else '-'})"

    rows.sort(key=lambda u: (ROLE_ORDER.get(u.role, 9), scope_text(u).lower()))

    # ── Susun HTML laporan ──────────────────────────────────────────
    now = datetime.now().strftime("%d %B %Y %H:%M")
    body_rows = []
    for i, u in enumerate(rows, 1):
        pw = DEFAULT_PASSWORD if u.email.lower() in created_emails else "(tidak diubah)"
        body_rows.append(
            f"<tr><td class='c'>{i}</td>"
            f"<td>{html.escape(ROLE_LABEL.get(u.role, u.role))}</td>"
            f"<td>{html.escape(scope_text(u))}</td>"
            f"<td class='mono'>{html.escape(u.email)}</td>"
            f"<td class='mono'>{html.escape(pw)}</td></tr>"
        )

    n_uni = sum(1 for u in rows if u.role == "admin_universitas")
    n_fak = sum(1 for u in rows if u.role == "admin_fakultas")
    n_pro = sum(1 for u in rows if u.role == "admin_prodi")

    doc = f"""<!doctype html><html lang="id"><head><meta charset="utf-8">
<title>Laporan Akun SINOKU</title>
<style>
  body{{font-family:-apple-system,Segoe UI,Arial,sans-serif;color:#1a202c;margin:32px;}}
  h1{{color:#1a365d;margin:0 0 4px;font-size:22px;}}
  .sub{{color:#718096;font-size:13px;margin-bottom:18px;}}
  .note{{background:#fffaf0;border:1px solid #f6e05e;border-radius:8px;padding:10px 14px;font-size:12px;margin-bottom:18px;}}
  .sum{{display:flex;gap:24px;margin-bottom:18px;font-size:13px;}}
  .sum b{{color:#1a365d;font-size:18px;display:block;}}
  table{{width:100%;border-collapse:collapse;font-size:12px;}}
  th{{background:#1a365d;color:#fff;text-align:left;padding:8px 10px;}}
  td{{padding:7px 10px;border-bottom:1px solid #edf2f7;}}
  td.c{{text-align:center;color:#718096;}}
  .mono{{font-family:Consolas,monospace;}}
  tr:nth-child(even) td{{background:#f7fafc;}}
  @media print{{body{{margin:0;}} th{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}}}
</style></head><body>
<h1>Laporan Akun Admin — SINOKU</h1>
<div class="sub">Digenerate otomatis · {now}</div>
<div class="note"><b>Kata sandi awal semua akun (yang baru dibuat): {DEFAULT_PASSWORD}</b><br>
Segera minta tiap pemilik akun mengganti kata sandinya setelah login pertama.</div>
<div class="sum">
  <div><b>{n_uni}</b> Admin Universitas</div>
  <div><b>{n_fak}</b> Admin Fakultas</div>
  <div><b>{n_pro}</b> Admin Prodi</div>
  <div><b>{len(rows)}</b> Total</div>
</div>
<table>
  <thead><tr><th>No</th><th>Peran</th><th>Entitas</th><th>Email (login)</th><th>Kata Sandi</th></tr></thead>
  <tbody>{''.join(body_rows)}</tbody>
</table>
</body></html>"""

    with open(REPORT_FILE, "w", encoding="utf-8") as fp:
        fp.write(doc)

    print(f"\n=== SELESAI ===")
    print(f"Akun baru dibuat: {len(created_emails)} | dilewati (sudah ada): {skipped}")
    print(f"Total akun admin berjenjang: {len(rows)}")
    print(f"Laporan lengkap ditulis ke: {REPORT_FILE}")
    print("Ambil & cetak jadi PDF:")
    print("  docker compose cp backend:/app/akun_sinoku_report.html ./akun_sinoku_report.html")
    print("  (buka di browser → Ctrl+P → Save as PDF)")


if __name__ == "__main__":
    asyncio.run(main())
