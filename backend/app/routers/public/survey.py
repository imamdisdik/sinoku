from fastapi import APIRouter, Depends, HTTPException, status, Request
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
