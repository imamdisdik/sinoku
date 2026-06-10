from fastapi import APIRouter, Depends
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
