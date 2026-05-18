from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        try:
            existing_user = await self.user_repository.get_by_email(data.email)
            if existing_user:
                raise BadRequestException("Email already registered.")

            user = await self.user_repository.create(
                full_name=data.full_name,
                email=data.email,
                hashed_password=hash_password(data.password),
            )

            await self.session.commit()
            return user

        except BadRequestException:
            await self.session.rollback()
            raise
        except IntegrityError as exc:
            await self.session.rollback()
            raise BadRequestException("Email already registered.") from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise BadRequestException("Could not create user.") from exc

    async def authenticate(self, email: str, password: str) -> TokenResponse:
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise UnauthorizedException("Invalid email or password.")

            if not user.is_active:
                raise UnauthorizedException("User account is inactive.")

            if not verify_password(password, user.hashed_password):
                raise UnauthorizedException("Invalid email or password.")

            return TokenResponse(
                access_token=create_access_token(user.id),
                refresh_token=create_refresh_token(user.id),
            )

        except UnauthorizedException:
            raise
        except SQLAlchemyError as exc:
            raise BadRequestException("Authentication failed.") from exc

    async def refresh_tokens(self, user_id: int) -> TokenResponse:
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise UnauthorizedException("User not found.")

            if not user.is_active:
                raise UnauthorizedException("User account is inactive.")

            return TokenResponse(
                access_token=create_access_token(user.id),
                refresh_token=create_refresh_token(user.id),
            )

        except UnauthorizedException:
            raise
        except SQLAlchemyError as exc:
            raise BadRequestException("Could not refresh token.") from exc