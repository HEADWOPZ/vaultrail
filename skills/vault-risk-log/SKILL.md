---
name: vault-risk-log
description: Append a size, invalidation, or tilt entry to the VaultRail risk journal.
compatibility: Requires VaultRail MCP (vault_append, daily_note, vault_search).
metadata:
  author: Kevin Lance Murray (HEADWOPZ)
  version: "0.1.0"
  license: MIT
---

# Vault risk log

Write the rule the operator will actually follow.

## Sequence

1. `vault_search` `folder=risk-journal` (and `tag=risk`) so you do not duplicate a standing rule.
2. Prefer a dated file: `vault_append` `risk-journal/YYYY-MM-DD-<slug>.md`.
3. Also `daily_note` with `append` so the day note points at the journal path.

Template:

```markdown
---
type: risk
tags: [risk]
---

# YYYY-MM-DD <slug>

- Rule:
- Invalidation:
- Size:
```

Never log seeds, private keys, or exchange passwords. Pubkeys only if a wallet is relevant.
