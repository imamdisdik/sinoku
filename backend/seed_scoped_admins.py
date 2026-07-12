"""
Seed akun admin berjenjang untuk SETIAP universitas/fakultas/prodi yang ada:
  - 1x admin_universitas per Universitas
  - 1x admin_fakultas    per Fakultas
  - 1x admin_prodi       per Program Studi

Idempotent: melewati akun yang email-nya sudah ada. Aman dijalankan berulang.

Jalankan di VPS:
  docker compose exec -T backend python seed_scoped_admins.py

Ubah DEFAULT_PASSWORD di bawah bila ingin kata sandi awal berbeda.
"""
import asyncio
import re
import sys
sys.path.insert(0, '/app')

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.auth import User
from app.models.academic import University, Faculty, Program
from app.core.security import hash_password

DEFAULT_PASSWORD = "sinoku123"
EMAIL_DOMAIN = "sinoku.id"


def slug(text: str) -> str:
    """nama_singkat → potongan email yang aman (huruf/angka saja, lowercase)."""
    s = re.sub(r"[^a-z0-9]+", "", (text or "").lower())
    return s or "x"


async def main():
    created = []
    skipped = 0

    async with AsyncSessionLocal() as db:
        # Kumpulkan email yang sudah ada agar tidak bentrok
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
                email=email,
                full_name=full_name,
                hashed_password=hash_password(DEFAULT_PASSWORD),
                role=role,
                university_id=university_id,
                faculty_id=faculty_id,
                program_id=program_id,
                is_active=True,
            ))
            existing_emails.add(email)
            created.append((email, role, full_name))

        # ── Universitas ─────────────────────────────────────────────
        univs = (await db.execute(select(University))).scalars().all()
        for u in univs:
            make(
                f"admin.univ.{slug(u.nama_singkat)}.{u.id}@{EMAIL_DOMAIN}",
                f"Admin Universitas — {u.nama}",
                "admin_universitas",
                university_id=u.id,
            )

        # ── Fakultas ────────────────────────────────────────────────
        faks = (await db.execute(select(Faculty))).scalars().all()
        for f in faks:
            make(
                f"admin.fak.{slug(f.nama_singkat)}.{f.id}@{EMAIL_DOMAIN}",
                f"Admin Fakultas — {f.nama}",
                "admin_fakultas",
                university_id=f.university_id,
                faculty_id=f.id,
            )

        # ── Program Studi ───────────────────────────────────────────
        progs = (await db.execute(select(Program))).scalars().all()
        for p in progs:
            make(
                f"admin.prodi.{slug(p.nama_singkat)}.{p.id}@{EMAIL_DOMAIN}",
                f"Admin Prodi — {p.nama}",
                "admin_prodi",
                university_id=p.university_id,
                faculty_id=p.faculty_id,
                program_id=p.id,
            )

        await db.commit()

    # ── Ringkasan ───────────────────────────────────────────────────
    print("\n=== AKUN DIBUAT ===")
    print(f"Kata sandi (semua): {DEFAULT_PASSWORD}\n")
    for email, role, name in created:
        print(f"  [{role:18}] {email}   →  {name}")
    print(f"\nTotal dibuat: {len(created)} | dilewati (sudah ada): {skipped}")
    print("PENTING: minta tiap pemilik akun mengganti kata sandinya setelah login.")


if __name__ == "__main__":
    asyncio.run(main())
