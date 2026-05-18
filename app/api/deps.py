from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.db.database import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
Token = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(
    session: DbSession,
    token: Token,
) -> User:
    payload = decode_token(
        token=token,
        expected_type="access",
    )

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload.")

    try:
        user_repository = UserRepository(session)
        user = await user_repository.get_by_id(int(user_id))

        if not user:
            raise UnauthorizedException("User not found.")

        if not user.is_active:
            raise ForbiddenException("Inactive user.")

        return user

    except ValueError as exc:
        raise UnauthorizedException("Invalid user id in token.") from exc
    except SQLAlchemyError as exc:
        raise UnauthorizedException("Could not validate user.") from exc


CurrentUser = Annotated[User, Depends(get_current_user)]