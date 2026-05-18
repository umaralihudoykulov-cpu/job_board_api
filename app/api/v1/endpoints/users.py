from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserMe

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMe)
async def get_me(current_user: CurrentUser) -> UserMe:
    return current_user