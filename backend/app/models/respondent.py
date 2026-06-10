from sqlalchemy import String, Boolean, Integer, SmallInteger, ForeignKey, Text, DateTime
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
