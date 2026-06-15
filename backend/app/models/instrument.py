from sqlalchemy import String, Boolean, Integer, BigInteger, SmallInteger, ForeignKey, Text, DateTime, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime, timezone
import uuid
from app.database import Base


class CippDimension(Base):
    __tablename__ = "cipp_dimensions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kode: Mapped[str] = mapped_column(CHAR(1), unique=True, nullable=False)  # B | C | D | E
    nama_dimensi: Mapped[str] = mapped_column(String(50), nullable=False)
    nama_id: Mapped[str] = mapped_column(String(100), nullable=False)
    nama_zh: Mapped[str] = mapped_column(String(100), nullable=False)
    deskripsi_id: Mapped[str] = mapped_column(Text, nullable=False)
    urutan: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    warna_hex: Mapped[str] = mapped_column(String(7), nullable=False)

    sub_dimensions: Mapped[list["CippSubDimension"]] = relationship("CippSubDimension", back_populates="dimension", order_by="CippSubDimension.urutan")


class CippSubDimension(Base):
    __tablename__ = "cipp_sub_dimensions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dimension_id: Mapped[int] = mapped_column(Integer, ForeignKey("cipp_dimensions.id", ondelete="CASCADE"), nullable=False)
    kode: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # B.1 | B.2 | ...
    nama_id: Mapped[str] = mapped_column(String(200), nullable=False)
    nama_zh: Mapped[str] = mapped_column(String(200), nullable=False)
    urutan: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    dimension: Mapped["CippDimension"] = relationship("CippDimension", back_populates="sub_dimensions")
    items: Mapped[list["InstrumentItem"]] = relationship("InstrumentItem", back_populates="sub_dimension", order_by="InstrumentItem.nomor_urut")


class InstrumentItem(Base):
    __tablename__ = "instrument_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sub_dimension_id: Mapped[int] = mapped_column(Integer, ForeignKey("cipp_sub_dimensions.id", ondelete="CASCADE"), nullable=False)
    kode: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # B1, B2, ... E17
    nomor_urut: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    text_id_dosen: Mapped[str] = mapped_column(Text, nullable=False)
    text_id_mahasiswa: Mapped[str] = mapped_column(Text, nullable=False)
    text_zh_dosen: Mapped[str] = mapped_column(Text, nullable=False)
    text_zh_mahasiswa: Mapped[str] = mapped_column(Text, nullable=False)
    indikator: Mapped[str | None] = mapped_column(String(200), nullable=True)
    kompetensi_dosen: Mapped[str | None] = mapped_column(String(200), nullable=True)
    kompetensi_mahasiswa: Mapped[str | None] = mapped_column(String(200), nullable=True)
    answer_type: Mapped[str] = mapped_column(String(20), default="likert")
    scale_min: Mapped[int] = mapped_column(SmallInteger, default=1)
    scale_max: Mapped[int] = mapped_column(SmallInteger, default=5)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sub_dimension: Mapped["CippSubDimension"] = relationship("CippSubDimension", back_populates="items")
    response_items: Mapped[list["ResponseItem"]] = relationship("ResponseItem", back_populates="item")


class InstrumentItemHistory(Base):
    """F-09.4: snapshot item instrumen sebelum tiap perubahan (audit trail)."""
    __tablename__ = "instrument_item_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("instrument_items.id", ondelete="SET NULL"), nullable=True)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # update | delete
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OpenQuestion(Base):
    __tablename__ = "open_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kode: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    pertanyaan_id: Mapped[str] = mapped_column(Text, nullable=False)
    pertanyaan_zh: Mapped[str] = mapped_column(Text, nullable=False)
    tujuan: Mapped[str] = mapped_column(String(200), nullable=False)
    target_role: Mapped[str] = mapped_column(String(20), nullable=False)  # dosen | mahasiswa | semua
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    urutan: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    open_answers: Mapped[list["ResponseOpenAnswer"]] = relationship("ResponseOpenAnswer", back_populates="question")
