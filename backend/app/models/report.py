from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date, timezone
import uuid
from app.database import Base


class DiagnosticReport(Base):
    __tablename__ = "diagnostic_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    university_id: Mapped[int] = mapped_column(Integer, ForeignKey("universities.id", ondelete="RESTRICT"), nullable=False)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("programs.id", ondelete="RESTRICT"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    periode_start: Mapped[date] = mapped_column(Date, nullable=False)
    periode_end: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
