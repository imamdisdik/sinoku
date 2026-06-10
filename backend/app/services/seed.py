"""Seed data awal: 4 dimensi CIPP, 15 sub-dimensi, 59 item, 8 pertanyaan terbuka."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem, OpenQuestion


DIMENSIONS = [
    {"kode": "B", "nama_dimensi": "Context",  "nama_id": "Konteks",  "nama_zh": "背景", "urutan": 1, "warna_hex": "#3182CE",
     "deskripsi_id": "Evaluasi relevansi dan kebutuhan program MK Budaya Tiongkok"},
    {"kode": "C", "nama_dimensi": "Input",    "nama_id": "Masukan",  "nama_zh": "投入", "urutan": 2, "warna_hex": "#38A169",
     "deskripsi_id": "Evaluasi kualitas sumber daya, kurikulum, dan fasilitas pendukung"},
    {"kode": "D", "nama_dimensi": "Process",  "nama_id": "Proses",   "nama_zh": "过程", "urutan": 3, "warna_hex": "#D69E2E",
     "deskripsi_id": "Evaluasi pelaksanaan pembelajaran dan interaksi dalam kelas"},
    {"kode": "E", "nama_dimensi": "Product",  "nama_id": "Produk",   "nama_zh": "成果", "urutan": 4, "warna_hex": "#E53E3E",
     "deskripsi_id": "Evaluasi hasil belajar, capaian kompetensi, dan dampak program"},
]

SUB_DIMENSIONS = [
    # Context
    {"kode": "B.1", "dim_kode": "B", "nama_id": "Relevansi Kurikulum",           "nama_zh": "课程相关性",   "urutan": 1},
    {"kode": "B.2", "dim_kode": "B", "nama_id": "Kebutuhan Pemangku Kepentingan", "nama_zh": "利益相关者需求", "urutan": 2},
    {"kode": "B.3", "dim_kode": "B", "nama_id": "Landasan Kebijakan",            "nama_zh": "政策基础",     "urutan": 3},
    # Input
    {"kode": "C.1", "dim_kode": "C", "nama_id": "Kompetensi Dosen",              "nama_zh": "教师能力",     "urutan": 1},
    {"kode": "C.2", "dim_kode": "C", "nama_id": "Kualitas Bahan Ajar",           "nama_zh": "教学材料质量",  "urutan": 2},
    {"kode": "C.3", "dim_kode": "C", "nama_id": "Fasilitas & Teknologi",         "nama_zh": "设施与技术",   "urutan": 3},
    {"kode": "C.4", "dim_kode": "C", "nama_id": "Desain Kurikulum & RPS",        "nama_zh": "课程设计",     "urutan": 4},
    # Process
    {"kode": "D.1", "dim_kode": "D", "nama_id": "Strategi Pembelajaran",         "nama_zh": "教学策略",     "urutan": 1},
    {"kode": "D.2", "dim_kode": "D", "nama_id": "Interaksi Kelas",               "nama_zh": "课堂互动",     "urutan": 2},
    {"kode": "D.3", "dim_kode": "D", "nama_id": "Asesmen & Umpan Balik",         "nama_zh": "评估与反馈",   "urutan": 3},
    {"kode": "D.4", "dim_kode": "D", "nama_id": "Manajemen Kelas",               "nama_zh": "课堂管理",     "urutan": 4},
    # Product
    {"kode": "E.1", "dim_kode": "E", "nama_id": "Capaian Kompetensi",            "nama_zh": "能力达成",     "urutan": 1},
    {"kode": "E.2", "dim_kode": "E", "nama_id": "Sikap & Apresiasi Budaya",      "nama_zh": "文化态度与欣赏", "urutan": 2},
    {"kode": "E.3", "dim_kode": "E", "nama_id": "Dampak dan Reputasi",           "nama_zh": "影响力与声誉",  "urutan": 3},
    {"kode": "E.4", "dim_kode": "E", "nama_id": "Kepuasan Pembelajaran",         "nama_zh": "学习满意度",    "urutan": 4},
]

OPEN_QUESTIONS = [
    {"kode": "OQ1", "pertanyaan_id": "Apa kelebihan utama mata kuliah ini menurut Anda?",
     "pertanyaan_zh": "您认为这门课程的主要优点是什么？", "tujuan": "kelebihan", "target_role": "semua", "is_required": False, "urutan": 1},
    {"kode": "OQ2", "pertanyaan_id": "Apa yang perlu diperbaiki dari mata kuliah ini?",
     "pertanyaan_zh": "这门课程需要改进哪些方面？", "tujuan": "perbaikan", "target_role": "semua", "is_required": False, "urutan": 2},
    {"kode": "OQ3", "pertanyaan_id": "Metode pembelajaran mana yang paling efektif menurut Anda?",
     "pertanyaan_zh": "您认为哪种教学方法最有效？", "tujuan": "metode", "target_role": "semua", "is_required": False, "urutan": 3},
    {"kode": "OQ4", "pertanyaan_id": "Bagaimana relevansi materi dengan kebutuhan industri/karir?",
     "pertanyaan_zh": "课程内容与行业/职业需求的相关性如何？", "tujuan": "relevansi", "target_role": "semua", "is_required": False, "urutan": 4},
    {"kode": "OQ5", "pertanyaan_id": "Tantangan terbesar apa yang Anda hadapi saat mengajar mata kuliah ini?",
     "pertanyaan_zh": "您在教授这门课程时面临的最大挑战是什么？", "tujuan": "tantangan_dosen", "target_role": "dosen", "is_required": False, "urutan": 5},
    {"kode": "OQ6", "pertanyaan_id": "Sumber daya apa yang dibutuhkan untuk meningkatkan kualitas pengajaran?",
     "pertanyaan_zh": "提高教学质量需要哪些资源？", "tujuan": "kebutuhan_dosen", "target_role": "dosen", "is_required": False, "urutan": 6},
    {"kode": "OQ7", "pertanyaan_id": "Bagaimana mata kuliah ini memengaruhi minat Anda terhadap budaya Tiongkok?",
     "pertanyaan_zh": "这门课程如何影响了您对中国文化的兴趣？", "tujuan": "minat_mhs", "target_role": "mahasiswa", "is_required": False, "urutan": 7},
    {"kode": "OQ8", "pertanyaan_id": "Saran Anda untuk pengembangan mata kuliah ini ke depan?",
     "pertanyaan_zh": "您对未来课程发展的建议是什么？", "tujuan": "saran", "target_role": "semua", "is_required": False, "urutan": 8},
]


async def seed_dimensions(db: AsyncSession) -> dict:
    """Seed 4 dimensi CIPP. Return map kode -> id."""
    result = await db.execute(select(CippDimension))
    existing = {d.kode: d for d in result.scalars().all()}
    dim_map = {}
    for d in DIMENSIONS:
        if d["kode"] not in existing:
            dim = CippDimension(**{k: v for k, v in d.items()})
            db.add(dim)
            await db.flush()
            dim_map[d["kode"]] = dim.id
        else:
            dim_map[d["kode"]] = existing[d["kode"]].id
    return dim_map


async def seed_sub_dimensions(db: AsyncSession, dim_map: dict) -> dict:
    """Seed 15 sub-dimensi. Return map kode -> id."""
    result = await db.execute(select(CippSubDimension))
    existing = {sd.kode: sd for sd in result.scalars().all()}
    sd_map = {}
    for sd in SUB_DIMENSIONS:
        if sd["kode"] not in existing:
            obj = CippSubDimension(
                dimension_id=dim_map[sd["dim_kode"]],
                kode=sd["kode"], nama_id=sd["nama_id"], nama_zh=sd["nama_zh"], urutan=sd["urutan"],
            )
            db.add(obj)
            await db.flush()
            sd_map[sd["kode"]] = obj.id
        else:
            sd_map[sd["kode"]] = existing[sd["kode"]].id
    return sd_map


async def seed_open_questions(db: AsyncSession):
    result = await db.execute(select(OpenQuestion))
    existing_kodes = {q.kode for q in result.scalars().all()}
    for q in OPEN_QUESTIONS:
        if q["kode"] not in existing_kodes:
            db.add(OpenQuestion(**q))


async def run_all_seeds(db: AsyncSession):
    dim_map = await seed_dimensions(db)
    sd_map = await seed_sub_dimensions(db, dim_map)
    await seed_open_questions(db)
    await db.flush()
    print(f"[seed] {len(dim_map)} dimensi, {len(sd_map)} sub-dimensi, {len(OPEN_QUESTIONS)} open questions seeded.")
