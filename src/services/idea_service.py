import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.adapters.logger import logger
from src.board_status import BoardStatus
from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.schemas.idea import IdeaCreate, IdeaUpdateDescription, IdeaUpdateTitle
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus


class IdeaMaintainService:
    async def create_idea(self, uow: DBWorkUnit, data: IdeaCreate):
        async with uow:
            board = await uow.repositories[Board].get(data.board_id)

            if board is None:
                raise NotFoundException(Board)

            await self._check_board_compatibility(uow, board.id)

            new_idea = await uow.repositories[Idea].create(**data.model_dump())

            logger.info(
                "New idea was successfully created",
                extra={"board_id": str(board.id), "idea_id": str(new_idea.id)},
            )

            return new_idea

    async def get_idea(self, uow: DBWorkUnit, idea_id: uuid.UUID):
        async with uow:
            result = await uow.repositories[Idea].get(idea_id)

            if result is None:
                raise NotFoundException(Idea)

            return result

    async def get_all_board_ideas(self, uow: DBWorkUnit, board_id: uuid.UUID):
        async with uow:
            if await uow.repositories[Board].get(board_id) is None:
                raise NotFoundException(Board)

            return await uow.repositories[Idea].get_all_from_one_board(board_id)

    async def _check_board_compatibility(self, uow: DBWorkUnit, board_id: uuid.UUID):
        async with uow:
            idea_board = await uow.repositories[Board].get(board_id)

            if idea_board.status != BoardStatus.draft:
                raise InvalidBoardStatus(
                    current_state=idea_board.status,
                    related_state=BoardStatus.draft,
                    board_id=board_id,
                )

    async def change_title(self, uow: DBWorkUnit, idea_id: uuid.UUID, data: IdeaUpdateTitle):
        async with uow:
            idea = await self.get_idea(uow, idea_id)
            await self._check_board_compatibility(uow, idea.board_id)

            logger.info(
                "Idea title changed successfully",
                extra={"idea_id": str(idea_id), "old_title": idea.title, "new_title": data.title},
            )

            return await uow.repositories[Idea].update_title(idea_id, **data.model_dump())

    async def change_description(
        self, uow: DBWorkUnit, idea_id: uuid.UUID, data: IdeaUpdateDescription
    ):
        async with uow:
            idea = await self.get_idea(uow, idea_id)
            await self._check_board_compatibility(uow, idea.board_id)

            logger.info(
                "Idea description changed successfully",
                extra={
                    "idea_id": str(idea_id),
                    "old_desc": idea.description,
                    "new_desc": data.description,
                },
            )

            return await uow.repositories[Idea].update_description(idea_id, **data.model_dump())

    async def delete_idea(self, uow: DBWorkUnit, idea_id: uuid.UUID):
        async with uow:
            idea = await self.get_idea(uow, idea_id)
            await self._check_board_compatibility(uow, idea.board_id)

            logger.info(
                "Idea deleted successfully",
                extra={"idea_id": str(idea_id), "board_id": str(idea.board_id)},
            )

            await uow.repositories[Idea].delete(idea_id)
