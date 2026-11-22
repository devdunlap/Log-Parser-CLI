"""Duplicate detection for parsed records.

The problem this exists for: a misconfigured logger (the classic case is
a missing additivity="false" in a logback config) writes every error
twice, and the duplicates inflate alert counts. Dedupe makes the
duplication visible and countable instead of hidden.

Contract:
- A duplicate is a record with the same (timestamp, level, message) as
  an earlier record. The first occurrence is kept; later ones are
  duplicates.
- dedupe_records returns the kept records and a report of how many
  duplicates were found, grouped by the duplicated message.
- Nothing is silently dropped: the report is part of the output.
"""

from dataclasses import dataclass, field

from .records import LogRecord


@dataclass
class DedupeReport:
    total_in: int
    kept: int
    duplicates: int
    by_message: dict[str, int] = field(default_factory=dict)


def dedupe_records(records: list[LogRecord]) -> tuple[list[LogRecord], DedupeReport]:
    """Split records into (kept, report). See module docstring."""
    raise NotImplementedError("Weekend 2: implement dedupe")


def dedupe_file(in_path: str, out_path: str) -> DedupeReport:
    """Read JSONL records from in_path, write the kept records to
    out_path, and return the report for the CLI to print."""
    raise NotImplementedError("Weekend 2: implement dedupe_file")
