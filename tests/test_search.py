from __future__ import annotations

from pathlib import Path

from vaultrail.vault import Vault


def test_search_finds_restaking_conclusion(fixture_vault: Path) -> None:
    hits = Vault(fixture_vault).search("restaking last week")
    paths = [h.path for h in hits]
    assert "theses/sol-restaking.md" in paths
    top = next(h for h in hits if h.path.endswith("sol-restaking.md"))
    assert "concluded" in top.snippet.lower() or "restaking" in top.title.lower()
    assert "thesis" in top.tags


def test_search_and_requires_all_tokens(fixture_vault: Path) -> None:
    vault = Vault(fixture_vault)
    hits = vault.search("restaking memecoin")
    assert hits == []
    assert vault.search("memecoin trench")


def test_search_folder_and_casefold(fixture_vault: Path) -> None:
    hits = Vault(fixture_vault).search("TREASURY", folder="wallets")
    assert hits
    assert all(h.path.startswith("wallets/") for h in hits)


def test_tag_query_frontmatter_and_inline(fixture_vault: Path) -> None:
    vault = Vault(fixture_vault)
    risk = vault.tag_query("risk")
    paths = {h.path for h in risk}
    assert "theses/sol-restaking.md" in paths  # inline #risk
    assert "risk-journal/2026-09-11-size.md" in paths
    assert "theses/memecoin-risk.md" in paths
    wallets = vault.tag_query("phantombridge", folder="wallets")
    assert any("phantom-treasury" in h.path for h in wallets)


def test_search_skips_dot_dirs(tmp_vault: Path) -> None:
    hidden = tmp_vault / ".obsidian" / "secret.md"
    hidden.parent.mkdir()
    hidden.write_text("# secret restaking\n", encoding="utf-8")
    hits = Vault(tmp_vault).search("secret restaking")
    assert all(".obsidian" not in h.path for h in hits)
