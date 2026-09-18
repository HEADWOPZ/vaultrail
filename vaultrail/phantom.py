"""Read-only PhantomBridge pubkey conventions. No wallet RPC, no live reads."""

from __future__ import annotations

import re
from typing import Any

# Solana-ish base58 (no 0, O, I, l). Length is a soft check, not a checksum.
BASE58_RE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")

PHANTOM_DOC = (
    "PhantomBridge link notes are markdown only. VaultRail never fetches "
    "balances, signatures, or token accounts."
)


def parse_link_note(
    frontmatter: dict[str, Any], body: str = ""
) -> dict[str, Any] | None:
    """Extract a read-only pubkey citation if the note opts in.

    A note qualifies when ``phantombridge`` is truthy or ``type`` is ``wallet``
    and a ``pubkey`` field (or first base58-looking token) is present.
    """
    flagged = bool(frontmatter.get("phantombridge"))
    is_wallet = str(frontmatter.get("type", "")).lower() == "wallet"
    pubkey = frontmatter.get("pubkey")
    if isinstance(pubkey, str):
        pubkey = pubkey.strip()
    else:
        pubkey = ""

    if not pubkey:
        match = BASE58_RE.search(body)
        if match:
            pubkey = match.group(0)

    if not pubkey:
        return None
    if not (flagged or is_wallet):
        return None
    if not BASE58_RE.fullmatch(pubkey):
        return None

    return {
        "pubkey": pubkey,
        "chain": str(frontmatter.get("chain") or "solana"),
        "phantombridge": True,
        "live": False,
        "note": PHANTOM_DOC,
    }
