"""Local markdown search. AND tokens, title/tag/path boosts, snippet windows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from vaultrail.frontmatter import extract_tags, note_title, split_frontmatter

SKIP_DIR_NAMES = {".git", ".obsidian", ".trash", "__pycache__", ".smart-env"}
SNIPPET_RADIUS = 90


@dataclass(frozen=True)
class SearchHit:
    path: str
    title: str
    score: float
    snippet: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def tokenize_query(query: str) -> list[str]:
    return [part.lower() for part in query.split() if part.strip()]


def iter_markdown(root: Path, folder: str | None = None) -> list[Path]:
    base = root if not folder else (root / folder)
    if not base.exists():
        return []
    files: list[Path] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return files


def score_note(
    tokens: list[str],
    rel: str,
    title: str,
    tags: list[str],
    body: str,
) -> float:
    if not tokens:
        return 0.0
    rel_l = rel.lower()
    title_l = title.lower()
    body_l = body.lower()
    tag_l = {t.lower() for t in tags}
    score = 0.0
    for token in tokens:
        bare = token.lstrip("#")
        if bare in tag_l or token in tag_l:
            score += 3.0
        if bare in title_l:
            score += 5.0
        if bare in rel_l:
            score += 2.0
        if bare in body_l:
            score += 1.0
    phrase = " ".join(tokens)
    if len(tokens) > 1 and phrase in body_l:
        score += 2.0
    if len(tokens) > 1 and phrase in title_l:
        score += 3.0
    return score


def make_snippet(body: str, tokens: list[str], radius: int = SNIPPET_RADIUS) -> str:
    collapsed = " ".join(body.split())
    if not collapsed:
        return ""
    lower = collapsed.lower()
    idx = -1
    for token in tokens:
        idx = lower.find(token.lstrip("#"))
        if idx != -1:
            break
    if idx == -1:
        snippet = collapsed[: radius * 2]
        return snippet + ("…" if len(collapsed) > len(snippet) else "")
    start = max(0, idx - radius)
    end = min(len(collapsed), idx + radius)
    snippet = collapsed[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(collapsed):
        snippet = snippet + "…"
    return snippet


def note_matches_tokens(
    tokens: list[str], rel: str, title: str, tags: list[str], body: str
) -> bool:
    if not tokens:
        return True
    hay = " ".join([rel, title, body, " ".join(tags)]).lower()
    return all(token.lstrip("#") in hay for token in tokens)


def search_files(
    root: Path,
    query: str,
    *,
    folder: str | None = None,
    tag: str | None = None,
    limit: int = 10,
) -> list[SearchHit]:
    tokens = tokenize_query(query)
    wanted_tag = tag.lstrip("#").lower() if tag else None
    hits: list[SearchHit] = []

    for path in iter_markdown(root, folder):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        tags = extract_tags(frontmatter, body)
        if wanted_tag and wanted_tag not in tags:
            continue
        title = note_title(path.name, frontmatter, body)
        if tokens and not note_matches_tokens(tokens, rel, title, tags, body):
            continue
        score = score_note(tokens, rel, title, tags, body)
        if not tokens:
            score = 1.0
        hits.append(
            SearchHit(
                path=rel,
                title=title,
                score=round(score, 2),
                snippet=make_snippet(body, tokens),
                tags=tags,
            )
        )

    hits.sort(key=lambda h: (-h.score, h.path))
    return hits[: max(1, min(limit, 50))]
