"""Opinionated Obsidian folder schema for CT/DeFi agent state."""

from __future__ import annotations

from pathlib import Path

SCHEMA_FOLDERS = (
    "wallets",
    "theses",
    "ct-drafts",
    "risk-journal",
    "daily",
)

# Folders the brief called out; daily/ is added because daily_note needs a home.
BRIEF_FOLDERS = ("wallets", "theses", "ct-drafts", "risk-journal")

ROOT_README = """# VaultRail vault

Local second-brain for CT / DeFi agent state. **Files stay on this machine.**
VaultRail does not sync, upload, or index this folder in the cloud.

## Folders

| Folder | What lives here |
|--------|-----------------|
| `wallets/` | Watchlist notes. Pubkeys only. Never seeds or private keys. |
| `theses/` | Durable market / protocol views and what you concluded. |
| `ct-drafts/` | X/CT post drafts. Not a scheduler (that is AlgoDesk). |
| `risk-journal/` | Size, invalidation, tilt. Dated entries. |
| `daily/` | Daily notes (`YYYY-MM-DD.md`). Created by `daily_note`. |

## Conventions

- One idea per note. Filename is `kebab-case.md`.
- YAML frontmatter + `#inline-tags` are both first-class for `tag_query`.
- Wikilinks `[[theses/sol-restaking]]` are stored as text; VaultRail does not rewrite them.
- Agents **search / read / append**. They should not invent cloud backup.

## PhantomBridge (optional, read-only)

Wallet notes may cite a pubkey so Hermes/Claude can *name* an address.
VaultRail never calls a wallet RPC. See `wallets/_example.phantombridge.md`.

```yaml
---
type: wallet
chain: solana
pubkey: <base58>
phantombridge: true
tags: [wallet, phantombridge]
---
```

## What this vault is not

- Not SkillRail (skill registry)
- Not LoopForge (job runtime)
- Not AlgoDesk (X draft/schedule)
"""

FOLDER_READMES: dict[str, str] = {
    "wallets": """# wallets/

Watchlist notes for addresses you care about.

- One note per wallet or cluster.
- Store **pubkeys only**. Never seed phrases, private keys, or keystore JSON.
- Optional PhantomBridge link notes are markdown conventions — read-only, no live RPC.

Suggested frontmatter:

```yaml
---
type: wallet
chain: solana
pubkey: <base58>
phantombridge: true
tags: [wallet]
---
```
""",
    "theses": """# theses/

Durable views: why you like / fade a protocol, narrative, or risk factor.

- Lead with the conclusion. Agents will search this folder first for "what did I decide?"
- Update by appending a dated section rather than rewriting history silently.
- Tag with `#thesis` plus the venue (`#solana`, `#perps`, `#prediction`).

Suggested frontmatter:

```yaml
---
type: thesis
status: open
tags: [thesis]
---
```
""",
    "ct-drafts": """# ct-drafts/

Draft posts and threads. This is **agent memory**, not a publisher.

- AlgoDesk owns scheduling / algo-aware posting. Keep hooks and angles here.
- Include the intended account and a `status: draft|ready|shipped` field.

Suggested frontmatter:

```yaml
---
type: ct-draft
status: draft
tags: [ct]
---
```
""",
    "risk-journal": """# risk-journal/

Size, invalidation, tilt, and post-mortems.

- Prefer dated filenames: `2026-09-18-size.md` or append to the daily note.
- Write the rule you will actually follow, not the vibe.

Suggested frontmatter:

```yaml
---
type: risk
tags: [risk]
---
```
""",
    "daily": """# daily/

One note per day: `YYYY-MM-DD.md`.

Created and appended by the `daily_note` MCP/CLI tool. Use it as the scratch
layer; promote lasting conclusions into `theses/` or `risk-journal/`.
""",
}

PHANTOM_EXAMPLE = """---
type: wallet
chain: solana
pubkey: 11111111111111111111111111111111
phantombridge: true
tags: [wallet, phantombridge, example]
---

# Example PhantomBridge link note

This is a **read-only** pubkey citation.

- VaultRail will parse `pubkey` / `phantombridge: true` for agents.
- It will **not** fetch balances, signatures, or token accounts.
- Replace the dummy pubkey with a real one, or delete this example.

Related: `[[wallets/]]` · PhantomBridge (separate HEADWOPZ tool) for live reads.
"""


def ensure_schema(root: Path, *, overwrite_readmes: bool = False) -> list[str]:
    """Create schema folders and convention READMEs. Returns created paths."""
    created: list[str] = []
    root.mkdir(parents=True, exist_ok=True)

    readme = root / "README.md"
    if overwrite_readmes or not readme.exists():
        readme.write_text(ROOT_README, encoding="utf-8")
        created.append("README.md")

    for folder in SCHEMA_FOLDERS:
        dest = root / folder
        dest.mkdir(parents=True, exist_ok=True)
        folder_readme = dest / "README.md"
        if overwrite_readmes or not folder_readme.exists():
            folder_readme.write_text(FOLDER_READMES[folder], encoding="utf-8")
            created.append(f"{folder}/README.md")

    example = root / "wallets" / "_example.phantombridge.md"
    if overwrite_readmes or not example.exists():
        example.write_text(PHANTOM_EXAMPLE, encoding="utf-8")
        created.append("wallets/_example.phantombridge.md")

    return created
