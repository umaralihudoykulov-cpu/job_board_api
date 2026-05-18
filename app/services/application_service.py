from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.application import Application
from app.models.user import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.schemas.application import ApplicationCreate, ApplicationUpdateStatus


class ApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.application_repository = ApplicationRepository(session)
        self.job_repository = JobRepository(session)

    async def apply_to_job(
        self,
        data: ApplicationCreate,
        current_user: User,
    ) -> Application:
        try:
            job = await self.job_repository.get_by_id(data.job_id)
            if not job:
                raise NotFoundException("Job not found.")

            if not job.is_active:
                raise BadRequestException("This job is not active.")

            if job.owner_id == current_user.id:
                raise ForbiddenException("You cannot apply to your own job.")

            existing_application = (
                await self.application_repository.get_by_job_and_user(
                    job_id=data.job_id,
                    applicant_id=current_user.id,
                )
            )
            if existing_application:
                raise BadRequestException("You already applied to this job.")

            application = await self.application_repository.create(
                data=data,
                applicant_id=current_user.id,
            )
            await self.session.commit()
            return application

        except (BadRequestException, ForbiddenException, NotFoundException):
            await self.session.rollback()
            raise
        except IntegrityError as exc:
            await self.session.rollback()
            raise BadRequestException("You already applied to this job.") from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise BadRequestException("Could not create application.") from exc

    async def list_my_applications(
        self,
        current_user: User,
        skip: int,
        limit: int,
    ) -> list[Application]:
        try:
            return await self.application_repository.list_my_applications(
                applicant_id=current_user.id,
                skip=skip,
                limit=limit,
            )
        except SQLAlchemyError as exc:
            raise BadRequestException("Could not list applications.") from exc

    async def list_job_applications(
        self,
        job_id: int,
        current_user: User,
        skip: int,
        limit: int,
    ) -> list[Application]:
        try:
            job = await self.job_repository.get_by_id(job_id)
            if not job:
                raise NotFoundException("Job not found.")

            if job.owner_id != current_user.id and not current_user.is_superuser:
                raise ForbiddenException("You cannot view these applications.")

            return await self.application_repository.list_job_applications(
                job_id=job_id,
                skip=skip,
                limit=limit,
            )

        except (NotFoundException, ForbiddenException):
            raise
        except SQLAlchemyError as exc:
            raise BadRequestException("Could not list job applications.") from exc

    async def update_application_status(
        self,
        application_id: int,
        data: ApplicationUpdateStatus,
        current_user: User,
    ) -> Application:
        try:
            application = await self.application_repository.get_by_id(
                application_id,
            )
            if not application:
                raise NotFoundException("Application not found.")

            if (
                application.job.owner_id != current_user.id
                and not current_user.is_superuser
            ):
                raise ForbiddenException(
                    "You cannot update this application status.",
                )

            updated_application = (
                await self.application_repository.update_status(
                    application=application,
                    status=data.status,
                )
            )
            await self.session.commit()
            return updated_application

        except (NotFoundException, ForbiddenException):
            await self.session.rollback()
            raise
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise BadRequestException(
                "Could not update application status.",
            ) from exc