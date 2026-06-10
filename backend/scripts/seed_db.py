"""Jalankan: python -m scripts.seed_db dari folder backend/"""
import asyncio
from app.database import AsyncSessionLocal
from app.services.seed import run_all_seeds


async def main():
    async with AsyncSessionLocal() as db:
        await run_all_seeds(db)
        await db.commit()
        print("Seed selesai!")


asyncio.run(main())
