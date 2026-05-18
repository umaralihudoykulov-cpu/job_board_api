from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password cannot be longer than 72 bytes.")
        return value


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserMe(UserRead):
    pass