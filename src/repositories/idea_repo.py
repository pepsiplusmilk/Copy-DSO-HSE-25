import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.idea import Idea


class IdeaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, title: str, description: str, board_id: uuid.UUID):
        idea = Idea(title=title, description=description, board_id=board_id)

        self.session.add(idea)
        await self.session.flush()

        return idea

    async def get(self, idea_id: uuid.UUID):
        result = await self.session.execute(select(Idea).where(Idea.id == idea_id))

        return result.scalar_one_or_none()

    async def get_all_from_one_board(self, board_id: uuid.UUID):
        result = await self.session.execute(select(Idea).where(Idea.board_id == board_id))

        return result.scalars().all()

    async def update_title(self, idea_id: uuid.UUID, title: str):
        await self.session.execute(update(Idea).where(Idea.id == idea_id).values(title=title))

        await self.session.flush()
        return await self.get(idea_id)

    async def update_description(self, idea_id: uuid.UUID, description: str):
        await self.session.execute(
            update(Idea).where(Idea.id == idea_id).values(description=description)
        )

        await self.session.flush()
        return await self.get(idea_id)

    async def delete(self, idea_id: uuid.UUID):
        idea = await self.get(idea_id)

        if idea is None:
            return False

        # Hard del might rethink
        await self.session.delete(idea)
        return True
