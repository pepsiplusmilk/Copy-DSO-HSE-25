import uuid

import pytest

from src.board_status import BoardStatus
from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.models.user import User
from src.domain.models.vote import Vote
from src.domain.schemas.vote import VoteCreate
from src.exceptions.board import InvalidBoardStatus
from src.exceptions.vote import AlreadyVoted
from src.services.vote_service import VoteMaintainService

pytestmark = pytest.mark.unit


class TestVoteService:
    @pytest.fixture
    def vote_service(self):
        return VoteMaintainService()

    @pytest.fixture
    def sample_user(self):
        return User(id=uuid.uuid4(), name="Test User", is_deleted=False)

    @pytest.fixture
    def sample_board(self):
        return Board(id=uuid.uuid4(), title="Test Board", status=BoardStatus.published)

    @pytest.fixture
    def sample_idea(self, sample_board):
        return Idea(
            id=uuid.uuid4(), title="Test Idea", description="Test", board_id=sample_board.id
        )

    @pytest.mark.asyncio
    async def test_vote_created_for_published_board(
        self, vote_service, mock_uow, sample_user, sample_idea, sample_board
    ):
        vote = Vote(id=uuid.uuid4(), idea_id=sample_idea.id, user_id=sample_user.id)

        mock_uow.repositories[User].get.return_value = sample_user
        mock_uow.repositories[Idea].get.return_value = sample_idea
        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Vote].is_voted_already.return_value = False
        mock_uow.repositories[Vote].create.return_value = vote

        data = VoteCreate(idea_id=sample_idea.id, user_id=sample_user.id)
        result = await vote_service.create_vote(mock_uow, data)

        assert result.idea_id == sample_idea.id

    @pytest.mark.asyncio
    async def test_cannot_vote_twice_on_same_board(
        self, vote_service, mock_uow, sample_user, sample_idea, sample_board
    ):
        mock_uow.repositories[User].get.return_value = sample_user
        mock_uow.repositories[Idea].get.return_value = sample_idea
        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Vote].is_voted_already.return_value = True

        data = VoteCreate(idea_id=sample_idea.id, user_id=sample_user.id)

        with pytest.raises(AlreadyVoted):
            await vote_service.create_vote(mock_uow, data)

    @pytest.mark.asyncio
    async def test_cannot_vote_on_draft_board(
        self, vote_service, mock_uow, sample_user, sample_idea, sample_board
    ):
        sample_board.status = BoardStatus.draft

        mock_uow.repositories[User].get.return_value = sample_user
        mock_uow.repositories[Idea].get.return_value = sample_idea
        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Vote].is_voted_already.return_value = False

        data = VoteCreate(idea_id=sample_idea.id, user_id=sample_user.id)

        with pytest.raises(InvalidBoardStatus):
            await vote_service.create_vote(mock_uow, data)
