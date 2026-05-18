from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: JobCreate, owner_id: int) -> Job:
        try:
            job = Job(
                title=data.title,
                company_name=data.company_name,
                description=data.description,
                location=data.location,
                salary_min=data.salary_min,
                salary_max=data.salary_max,
                owner_id=owner_id,
            )
            self.session.add(job)
            await self.session.flush()
            await self.session.refresh(job)
            return job
        except SQLAlchemyError:
            raise

    async def get_by_id(self, job_id: int) -> Job | None:
        try:
            result = await self.session.execute(
                select(Job)
                .options(selectinload(Job.owner))
                .where(Job.id == job_id),
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    async def list_jobs(
        self,
        keyword: str | None,
        salary_min: int | None,
        salary_max: int | None,
        location: str | None,
        skip: int,
        limit: int,
    ) -> list[Job]:
        try:
            conditions = [Job.is_active.is_(True)]

            if keyword:
                search = f"%{keyword}%"
                conditions.append(
                    or_(
                        Job.title.ilike(search),
                        Job.company_name.ilike(search),
                        Job.description.ilike(search),
                    ),
                )

            if location:
                conditions.append(Job.location.ilike(f"%{location}%"))

            if salary_min is not None:
                conditions.append(
                    or_(
                        Job.salary_max.is_(None),
                        Job.salary_max >= salary_min,
                    ),
                )

            if salary_max is not None:
                conditions.append(
                    or_(
                        Job.salary_min.is_(None),
                        Job.salary_min <= salary_max,
                    ),
                )

            result = await self.session.execute(
                select(Job)
                .options(selectinload(Job.owner))
                .where(and_(*conditions))
                .order_by(Job.created_at.desc())
                .offset(skip)
                .limit(limit),
            )
            return list(result.scalars().all())
        except SQLAlchemyError:
            raise

    async def update(self, job: Job, data: JobUpdate) -> Job:
        try:
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(job, field, value)

            await self.session.flush()
            await self.session.refresh(job)
            return job
        except SQLAlchemyError:
            raise

    async def delete(self, job: Job) -> None:
        try:
            await self.session.delete(job)
            await self.session.flush()
        except SQLAlchemyError:
            raise