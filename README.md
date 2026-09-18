# VaultRail

**Local Obsidian / Claude second-brain MCP for CT/DeFi agent state.**

Most agents forget everything between chats. VaultRail wires Hermes or Claude
to a folder of markdown notes — wallets watched, theses, post drafts, risk
journals — so conclusions persist as searchable files.

Owner: **Kevin Lance Murray (HEADWOPZ)** · License: **MIT**

This is **personal knowledge / agent memory**. It is not SkillRail (skill
registry), not LoopForge (job runtime), and not AlgoDesk (X draft/schedule).

## What it does

| Surface | Commands / tools |
|---------|------------------|
| CLI | `vaultrail init` · `vaultrail search` · `vaultrail serve` |
| MCP (stdio) | `vault_search` · `vault_read` · `vault_append` · `daily_note` · `tag_query` |
| Schema | `wallets/` `theses/` `ct-drafts/` `risk-journal/` (+ `daily/`) |
| Skills | Hermes/Claude pack under [`skills/`](skills/) |

Optional PhantomBridge pubkey notes are a **markdown convention only**. VaultRail
never calls a wallet RPC.

## Privacy

**Local files only.** VaultRail reads and writes markdown under `VAULTRAIL_ROOT`.
It does not sync, upload, index, or back up your vault to any cloud. There is
no telemetry. Treat the vault like any other Obsidian folder: you own the disk.

Do not store seed phrases or private keys. Pubkeys are fine.

## Install

Python 3.10+.

```bash
pip install -e .
# or from the repo root after clone:
pip install .
```

Dev extras (pytest):

```bash
pip install -e ".[dev]"
pytest -q
```

## Quick start

```bash
export VAULTRAIL_ROOT="$HOME/Notes/ct-vault"
vaultrail init "$VAULTRAIL_ROOT"
vaultrail search "what did I conclude about restaking"
vaultrail daily --append "- morning pass"
```

`init` is idempotent. It writes convention READMEs and
`wallets/_example.phantombridge.md` without clobbering notes you already have.

Against the bundled fixture vault (offline, used by CI):

```bash
vaultrail --root tests/fixtures/sample-vault search "restaking last week"
```

## Opinionated schema

```
vault/
  README.md                 # conventions (written by init)
  wallets/                  # pubkey watchlist — never seeds
  theses/                   # durable views / conclusions
  ct-drafts/                # post drafts (not a publisher)
  risk-journal/             # size, invalidation, tilt
  daily/                    # YYYY-MM-DD.md from daily_note
```

Notes are markdown. YAML frontmatter `tags:` and inline `#tags` both feed
`tag_query`. Filenames are `kebab-case.md`.

### PhantomBridge link notes (read-only)

```yaml
---
type: wallet
chain: solana
pubkey: <base58>
phantombridge: true
tags: [wallet, phantombridge]
---
```

Agents may cite the pubkey. They must not ask VaultRail for balances — that
belongs to PhantomBridge, a separate tool.

## MCP config

`vaultrail serve` speaks MCP over **stdio**. Set `VAULTRAIL_ROOT` in the host
environment. Logs go to stderr only.

### Cursor

`~/.cursor/mcp.json` (or project `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "vaultrail": {
      "command": "vaultrail",
      "args": ["serve"],
      "env": {
        "VAULTRAIL_ROOT": "/absolute/path/to/your/vault"
      }
    }
  }
}
```

### Claude Desktop

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vaultrail": {
      "command": "vaultrail",
      "args": ["serve"],
      "env": {
        "VAULTRAIL_ROOT": "/absolute/path/to/your/vault"
      }
    }
  }
}
```

If `vaultrail` is not on `PATH`, use the absolute interpreter plus
`["-m", "vaultrail", "serve"]`.

### MCP tools

| Tool | Role |
|------|------|
| `vault_search` | AND keyword search; optional `folder`, `tag`, `limit` |
| `vault_read` | Read one relative `.md` path |
| `vault_append` | Append markdown; `create=true` makes a new note |
| `daily_note` | Open/create `daily/YYYY-MM-DD.md`; optional `append` |
| `tag_query` | Notes with a frontmatter or inline tag |

Paths are relative to the vault. `..`, absolute paths, and non-markdown files
are rejected.

## CLI extras

The required surface is `init` / `search` / `serve`. These are also available:

```
vaultrail read theses/sol-restaking.md
vaultrail append risk-journal/2026-09-18.md --content "- cut size"
vaultrail daily --date 2026-09-18
vaultrail tags phantombridge
vaultrail info
```

`--json` prints machine-readable objects. `--root` overrides `$VAULTRAIL_ROOT`.

## Skills

See [`skills/README.md`](skills/README.md). Copy folders into
`~/.claude/skills/` or point Hermes at `skills/pack.yaml`.

## Tests & CI

```bash
pytest -q
```

Tests run entirely offline against `tests/fixtures/sample-vault/` and temp
copies. GitHub Actions (`.github/workflows/ci.yml`) installs the package and
runs the same suite on Python 3.10 and 3.12.

## What this is not

| Product | Lane |
|---------|------|
| **VaultRail** | Local vault / agent memory |
| SkillRail | Installable skill registry |
| LoopForge | Schedule → maker → checker runtime |
| AlgoDesk | X algo-aware draft and schedule |

No cloud sync. No live wallet calls. No posting.

## License

[MIT](LICENSE) © 2026 Kevin Lance Murray (HEADWOPZ)
