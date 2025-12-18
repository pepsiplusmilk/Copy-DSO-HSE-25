import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.board_status import BoardStatus
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus
from src.models.board import Board
from src.models.vote import Vote
from src.schemas.board import BoardCreate, BoardStatusUpdate


class BoardMaintainService:
    async def create_board(self, uow: DBWorkUnit, data: BoardCreate):
        async with uow:
            board = Board(**data.model_dump())
            board = await uow.repositories[Board].create(board)

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
                    related_state=BoardStatus.closed,
                    board_id=board_id,
                    operation="changing status of board",
                )

            # Cleaning all votes before mark board as draft
            if data.status == BoardStatus.draft:
                board_votes = await uow.repositories[Vote].get_board_votes(board_id)
                await uow.repositories[Vote].vote_mass_delete(board_votes)

            return await uow.repositories[Board].update_status(board_id, **data.model_dump())
