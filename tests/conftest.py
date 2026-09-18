from __future__ import annotations

import shutil
from pathlib import Path

import pytest

FIXTURE_VAULT = Path(__file__).parent / "fixtures" / "sample-vault"


@pytest.fixture
def fixture_vault() -> Path:
    return FIXTURE_VAULT


@pytest.fixture
def tmp_vault(tmp_path: Path) -> Path:
    dest = tmp_path / "vault"
    shutil.copytree(FIXTURE_VAULT, dest)
    return dest


@pytest.fixture
def isolated_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "empty-vault"
    root.mkdir()
    monkeypatch.setenv("VAULTRAIL_ROOT", str(root))
    return root
