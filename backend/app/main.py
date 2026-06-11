from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.core.exceptions import validation_exception_handler, generic_exception_handler
from app.core.middleware import log_request_middleware
from app.routers.auth import router as auth_router
from app.routers.public.landing import router as landing_router
from app.routers.public.survey import router as survey_router
from app.routers.public.result import router as result_router
from app.routers.admin.academic import router as academic_router
from app.routers.admin.dashboard import router as dashboard_router
from app.routers.admin.users import router as users_router

app = FastAPI(
    title="SINOKU API",
    description="Sistem Evaluasi & Monitoring Mata Kuliah Budaya Tiongkok",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

API_PREFIX = "/api/v1"
app.include_router(auth_router,      prefix=API_PREFIX)
app.include_router(landing_router,   prefix=API_PREFIX)
app.include_router(survey_router,    prefix=API_PREFIX)
app.include_router(result_router,    prefix=API_PREFIX)
app.include_router(academic_router,  prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(users_router,     prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sinoku-api"}
