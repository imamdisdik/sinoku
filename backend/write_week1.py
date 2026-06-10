"""Tulis semua file implementasi Minggu 1 SINOKU backend."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"D:\Tesis SINOKA\sinoku\backend"

FILES = {}

# ── app/config.py ────────────────────────────────────────────────────────────
FILES["app/config.py"] = '''from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    CORS_ORIGINS: str = \'["http://localhost:5173"]\'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
'''

# ── app/database.py ───────────────────────────────────────────────────────────
FILES["app/database.py"] = '''from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
'''

# ── app/core/security.py ──────────────────────────────────────────────────────
FILES["app/core/security.py"] = '''from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
'''

# ── app/core/exceptions.py ────────────────────────────────────────────────────
FILES["app/core/exceptions.py"] = '''from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Terjadi kesalahan server"},
    )
'''

# ── app/core/middleware.py ────────────────────────────────────────────────────
FILES["app/core/middleware.py"] = '''import time
import logging
from fastapi import Request

logger = logging.getLogger("sinoku")


async def log_request_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration:.1f}ms)")
    return response
'''

# ── app/core/pagination.py ────────────────────────────────────────────────────
FILES["app/core/pagination.py"] = '''from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = 1
    limit: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PagedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int
'''

# ── app/models/auth.py ────────────────────────────────────────────────────────
FILES["app/models/auth.py"] = '''from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, INET
from datetime import datetime, timezone
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # superadmin | admin | dosen
    university_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("universities.id", ondelete="SET NULL"), nullable=True)
    program_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("programs.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="sessions")
'''

# ── app/models/academic.py ────────────────────────────────────────────────────
FILES["app/models/academic.py"] = '''from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.database import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(200), nullable=False)
    nama_singkat: Mapped[str] = mapped_column(String(20), nullable=False)
    jenis: Mapped[str] = mapped_column(String(50), nullable=False)  # negeri | swasta
    kota: Mapped[str] = mapped_column(String(100), nullable=False)
    provinsi: Mapped[str] = mapped_column(String(100), nullable=False)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    akreditasi: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tahun_berdiri: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    programs: Mapped[list["Program"]] = relationship("Program", back_populates="university")
    respondents: Mapped[list["Respondent"]] = relationship("Respondent", back_populates="university")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    nama: Mapped[str] = mapped_column(String(200), nullable=False)
    nama_singkat: Mapped[str] = mapped_column(String(20), nullable=False)
    jenjang: Mapped[str] = mapped_column(String(10), nullable=False)  # S1 | S2 | D3 | D4
    tahun_berdiri: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    akreditasi: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    university: Mapped["University"] = relationship("University", back_populates="programs")
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="program")
    cpls: Mapped[list["Cpl"]] = relationship("Cpl", back_populates="program")
    respondents: Mapped[list["Respondent"]] = relationship("Respondent", back_populates="program")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    kode_mk: Mapped[str] = mapped_column(String(20), nullable=False)
    nama_id: Mapped[str] = mapped_column(String(200), nullable=False)
    nama_zh: Mapped[str] = mapped_column(String(200), nullable=False)
    sks: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    semester: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status_mk: Mapped[str] = mapped_column(String(20), default="wajib")  # wajib | pilihan | mbkm
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    program: Mapped["Program"] = relationship("Program", back_populates="courses")
    cpmks: Mapped[list["Cpmk"]] = relationship("Cpmk", back_populates="course")
    responses: Mapped[list["Response"]] = relationship("Response", back_populates="course")


class Cpl(Base):
    __tablename__ = "cpls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    kode_cpl: Mapped[str] = mapped_column(String(20), nullable=False)
    deskripsi_id: Mapped[str] = mapped_column(Text, nullable=False)
    deskripsi_zh: Mapped[str] = mapped_column(Text, nullable=False)
    kategori: Mapped[str] = mapped_column(String(50), nullable=False)  # sikap | pengetahuan | keterampilan
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    program: Mapped["Program"] = relationship("Program", back_populates="cpls")


class Cpmk(Base):
    __tablename__ = "cpmks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    kode_cpmk: Mapped[str] = mapped_column(String(20), nullable=False)
    deskripsi_id: Mapped[str] = mapped_column(Text, nullable=False)
    deskripsi_zh: Mapped[str] = mapped_column(Text, nullable=False)
    bobot_persen: Mapped[float] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    course: Mapped["Course"] = relationship("Course", back_populates="cpmks")


class CourseCplMapping(Base):
    __tablename__ = "course_cpl_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    cpl_id: Mapped[int] = mapped_column(Integer, ForeignKey("cpls.id", ondelete="CASCADE"), nullable=False)


class CpmkCplMapping(Base):
    __tablename__ = "cpmk_cpl_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cpmk_id: Mapped[int] = mapped_column(Integer, ForeignKey("cpmks.id", ondelete="CASCADE"), nullable=False)
    cpl_id: Mapped[int] = mapped_column(Integer, ForeignKey("cpls.id", ondelete="CASCADE"), nullable=False)
'''

# ── app/models/instrument.py ──────────────────────────────────────────────────
FILES["app/models/instrument.py"] = '''from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
'''

# ── app/models/respondent.py ──────────────────────────────────────────────────
FILES["app/models/respondent.py"] = '''from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.database import Base


class Respondent(Base):
    __tablename__ = "respondents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # dosen | mahasiswa
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    university_id: Mapped[int] = mapped_column(Integer, ForeignKey("universities.id", ondelete="RESTRICT"), nullable=False)
    faculty: Mapped[str | None] = mapped_column(String(200), nullable=True)
    program_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("programs.id", ondelete="SET NULL"), nullable=True)
    # Atribut dosen
    academic_position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    teaching_duration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    education_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    china_experience_dosen: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hsk_level_dosen: Mapped[str | None] = mapped_column(String(10), nullable=True)
    avg_class_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Atribut mahasiswa
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    age: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    current_semester: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mandarin_study_duration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hsk_level_mahasiswa: Mapped[str | None] = mapped_column(String(10), nullable=True)
    china_stay_duration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    chinese_friends: Mapped[str | None] = mapped_column(String(50), nullable=True)
    has_taken_culture_course: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    culture_course_count: Mapped[str | None] = mapped_column(String(20), nullable=True)
    course_status_taken: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cultural_interaction_freq: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    university: Mapped["University"] = relationship("University", back_populates="respondents")
    program: Mapped["Program"] = relationship("Program", back_populates="respondents")
    responses: Mapped[list["Response"]] = relationship("Response", back_populates="respondent")
    course_taught: Mapped[list["RespondentCourseTaught"]] = relationship("RespondentCourseTaught", back_populates="respondent", cascade="all, delete-orphan")
    course_taken: Mapped[list["RespondentCourseTaken"]] = relationship("RespondentCourseTaken", back_populates="respondent", cascade="all, delete-orphan")
    motivations: Mapped[list["RespondentMotivation"]] = relationship("RespondentMotivation", back_populates="respondent", cascade="all, delete-orphan")
    career_goals: Mapped[list["RespondentCareerGoal"]] = relationship("RespondentCareerGoal", back_populates="respondent", cascade="all, delete-orphan")
    media_usage: Mapped[list["RespondentMediaUsage"]] = relationship("RespondentMediaUsage", back_populates="respondent", cascade="all, delete-orphan")
    activities: Mapped[list["RespondentActivity"]] = relationship("RespondentActivity", back_populates="respondent", cascade="all, delete-orphan")


class RespondentCourseTaught(Base):
    __tablename__ = "respondent_course_taught"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="CASCADE"))
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="course_taught")


class RespondentCourseTaken(Base):
    __tablename__ = "respondent_course_taken"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="CASCADE"))
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    semester_taken: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    final_grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="course_taken")


class RespondentMotivation(Base):
    __tablename__ = "respondent_motivations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="CASCADE"))
    motivasi: Mapped[str] = mapped_column(String(200), nullable=False)
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="motivations")


class RespondentCareerGoal(Base):
    __tablename__ = "respondent_career_goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="CASCADE"))
    bidang_karir: Mapped[str] = mapped_column(String(200), nullable=False)
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="career_goals")


class RespondentMediaUsage(Base):
    __tablename__ = "respondent_media_usage"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="CASCADE"))
    media: Mapped[str] = mapped_column(String(200), nullable=False)
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="media_usage")


class RespondentActivity(Base):
    __tablename__ = "respondent_activities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("respondents.id", ondelete="CASCADE"))
    aktivitas: Mapped[str] = mapped_column(String(200), nullable=False)
    respondent: Mapped["Respondent"] = relationship("Respondent", back_populates="activities")
'''

# ── app/models/response.py ────────────────────────────────────────────────────
FILES["app/models/response.py"] = '''from sqlalchemy import String, Boolean, Integer, SmallInteger, BigInteger, ForeignKey, Text, DateTime, UniqueConstraint
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
'''

# ── app/models/rps.py ─────────────────────────────────────────────────────────
FILES["app/models/rps.py"] = '''from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime
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
'''

# ── app/models/assessment.py ──────────────────────────────────────────────────
FILES["app/models/assessment.py"] = '''from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AssessmentScheme(Base):
    __tablename__ = "assessment_schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    rps_version_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("rps_versions.id", ondelete="SET NULL"), nullable=True)
    nama_komponen: Mapped[str] = mapped_column(String(200), nullable=False)
    tipe: Mapped[str] = mapped_column(String(50), nullable=False)
    bobot_persen: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)

    rubrics: Mapped[list["AssessmentRubric"]] = relationship("AssessmentRubric", back_populates="scheme", cascade="all, delete-orphan")


class AssessmentRubric(Base):
    __tablename__ = "assessment_rubrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey("assessment_schemes.id", ondelete="CASCADE"), nullable=False)
    cpmk_id: Mapped[int] = mapped_column(Integer, ForeignKey("cpmks.id", ondelete="CASCADE"), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    skor_min: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    skor_max: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    deskriptor: Mapped[str] = mapped_column(Text, nullable=False)

    scheme: Mapped["AssessmentScheme"] = relationship("AssessmentScheme", back_populates="rubrics")


class MbkmIntegration(Base):
    __tablename__ = "mbkm_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    jenis_program: Mapped[str] = mapped_column(String(100), nullable=False)
    nama_mitra: Mapped[str] = mapped_column(String(200), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    sks_diakui: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    tahun_akademik: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
'''

# ── app/models/report.py ──────────────────────────────────────────────────────
FILES["app/models/report.py"] = '''from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Date
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
'''

# ── app/models/__init__.py ────────────────────────────────────────────────────
FILES["app/models/__init__.py"] = '''from app.models.auth import User, Session
from app.models.academic import University, Program, Course, Cpl, Cpmk, CourseCplMapping, CpmkCplMapping
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem, OpenQuestion
from app.models.respondent import (Respondent, RespondentCourseTaught, RespondentCourseTaken,
                                    RespondentMotivation, RespondentCareerGoal,
                                    RespondentMediaUsage, RespondentActivity)
from app.models.response import Response, ResponseItem, ResponseOpenAnswer, AnonymousCode
from app.models.rps import RpsVersion, RpsChecklistItem, RpsChecklistResponse
from app.models.assessment import AssessmentScheme, AssessmentRubric, MbkmIntegration
from app.models.report import DiagnosticReport

__all__ = [
    "User", "Session",
    "University", "Program", "Course", "Cpl", "Cpmk", "CourseCplMapping", "CpmkCplMapping",
    "CippDimension", "CippSubDimension", "InstrumentItem", "OpenQuestion",
    "Respondent", "RespondentCourseTaught", "RespondentCourseTaken",
    "RespondentMotivation", "RespondentCareerGoal", "RespondentMediaUsage", "RespondentActivity",
    "Response", "ResponseItem", "ResponseOpenAnswer", "AnonymousCode",
    "RpsVersion", "RpsChecklistItem", "RpsChecklistResponse",
    "AssessmentScheme", "AssessmentRubric", "MbkmIntegration",
    "DiagnosticReport",
]
'''

# ── app/schemas/auth.py ───────────────────────────────────────────────────────
FILES["app/schemas/auth.py"] = '''from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class UserInfo(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    university_id: Optional[int] = None

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
'''

# ── app/schemas/academic.py ───────────────────────────────────────────────────
FILES["app/schemas/academic.py"] = '''from pydantic import BaseModel
from typing import Optional


class UniversityPublic(BaseModel):
    id: int
    nama: str
    nama_singkat: str
    kota: str
    provinsi: str
    model_config = {"from_attributes": True}


class ProgramPublic(BaseModel):
    id: int
    nama: str
    nama_singkat: str
    jenjang: str
    model_config = {"from_attributes": True}


class CoursePublic(BaseModel):
    id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    model_config = {"from_attributes": True}


class UniversityCreate(BaseModel):
    nama: str
    nama_singkat: str
    jenis: str
    kota: str
    provinsi: str
    website: Optional[str] = None
    akreditasi: Optional[str] = None
    tahun_berdiri: Optional[int] = None


class ProgramCreate(BaseModel):
    university_id: int
    nama: str
    nama_singkat: str
    jenjang: str
    tahun_berdiri: Optional[int] = None
    akreditasi: Optional[str] = None


class CourseCreate(BaseModel):
    program_id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    status_mk: str = "wajib"
    deskripsi: Optional[str] = None
'''

# ── app/schemas/respondent.py ─────────────────────────────────────────────────
FILES["app/schemas/respondent.py"] = '''from pydantic import BaseModel
from typing import Optional, List
import uuid


class CourseTaughtIn(BaseModel):
    course_name: str
    course_id: Optional[int] = None


class CourseTakenIn(BaseModel):
    course_name: str
    course_id: Optional[int] = None
    semester_taken: Optional[int] = None
    final_grade: Optional[str] = None


class SurveyStartRequest(BaseModel):
    course_id: int
    role: str  # dosen | mahasiswa
    bahasa: str  # id | zh
    # Profil umum
    full_name: Optional[str] = None
    university_id: int
    program_id: Optional[int] = None
    faculty: Optional[str] = None
    # Atribut dosen
    academic_position: Optional[str] = None
    teaching_duration: Optional[str] = None
    education_level: Optional[str] = None
    china_experience_dosen: Optional[str] = None
    hsk_level_dosen: Optional[str] = None
    avg_class_size: Optional[str] = None
    course_taught: List[CourseTaughtIn] = []
    # Atribut mahasiswa
    gender: Optional[str] = None
    age: Optional[int] = None
    current_semester: Optional[int] = None
    mandarin_study_duration: Optional[str] = None
    hsk_level_mahasiswa: Optional[str] = None
    china_stay_duration: Optional[str] = None
    chinese_friends: Optional[str] = None
    has_taken_culture_course: Optional[bool] = None
    culture_course_count: Optional[str] = None
    course_status_taken: Optional[str] = None
    cultural_interaction_freq: Optional[str] = None
    course_taken: List[CourseTakenIn] = []
    # Multi-pilih
    motivations: List[str] = []
    career_goals: List[str] = []
    media_usage: List[str] = []
    activities: List[str] = []


class SurveyStartResponse(BaseModel):
    response_id: uuid.UUID
    respondent_id: uuid.UUID
    role: str
    bahasa: str
'''

# ── app/schemas/response.py ───────────────────────────────────────────────────
FILES["app/schemas/response.py"] = '''from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime


class ItemAnswer(BaseModel):
    item_id: int
    skor: int


class OpenAnswer(BaseModel):
    open_question_id: int
    jawaban_teks: str


class AnswerRequest(BaseModel):
    items: List[ItemAnswer] = []
    open_answers: List[OpenAnswer] = []


class AnswerResponse(BaseModel):
    saved: int
    response_id: uuid.UUID


class SubmitResponse(BaseModel):
    kode_anonim: str
    generated_at: datetime
    message_id: str
    message_zh: str


class ItemOut(BaseModel):
    id: int
    kode: str
    nomor_urut: int
    teks: str
    answer_type: str
    scale_min: int
    scale_max: int
    is_required: bool
    model_config = {"from_attributes": True}


class SubDimensionOut(BaseModel):
    id: int
    kode: str
    nama: str
    items: List[ItemOut]
    model_config = {"from_attributes": True}


class OpenQuestionOut(BaseModel):
    id: int
    kode: str
    pertanyaan: str
    is_required: bool
    model_config = {"from_attributes": True}


class SurveyItemsResponse(BaseModel):
    dimensi: str
    nama_dimensi: str
    sub_dimensions: List[SubDimensionOut]
    open_questions: List[OpenQuestionOut]


class CippScoreOut(BaseModel):
    dimensi: str
    kode: str
    skor_rata: float
    std_dev: float
    jumlah_item: int


class OpenAnswerOut(BaseModel):
    pertanyaan: str
    jawaban: str


class ResultResponse(BaseModel):
    kode: str
    course: dict
    role: str
    bahasa: str
    submitted_at: Optional[datetime]
    cipp_scores: List[CippScoreOut]
    open_answers: List[OpenAnswerOut]
'''

# ── app/services/code_generator.py ───────────────────────────────────────────
FILES["app/services/code_generator.py"] = '''import random
import string
from datetime import datetime


def generate_anonymous_code(year: int | None = None) -> str:
    """Generate kode anonim format SIN-YYYY-XXXX."""
    y = year or datetime.now().year
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SIN-{y}-{suffix}"
'''

# ── app/dependencies.py ───────────────────────────────────────────────────────
FILES["app/dependencies.py"] = '''from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from app.database import get_db
from app.core.security import decode_token
from app.models.auth import User, Session
from datetime import datetime, timezone

bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid atau kadaluarsa")

    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("superadmin", "admin", "dosen"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    if user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
    return user
'''

# ── app/routers/auth.py ───────────────────────────────────────────────────────
FILES["app/routers/auth.py"] = '''from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.auth import User, Session
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo, RefreshRequest, LogoutRequest
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.config import settings
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email atau password salah")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    session = Session(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=request.client.host if request.client else None,
    )
    db.add(session)
    user.last_login = datetime.now(timezone.utc)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo.model_validate(user),
    )


@router.post("/logout")
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).where(Session.refresh_token == body.refresh_token))
    session = result.scalar_one_or_none()
    if session:
        session.is_revoked = True
    return {"message": "Logout berhasil"}


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token tidak valid atau kadaluarsa")

    result = await db.execute(
        select(Session).where(
            Session.refresh_token == body.refresh_token,
            Session.is_revoked == False,
            Session.expires_at > datetime.now(timezone.utc),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token tidak valid atau sudah digunakan")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak aktif")

    new_access = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": new_access, "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}
'''

# ── app/routers/public/landing.py ─────────────────────────────────────────────
FILES["app/routers/public/landing.py"] = '''from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.academic import University
from app.models.response import Response
from app.schemas.academic import UniversityPublic

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/landing")
async def landing_data(db: AsyncSession = Depends(get_db)):
    univ_result = await db.execute(
        select(University).where(University.is_active == True).order_by(University.nama)
    )
    universities = univ_result.scalars().all()

    total_univ = len(universities)

    total_resp = await db.execute(select(func.count(Response.id)).where(Response.is_complete == True))
    total_respondents = total_resp.scalar_one() or 0

    from app.models.academic import Course
    from sqlalchemy import distinct
    courses_eval = await db.execute(
        select(func.count(distinct(Response.course_id))).where(Response.is_complete == True)
    )
    total_courses = courses_eval.scalar_one() or 0

    return {
        "total_universities": total_univ,
        "total_respondents": total_respondents,
        "total_courses_evaluated": total_courses,
        "avg_cipp_score": None,
        "universities": [UniversityPublic.model_validate(u) for u in universities],
    }
'''

# ── app/routers/public/survey.py ──────────────────────────────────────────────
FILES["app/routers/public/survey.py"] = '''from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
import hashlib
from app.database import get_db
from app.models.academic import University, Program, Course
from app.models.instrument import CippDimension, CippSubDimension, InstrumentItem, OpenQuestion
from app.models.respondent import (Respondent, RespondentCourseTaught, RespondentCourseTaken,
                                   RespondentMotivation, RespondentCareerGoal,
                                   RespondentMediaUsage, RespondentActivity)
from app.models.response import Response, ResponseItem, ResponseOpenAnswer, AnonymousCode
from app.schemas.academic import UniversityPublic, ProgramPublic, CoursePublic
from app.schemas.respondent import SurveyStartRequest, SurveyStartResponse
from app.schemas.response import (AnswerRequest, AnswerResponse, SubmitResponse,
                                   SurveyItemsResponse, SubDimensionOut, ItemOut, OpenQuestionOut)
from app.services.code_generator import generate_anonymous_code

router = APIRouter(prefix="/public", tags=["public-survey"])


@router.get("/universities")
async def list_universities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(University).where(University.is_active == True).order_by(University.nama))
    return {"data": [UniversityPublic.model_validate(u) for u in result.scalars().all()]}


@router.get("/universities/{university_id}/programs")
async def list_programs(university_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Program).where(Program.university_id == university_id, Program.is_active == True)
    )
    return {"data": [ProgramPublic.model_validate(p) for p in result.scalars().all()]}


@router.get("/programs/{program_id}/courses")
async def list_courses(program_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(Course.program_id == program_id, Course.is_active == True)
    )
    return {"data": [CoursePublic.model_validate(c) for c in result.scalars().all()]}


@router.post("/survey/start", response_model=SurveyStartResponse, status_code=201)
async def start_survey(body: SurveyStartRequest, request: Request, db: AsyncSession = Depends(get_db)):
    course = await db.get(Course, body.course_id)
    if not course or not course.is_active:
        raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")

    respondent = Respondent(
        role=body.role, full_name=body.full_name, university_id=body.university_id,
        program_id=body.program_id, faculty=body.faculty,
        academic_position=body.academic_position, teaching_duration=body.teaching_duration,
        education_level=body.education_level, china_experience_dosen=body.china_experience_dosen,
        hsk_level_dosen=body.hsk_level_dosen, avg_class_size=body.avg_class_size,
        gender=body.gender, age=body.age, current_semester=body.current_semester,
        mandarin_study_duration=body.mandarin_study_duration, hsk_level_mahasiswa=body.hsk_level_mahasiswa,
        china_stay_duration=body.china_stay_duration, chinese_friends=body.chinese_friends,
        has_taken_culture_course=body.has_taken_culture_course, culture_course_count=body.culture_course_count,
        course_status_taken=body.course_status_taken, cultural_interaction_freq=body.cultural_interaction_freq,
    )
    db.add(respondent)
    await db.flush()

    for ct in body.course_taught:
        db.add(RespondentCourseTaught(respondent_id=respondent.id, course_name=ct.course_name, course_id=ct.course_id))
    for ct in body.course_taken:
        db.add(RespondentCourseTaken(respondent_id=respondent.id, course_name=ct.course_name,
                                     course_id=ct.course_id, semester_taken=ct.semester_taken, final_grade=ct.final_grade))
    for m in body.motivations:
        db.add(RespondentMotivation(respondent_id=respondent.id, motivasi=m))
    for c in body.career_goals:
        db.add(RespondentCareerGoal(respondent_id=respondent.id, bidang_karir=c))
    for m in body.media_usage:
        db.add(RespondentMediaUsage(respondent_id=respondent.id, media=m))
    for a in body.activities:
        db.add(RespondentActivity(respondent_id=respondent.id, aktivitas=a))

    raw_ip = request.client.host if request.client else ""
    ip_hash = hashlib.sha256(raw_ip.encode()).hexdigest() if raw_ip else None

    response = Response(
        respondent_id=respondent.id, course_id=body.course_id,
        role=body.role, bahasa=body.bahasa, ip_hash=ip_hash,
    )
    db.add(response)
    await db.flush()

    return SurveyStartResponse(response_id=response.id, respondent_id=respondent.id,
                                role=body.role, bahasa=body.bahasa)


@router.get("/survey/{response_id}/items", response_model=SurveyItemsResponse)
async def get_survey_items(response_id: str, dimensi: str | None = None, db: AsyncSession = Depends(get_db)):
    response = await db.get(Response, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response tidak ditemukan")

    role = response.role
    bahasa = response.bahasa

    dim_q = select(CippDimension).options(
        selectinload(CippDimension.sub_dimensions).selectinload(CippSubDimension.items)
    ).order_by(CippDimension.urutan)
    if dimensi:
        dim_q = dim_q.where(CippDimension.kode == dimensi.upper())

    dim_result = await db.execute(dim_q)
    dimension = dim_result.scalar_one_or_none()
    if not dimension:
        raise HTTPException(status_code=404, detail="Dimensi tidak ditemukan")

    sub_dims_out = []
    for sd in dimension.sub_dimensions:
        active_items = [i for i in sd.items if i.is_active]
        items_out = []
        for item in active_items:
            if bahasa == "id":
                teks = item.text_id_dosen if role == "dosen" else item.text_id_mahasiswa
            else:
                teks = item.text_zh_dosen if role == "dosen" else item.text_zh_mahasiswa
            items_out.append(ItemOut(
                id=item.id, kode=item.kode, nomor_urut=item.nomor_urut,
                teks=teks, answer_type=item.answer_type,
                scale_min=item.scale_min, scale_max=item.scale_max, is_required=item.is_required,
            ))
        sub_dims_out.append(SubDimensionOut(
            id=sd.id, kode=sd.kode,
            nama=sd.nama_id if bahasa == "id" else sd.nama_zh,
            items=items_out,
        ))

    open_q_result = await db.execute(
        select(OpenQuestion).where(
            OpenQuestion.is_active == True,
            OpenQuestion.target_role.in_([role, "semua"])
        ).order_by(OpenQuestion.urutan)
    )
    open_questions = [
        OpenQuestionOut(
            id=q.id, kode=q.kode,
            pertanyaan=q.pertanyaan_id if bahasa == "id" else q.pertanyaan_zh,
            is_required=q.is_required,
        )
        for q in open_q_result.scalars().all()
    ]

    return SurveyItemsResponse(
        dimensi=dimension.kode,
        nama_dimensi=dimension.nama_id if bahasa == "id" else dimension.nama_zh,
        sub_dimensions=sub_dims_out,
        open_questions=open_questions if not dimensi else [],
    )


@router.post("/survey/{response_id}/answers", response_model=AnswerResponse)
async def save_answers(response_id: str, body: AnswerRequest, db: AsyncSession = Depends(get_db)):
    response = await db.get(Response, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response tidak ditemukan")
    if response.is_complete:
        raise HTTPException(status_code=400, detail="Kuesioner sudah di-submit")

    count = 0
    for ans in body.items:
        if not (1 <= ans.skor <= 5):
            raise HTTPException(status_code=400, detail=f"Skor item {ans.item_id} harus antara 1-5")
        existing = await db.execute(
            select(ResponseItem).where(
                ResponseItem.response_id == response.id,
                ResponseItem.item_id == ans.item_id,
            )
        )
        ri = existing.scalar_one_or_none()
        if ri:
            ri.skor = ans.skor
        else:
            db.add(ResponseItem(response_id=response.id, item_id=ans.item_id, skor=ans.skor))
        count += 1

    for oa in body.open_answers:
        existing = await db.execute(
            select(ResponseOpenAnswer).where(
                ResponseOpenAnswer.response_id == response.id,
                ResponseOpenAnswer.open_question_id == oa.open_question_id,
            )
        )
        roa = existing.scalar_one_or_none()
        if roa:
            roa.jawaban_teks = oa.jawaban_teks
        else:
            db.add(ResponseOpenAnswer(response_id=response.id,
                                      open_question_id=oa.open_question_id,
                                      jawaban_teks=oa.jawaban_teks))

    return AnswerResponse(saved=count, response_id=response.id)


@router.post("/survey/{response_id}/submit", response_model=SubmitResponse, status_code=201)
async def submit_survey(response_id: str, db: AsyncSession = Depends(get_db)):
    response = await db.get(Response, response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response tidak ditemukan")
    if response.is_complete:
        existing_code = await db.execute(
            select(AnonymousCode).where(AnonymousCode.response_id == response.id)
        )
        code = existing_code.scalar_one_or_none()
        if code:
            return SubmitResponse(
                kode_anonim=code.kode,
                generated_at=code.generated_at,
                message_id="Terima kasih, kuesioner Anda sudah tersimpan.",
                message_zh="感谢您，您的问卷已提交。",
            )

    response.is_complete = True
    response.submitted_at = datetime.now(timezone.utc)

    for attempt in range(10):
        kode = generate_anonymous_code()
        existing = await db.execute(select(AnonymousCode).where(AnonymousCode.kode == kode))
        if not existing.scalar_one_or_none():
            break

    anon = AnonymousCode(kode=kode, response_id=response.id)
    db.add(anon)
    await db.flush()

    return SubmitResponse(
        kode_anonim=kode,
        generated_at=anon.generated_at,
        message_id="Terima kasih! Simpan kode anonim Anda untuk melihat hasil.",
        message_zh="谢谢！请保存您的匿名代码以查看结果。",
    )
'''

# ── app/routers/public/result.py ──────────────────────────────────────────────
FILES["app/routers/public/result.py"] = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.database import get_db
from app.models.response import AnonymousCode, Response, ResponseItem, ResponseOpenAnswer
from app.models.instrument import InstrumentItem, CippSubDimension, CippDimension, OpenQuestion
from app.schemas.response import ResultResponse, CippScoreOut, OpenAnswerOut
import math

router = APIRouter(prefix="/public", tags=["public-result"])


@router.get("/result/{kode}", response_model=ResultResponse)
async def get_result(kode: str, db: AsyncSession = Depends(get_db)):
    anon_result = await db.execute(
        select(AnonymousCode).where(AnonymousCode.kode == kode)
    )
    anon = anon_result.scalar_one_or_none()
    if not anon:
        raise HTTPException(status_code=404, detail="Kode tidak ditemukan")
    if not anon.is_accessible:
        raise HTTPException(status_code=403, detail="Akses kode anonim tidak aktif")

    anon.last_accessed = datetime.now(timezone.utc)

    response = await db.get(Response, anon.response_id)
    course = await db.get_one.__class__  # noqa
    from app.models.academic import Course
    course = await db.get(Course, response.course_id)

    items_result = await db.execute(
        select(ResponseItem).where(ResponseItem.response_id == response.id)
    )
    response_items = items_result.scalars().all()

    dims_result = await db.execute(
        select(CippDimension).options(
            selectinload(CippDimension.sub_dimensions).selectinload(CippSubDimension.items)
        ).order_by(CippDimension.urutan)
    )
    dimensions = dims_result.scalars().all()

    item_score_map = {ri.item_id: ri.skor for ri in response_items}
    bahasa = response.bahasa

    cipp_scores = []
    for dim in dimensions:
        scores = []
        for sd in dim.sub_dimensions:
            for item in sd.items:
                if item.id in item_score_map:
                    scores.append(item_score_map[item.id])
        if scores:
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            cipp_scores.append(CippScoreOut(
                dimensi=dim.nama_id if bahasa == "id" else dim.nama_zh,
                kode=dim.kode,
                skor_rata=round(mean, 2),
                std_dev=round(math.sqrt(variance), 2),
                jumlah_item=len(scores),
            ))

    open_result = await db.execute(
        select(ResponseOpenAnswer).where(ResponseOpenAnswer.response_id == response.id)
    )
    open_answers_db = open_result.scalars().all()
    open_answers = []
    for oa in open_answers_db:
        q = await db.get(OpenQuestion, oa.open_question_id)
        if q:
            open_answers.append(OpenAnswerOut(
                pertanyaan=q.pertanyaan_id if bahasa == "id" else q.pertanyaan_zh,
                jawaban=oa.jawaban_teks,
            ))

    return ResultResponse(
        kode=anon.kode,
        course={"nama_id": course.nama_id, "nama_zh": course.nama_zh, "kode_mk": course.kode_mk},
        role=response.role,
        bahasa=response.bahasa,
        submitted_at=response.submitted_at,
        cipp_scores=cipp_scores,
        open_answers=open_answers,
    )
'''

# ── app/main.py ───────────────────────────────────────────────────────────────
FILES["app/main.py"] = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.core.exceptions import validation_exception_handler, generic_exception_handler
from app.core.middleware import log_request_middleware
from app.routers.auth import router as auth_router
from app.routers.public.landing import router as landing_router
from app.routers.public.survey import router as survey_router
from app.routers.public.result import router as result_router

app = FastAPI(
    title="SINOKU API",
    description="Sistem Evaluasi & Monitoring Mata Kuliah Budaya Tiongkok",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(landing_router, prefix=API_PREFIX)
app.include_router(survey_router, prefix=API_PREFIX)
app.include_router(result_router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sinoku-api"}
'''

# ── migrations/env.py ─────────────────────────────────────────────────────────
FILES["migrations/env.py"] = '''import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.config import settings
from app.database import Base

# Import semua model agar Alembic mendeteksi tabel
import app.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

# ── alembic.ini ───────────────────────────────────────────────────────────────
FILES["alembic.ini"] = '''[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''

# ── migrations/script.py.mako ─────────────────────────────────────────────────
FILES["migrations/script.py.mako"] = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

# ── seed data ─────────────────────────────────────────────────────────────────
FILES["app/services/seed.py"] = '''"""Seed data awal: 4 dimensi CIPP, 15 sub-dimensi, 59 item, 8 pertanyaan terbuka."""
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
'''

# ── scripts/seed_db.py ────────────────────────────────────────────────────────
FILES["scripts/seed_db.py"] = '''"""Jalankan: python -m scripts.seed_db dari folder backend/"""
import asyncio
from app.database import AsyncSessionLocal
from app.services.seed import run_all_seeds


async def main():
    async with AsyncSessionLocal() as db:
        await run_all_seeds(db)
        await db.commit()
        print("Seed selesai!")


asyncio.run(main())
'''

# ── Dockerfile ────────────────────────────────────────────────────────────────
FILES["Dockerfile"] = '''FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

# ─────────────────────────────────────────────────────────────────────────────
# Tulis semua file
# ─────────────────────────────────────────────────────────────────────────────
written = 0
for rel, content in FILES.items():
    full = os.path.join(BASE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    written += 1
    print(f"[OK] {rel}")

print(f"\n{written} file backend berhasil ditulis.")
