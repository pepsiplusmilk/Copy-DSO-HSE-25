import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.board_status import BoardStatus
from src.domain import constants
from src.domain.models.board import Board
from src.domain.models.idea import Idea
from src.domain.schemas.idea import IdeaCreate, IdeaUpdateTitle
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus
from src.services.idea_service import IdeaMaintainService

pytestmark = pytest.mark.unit


class TestIdeasService:
    @pytest.fixture
    def idea_service(self):
        return IdeaMaintainService()

    @pytest.fixture
    def sample_board(self):
        return Board(id=uuid.uuid4(), title="Test Board", status=BoardStatus.draft)

    @pytest.fixture
    def sample_idea(self, sample_board):
        return Idea(
            id=uuid.uuid4(),
            title="Test Idea",
            description="Test Description",
            board_id=sample_board.id,
        )

    @pytest.mark.asyncio
    async def test_idea_created_for_existing_board(
        self, idea_service, mock_uow, sample_board, sample_idea
    ):
        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Idea].create.return_value = sample_idea

        data = IdeaCreate(
            title="Test Idea", description="Test Description", board_id=sample_board.id
        )
        result = await idea_service.create_idea(mock_uow, data)

        assert result.title == "Test Idea"
        assert result.board_id == sample_board.id

    @pytest.mark.asyncio
    async def test_creating_idea_for_nonexistent_board_failed(self, idea_service, mock_uow):
        board_id = uuid.uuid4()
        mock_uow.repositories[Board].get.return_value = None

        data = IdeaCreate(title="Test Idea", description="Test", board_id=board_id)

        with pytest.raises(NotFoundException):
            await idea_service.create_idea(mock_uow, data)

    @pytest.mark.asyncio
    async def test_idea_title_updated_when_board_is_draft(
        self, idea_service, mock_uow, sample_board, sample_idea
    ):
        updated_idea = Idea(
            id=sample_idea.id,
            title="New Title",
            description=sample_idea.description,
            board_id=sample_board.id,
        )

        mock_uow.repositories[Idea].get.return_value = sample_idea
        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Idea].update_title.return_value = updated_idea

        data = IdeaUpdateTitle(title="New Title")
        result = await idea_service.change_title(mock_uow, sample_idea.id, data)

        assert result.title == "New Title"

    @pytest.mark.asyncio
    async def test_cannot_update_idea_when_board_published(
        self, idea_service, mock_uow, sample_board, sample_idea
    ):
        sample_board.status = BoardStatus.published

        mock_uow.repositories[Idea].get.return_value = sample_idea
        mock_uow.repositories[Board].get.return_value = sample_board

        data = IdeaUpdateTitle(title="New Title")

        with pytest.raises(InvalidBoardStatus):
            await idea_service.change_title(mock_uow, sample_idea.id, data)


from src.app.main import app


class TestIdeaValidation:
    async def test_idea_title_too_long_rejected(self, mock_uow):
        long_title = "A" * (constants.IDEA_TITLE_MAX_LENGTH + 1)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/ideas/",
                json={
                    "title": long_title,
                    "description": "Test",
                    "board_id": "00000000-0000-0000-0000-000000000000",
                },
            )

        assert response.status_code == 422

    async def test_idea_description_too_long_rejected(self, mock_uow):
        long_desc = "A" * (constants.IDEA_DESC_MAX_LENGTH + 1)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/ideas/",
                json={
                    "title": "Test",
                    "description": long_desc,
                    "board_id": "00000000-0000-0000-0000-000000000000",
                },
            )

        assert response.status_code == 422

    async def test_sql_injection_in_title_rejected(self, mock_uow):
        sql_injection = "'; DROP TABLE ideas; --"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/ideas/",
                json={
                    "title": sql_injection,
                    "description": "Test",
                    "board_id": "00000000-0000-0000-0000-000000000000",
                },
            )

        assert response.status_code in [422, 409, 404, 400]
