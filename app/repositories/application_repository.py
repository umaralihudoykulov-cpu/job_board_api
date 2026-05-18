from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, application_id: int) -> Application | None:
        try:
            result = await self.session.execute(
                select(Application)
                .options(
                    selectinload(Application.job),
                    selectinload(Application.applicant),
                )
                .where(Application.id == application_id),
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    async def get_by_job_and_user(
        self,
        job_id: int,
        applicant_id: int,
    ) -> Application | None:
        try:
            result = await self.session.execute(
                select(Application).where(
                    Application.job_id == job_id,
                    Application.applicant_id == applicant_id,
                ),
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    async def create(
        self,
        data: ApplicationCreate,
        applicant_id: int,
    ) -> Application:
        try:
            application = Application(
                job_id=data.job_id,
                applicant_id=applicant_id,
                cover_letter=data.cover_letter,
            )
            self.session.add(application)
            await self.session.flush()
            await self.session.refresh(application)
            return application
        except SQLAlchemyError:
            raise

    async def list_my_applications(
        self,
        applicant_id: int,
        skip: int,
        limit: int,
    ) -> list[Application]:
        try:
            result = await self.session.execute(
                select(Application)
                .options(
                    selectinload(Application.job),
                    selectinload(Application.applicant),
                )
                .where(Application.applicant_id == applicant_id)
                .order_by(Application.created_at.desc())
                .offset(skip)
                .limit(limit),
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            raise

    async def list_job_applications(
        self,
        job_id: int,
        skip: int,
        limit: int,
    ) -> list[Application]:
        try:
            result = await self.session.execute(
                select(Application)
                .options(
                    selectinload(Application.job),
                    selectinload(Application.applicant),
                )
                .where(Application.job_id == job_id)
                .order_by(Application.created_at.desc())
                .offset(skip)
                .limit(limit),
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            raise

    async def update_status(
        self,
        application: Application,
        status: ApplicationStatus,
    ) -> Application:
        try:
            application.status = status
            await self.session.flush()
            await self.session.refresh(application)
            return application
        except SQLAlchemyError:
            raise