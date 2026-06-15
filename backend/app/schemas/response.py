from pydantic import BaseModel
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


class CapaianOut(BaseModel):
    """F-05.3: rincian capaian pembelajaran per sub-dimensi Produk (E)."""
    kode: str
    nama: str
    skor_rata: float
    target: float
    tercapai: bool
    jumlah_item: int


class ResultResponse(BaseModel):
    kode: str
    course: dict
    role: str
    bahasa: str
    submitted_at: Optional[datetime]
    cipp_scores: List[CippScoreOut]
    capaian_pembelajaran: List[CapaianOut] = []
    open_answers: List[OpenAnswerOut]
