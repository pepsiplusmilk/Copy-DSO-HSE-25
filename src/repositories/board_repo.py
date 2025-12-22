import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.board_status import BoardStatus
from src.domain.models.board import Board


class BoardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, new_board: Board):
        self.session.add(new_board)

        await self.session.flush()
        return new_board

    async def get(self, board_id: uuid.UUID):
        result = await self.session.execute(select(Board).where(Board.id == board_id))

        return result.scalar_one_or_none()

    async def get_all(self):
        result = await self.session.execute(select(Board))
        return result.scalars().all()

    async def update_status(self, board_id: uuid.UUID, status: BoardStatus):
        await self.session.execute(update(Board).where(Board.id == board_id).values(status=status))

        await self.session.flush()
        return await self.get(board_id)
