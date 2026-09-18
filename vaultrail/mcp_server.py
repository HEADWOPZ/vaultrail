"""MCP stdio server. Tools operate on the local VAULTRAIL_ROOT vault only."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from mcp.server import MCPServer

from vaultrail import __version__
from vaultrail.errors import VaultError
from vaultrail.vault import Vault

log = logging.getLogger("vaultrail")

TOOL_NAMES = (
    "vault_search",
    "vault_read",
    "vault_append",
    "daily_note",
    "tag_query",
)

INSTRUCTIONS = (
    "VaultRail is a local Obsidian/markdown second-brain for CT/DeFi agent state. "
    "Tools read and write files under VAULTRAIL_ROOT only. There is no cloud sync, "
    "no wallet RPC, and no X posting. Distinct from SkillRail, LoopForge, and AlgoDesk."
)


def _vault() -> Vault:
    return Vault.from_env()


def _hits_payload(hits) -> list[dict[str, Any]]:
    return [hit.to_dict() for hit in hits]


def _err(exc: Exception) -> dict[str, Any]:
    return {"ok": False, "error": str(exc), "type": type(exc).__name__}


def create_server() -> MCPServer:
    """Build an MCPServer with the five vault tools."""
    mcp = MCPServer(
        name="VaultRail",
        title="VaultRail",
        description="Local Obsidian second-brain for CT/DeFi agent state",
        instructions=INSTRUCTIONS,
        version=__version__,
        website_url="https://github.com/HEADWOPZ/vaultrail",
    )

    @mcp.tool()
    def vault_search(
        query: str,
        folder: str = "",
        tag: str = "",
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search markdown notes in the local VaultRail vault (AND keywords).

        Args:
            query: Space-separated keywords. All tokens must match.
            folder: Optional folder under the vault (wallets, theses, ct-drafts,
                risk-journal, daily).
            tag: Optional tag without '#'. Matches frontmatter and inline tags.
            limit: Max hits, 1–50.
        """
        try:
            hits = _vault().search(
                query,
                folder=folder or None,
                tag=tag or None,
                limit=limit,
            )
            return {
                "ok": True,
                "query": query,
                "folder": folder or None,
                "tag": tag or None,
                "count": len(hits),
                "hits": _hits_payload(hits),
            }
        except VaultError as exc:
            return _err(exc)

    @mcp.tool()
    def vault_read(path: str) -> dict[str, Any]:
        """Read one markdown note. Path is relative to VAULTRAIL_ROOT.

        Args:
            path: Relative path such as theses/sol-restaking.md.
        """
        try:
            note = _vault().read(path)
            note["ok"] = True
            return note
        except VaultError as exc:
            return _err(exc)

    @mcp.tool()
    def vault_append(path: str, content: str, create: bool = True) -> dict[str, Any]:
        """Append text to a markdown note, optionally creating it.

        Args:
            path: Relative path such as risk-journal/2026-09-18-size.md.
            content: Markdown to append. A trailing newline is added if missing.
            create: Create the file (and parents) when it does not exist.
        """
        try:
            result = _vault().append(path, content, create=create)
            result["ok"] = True
            return result
        except VaultError as exc:
            return _err(exc)

    @mcp.tool()
    def daily_note(date: str = "", append: str = "") -> dict[str, Any]:
        """Open today's daily note (or a given YYYY-MM-DD), creating it if needed.

        Args:
            date: YYYY-MM-DD, or empty for today.
            append: Optional markdown block to append after open/create.
        """
        try:
            note = _vault().daily_note(date or None, append=append or None)
            note["ok"] = True
            return note
        except VaultError as exc:
            return _err(exc)

    @mcp.tool()
    def tag_query(tag: str, folder: str = "", limit: int = 50) -> dict[str, Any]:
        """List notes that carry a frontmatter or inline tag.

        Args:
            tag: Tag without '#', e.g. thesis, risk, phantombridge.
            folder: Optional folder under the vault.
            limit: Max hits, 1–50.
        """
        try:
            hits = _vault().tag_query(tag, folder=folder or None, limit=limit)
            return {
                "ok": True,
                "tag": tag.lstrip("#"),
                "folder": folder or None,
                "count": len(hits),
                "hits": _hits_payload(hits),
            }
        except VaultError as exc:
            return _err(exc)

    return mcp


def run_stdio() -> None:
    """Serve tools over MCP stdio. Logs go to stderr only."""
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="vaultrail: %(message)s")
    try:
        vault = _vault()
    except VaultError as exc:
        print(f"vaultrail: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    log.info("serving vault %s (local files only; no cloud sync)", vault.root)
    create_server().run(transport="stdio")


def dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)
