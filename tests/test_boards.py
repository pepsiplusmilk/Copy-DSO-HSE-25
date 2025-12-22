import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.board_status import BoardStatus
from src.domain import constants
from src.domain.models.board import Board
from src.domain.models.vote import Vote
from src.domain.schemas.board import BoardCreate, BoardStatusUpdate
from src.exceptions.base import NotFoundException
from src.exceptions.board import InvalidBoardStatus
from src.services.board_service import BoardMaintainService

pytestmark = pytest.mark.unit


class TestBoardsService:
    @pytest.fixture
    def board_service(self):
        return BoardMaintainService()

    @pytest.fixture
    def sample_board(self):
        return Board(id=uuid.uuid4(), title="Test Board", status=BoardStatus.draft)

    @pytest.mark.asyncio
    async def test_board_created_successfully(self, board_service, mock_uow, sample_board):
        mock_uow.repositories[Board].create.return_value = sample_board

        data = BoardCreate(title="Test Board")
        result = await board_service.create_board(mock_uow, data)

        assert result.title == "Test Board"
        assert result.status == BoardStatus.draft
        mock_uow.repositories[Board].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_board_retrieved_by_id(self, board_service, mock_uow, sample_board):
        board_id = sample_board.id
        mock_uow.repositories[Board].get.return_value = sample_board

        result = await board_service.get_board(mock_uow, board_id)

        assert result.id == board_id
        mock_uow.repositories[Board].get.assert_called_once_with(board_id)

    @pytest.mark.asyncio
    async def test_board_not_found_raises_exception(self, board_service, mock_uow):
        board_id = uuid.uuid4()
        mock_uow.repositories[Board].get.return_value = None

        with pytest.raises(NotFoundException):
            await board_service.get_board(mock_uow, board_id)

    @pytest.mark.asyncio
    async def test_published_from_draft_board(self, board_service, mock_uow, sample_board):
        board_id = sample_board.id
        updated_board = Board(id=board_id, title=sample_board.title, status=BoardStatus.published)

        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Board].update_status.return_value = updated_board

        data = BoardStatusUpdate(status=BoardStatus.published)
        result = await board_service.change_board_status(mock_uow, board_id, data)

        assert result.status == BoardStatus.published

    @pytest.mark.asyncio
    async def test_closed_board_cannot_be_reopened(self, board_service, mock_uow, sample_board):
        sample_board.status = BoardStatus.closed
        board_id = sample_board.id

        mock_uow.repositories[Board].get.return_value = sample_board

        data = BoardStatusUpdate(status=BoardStatus.published)

        with pytest.raises(InvalidBoardStatus) as exc_info:
            await board_service.change_board_status(mock_uow, board_id, data)

        assert exc_info.value.current_state == BoardStatus.closed

    @pytest.mark.asyncio
    async def test_changing_to_draft_removes_all_votes(self, board_service, mock_uow, sample_board):
        sample_board.status = BoardStatus.published
        board_id = sample_board.id

        vote_ids = [uuid.uuid4(), uuid.uuid4()]

        mock_uow.repositories[Board].get.return_value = sample_board
        mock_uow.repositories[Vote].get_board_votes.return_value = vote_ids
        mock_uow.repositories[Board].update_status.return_value = sample_board

        data = BoardStatusUpdate(status=BoardStatus.draft)
        await board_service.change_board_status(mock_uow, board_id, data)

        mock_uow.repositories[Vote].vote_mass_delete.assert_called_once_with(vote_ids)


from src.app.main import app


class TestBoardValidation:
    @pytest.mark.asyncio
    async def test_board_empty_title_rejected(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/boards/", json={"title": ""})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["status"] == 422

    @pytest.mark.asyncio
    async def test_board_title_too_long_rejected(self, mock_uow):
        """Слишком длинный заголовок доски должен быть отклонён"""
        long_title = "A" * (constants.BOARD_TITLE_MAX_LENGTH + 1)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/boards/", json={"title": long_title})

        assert response.status_code == 422
        data = response.json()
        assert "validation" in data["type"].lower() or "errors" in data
