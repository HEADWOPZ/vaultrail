"""Local-file vault operations used by both the CLI and the MCP server."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from vaultrail.config import resolve_root
from vaultrail.errors import VaultPathError
from vaultrail.frontmatter import extract_tags, note_title, split_frontmatter
from vaultrail.phantom import parse_link_note
from vaultrail.schema import SCHEMA_FOLDERS, ensure_schema
from vaultrail.search import SearchHit, search_files

MAX_NOTE_BYTES = 1_000_000
DAILY_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALLOWED_SUFFIXES = {".md", ".markdown"}


class Vault:
    """A markdown vault rooted at *root* (must stay on the local disk)."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()

    @classmethod
    def from_env(cls, explicit: str | Path | None = None) -> Vault:
        return cls(resolve_root(explicit))

    def init(self, *, overwrite_readmes: bool = False) -> list[str]:
        return ensure_schema(self.root, overwrite_readmes=overwrite_readmes)

    # ----- path safety -------------------------------------------------

    def resolve_note(self, rel: str, *, must_exist: bool = False) -> Path:
        if not rel or not str(rel).strip():
            raise VaultPathError("path is required and must be relative to the vault")
        raw = str(rel).strip().replace("\\", "/")
        if raw.startswith("/") or raw.startswith("~") or re.match(r"^[A-Za-z]:/", raw):
            raise VaultPathError("path must be relative to the vault root")
        if "\x00" in raw:
            raise VaultPathError("path contains a null byte")
        parts = [p for p in raw.split("/") if p and p != "."]
        if any(p == ".." for p in parts):
            raise VaultPathError("path must not contain '..'")
        if any(p in {".git", ".obsidian", ".trash"} for p in parts):
            raise VaultPathError("cannot read hidden vault internals")

        candidate = (self.root.joinpath(*parts)).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise VaultPathError("path escapes the vault root") from exc

        suffix = candidate.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise VaultPathError("only markdown notes (.md) are allowed")

        if must_exist and not candidate.is_file():
            raise VaultPathError(f"note not found: {self._rel(candidate)}")
        return candidate

    def _rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    # ----- read / append -----------------------------------------------

    def read(self, rel: str) -> dict[str, Any]:
        path = self.resolve_note(rel, must_exist=True)
        size = path.stat().st_size
        if size > MAX_NOTE_BYTES:
            raise VaultPathError(f"note exceeds {MAX_NOTE_BYTES} bytes")
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        tags = extract_tags(frontmatter, body)
        phantom = parse_link_note(frontmatter, body)
        return {
            "path": self._rel(path),
            "title": note_title(path.name, frontmatter, body),
            "tags": tags,
            "frontmatter": frontmatter,
            "body": body,
            "text": text,
            "phantombridge": phantom,
            "bytes": size,
        }

    def append(self, rel: str, content: str, *, create: bool = True) -> dict[str, Any]:
        if content is None or str(content) == "":
            raise VaultPathError("append content is empty")
        path = self.resolve_note(rel, must_exist=False)
        created = False
        if not path.exists():
            if not create:
                raise VaultPathError(f"note not found: {self._rel(path)}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
            created = True
        elif not path.is_file():
            raise VaultPathError("append target is not a file")

        existing = path.read_text(encoding="utf-8", errors="replace")
        chunk = str(content)
        if existing and not existing.endswith("\n"):
            existing += "\n"
        if not chunk.endswith("\n"):
            chunk += "\n"
        # Blank line between existing body and the new block.
        separator = "\n" if existing and not existing.endswith("\n\n") else ""
        path.write_text(existing + separator + chunk, encoding="utf-8")
        return {
            "path": self._rel(path),
            "created": created,
            "appended_chars": len(chunk),
            "bytes": path.stat().st_size,
        }

    # ----- search / tags -----------------------------------------------

    def search(
        self,
        query: str,
        *,
        folder: str | None = None,
        tag: str | None = None,
        limit: int = 10,
    ) -> list[SearchHit]:
        folder_clean = self._bounded_folder(folder)
        return search_files(
            self.root,
            query,
            folder=folder_clean,
            tag=tag,
            limit=limit,
        )

    def tag_query(
        self, tag: str, *, folder: str | None = None, limit: int = 50
    ) -> list[SearchHit]:
        if not tag or not tag.strip():
            raise VaultPathError("tag is required")
        return self.search("", folder=folder, tag=tag, limit=limit)

    def _bounded_folder(self, folder: str | None) -> str | None:
        if not folder:
            return None
        cleaned = folder.strip().replace("\\", "/").strip("/")
        if not cleaned:
            return None
        # Allow schema folders and any single relative directory under root.
        probe = self.root / cleaned
        try:
            probe.resolve().relative_to(self.root)
        except ValueError as exc:
            raise VaultPathError("folder escapes the vault root") from exc
        if ".." in Path(cleaned).parts:
            raise VaultPathError("folder must not contain '..'")
        return cleaned

    # ----- daily -------------------------------------------------------

    def daily_note(
        self,
        when: str | date | None = None,
        *,
        append: str | None = None,
    ) -> dict[str, Any]:
        day = _coerce_date(when)
        rel = f"daily/{day.isoformat()}.md"
        path = self.root / "daily" / f"{day.isoformat()}.md"
        created = False
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_daily_template(day), encoding="utf-8")
            created = True
        if append:
            self.append(rel, append, create=False)
        note = self.read(rel)
        note["created"] = created
        note["date"] = day.isoformat()
        return note

    def info(self) -> dict[str, Any]:
        folders = {
            name: (self.root / name).is_dir() for name in SCHEMA_FOLDERS
        }
        return {
            "root": str(self.root),
            "exists": self.root.is_dir(),
            "folders": folders,
            "privacy": "local-files-only",
            "cloud_sync": False,
        }


def _coerce_date(when: str | date | None) -> date:
    if when is None or when == "" or when == "today":
        return date.today()
    if isinstance(when, datetime):
        return when.date()
    if isinstance(when, date):
        return when
    text = str(when).strip()
    if not DAILY_NAME_RE.match(text):
        raise VaultPathError("date must be YYYY-MM-DD")
    return date.fromisoformat(text)


def _daily_template(day: date) -> str:
    return (
        f"---\n"
        f"type: daily\n"
        f"date: {day.isoformat()}\n"
        f"tags: [daily]\n"
        f"---\n\n"
        f"# {day.isoformat()}\n\n"
        f"## Watched\n\n-\n\n"
        f"## Theses touched\n\n-\n\n"
        f"## CT drafts\n\n-\n\n"
        f"## Risk journal\n\n-\n"
    )

