from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.dependencies import require_admin
from app.models.auth import User
from app.models.response import AnonymousCode, Response
from app.models.respondent import Respondent
from app.models.academic import Course, Program

router = APIRouter(prefix="/admin/anonymous-codes", tags=["admin-anonymous"])


class AnonCodeOut(BaseModel):
    id: int
    kode: str
    is_accessible: bool
    generated_at: datetime
    last_accessed: Optional[datetime] = None
    response_id: str
    role: str
    course_id: int
    is_complete: bool
    submitted_at: Optional[datetime] = None
    respondent_name: Optional[str] = None
    model_config = {"from_attributes": True}


@router.get("")
async def list_anonymous_codes(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    course_id: Optional[int] = None,
    is_accessible: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    q = (
        select(AnonymousCode, Response, Respondent)
        .join(Response, AnonymousCode.response_id == Response.id)
        .outerjoin(Respondent, Response.respondent_id == Respondent.id)
    )

    # Scoping: admin universitas hanya lihat kode dari universitasnya sendiri
    if current_user.role in ("admin", "dosen") and current_user.university_id:
        q = q.join(Course, Response.course_id == Course.id).join(
            Program, Course.program_id == Program.id
        ).where(Program.university_id == current_user.university_id)

    if search:
        q = q.where(AnonymousCode.kode.ilike(f"%{search}%"))
    if role:
        q = q.where(Response.role == role)
    if course_id:
        q = q.where(Response.course_id == course_id)
    if is_accessible is not None:
        q = q.where(AnonymousCode.is_accessible == is_accessible)

    total = (await db.execute(
        select(func.count()).select_from(q.subquery())
    )).scalar_one()

    q = q.order_by(AnonymousCode.generated_at.desc())
    q = q.offset((page - 1) * limit).limit(limit)

    rows = (await db.execute(q)).all()

    data = []
    for anon, resp, respondent in rows:
        data.append({
            "id": anon.id,
            "kode": anon.kode,
            "is_accessible": anon.is_accessible,
            "generated_at": anon.generated_at,
            "last_accessed": anon.last_accessed,
            "response_id": str(resp.id),
            "role": resp.role,
            "course_id": resp.course_id,
            "is_complete": resp.is_complete,
            "submitted_at": resp.submitted_at,
            "respondent_name": respondent.full_name if respondent else None,
        })

    return {"data": data, "total": total, "page": page, "limit": limit}


@router.patch("/{kode}/toggle")
async def toggle_accessible(
    kode: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    anon = (await db.execute(
        select(AnonymousCode).where(AnonymousCode.kode == kode)
    )).scalar_one_or_none()
    if not anon:
        raise HTTPException(status_code=404, detail="Kode tidak ditemukan")
    anon.is_accessible = not anon.is_accessible
    return {"kode": anon.kode, "is_accessible": anon.is_accessible}
