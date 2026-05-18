from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.job import JobCreate, JobDetail, JobRead, JobUpdate
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> JobRead:
    service = JobService(session)
    return await service.create_job(data, current_user)


@router.get("/", response_model=list[JobRead])
async def list_jobs(
    session: DbSession,
    keyword: str | None = Query(default=None, min_length=1),
    salary_min: int | None = Query(default=None, ge=0),
    salary_max: int | None = Query(default=None, ge=0),
    location: str | None = Query(default=None, min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[JobRead]:
    service = JobService(session)
    return await service.list_jobs(
        keyword=keyword,
        salary_min=salary_min,
        salary_max=salary_max,
        location=location,
        skip=skip,
        limit=limit,
    )


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: int,
    session: DbSession,
) -> JobDetail:
    service = JobService(session)
    return await service.get_job(job_id)


@router.patch("/{job_id}", response_model=JobRead)
async def update_job(
    job_id: int,
    data: JobUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> JobRead:
    service = JobService(session)
    return await service.update_job(job_id, data, current_user)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    service = JobService(session)
    await service.delete_job(job_id, current_user)