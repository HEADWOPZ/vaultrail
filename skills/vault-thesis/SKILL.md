---
name: vault-thesis
description: Capture or update a durable market/protocol thesis in the local VaultRail vault.
compatibility: Requires VaultRail MCP (vault_search, vault_read, vault_append).
metadata:
  author: Kevin Lance Murray (HEADWOPZ)
  version: "0.1.0"
  license: MIT
---

# Vault thesis

Theses are the answers to “what did I conclude about X?”

## Sequence

1. `vault_search` in `folder=theses` before writing. Update an existing note when it is the same idea.
2. To create: `vault_append` a new `theses/<kebab-case>.md` with frontmatter:

```markdown
---
type: thesis
status: open
tags: [thesis]
---

# Title

**Conclusion:** one paragraph.

```

3. To update: append a dated section. Do not silently rewrite an old conclusion.

Lead with the conclusion. Tag venue (`#solana`, `#perps`, `#prediction`) in the body.
