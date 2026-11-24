"""One parser function per input format.

Conventions (from the spec):
- Regexes are compiled once, at module level, with named groups.
- A parser never raises on a bad line: the line becomes a Reject with a
  reason, and parsing continues.
- Multi-line stack traces belong to the entry above them: continuation
  lines are appended to that entry's message, not parsed as new entries.
- Timestamps are normalized to ISO 8601 in the record.

The remaining parser stubs have their contracts written out below.
"""

import re
from collections.abc import Iterable
from datetime import datetime

from .records import LogRecord, ParseOutcome, Reject

LOGBACK_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    r"(?:[.,]\d{1,6})?)\s+"
    r"(?P<level>[A-Z]+)\s+\[(?P<thread>[^\]]+)\]\s+"
    r"(?:\[(?P<mdc_before>[^\]]*)\]\s+)?"
    r"(?P<logger>\S+)\s+"
    r"(?:\[(?P<mdc_after>[^\]]*)\]\s+)?"
    r"-\s*(?:\[(?P<mdc_message>(?=[^\]]*(?<![A-Za-z0-9_])"
    r"(?:traceId|trace_id|correlationId|correlation_id)=[^\s,\]])[^\]]*)\]\s*)?"
    r"(?P<message>.*)$"
)

# TODO(you): compile patterns for the remaining formats.
#
# logback:  timestamp, level, [thread], logger, message
#           2026-11-21 14:02:11.403 ERROR [pool-2] com.example.App - msg
# syslog:   month, day, time, host, process[pid], message  (no year)
# apache:   host, ident, user, [time], "request", status, bytes,
#           "referrer", "user-agent"   (bytes/referrer can be "-")
# json-ish: a JSON object per line; some lines are truncated/malformed


def _outcome(
    records: list[LogRecord], rejects: list[Reject], total: int
) -> ParseOutcome:
    return ParseOutcome(records=records, rejects=rejects, total_lines=total)


def parse_logback(lines: Iterable[str]) -> ParseOutcome:
    """Parse Logback/Java-style lines.

    Lines that start with whitespace, or that do not match the entry
    pattern but follow a parsed entry, are continuation lines (stack
    traces) and are appended to the previous record's message.
    A non-matching line with no previous record is a Reject.
    """
    records: list[LogRecord] = []
    rejects: list[Reject] = []
    current: LogRecord | None = None
    total = 0

    for total, raw in enumerate(lines, start=1):
        line = raw.rstrip("\r\n")
        match = LOGBACK_PATTERN.match(line)
        if match is None:
            if current is None:
                rejects.append(Reject(total, line, "Not a Logback entry"))
            else:
                current.message += "\n" + line
            continue

        timestamp = match["timestamp"].replace(",", ".")
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            rejects.append(Reject(total, line, "Invalid Logback timestamp"))
            current = None
            continue

        extra = {"thread": match["thread"]}
        for group in (match["mdc_before"], match["mdc_after"], match["mdc_message"]):
            if group:
                for item in group.replace(",", " ").split():
                    key, separator, value = item.partition("=")
                    if separator and value and key in (
                        "traceId", "trace_id", "correlationId", "correlation_id"
                    ):
                        extra[key] = value

        current = LogRecord(
            timestamp=timestamp.replace(" ", "T", 1),
            level=match["level"],
            source=match["logger"],
            message=match["message"],
            extra=extra,
        )
        records.append(current)

    return _outcome(records, rejects, total)


def parse_syslog(lines: Iterable[str], *, year: int) -> ParseOutcome:
    """Parse syslog-style lines. Syslog carries no year: `year` is
    supplied by the caller (the CLI passes the current year). Spacing
    varies (single-digit days are space-padded)."""
    raise NotImplementedError("Week 1: implement the syslog parser")


def parse_apache(lines: Iterable[str]) -> ParseOutcome:
    """Parse Apache combined access-log lines. Missing bytes or
    referrer appear as "-" and must be kept as None, not crash.
    Quoted fields (request, user-agent) can contain spaces."""
    raise NotImplementedError("Week 1: implement the apache parser")


def parse_json_lines(lines: Iterable[str]) -> ParseOutcome:
    """Parse JSON-ish lines: one JSON object per line, some of them
    truncated or malformed. Well-formed lines become records using the
    shared shape; malformed lines become Rejects with the reason."""
    raise NotImplementedError("Weekend 2: implement the JSON-lines parser")


PARSERS = {
    "logback": parse_logback,
    "syslog": parse_syslog,
    "apache": parse_apache,
    "json": parse_json_lines,
}
