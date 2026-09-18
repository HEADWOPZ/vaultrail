---
name: vault-morning-brief
description: Morning pass over yesterday's daily note, open theses, and the risk journal in the local VaultRail vault.
compatibility: Requires VaultRail MCP (daily_note, vault_search, vault_read, tag_query).
metadata:
  author: Kevin Lance Murray (HEADWOPZ)
  version: "0.1.0"
  license: MIT
---

# Vault morning brief

Start-of-day ritual for a CT/DeFi operator. Durable state lives in the vault, not in chat.

## Sequence

1. `daily_note` with no date (today). Summarize what is already there.
2. `vault_read` on `daily/<yesterday>.md` if it exists (search `folder=daily` if the date is unknown).
3. `tag_query` for `thesis` and `risk`. Read the two hottest notes.
4. Optional: `vault_search` for any name the operator mentions.

## Output shape

- **Carried theses** — one line each, with path.
- **Open risk rules** — size / invalidation only.
- **Gaps** — questions the vault does not answer yet. Offer to `vault_append`, do not invent history.

Do not sync, upload, or “back up” the vault. Do not post drafts.
