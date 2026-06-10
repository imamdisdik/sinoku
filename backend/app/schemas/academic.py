from pydantic import BaseModel
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
