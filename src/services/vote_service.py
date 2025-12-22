import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.adapters.logger import logger
from src.board_status import BoardStatus
from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.models.user import User
from src.domain.models.vote import Vote
from src.domain.schemas.vote import VoteCreate
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus
from src.exceptions.vote import AlreadyVoted


class VoteMaintainService:
    async def create_vote(self, uow: DBWorkUnit, data: VoteCreate):
        async with uow:
            idea_id, user_id = data.model_dump().values()

            if await uow.repositories[User].get(user_id) is None:
                raise NotFoundException(User)

            idea = await uow.repositories[Idea].get(idea_id)
            if idea is None:
                raise NotFoundException(Idea)

            board = await uow.repositories[Board].get(idea.board_id)

            if board.status != BoardStatus.published:
                raise InvalidBoardStatus(
                    current_state=board.status,
                    related_state=BoardStatus.published,
                    board_id=board.id,
                    operation="voting",
                )

            if await uow.repositories[Vote].is_voted_already(user_id, board.id):
                raise AlreadyVoted(
                    user_id=user_id,
                    board_id=board.id,
                )

            new_vote = await uow.repositories[Vote].create(idea_id, user_id)

            logger.info(
                "User successfully voted for idea",
                extra={"vote_id": str(new_vote.id), "board_id": str(board.id)},
            )

            return new_vote

    async def delete_vote(self, uow: DBWorkUnit, vote_id: uuid.UUID):
        async with uow:
            vote = await uow.repositories[Vote].get(vote_id)
            if vote is None:
                raise NotFoundException(Vote)

            idea = await uow.repositories[Idea].get(vote.idea_id)
            board = await uow.repositories[Board].get(idea.board_id)

            if board.status != BoardStatus.published:
                raise InvalidBoardStatus(
                    current_state=board.status,
                    related_state=BoardStatus.published,
                    board_id=board.id,
                    operation="vote canceling",
                )

            logger.info(
                "Vote successfully canceled",
                extra={"vote_id": str(vote_id), "board_id": str(board.id)},
            )

            await uow.repositories[Vote].delete(vote_id)
