"""VaultRail command line: init, search, serve, plus read/append/daily/tags."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from vaultrail import __owner__, __version__
from vaultrail.config import ENV_ROOT
from vaultrail.errors import VaultError
from vaultrail.schema import SCHEMA_FOLDERS
from vaultrail.vault import Vault


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except VaultError as exc:
        print(f"vaultrail: {exc}", file=sys.stderr)
        return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vaultrail",
        description=(
            "Local Obsidian/markdown second-brain for CT/DeFi agent state. "
            "No cloud sync. Distinct from SkillRail, LoopForge, and AlgoDesk."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"vaultrail {__version__} — {__owner__}",
    )
    parser.add_argument(
        "--root",
        default=None,
        help=f"Vault directory (else ${ENV_ROOT} or an initialized cwd)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable JSON on stdout",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create the opinionated vault folders")
    p_init.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Directory to initialize (default: --root / $VAULTRAIL_ROOT / cwd)",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite convention README files",
    )
    p_init.set_defaults(func=cmd_init)

    p_search = sub.add_parser("search", help="Search markdown notes (AND keywords)")
    p_search.add_argument("query", help="Space-separated keywords")
    p_search.add_argument("--folder", default=None, help="Limit to a vault folder")
    p_search.add_argument("--tag", default=None, help="Require this tag")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.set_defaults(func=cmd_search)

    p_read = sub.add_parser("read", help="Print one note")
    p_read.add_argument("path", help="Relative path, e.g. theses/sol-restaking.md")
    p_read.set_defaults(func=cmd_read)

    p_append = sub.add_parser("append", help="Append markdown to a note")
    p_append.add_argument("path", help="Relative path")
    p_append.add_argument("--content", required=True, help="Markdown to append")
    p_append.add_argument(
        "--no-create",
        action="store_true",
        help="Fail if the note does not exist",
    )
    p_append.set_defaults(func=cmd_append)

    p_daily = sub.add_parser("daily", help="Open or append today's daily note")
    p_daily.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")
    p_daily.add_argument("--append", default=None, help="Markdown to append")
    p_daily.set_defaults(func=cmd_daily)

    p_tags = sub.add_parser("tags", help="List notes that carry a tag")
    p_tags.add_argument("tag", help="Tag without #")
    p_tags.add_argument("--folder", default=None)
    p_tags.add_argument("--limit", type=int, default=50)
    p_tags.set_defaults(func=cmd_tags)

    p_info = sub.add_parser("info", help="Show resolved vault root and schema")
    p_info.set_defaults(func=cmd_info)

    p_serve = sub.add_parser("serve", help="Run the MCP server on stdio")
    p_serve.set_defaults(func=cmd_serve)

    return parser


def _vault(args: argparse.Namespace) -> Vault:
    explicit = getattr(args, "path", None) or args.root
    if args.command == "init":
        # init may target a brand-new directory; do not require a vault yet.
        from pathlib import Path

        from vaultrail.config import ENV_ROOT as _ENV
        import os

        if getattr(args, "path", None):
            return Vault(args.path)
        if args.root:
            return Vault(args.root)
        env = os.environ.get(_ENV, "").strip()
        if env:
            return Vault(env)
        return Vault(Path.cwd())
    return Vault.from_env(args.root)


def _emit(args: argparse.Namespace, payload: Any, text: str) -> int:
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(text)
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    vault = _vault(args)
    created = vault.init(overwrite_readmes=args.force)
    payload = {
        "root": str(vault.root),
        "created": created,
        "folders": list(SCHEMA_FOLDERS),
        "cloud_sync": False,
    }
    lines = [
        f"Initialized VaultRail vault at {vault.root}",
        "Folders: " + ", ".join(SCHEMA_FOLDERS),
        "Local files only — no cloud sync.",
    ]
    if created:
        lines.append("Wrote: " + ", ".join(created))
    else:
        lines.append("Schema already present.")
    return _emit(args, payload, "\n".join(lines))


def cmd_search(args: argparse.Namespace) -> int:
    hits = _vault(args).search(
        args.query, folder=args.folder, tag=args.tag, limit=args.limit
    )
    payload = {"count": len(hits), "hits": [h.to_dict() for h in hits]}
    if not hits:
        text = "No matches."
    else:
        blocks = []
        for hit in hits:
            tag_s = f"  [{', '.join(hit.tags)}]" if hit.tags else ""
            snippet = f"\n  {hit.snippet}" if hit.snippet else ""
            blocks.append(f"{hit.path}  {hit.title}{tag_s}  score={hit.score}{snippet}")
        text = "\n".join(blocks)
    return _emit(args, payload, text)


def cmd_read(args: argparse.Namespace) -> int:
    note = _vault(args).read(args.path)
    return _emit(args, note, note["text"].rstrip() + "\n")


def cmd_append(args: argparse.Namespace) -> int:
    result = _vault(args).append(
        args.path, args.content, create=not args.no_create
    )
    text = f"Appended to {result['path']} ({result['appended_chars']} chars)"
    if result["created"]:
        text += " [created]"
    return _emit(args, result, text)


def cmd_daily(args: argparse.Namespace) -> int:
    note = _vault(args).daily_note(args.date, append=args.append)
    flag = "created" if note.get("created") else "opened"
    header = f"{note['path']} ({flag})"
    return _emit(args, note, header + "\n\n" + note["text"].rstrip() + "\n")


def cmd_tags(args: argparse.Namespace) -> int:
    hits = _vault(args).tag_query(args.tag, folder=args.folder, limit=args.limit)
    payload = {
        "tag": args.tag.lstrip("#"),
        "count": len(hits),
        "hits": [h.to_dict() for h in hits],
    }
    if not hits:
        text = f"No notes tagged #{args.tag.lstrip('#')}."
    else:
        text = "\n".join(f"{h.path}  {h.title}  [{', '.join(h.tags)}]" for h in hits)
    return _emit(args, payload, text)


def cmd_info(args: argparse.Namespace) -> int:
    info = _vault(args).info()
    folders = ", ".join(
        f"{name}{'✓' if ok else '✗'}" for name, ok in info["folders"].items()
    )
    text = (
        f"root: {info['root']}\n"
        f"folders: {folders}\n"
        f"privacy: local files only (cloud_sync={info['cloud_sync']})"
    )
    return _emit(args, info, text)


def cmd_serve(args: argparse.Namespace) -> int:
    if args.root:
        import os

        os.environ[ENV_ROOT] = str(Vault(args.root).root)
    from vaultrail.mcp_server import run_stdio

    run_stdio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
