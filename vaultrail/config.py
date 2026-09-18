"""Resolve the local vault root. Files stay on disk; nothing is synced."""

from __future__ import annotations

import os
from pathlib import Path

from vaultrail.errors import VaultNotFoundError
from vaultrail.schema import SCHEMA_FOLDERS

ENV_ROOT = "VAULTRAIL_ROOT"


def looks_like_vault(path: Path) -> bool:
    """True if *path* already has the opinionated schema folders."""
    if not path.is_dir():
        return False
    present = {child.name for child in path.iterdir() if child.is_dir()}
    required = {"wallets", "theses", "ct-drafts", "risk-journal"}
    return required.issubset(present)


def resolve_root(explicit: str | Path | None = None) -> Path:
    """Resolve the vault directory.

    Order: explicit argument → ``VAULTRAIL_ROOT`` → cwd if it looks like a vault.
    """
    if explicit is not None:
        root = Path(explicit).expanduser()
        return root.resolve()

    env = os.environ.get(ENV_ROOT, "").strip()
    if env:
        return Path(env).expanduser().resolve()

    cwd = Path.cwd().resolve()
    if looks_like_vault(cwd):
        return cwd

    raise VaultNotFoundError(
        "No vault root. Set VAULTRAIL_ROOT, pass --root, or run from an "
        f"initialized vault (expected folders: {', '.join(SCHEMA_FOLDERS)})."
    )
