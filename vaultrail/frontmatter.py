"""Tiny YAML-subset frontmatter + tag helpers. No PyYAML dependency."""

from __future__ import annotations

import re
from typing import Any

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
# Inline tags: #solana, #ct/draft — skip hex colors and issue refs like #12.
INLINE_TAG_RE = re.compile(r"(?<![\w/#])#([A-Za-z][\w/-]{0,62})\b")
LIST_RE = re.compile(r"^\[(.*)\]$")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter dict, body). Missing frontmatter → ({}, text)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    return _parse_simple_yaml(match.group(1)), text[match.end() :]


def _parse_simple_yaml(block: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        data[key] = _coerce(value)
    return data


def _coerce(value: str) -> Any:
    if value == "":
        return ""
    if value.lower() in {"true", "yes"}:
        return True
    if value.lower() in {"false", "no"}:
        return False
    listed = LIST_RE.match(value)
    if listed:
        inner = listed.group(1).strip()
        if not inner:
            return []
        return [_unquote(part.strip()) for part in inner.split(",") if part.strip()]
    return _unquote(value)


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def extract_tags(frontmatter: dict[str, Any], body: str) -> list[str]:
    """Union of frontmatter ``tags`` and inline ``#tags``, de-duped, lowercased."""
    found: list[str] = []
    seen: set[str] = set()

    raw = frontmatter.get("tags", [])
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip()]
    elif isinstance(raw, list):
        parts = [str(p).strip() for p in raw if str(p).strip()]
    else:
        parts = []

    for part in parts:
        _add_tag(found, seen, part)

    for match in INLINE_TAG_RE.finditer(body):
        _add_tag(found, seen, match.group(1))

    return found


def _add_tag(found: list[str], seen: set[str], tag: str) -> None:
    cleaned = tag.lstrip("#").strip().lower()
    if cleaned and cleaned not in seen:
        seen.add(cleaned)
        found.append(cleaned)


def note_title(path_name: str, frontmatter: dict[str, Any], body: str) -> str:
    """Prefer frontmatter title, then first ATX heading, then filename stem."""
    title = frontmatter.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return path_name.removesuffix(".md").removesuffix(".markdown")
