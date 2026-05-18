from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | int) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str | int) -> str:
    expire = datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days,
    )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        token_type = payload.get("type")
        if token_type != expected_type:
            raise UnauthorizedException("Invalid token type.")

        return payload

    except InvalidTokenError as exc:
        raise UnauthorizedException("Could not validate token.") from exc