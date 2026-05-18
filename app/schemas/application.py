from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus
from app.schemas.job import JobRead
from app.schemas.user import UserRead


class ApplicationCreate(BaseModel):
    job_id: int = Field(gt=0)
    cover_letter: str | None = Field(default=None, max_length=5000)


class ApplicationUpdateStatus(BaseModel):
    status: ApplicationStatus


class ApplicationRead(BaseModel):
    id: int
    cover_letter: str | None
    status: ApplicationStatus
    job_id: int
    applicant_id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ApplicationDetail(ApplicationRead):
    job: JobRead
    applicant: UserRead