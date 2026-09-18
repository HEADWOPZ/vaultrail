from __future__ import annotations

from pathlib import Path

from vaultrail.schema import BRIEF_FOLDERS, SCHEMA_FOLDERS, ensure_schema
from vaultrail.vault import Vault


def test_init_creates_brief_folders(tmp_path: Path) -> None:
    root = tmp_path / "new-vault"
    created = ensure_schema(root)
    for folder in BRIEF_FOLDERS:
        assert (root / folder).is_dir()
        assert (root / folder / "README.md").is_file()
    assert (root / "daily").is_dir()
    assert (root / "README.md").is_file()
    assert (root / "wallets" / "_example.phantombridge.md").is_file()
    assert created
    text = (root / "README.md").read_text(encoding="utf-8")
    assert "does not sync" in text
    assert "SkillRail" in text


def test_init_is_idempotent(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    first = Vault(root).init()
    (root / "theses" / "keep-me.md").write_text("# keep\n", encoding="utf-8")
    second = Vault(root).init()
    assert first
    assert second == []
    assert (root / "theses" / "keep-me.md").read_text(encoding="utf-8") == "# keep\n"
    for folder in SCHEMA_FOLDERS:
        assert (root / folder).is_dir()


def test_force_overwrites_readme_only(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    Vault(root).init()
    readme = root / "README.md"
    readme.write_text("operator note\n", encoding="utf-8")
    custom = root / "theses" / "custom.md"
    custom.write_text("stay\n", encoding="utf-8")
    Vault(root).init(overwrite_readmes=True)
    assert "VaultRail vault" in readme.read_text(encoding="utf-8")
    assert custom.read_text(encoding="utf-8") == "stay\n"
