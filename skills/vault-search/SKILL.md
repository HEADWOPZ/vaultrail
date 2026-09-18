---
name: vault-search
description: Search the local VaultRail Obsidian vault for theses, wallets, CT drafts, and risk notes.
compatibility: Requires the VaultRail MCP server (vault_search, vault_read, tag_query).
metadata:
  author: Kevin Lance Murray (HEADWOPZ)
  version: "0.1.0"
  license: MIT
---

# Vault search

Use this when the operator asks what they already concluded, watched, or drafted.

## Tools

1. `vault_search` with AND keywords. Add `folder` (`theses`, `wallets`, `ct-drafts`, `risk-journal`, `daily`) or `tag` when the ask is narrow.
2. `tag_query` when they name a tag (`#risk`, `#phantombridge`).
3. `vault_read` on the best one or two hits. Quote paths and short snippets.

## Rules

- Stay inside VAULTRAIL_ROOT. If a tool rejects a path, do not retry with `..`.
- Prefer citing the note path over paraphrasing away the conclusion.
- PhantomBridge fields are **read-only pubkey citations**. Do not fetch balances.
- This is not SkillRail (no skill install), not LoopForge (no job run), not AlgoDesk (no posting).
