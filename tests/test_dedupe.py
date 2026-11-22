"""Dedupe tests - named specs for Weekend 2."""

import pytest

from logparse.dedupe import dedupe_records
from logparse.records import LogRecord


def rec(message: str, ts: str = "2026-11-21T14:02:11.403", level: str = "ERROR"):
    return LogRecord(timestamp=ts, level=level, source="com.example.App", message=message)


@pytest.mark.skip(reason="Weekend 2: dedupe (the additivity case - same error written twice)")
def test_exact_duplicates_flagged_and_counted():
    kept, report = dedupe_records([rec("boom"), rec("boom"), rec("other")])
    assert len(kept) == 2
    assert report.duplicates == 1
    assert report.by_message["boom"] == 1


@pytest.mark.skip(reason="Weekend 2: dedupe")
def test_same_message_different_timestamp_is_not_a_duplicate():
    kept, report = dedupe_records(
        [rec("boom", ts="2026-11-21T14:02:11.403"), rec("boom", ts="2026-11-21T14:05:00.000")]
    )
    assert len(kept) == 2
    assert report.duplicates == 0


@pytest.mark.skip(reason="Weekend 2: dedupe")
def test_no_duplicates_keeps_everything():
    kept, report = dedupe_records([rec("a"), rec("b")])
    assert len(kept) == 2
    assert report.total_in == 2
    assert report.kept == 2
