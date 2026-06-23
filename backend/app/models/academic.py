from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime
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

    faculties: Mapped[list["Faculty"]] = relationship("Faculty", back_populates="university")
    programs: Mapped[list["Program"]] = relationship("Program", back_populates="university")
    respondents: Mapped[list["Respondent"]] = relationship("Respondent", back_populates="university")


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    nama: Mapped[str] = mapped_column(String(200), nullable=False)
    nama_singkat: Mapped[str] = mapped_column(String(20), nullable=False)
    rumpun_keilmuan: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    university: Mapped["University"] = relationship("University", back_populates="faculties")
    programs: Mapped[list["Program"]] = relationship("Program", back_populates="faculty")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    faculty_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faculties.id", ondelete="SET NULL"), nullable=True)
    nama: Mapped[str] = mapped_column(String(200), nullable=False)
    nama_singkat: Mapped[str] = mapped_column(String(20), nullable=False)
    jenjang: Mapped[str] = mapped_column(String(10), nullable=False)  # S1 | S2 | D3 | D4
    tahun_berdiri: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    akreditasi: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    university: Mapped["University"] = relationship("University", back_populates="programs")
    faculty: Mapped["Faculty"] = relationship("Faculty", back_populates="programs")
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
