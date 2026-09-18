from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from vaultrail.errors import VaultPathError
from vaultrail.vault import Vault


def test_read_thesis(fixture_vault: Path) -> None:
    note = Vault(fixture_vault).read("theses/sol-restaking.md")
    assert note["title"] == "SOL restaking"
    assert "thesis" in note["tags"]
    assert "Stay small" in note["body"]
    assert note["phantombridge"] is None


def test_append_creates_and_extends(tmp_vault: Path) -> None:
    vault = Vault(tmp_vault)
    created = vault.append("risk-journal/new-rule.md", "- first line", create=True)
    assert created["created"] is True
    again = vault.append("risk-journal/new-rule.md", "- second line")
    assert again["created"] is False
    text = vault.read("risk-journal/new-rule.md")["text"]
    assert "first line" in text
    assert "second line" in text


def test_append_no_create(tmp_vault: Path) -> None:
    with pytest.raises(VaultPathError, match="not found"):
        Vault(tmp_vault).append("theses/missing.md", "x", create=False)


def test_daily_note_create_and_append(tmp_path: Path) -> None:
    vault = Vault(tmp_path / "vault")
    vault.init()
    note = vault.daily_note(date(2026, 9, 18), append="- sized down SOL")
    assert note["created"] is True
    assert note["date"] == "2026-09-18"
    assert note["path"] == "daily/2026-09-18.md"
    assert "sized down SOL" in note["text"]
    again = vault.daily_note("2026-09-18")
    assert again["created"] is False


def test_daily_rejects_bad_date(fixture_vault: Path) -> None:
    with pytest.raises(VaultPathError, match="YYYY-MM-DD"):
        Vault(fixture_vault).daily_note("09/18/2026")


def test_info_reports_local_only(fixture_vault: Path) -> None:
    info = Vault(fixture_vault).info()
    assert info["cloud_sync"] is False
    assert info["privacy"] == "local-files-only"
    assert info["folders"]["theses"] is True
