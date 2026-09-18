from __future__ import annotations

from pathlib import Path

from vaultrail.frontmatter import split_frontmatter
from vaultrail.phantom import PHANTOM_DOC, parse_link_note
from vaultrail.vault import Vault


def test_fixture_wallet_is_readonly_link(fixture_vault: Path) -> None:
    note = Vault(fixture_vault).read("wallets/phantom-treasury.md")
    link = note["phantombridge"]
    assert link is not None
    assert link["live"] is False
    assert link["pubkey"] == "11111111111111111111111111111111"
    assert link["chain"] == "solana"
    assert "never fetches" in link["note"].lower()
    assert PHANTOM_DOC in link["note"]


def test_plain_thesis_is_not_a_wallet_link(fixture_vault: Path) -> None:
    note = Vault(fixture_vault).read("theses/sol-restaking.md")
    assert note["phantombridge"] is None


def test_parse_requires_opt_in() -> None:
    fm, body = split_frontmatter(
        "---\ntitle: no\n---\n\nSome 11111111111111111111111111111111 text\n"
    )
    assert parse_link_note(fm, body) is None
