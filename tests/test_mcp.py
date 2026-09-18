from __future__ import annotations

import json
from pathlib import Path

import pytest

from vaultrail.mcp_server import TOOL_NAMES, create_server


@pytest.fixture
def server(tmp_vault: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VAULTRAIL_ROOT", str(tmp_vault))
    return create_server()


def _text(result) -> str:
    if getattr(result, "is_error", False):
        raise AssertionError(f"tool error: {result}")
    if result.content:
        return result.content[0].text
    return ""


def _payload(result) -> dict:
    raw = _text(result)
    data = json.loads(raw)
    assert data.get("ok") is True, data
    return data


@pytest.mark.asyncio
async def test_lists_required_tools(server) -> None:
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert set(TOOL_NAMES) <= names


@pytest.mark.asyncio
async def test_vault_search_and_read(server) -> None:
    found = _payload(await server.call_tool("vault_search", {"query": "restaking"}))
    assert found["count"] >= 1
    assert any(h["path"].endswith("sol-restaking.md") for h in found["hits"])

    note = _payload(
        await server.call_tool("vault_read", {"path": "theses/sol-restaking.md"})
    )
    assert "Stay small" in note["body"]


@pytest.mark.asyncio
async def test_vault_append_daily_and_tags(server) -> None:
    appended = _payload(
        await server.call_tool(
            "vault_append",
            {
                "path": "risk-journal/mcp-note.md",
                "content": "- mcp append",
                "create": True,
            },
        )
    )
    assert appended["created"] is True

    daily = _payload(
        await server.call_tool(
            "daily_note",
            {"date": "2026-09-18", "append": "- from mcp"},
        )
    )
    assert daily["path"] == "daily/2026-09-18.md"
    assert "from mcp" in daily["text"]

    tags = _payload(await server.call_tool("tag_query", {"tag": "phantombridge"}))
    assert tags["count"] >= 1


@pytest.mark.asyncio
async def test_vault_read_rejects_escape(server) -> None:
    result = await server.call_tool("vault_read", {"path": "../README.md"})
    data = json.loads(_text(result))
    assert data["ok"] is False
    assert "path" in data["error"].lower() or "relative" in data["error"].lower()
