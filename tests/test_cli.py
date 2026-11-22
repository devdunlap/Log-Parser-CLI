"""End-to-end CLI tests."""

import pytest

from logparse.cli import main


def test_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    assert "parse" in capsys.readouterr().out


@pytest.mark.skip(reason="Weekend 1: passes once the logback parser lands")
def test_parse_logback_sample_end_to_end(tmp_path):
    out = tmp_path / "parsed.jsonl"
    rc = main(["parse", "samples/app.log", "--format", "logback", "--out", str(out)])
    assert rc == 0
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 5  # the sample's real entries, stack trace attached
