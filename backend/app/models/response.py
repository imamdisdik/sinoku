from sqlalchemy import String, Boolean, Integer, SmallInteger, BigInteger, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.database import Base


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="RESTRICT"), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    instrument_version: Mapped[str] = mapped_column(String(20), default="1.0")
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    bahasa: Mapped[str] = mapped_column(String(5), nullable=False)  # id | zh
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256 hash

    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="responses")
    course: Mapped["Course"] = relationship("Course", back_populates="responses")
    items: Mapped[list["ResponseItem"]] = relationship("ResponseItem", back_populates="response", cascade="all, delete-orphan")
    open_answers: Mapped[list["ResponseOpenAnswer"]] = relationship("ResponseOpenAnswer", back_populates="response", cascade="all, delete-orphan")
    anonymous_code: Mapped["AnonymousCode"] = relationship("AnonymousCode", back_populates="response", uselist=False)


class ResponseItem(Base):
    __tablename__ = "response_items"
    __table_args__ = (UniqueConstraint("response_id", "item_id", name="uq_response_item"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    response_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("responses.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("instrument_items.id", ondelete="RESTRICT"), nullable=False)
    skor: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    response: Mapped["Response"] = relationship("Response", back_populates="items")
    item: Mapped["InstrumentItem"] = relationship("InstrumentItem", back_populates="response_items")


class ResponseOpenAnswer(Base):
    __tablename__ = "response_open_answers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    response_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("responses.id", ondelete="CASCADE"), nullable=False)
    open_question_id: Mapped[int] = mapped_column(Integer, ForeignKey("open_questions.id", ondelete="RESTRICT"), nullable=False)
    jawaban_teks: Mapped[str] = mapped_column(Text, nullable=False)

    response: Mapped["Response"] = relationship("Response", back_populates="open_answers")
    question: Mapped["OpenQuestion"] = relationship("OpenQuestion", back_populates="open_answers")


class AnonymousCode(Base):
    __tablename__ = "anonymous_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    response_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("responses.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_accessed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    response: Mapped["Response"] = relationship("Response", back_populates="anonymous_code")
