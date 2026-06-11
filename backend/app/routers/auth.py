from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.auth import User, Session
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo, RefreshRequest, LogoutRequest
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.config import settings
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email atau password salah")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    session = Session(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=request.client.host if request.client else None,
    )
    db.add(session)
    user.last_login = datetime.now(timezone.utc)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo.model_validate(user),
    )


@router.post("/logout")
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).where(Session.refresh_token == body.refresh_token))
    session = result.scalar_one_or_none()
    if session:
        session.is_revoked = True
    return {"message": "Logout berhasil"}


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token tidak valid atau kadaluarsa")

    result = await db.execute(
        select(Session).where(
            Session.refresh_token == body.refresh_token,
            Session.is_revoked == False,
            Session.expires_at > datetime.now(timezone.utc),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token tidak valid atau sudah digunakan")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak aktif")

    new_access = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": new_access, "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}
