from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.job import Job
from app.models.user import User
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.job_repository = JobRepository(session)

    async def create_job(self, data: JobCreate, current_user: User) -> Job:
        try:
            job = await self.job_repository.create(
                data=data,
                owner_id=current_user.id,
            )
            await self.session.commit()
            return job
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise BadRequestException("Could not create job.") from exc

    async def get_job(self, job_id: int) -> Job:
        try:
            job = await self.job_repository.get_by_id(job_id)
            if not job:
                raise NotFoundException("Job not found.")
            return job
        except NotFoundException:
            raise
        except SQLAlchemyError as exc:
            raise BadRequestException("Could not get job.") from exc

    async def list_jobs(
        self,
        keyword: str | None,
        salary_min: int | None,
        salary_max: int | None,
        location: str | None,
        skip: int,
        limit: int,
    ) -> list[Job]:
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                raise BadRequestException(
                    "salary_min cannot be greater than salary_max.",
                )

        try:
            return await self.job_repository.list_jobs(
                keyword=keyword,
                salary_min=salary_min,
                salary_max=salary_max,
                location=location,
                skip=skip,
                limit=limit,
            )
        except SQLAlchemyError as exc:
            raise BadRequestException("Could not list jobs.") from exc

    async def update_job(
        self,
        job_id: int,
        data: JobUpdate,
        current_user: User,
    ) -> Job:
        try:
            job = await self.job_repository.get_by_id(job_id)
            if not job:
                raise NotFoundException("Job not found.")

            if job.owner_id != current_user.id and not current_user.is_superuser:
                raise ForbiddenException("You cannot update this job.")

            updated_job = await self.job_repository.update(job, data)
            await self.session.commit()
            return updated_job

        except (NotFoundException, ForbiddenException, BadRequestException):
            await self.session.rollback()
            raise
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise BadRequestException("Could not update job.") from exc

    async def delete_job(self, job_id: int, current_user: User) -> None:
        try:
            job = await self.job_repository.get_by_id(job_id)
            if not job:
                raise NotFoundException("Job not found.")

            if job.owner_id != current_user.id and not current_user.is_superuser:
                raise ForbiddenException("You cannot delete this job.")

            await self.job_repository.delete(job)
            await self.session.commit()

        except (NotFoundException, ForbiddenException):
            await self.session.rollback()
            raise
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise BadRequestException("Could not delete job.") from exc