---
name: vault-ct-draft
description: Store an X/CT post draft in the local VaultRail vault. Does not publish or schedule.
compatibility: Requires VaultRail MCP (vault_append, vault_search).
metadata:
  author: Kevin Lance Murray (HEADWOPZ)
  version: "0.1.0"
  license: MIT
---

# Vault CT draft

This is **agent memory for copy**, not a publisher.

- AlgoDesk is the X draft/schedule tool. VaultRail only stores the note.
- `vault_search` `folder=ct-drafts` before creating a near-duplicate.
- `vault_append` `ct-drafts/<kebab-case>.md` with `status: draft|ready|shipped`.

```markdown
---
type: ct-draft
status: draft
tags: [ct]
---

# Hook

Body.
```

Do not tweet, schedule, or call social APIs from this skill.
