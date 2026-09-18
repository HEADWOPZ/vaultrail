from __future__ import annotations

from pathlib import Path

import pytest

from vaultrail.errors import VaultPathError
from vaultrail.vault import Vault


@pytest.mark.parametrize(
    "rel",
    [
        "../README.md",
        "../../etc/passwd",
        "/etc/passwd",
        "~/.ssh/id_rsa",
        "theses/../../README.md",
        ".git/config",
        "theses/note.txt",
        "theses/note.md\x00",
    ],
)
def test_rejects_unsafe_paths(fixture_vault: Path, rel: str) -> None:
    with pytest.raises(VaultPathError):
        Vault(fixture_vault).resolve_note(rel)


def test_absolute_windows_style(fixture_vault: Path) -> None:
    with pytest.raises(VaultPathError):
        Vault(fixture_vault).resolve_note("C:/Windows/notepad.md")


def test_folder_escape(fixture_vault: Path) -> None:
    with pytest.raises(VaultPathError):
        Vault(fixture_vault).search("x", folder="../")
