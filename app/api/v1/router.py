from fastapi import APIRouter

from app.api.v1.endpoints import applications, auth, jobs, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(jobs.router)
api_router.include_router(applications.router)