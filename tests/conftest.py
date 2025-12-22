import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.adapters.db_work_unit import DBWorkUnit
from src.app.di_frame import get_uow
from src.app.main import app
from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.models.user import User
from src.domain.models.vote import Vote
from src.repositories.board_repo import BoardRepository
from src.repositories.idea_repo import IdeaRepository
from src.repositories.user_repo import UserRepository
from src.repositories.vote_repo import VoteRepository

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def mock_board_repo():
    return AsyncMock(spec=BoardRepository)


@pytest.fixture
def mock_idea_repo():
    return AsyncMock(spec=IdeaRepository)


@pytest.fixture
def mock_user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_vote_repo():
    return AsyncMock(spec=VoteRepository)


@pytest.fixture
def mock_uow(mock_board_repo, mock_idea_repo, mock_user_repo, mock_vote_repo):
    uow = AsyncMock(spec=DBWorkUnit)
    uow.repositories = {
        Board: mock_board_repo,
        Idea: mock_idea_repo,
        User: mock_user_repo,
        Vote: mock_vote_repo,
    }
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture(autouse=True)
def override_dependency(mock_uow):
    async def __get_uow():
        return mock_uow

    app.dependency_overrides[get_uow] = __get_uow
    yield mock_uow

    app.dependency_overrides.clear()
