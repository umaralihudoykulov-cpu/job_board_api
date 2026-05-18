from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.user import UserRead


class JobBase(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    company_name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=10)
    location: str = Field(min_length=2, max_length=150)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_salary_range(self) -> "JobBase":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max.")
        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    company_name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, min_length=10)
    location: str | None = Field(default=None, min_length=2, max_length=150)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_salary_range(self) -> "JobUpdate":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max.")
        return self


class JobRead(JobBase):
    id: int
    is_active: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class JobDetail(JobRead):
    owner: UserRead