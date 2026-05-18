from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id),
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    async def get_by_email(self, email: str) -> User | None:
        try:
            result = await self.session.execute(
                select(User).where(User.email == email.lower()),
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    async def create(
        self,
        full_name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        try:
            user = User(
                full_name=full_name,
                email=email.lower(),
                hashed_password=hashed_password,
            )
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError:
            raise