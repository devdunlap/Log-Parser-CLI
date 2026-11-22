"""The shared record shape every parser produces.

One shape for all formats is the core design decision of this tool:
downstream code (output writers, dedupe, and later the Postgres load in
Project 2) never has to care which format a record came from.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogRecord:
    """A single parsed log entry.

    timestamp: ISO 8601 string, normalized by the parser (syslog lines
        have no year - the parser supplies the current year).
    level:     Severity as written in the log (INFO, WARN, ERROR, ...).
        Access logs have no level; parsers use the HTTP status class.
    source:    Where the entry came from - logger name (logback),
        host + process (syslog), client host (apache), or the JSON
        source field.
    message:   The human-readable message. Multi-line stack traces are
        appended to the message of the entry they belong to.
    extra:     Format-specific fields that do not fit the shared shape
        (thread, logger, status, bytes, referrer, user_agent, ...).
    """

    timestamp: str | None
    level: str
    source: str
    message: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Reject:
    """A line that could not be parsed, kept with the reason why.

    Rejects are data, not errors: they are written to the --rejects file
    and counted in the summary, never silently dropped.
    """

    line_number: int
    raw: str
    reason: str


@dataclass
class ParseOutcome:
    """Everything a parser learned from one file."""

    records: list[LogRecord]
    rejects: list[Reject]
    total_lines: int
