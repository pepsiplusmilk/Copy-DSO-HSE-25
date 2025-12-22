import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str):
        user = User(name=name)

        self.session.add(user)
        await self.session.flush()

        return user

    async def get(self, user_id: uuid.UUID) -> User:
        result = await self.session.execute(select(User).where(User.id == user_id))

        return result.scalar_one_or_none()

    async def get_all(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def update_name(self, user_id: uuid.UUID, name: str):
        await self.session.execute(update(User).where(User.id == user_id).values(name=name))

        await self.session.flush()
        return await self.get(user_id)

    async def delete(self, user_id: uuid.UUID):
        user = await self.get(user_id)

        if user is None:
            return False

        await self.session.execute(update(User).where(User.id == user_id).values(is_deleted=True))

        await self.session.flush()
        return True
