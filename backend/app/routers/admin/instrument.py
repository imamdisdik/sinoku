from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
import csv
import io
from app.database import get_db
from app.dependencies import require_admin, require_superadmin_or_admin, get_current_user
from app.models.auth import User
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem, OpenQuestion, InstrumentItemHistory


def _snapshot_item(item: InstrumentItem) -> dict:
    """Ambil snapshot field-field item untuk riwayat (F-09.4)."""
    return {
        "kode": item.kode, "sub_dimension_id": item.sub_dimension_id, "nomor_urut": item.nomor_urut,
        "text_id_dosen": item.text_id_dosen, "text_id_mahasiswa": item.text_id_mahasiswa,
        "text_zh_dosen": item.text_zh_dosen, "text_zh_mahasiswa": item.text_zh_mahasiswa,
        "indikator": item.indikator, "kompetensi_dosen": item.kompetensi_dosen,
        "kompetensi_mahasiswa": item.kompetensi_mahasiswa, "answer_type": item.answer_type,
        "scale_min": item.scale_min, "scale_max": item.scale_max,
        "is_required": item.is_required, "is_active": item.is_active,
    }

router = APIRouter(prefix="/admin/instruments", tags=["admin-instruments"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class DimensiOut(BaseModel):
    id: int
    kode: str
    nama_dimensi: str
    nama_id: str
    nama_zh: str
    deskripsi_id: str
    urutan: int
    warna_hex: str
    model_config = {"from_attributes": True}


class SubDimensiOut(BaseModel):
    id: int
    dimension_id: int
    kode: str
    nama_id: str
    nama_zh: str
    urutan: int
    item_count: int = 0
    model_config = {"from_attributes": True}


class ItemOut(BaseModel):
    id: int
    sub_dimension_id: int
    kode: str
    nomor_urut: int
    text_id_dosen: str
    text_id_mahasiswa: str
    text_zh_dosen: str
    text_zh_mahasiswa: str
    indikator: Optional[str] = None
    answer_type: str
    scale_min: int
    scale_max: int
    is_required: bool
    is_active: bool
    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    sub_dimension_id: int
    kode: str
    nomor_urut: int
    text_id_dosen: str
    text_id_mahasiswa: str
    text_zh_dosen: str = ""
    text_zh_mahasiswa: str = ""
    indikator: Optional[str] = None
    answer_type: str = "likert"
    scale_min: int = 1
    scale_max: int = 5
    is_required: bool = True


class ItemUpdate(BaseModel):
    nomor_urut: Optional[int] = None
    text_id_dosen: Optional[str] = None
    text_id_mahasiswa: Optional[str] = None
    text_zh_dosen: Optional[str] = None
    text_zh_mahasiswa: Optional[str] = None
    indikator: Optional[str] = None
    answer_type: Optional[str] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    is_required: Optional[bool] = None


class OpenQOut(BaseModel):
    id: int
    kode: str
    pertanyaan_id: str
    pertanyaan_zh: str
    tujuan: str
    target_role: str
    is_required: bool
    urutan: int
    is_active: bool
    model_config = {"from_attributes": True}


class OpenQCreate(BaseModel):
    kode: str
    pertanyaan_id: str
    pertanyaan_zh: str = ""
    tujuan: str
    target_role: str = "semua"
    is_required: bool = False
    urutan: int


class OpenQUpdate(BaseModel):
    pertanyaan_id: Optional[str] = None
    pertanyaan_zh: Optional[str] = None
    tujuan: Optional[str] = None
    target_role: Optional[str] = None
    is_required: Optional[bool] = None
    urutan: Optional[int] = None


# ── Dimensi & Sub-Dimensi (read-only untuk admin biasa) ───────────────────────

@router.get("/dimensions")
async def list_dimensions(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    # Satu query: semua sub-dimensi beserta count item AKTIF-nya
    # (kondisi is_active diletakkan di ON clause agar sub-dimensi tanpa item aktif tetap muncul dengan count 0)
    subdim_counts = dict((await db.execute(
        select(CippSubDimension.id, func.count(InstrumentItem.id).label("cnt"))
        .outerjoin(
            InstrumentItem,
            (InstrumentItem.sub_dimension_id == CippSubDimension.id)
            & (InstrumentItem.is_active == True),
        )
        .group_by(CippSubDimension.id)
    )).all())

    subdims_all = (await db.execute(
        select(CippSubDimension).order_by(CippSubDimension.dimension_id, CippSubDimension.urutan)
    )).scalars().all()

    dims = (await db.execute(
        select(CippDimension).order_by(CippDimension.urutan)
    )).scalars().all()

    # Kelompokkan sub-dimensi per dimensi di Python
    from collections import defaultdict
    sd_by_dim: dict[int, list] = defaultdict(list)
    for sd in subdims_all:
        sd_by_dim[sd.dimension_id].append(
            {**SubDimensiOut.model_validate(sd).model_dump(), "item_count": subdim_counts.get(sd.id, 0)}
        )

    result = [
        {**DimensiOut.model_validate(dim).model_dump(), "sub_dimensions": sd_by_dim[dim.id]}
        for dim in dims
    ]
    return {"data": result}


@router.get("/dimensions/{dim_id}/items")
async def list_items(
    dim_id: int,
    sub_dimension_id: Optional[int] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    dim = await db.get(CippDimension, dim_id)
    if not dim:
        raise HTTPException(status_code=404, detail="Dimensi tidak ditemukan")

    subdim_ids = (await db.execute(
        select(CippSubDimension.id).where(CippSubDimension.dimension_id == dim_id)
    )).scalars().all()

    q = select(InstrumentItem).where(InstrumentItem.sub_dimension_id.in_(subdim_ids))
    if sub_dimension_id:
        q = q.where(InstrumentItem.sub_dimension_id == sub_dimension_id)
    if not include_inactive:
        q = q.where(InstrumentItem.is_active == True)
    q = q.order_by(InstrumentItem.sub_dimension_id, InstrumentItem.nomor_urut)

    items = (await db.execute(q)).scalars().all()
    return {"data": [ItemOut.model_validate(i) for i in items]}


# ── CRUD Item ─────────────────────────────────────────────────────────────────

@router.post("/items", status_code=201)
async def create_item(
    body: ItemCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_superadmin_or_admin),
):
    existing = (await db.execute(
        select(InstrumentItem).where(InstrumentItem.kode == body.kode)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"Kode item '{body.kode}' sudah digunakan")

    item = InstrumentItem(**body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ItemOut.model_validate(item)


@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    body: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    item = await db.get(InstrumentItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    # F-09.4: simpan snapshot kondisi SEBELUM diubah
    db.add(InstrumentItemHistory(
        item_id=item.id, snapshot=_snapshot_item(item),
        action="update", changed_by=current_user.id,
    ))
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(item, field, val)
    await db.commit()
    await db.refresh(item)
    return ItemOut.model_validate(item)


@router.get("/items/{item_id}/history")
async def item_history(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """F-09.4: riwayat perubahan satu item (snapshot sebelum tiap edit)."""
    rows = (await db.execute(
        select(InstrumentItemHistory)
        .where(InstrumentItemHistory.item_id == item_id)
        .order_by(InstrumentItemHistory.changed_at.desc())
    )).scalars().all()
    return {"data": [
        {"id": r.id, "action": r.action, "changed_at": r.changed_at.isoformat(), "snapshot": r.snapshot}
        for r in rows
    ]}


@router.patch("/items/{item_id}/toggle")
async def toggle_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_superadmin_or_admin),
):
    item = await db.get(InstrumentItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    item.is_active = not item.is_active
    await db.commit()
    return {"id": item.id, "kode": item.kode, "is_active": item.is_active}


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin_or_admin),
):
    item = await db.get(InstrumentItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    # F-09.4: catat snapshot terakhir sebelum hapus (history ikut terhapus via CASCADE,
    # namun snapshot disisipkan agar tercatat di transaksi yang sama bila diperlukan audit)
    db.add(InstrumentItemHistory(
        item_id=item.id, snapshot=_snapshot_item(item),
        action="delete", changed_by=current_user.id,
    ))
    await db.flush()
    await db.delete(item)
    await db.commit()


# ── Open Questions ────────────────────────────────────────────────────────────

@router.get("/open-questions")
async def list_open_questions(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    qs = (await db.execute(
        select(OpenQuestion).order_by(OpenQuestion.urutan)
    )).scalars().all()
    return {"data": [OpenQOut.model_validate(q) for q in qs]}


@router.post("/open-questions", status_code=201)
async def create_open_question(
    body: OpenQCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_superadmin_or_admin),
):
    oq = OpenQuestion(**body.model_dump())
    db.add(oq)
    await db.commit()
    await db.refresh(oq)
    return OpenQOut.model_validate(oq)


@router.put("/open-questions/{oq_id}")
async def update_open_question(
    oq_id: int,
    body: OpenQUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_superadmin_or_admin),
):
    oq = await db.get(OpenQuestion, oq_id)
    if not oq:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(oq, field, val)
    await db.commit()
    await db.refresh(oq)
    return OpenQOut.model_validate(oq)


@router.patch("/open-questions/{oq_id}/toggle")
async def toggle_open_question(
    oq_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_superadmin_or_admin),
):
    oq = await db.get(OpenQuestion, oq_id)
    if not oq:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan")
    oq.is_active = not oq.is_active
    await db.commit()
    return {"id": oq.id, "kode": oq.kode, "is_active": oq.is_active}


_ITEM_CSV_COLS = [
    "kode", "sub_dimension_id", "nomor_urut", "text_id_dosen", "text_id_mahasiswa",
    "text_zh_dosen", "text_zh_mahasiswa", "indikator", "answer_type",
    "scale_min", "scale_max", "is_required",
]


# ── Export Item via CSV / Template (F-09.6) ───────────────────────────────────

@router.get("/items/export")
async def export_items(
    template: bool = Query(False, description="True = unduh template kosong (header + 1 contoh)"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Export seluruh item instrumen ke CSV, atau template kosong bila template=true.

    Format kolom identik dengan endpoint import sehingga hasil export bisa
    langsung di-edit lalu di-import kembali.
    """
    buf = io.StringIO()
    buf.write("﻿")  # BOM agar Excel membaca UTF-8 (karakter Mandarin) dengan benar
    w = csv.DictWriter(buf, fieldnames=_ITEM_CSV_COLS)
    w.writeheader()

    if template:
        w.writerow({
            "kode": "CD1.1", "sub_dimension_id": 1, "nomor_urut": 1,
            "text_id_dosen": "Contoh pernyataan untuk dosen",
            "text_id_mahasiswa": "Contoh pernyataan untuk mahasiswa",
            "text_zh_dosen": "教师示例", "text_zh_mahasiswa": "学生示例",
            "indikator": "Contoh indikator", "answer_type": "likert",
            "scale_min": 1, "scale_max": 5, "is_required": "true",
        })
        filename = "template_item_instrumen.csv"
    else:
        items = (await db.execute(
            select(InstrumentItem)
            .where(InstrumentItem.is_active == True)
            .order_by(InstrumentItem.sub_dimension_id, InstrumentItem.nomor_urut)
        )).scalars().all()
        for it in items:
            w.writerow({
                "kode": it.kode, "sub_dimension_id": it.sub_dimension_id, "nomor_urut": it.nomor_urut,
                "text_id_dosen": it.text_id_dosen, "text_id_mahasiswa": it.text_id_mahasiswa,
                "text_zh_dosen": it.text_zh_dosen, "text_zh_mahasiswa": it.text_zh_mahasiswa,
                "indikator": it.indikator or "", "answer_type": it.answer_type,
                "scale_min": it.scale_min, "scale_max": it.scale_max,
                "is_required": str(it.is_required).lower(),
            })
        filename = "item_instrumen.csv"

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Import Item via CSV (UC-15) ───────────────────────────────────────────────

@router.post("/items/import")
async def import_items(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_superadmin_or_admin),
):
    """
    Import item instrumen dari file CSV.
    Kolom wajib: kode, sub_dimension_id, nomor_urut, text_id_dosen, text_id_mahasiswa
    Kolom opsional: text_zh_dosen, text_zh_mahasiswa, indikator, answer_type, scale_min, scale_max, is_required
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Hanya file CSV yang didukung (.csv)")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(400, "File harus berformat UTF-8")

    reader = csv.DictReader(io.StringIO(text))
    required_cols = {"kode", "sub_dimension_id", "nomor_urut", "text_id_dosen", "text_id_mahasiswa"}
    if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
        raise HTTPException(400, f"Kolom wajib tidak lengkap. Diperlukan: {', '.join(required_cols)}")

    imported, skipped, errors = 0, 0, []

    for i, row in enumerate(reader, start=2):
        kode = row.get("kode", "").strip()
        if not kode:
            errors.append(f"Baris {i}: kolom 'kode' kosong")
            skipped += 1
            continue

        # Cek duplikat kode
        existing = (await db.execute(
            select(InstrumentItem).where(InstrumentItem.kode == kode)
        )).scalar_one_or_none()
        if existing:
            errors.append(f"Baris {i}: kode '{kode}' sudah ada — dilewati")
            skipped += 1
            continue

        try:
            sub_dim_id = int(row["sub_dimension_id"])
            nomor_urut = int(row["nomor_urut"])
        except (ValueError, KeyError):
            errors.append(f"Baris {i}: sub_dimension_id / nomor_urut harus berupa angka")
            skipped += 1
            continue

        # Validasi sub_dimension ada
        sd = await db.get(CippSubDimension, sub_dim_id)
        if not sd:
            errors.append(f"Baris {i}: sub_dimension_id {sub_dim_id} tidak ditemukan")
            skipped += 1
            continue

        item = InstrumentItem(
            kode=kode,
            sub_dimension_id=sub_dim_id,
            nomor_urut=nomor_urut,
            text_id_dosen=row.get("text_id_dosen", "").strip(),
            text_id_mahasiswa=row.get("text_id_mahasiswa", "").strip(),
            text_zh_dosen=row.get("text_zh_dosen", "").strip(),
            text_zh_mahasiswa=row.get("text_zh_mahasiswa", "").strip(),
            indikator=row.get("indikator", "").strip() or None,
            answer_type=row.get("answer_type", "likert").strip() or "likert",
            scale_min=int(row.get("scale_min", 1) or 1),
            scale_max=int(row.get("scale_max", 5) or 5),
            is_required=str(row.get("is_required", "true")).lower() in ("true", "1", "ya", "yes"),
        )
        db.add(item)
        imported += 1

    await db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}
