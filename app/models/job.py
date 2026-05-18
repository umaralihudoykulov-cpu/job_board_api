from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(length=150),
        index=True,
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(
        String(length=150),
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    location: Mapped[str] = mapped_column(
        String(length=150),
        index=True,
        nullable=False,
    )
    salary_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    salary_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    owner_id: Mapped[int] = mapped_column(
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

    owner: Mapped["User"] = relationship(
        back_populates="jobs",
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )