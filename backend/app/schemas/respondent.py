from pydantic import BaseModel
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
