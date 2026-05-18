import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.user import User


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    accepted = "accepted"
    rejected = "rejected"


class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "applicant_id",
            name="uq_applications_job_applicant",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    cover_letter: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(
            ApplicationStatus,
            name="application_status",
            native_enum=False,
            validate_strings=True,
        ),
        default=ApplicationStatus.pending,
        nullable=False,
        index=True,
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    job: Mapped["Job"] = relationship(
        back_populates="applications",
    )

    applicant: Mapped["User"] = relationship(
        back_populates="applications",
    )