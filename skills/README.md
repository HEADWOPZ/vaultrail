# VaultRail skill pack

Hermes / Claude skills that drive the **VaultRail** MCP tools against a local
Obsidian vault. Copy a skill folder into your agent's skill directory.

| Skill | When to use |
|-------|-------------|
| `vault-search` | “What did I already write about X?” |
| `vault-morning-brief` | Start-of-day pass over daily + theses + risk |
| `vault-thesis` | Capture or update a durable view |
| `vault-risk-log` | Size / invalidation / tilt |
| `vault-ct-draft` | Store a post draft (does **not** publish) |
| `vault-daily` | Open or append `daily/YYYY-MM-DD.md` |

## Install

**Claude Code / Claude Desktop** — copy each `skills/<name>/` folder to
`~/.claude/skills/` (or the project's `.claude/skills/`).

**Hermes** — point the skill pack at this directory (`skills/pack.yaml` is the
manifest). Skills assume the VaultRail MCP server is already configured.

**Cursor** — add the MCP snippet from the repo README, then drop skills into
`.cursor/skills/` if your agent loads them from the project.

These skills never instruct the model to upload the vault or call a wallet RPC.
