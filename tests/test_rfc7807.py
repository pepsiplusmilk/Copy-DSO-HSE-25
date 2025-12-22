from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from src.app.main import app
from src.domain.models.user import User

pytestmark = pytest.mark.asyncio


class TestRFC7807Format:
    async def test_error_contains_required_fields(self, mock_uow):
        mock_uow.repositories[User].get.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/users/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404
        data = response.json()

        assert "type" in data
        assert "title" in data
        assert "status" in data
        assert "detail" in data
        assert "correlation_id" in data

    async def test_error_correlation_id_is_valid_uuid(self, mock_uow):
        mock_uow.repositories[User].get.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/users/00000000-0000-0000-0000-000000000000")

        data = response.json()
        UUID(data["correlation_id"])  # пытаемся скастовать -- смотрим есть ошибка или нет

    async def test_error_status_matches_http_code(self, mock_uow):
        mock_uow.repositories[User].get.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/users/00000000-0000-0000-0000-000000000000")

        data = response.json()
        assert data["status"] == response.status_code

    async def test_error_content_type_is_problem_json(self, mock_uow):
        mock_uow.repositories[User].get.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/users/00000000-0000-0000-0000-000000000000")

        assert "application/problem+json" in response.headers.get("content-type", "")
