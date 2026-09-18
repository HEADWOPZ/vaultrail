from __future__ import annotations

from pathlib import Path

import pytest

from vaultrail.config import looks_like_vault, resolve_root
from vaultrail.errors import VaultNotFoundError
from vaultrail.schema import ensure_schema


def test_looks_like_vault(fixture_vault: Path, tmp_path: Path) -> None:
    assert looks_like_vault(fixture_vault)
    assert not looks_like_vault(tmp_path)


def test_resolve_root_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAULTRAIL_ROOT", str(tmp_path / "from-env"))
    assert resolve_root() == (tmp_path / "from-env").resolve()
    assert resolve_root(tmp_path / "explicit") == (tmp_path / "explicit").resolve()


def test_resolve_root_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vault = tmp_path / "cwd-vault"
    ensure_schema(vault)
    monkeypatch.chdir(vault)
    monkeypatch.delenv("VAULTRAIL_ROOT", raising=False)
    assert resolve_root() == vault.resolve()


def test_resolve_root_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VAULTRAIL_ROOT", raising=False)
    with pytest.raises(VaultNotFoundError, match="VAULTRAIL_ROOT"):
        resolve_root()
