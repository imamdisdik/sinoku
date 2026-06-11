from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Public ───────────────────────────────────────────────────────────────────
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


# ── University ────────────────────────────────────────────────────────────────
class UniversityCreate(BaseModel):
    nama: str
    nama_singkat: str
    jenis: str
    kota: str
    provinsi: str
    website: Optional[str] = None
    akreditasi: Optional[str] = None
    tahun_berdiri: Optional[int] = None


class UniversityUpdate(BaseModel):
    nama: Optional[str] = None
    nama_singkat: Optional[str] = None
    jenis: Optional[str] = None
    kota: Optional[str] = None
    provinsi: Optional[str] = None
    website: Optional[str] = None
    akreditasi: Optional[str] = None
    tahun_berdiri: Optional[int] = None
    is_active: Optional[bool] = None


class UniversityOut(BaseModel):
    id: int
    nama: str
    nama_singkat: str
    jenis: str
    kota: str
    provinsi: str
    website: Optional[str]
    akreditasi: Optional[str]
    tahun_berdiri: Optional[int]
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Program ───────────────────────────────────────────────────────────────────
class ProgramCreate(BaseModel):
    university_id: int
    nama: str
    nama_singkat: str
    jenjang: str
    tahun_berdiri: Optional[int] = None
    akreditasi: Optional[str] = None


class ProgramUpdate(BaseModel):
    nama: Optional[str] = None
    nama_singkat: Optional[str] = None
    jenjang: Optional[str] = None
    tahun_berdiri: Optional[int] = None
    akreditasi: Optional[str] = None
    is_active: Optional[bool] = None


class ProgramOut(BaseModel):
    id: int
    university_id: int
    nama: str
    nama_singkat: str
    jenjang: str
    tahun_berdiri: Optional[int]
    akreditasi: Optional[str]
    is_active: bool
    model_config = {"from_attributes": True}


# ── Course ────────────────────────────────────────────────────────────────────
class CourseCreate(BaseModel):
    program_id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    status_mk: str = "wajib"
    deskripsi: Optional[str] = None


class CourseUpdate(BaseModel):
    kode_mk: Optional[str] = None
    nama_id: Optional[str] = None
    nama_zh: Optional[str] = None
    sks: Optional[int] = None
    semester: Optional[int] = None
    status_mk: Optional[str] = None
    deskripsi: Optional[str] = None
    is_active: Optional[bool] = None


class CourseOut(BaseModel):
    id: int
    program_id: int
    kode_mk: str
    nama_id: str
    nama_zh: str
    sks: int
    semester: int
    status_mk: str
    deskripsi: Optional[str]
    is_active: bool
    model_config = {"from_attributes": True}


# ── CPL ───────────────────────────────────────────────────────────────────────
class CplCreate(BaseModel):
    program_id: int
    kode_cpl: str
    deskripsi_id: str
    deskripsi_zh: str
    kategori: str  # sikap | pengetahuan | keterampilan


class CplUpdate(BaseModel):
    kode_cpl: Optional[str] = None
    deskripsi_id: Optional[str] = None
    deskripsi_zh: Optional[str] = None
    kategori: Optional[str] = None
    is_active: Optional[bool] = None


class CplOut(BaseModel):
    id: int
    program_id: int
    kode_cpl: str
    deskripsi_id: str
    deskripsi_zh: str
    kategori: str
    is_active: bool
    model_config = {"from_attributes": True}


# ── CPMK ──────────────────────────────────────────────────────────────────────
class CpmkCreate(BaseModel):
    course_id: int
    kode_cpmk: str
    deskripsi_id: str
    deskripsi_zh: str
    bobot_persen: float = Field(ge=0, le=100)


class CpmkUpdate(BaseModel):
    kode_cpmk: Optional[str] = None
    deskripsi_id: Optional[str] = None
    deskripsi_zh: Optional[str] = None
    bobot_persen: Optional[float] = None
    is_active: Optional[bool] = None


class CpmkOut(BaseModel):
    id: int
    course_id: int
    kode_cpmk: str
    deskripsi_id: str
    deskripsi_zh: str
    bobot_persen: float
    is_active: bool
    model_config = {"from_attributes": True}


# ── Mapping ───────────────────────────────────────────────────────────────────
class MappingIds(BaseModel):
    cpl_ids: List[int]


# ── Pagination wrapper ────────────────────────────────────────────────────────
class PagedUniversity(BaseModel):
    data: List[UniversityOut]
    total: int
    page: int
    limit: int


class PagedProgram(BaseModel):
    data: List[ProgramOut]
    total: int
    page: int
    limit: int


class PagedCourse(BaseModel):
    data: List[CourseOut]
    total: int
    page: int
    limit: int
