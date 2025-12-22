from typing import AsyncGenerator

from src.adapters.db_work_unit import DBWorkUnit
from src.app.storage_setup import async_session_factory
from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.models.user import User
from src.domain.models.vote import Vote
from src.repositories.board_repo import BoardRepository
from src.repositories.idea_repo import IdeaRepository
from src.repositories.user_repo import UserRepository
from src.repositories.vote_repo import VoteRepository


def create_uow() -> DBWorkUnit:
    uow = DBWorkUnit.create_with_repositories(
        async_session_factory,
        {
            Board: BoardRepository,
            Idea: IdeaRepository,
            User: UserRepository,
            Vote: VoteRepository,
        },
    )
    return uow


async def get_uow() -> AsyncGenerator[DBWorkUnit, None]:
    uow = create_uow()
    async with uow:
        yield uow
