from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, Numeric
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
