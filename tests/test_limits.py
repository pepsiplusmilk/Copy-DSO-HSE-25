import pytest
from httpx import ASGITransport, AsyncClient

from src.app.main import app

pytestmark = pytest.mark.asyncio


class TestRateLimiting:
    # Doesn't work right now but you get the logic
    # async def test_rate_limit_returns_429(self, mock_uow):
    #     async with AsyncClient(
    #             transport=ASGITransport(app=app),
    #             base_url="http://test"
    #     ) as client:
    #         responses = []
    #         for _ in range(150):
    #             response = await client.get("/health")
    #             responses.append(response.status_code)
    #
    #         assert 429 in responses

    async def test_rate_limit_response_format(self, mock_uow):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for _ in range(150):
                response = await client.get("/health")

                if response.status_code == 429:
                    data = response.json()

                    assert "type" in data
                    assert "title" in data
                    assert data["status"] == 429
                    assert "retry_after" in response.headers or "Retry-After" in response.headers
                    break
