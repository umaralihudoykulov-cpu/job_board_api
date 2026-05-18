from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.core.security import decode_token
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    session: DbSession,
) -> UserRead:
    service = AuthService(session)
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbSession,
) -> TokenResponse:
    service = AuthService(session)
    return await service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    data: RefreshTokenRequest,
    session: DbSession,
) -> TokenResponse:
    payload = decode_token(
        token=data.refresh_token,
        expected_type="refresh",
    )

    user_id = int(payload["sub"])

    service = AuthService(session)
    return await service.refresh_tokens(user_id)