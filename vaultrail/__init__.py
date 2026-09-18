"""VaultRail — local Obsidian/markdown vault as CT/DeFi agent state."""

from __future__ import annotations

__version__ = "0.1.0"
__owner__ = "Kevin Lance Murray (HEADWOPZ)"

from vaultrail.errors import VaultError, VaultNotFoundError, VaultPathError
from vaultrail.vault import Vault

__all__ = [
    "Vault",
    "VaultError",
    "VaultNotFoundError",
    "VaultPathError",
    "__owner__",
    "__version__",
]
