from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.database import Base


class RpsVersion(Base):
    __tablename__ = "rps_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    tahun_akademik: Mapped[str] = mapped_column(String(10), nullable=False)
    semester: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="draft")  # draft | aktif | arsip
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    checklist_responses: Mapped[list["RpsChecklistResponse"]] = relationship("RpsChecklistResponse", back_populates="rps_version", cascade="all, delete-orphan")


class RpsChecklistItem(Base):
    __tablename__ = "rps_checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kode: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    nama_komponen: Mapped[str] = mapped_column(String(200), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    urutan: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class RpsChecklistResponse(Base):
    __tablename__ = "rps_checklist_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rps_version_id: Mapped[int] = mapped_column(Integer, ForeignKey("rps_versions.id", ondelete="CASCADE"), nullable=False)
    checklist_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("rps_checklist_items.id", ondelete="RESTRICT"), nullable=False)
    is_fulfilled: Mapped[bool] = mapped_column(Boolean, default=False)
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rps_version: Mapped["RpsVersion"] = relationship("RpsVersion", back_populates="checklist_responses")
    checklist_item: Mapped["RpsChecklistItem"] = relationship("RpsChecklistItem")
