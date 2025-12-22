import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.adapters.logger import logger
from src.board_status import BoardStatus
from src.domain.models.board import Board
from src.domain.models.vote import Vote
from src.domain.schemas.board import BoardCreate, BoardStatusUpdate
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus


class BoardMaintainService:
    async def create_board(self, uow: DBWorkUnit, data: BoardCreate):
        async with uow:
            board = Board(**data.model_dump())
            board = await uow.repositories[Board].create(board)

            logger.info(
                "Board created successfully",
                extra={"board_id": str(board.id), "title": board.title},
            )

            return board

    async def get_board(self, uow: DBWorkUnit, board_id: uuid.UUID):
        async with uow:
            board = await uow.repositories[Board].get(board_id)

            if board is None:
                raise NotFoundException(Board)

            return board

    async def get_board_list(self, uow: DBWorkUnit):
        async with uow:
            board_list = await uow.repositories[Board].get_all()
            return board_list

    async def change_board_status(
        self, uow: DBWorkUnit, board_id: uuid.UUID, data: BoardStatusUpdate
    ):
        async with uow:
            board = await self.get_board(uow, board_id)

            if board.status == BoardStatus.closed:
                raise InvalidBoardStatus(
                    current_state=board.status,
                    related_state=data.status.value,
                    board_id=board_id,
                    operation="changing status of board",
                )

            # Cleaning all votes before mark board as draft
            if data.status == BoardStatus.draft:
                board_votes = await uow.repositories[Vote].get_board_votes(board_id)
                await uow.repositories[Vote].vote_mass_delete(board_votes)

            logger.info(
                "Board status changed and linked votes erased",
                extra={
                    "board_id": str(board_id),
                    "old_status": board.status.value,
                    "new_status": data.status.value,
                },
            )

            return await uow.repositories[Board].update_status(board_id, **data.model_dump())
