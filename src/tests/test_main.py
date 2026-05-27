import os

os.environ.setdefault("MEMORY_ID", "test-memory-id")

from unittest.mock import MagicMock, patch

from httpx import ASGITransport, AsyncClient

from app.main import app, invoke


def _make_ctx(session_id="sess-1"):
    ctx = MagicMock()
    ctx.session_id = session_id
    return ctx


def test_invoke_calls_agent():
    with (
        patch("app.main.AgentCoreMemorySessionManager"),
        patch("app.main.Agent") as MockAgent,
    ):
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(__str__=lambda self: "42")
        MockAgent.return_value = mock_instance
        result = invoke({"prompt": "What is 6x7?"}, _make_ctx())
    assert result == {"response": "42"}
    mock_instance.assert_called_once_with("What is 6x7?")


def test_invoke_empty_prompt():
    with (
        patch("app.main.AgentCoreMemorySessionManager"),
        patch("app.main.Agent") as MockAgent,
    ):
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(__str__=lambda self: "ok")
        MockAgent.return_value = mock_instance
        invoke({}, _make_ctx())
    mock_instance.assert_called_once_with("")


async def test_ping():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/ping")
    assert resp.status_code == 200
