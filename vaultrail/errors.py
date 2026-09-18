"""Typed errors for VaultRail. Messages are safe to show to an agent."""

from __future__ import annotations


class VaultError(Exception):
    """Base error for vault operations."""


class VaultNotFoundError(VaultError):
    """VAULTRAIL_ROOT is missing or is not a vault."""


class VaultPathError(VaultError):
    """Requested path is outside the vault or not a markdown note."""
