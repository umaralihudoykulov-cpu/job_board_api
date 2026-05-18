from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDetail,
    ApplicationRead,
    ApplicationUpdateStatus,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post(
    "/",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_job(
    data: ApplicationCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> ApplicationRead:
    service = ApplicationService(session)
    return await service.apply_to_job(data, current_user)


@router.get("/me", response_model=list[ApplicationDetail])
async def list_my_applications(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ApplicationDetail]:
    service = ApplicationService(session)
    return await service.list_my_applications(
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get("/jobs/{job_id}", response_model=list[ApplicationDetail])
async def list_job_applications(
    job_id: int,
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ApplicationDetail]:
    service = ApplicationService(session)
    return await service.list_job_applications(
        job_id=job_id,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.patch("/{application_id}/status", response_model=ApplicationDetail)
async def update_application_status(
    application_id: int,
    data: ApplicationUpdateStatus,
    session: DbSession,
    current_user: CurrentUser,
) -> ApplicationDetail:
    service = ApplicationService(session)
    return await service.update_application_status(
        application_id=application_id,
        data=data,
        current_user=current_user,
    )