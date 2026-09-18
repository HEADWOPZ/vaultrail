from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

from vaultrail.cli import main


def test_cli_init(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dest = tmp_path / "fresh"
    code = main(["--json", "init", str(dest)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["cloud_sync"] is False
    assert "wallets" in payload["folders"]
    assert (dest / "theses").is_dir()
    assert (dest / "ct-drafts").is_dir()
    assert (dest / "risk-journal").is_dir()


def test_cli_search_fixture(fixture_vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--root", str(fixture_vault), "--json", "search", "restaking"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    paths = [h["path"] for h in payload["hits"]]
    assert "theses/sol-restaking.md" in paths


def test_cli_read_and_tags(fixture_vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--root", str(fixture_vault), "read", "ct-drafts/vaultrail-launch.md"])
    assert code == 0
    out = capsys.readouterr().out
    assert "searchable state" in out

    code = main(["--root", str(fixture_vault), "--json", "tags", "ct"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] >= 1


def test_cli_append_and_daily(tmp_vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(
        [
            "--root",
            str(tmp_vault),
            "--json",
            "append",
            "theses/sol-restaking.md",
            "--content",
            "- still small as of fixture test",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["created"] is False

    code = main(
        [
            "--root",
            str(tmp_vault),
            "--json",
            "daily",
            "--date",
            "2026-09-18",
            "--append",
            "- cli daily works",
        ]
    )
    assert code == 0
    daily = json.loads(capsys.readouterr().out)
    assert daily["path"] == "daily/2026-09-18.md"
    assert "cli daily works" in daily["text"]


def test_cli_missing_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VAULTRAIL_ROOT", raising=False)
    code = main(["search", "anything"])
    assert code == 2
    err = capsys.readouterr().err
    assert "VAULTRAIL_ROOT" in err


def test_cli_help_lists_required_commands() -> None:
    buf = StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        try:
            main(["--help"])
        except SystemExit as exc:
            assert exc.code == 0
    finally:
        sys.stdout = old
    help_text = buf.getvalue()
    for name in ("init", "search", "serve"):
        assert name in help_text
