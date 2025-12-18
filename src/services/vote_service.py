import uuid

from src.adapters.db_work_unit import DBWorkUnit
from src.board_status import BoardStatus
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus
from src.exceptions.vote import AlreadyVoted
from src.models.board import Board
from src.models.idea import Idea
from src.models.user import User
from src.models.vote import Vote
from src.schemas.vote import VoteCreate


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

            return await uow.repositories[Vote].create(idea_id, user_id)

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

            await uow.repositories[Vote].delete(vote_id)
