import pytest
from httpx import ASGITransport, AsyncClient

from src.app.main import app

pytestmark = pytest.mark.asyncio


class TestSecurityHeadersConfiguration:
    async def test_x_frame_options_present(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

    async def test_x_content_type_options_present(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"

    async def test_x_xss_protection_present(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"

    async def test_referrer_policy_present(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

    async def test_security_headers_on_api_endpoints(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/boards")

        assert "x-frame-options" in response.headers
        assert "x-content-type-options" in response.headers


class TestSecurityHeadersNegative:
    async def test_no_x_powered_by_header(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert "x-powered-by" not in response.headers
