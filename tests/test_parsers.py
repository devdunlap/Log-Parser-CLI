"""Parser tests.

The logback tests are written as executable specs for Weekend 1: they
fail until parse_logback is implemented, and they define "done" for it.
The other formats' edge cases are named and skipped until their turn.
"""

import pytest

from logparse.parsers import parse_apache, parse_json_lines, parse_logback, parse_syslog

LOGBACK_LINE = (
    "2026-11-21 14:02:11.403 ERROR [pool-2-thread-1] "
    "com.example.payments.PaymentService - Payment failed for order 88131: card declined"
)


def test_logback_parses_basic_line():
    outcome = parse_logback([LOGBACK_LINE])
    assert outcome.total_lines == 1
    assert outcome.rejects == []
    (record,) = outcome.records
    assert record.level == "ERROR"
    assert record.source == "com.example.payments.PaymentService"
    assert record.message == "Payment failed for order 88131: card declined"
    assert record.extra["thread"] == "pool-2-thread-1"


def test_logback_normalizes_timestamp_to_iso():
    outcome = parse_logback([LOGBACK_LINE])
    assert outcome.records[0].timestamp == "2026-11-21T14:02:11.403"


def test_logback_attaches_stack_trace_to_previous_entry():
    lines = [
        "2026-11-21 14:03:02.118 ERROR [http-nio-8080-exec-4] "
        "com.example.api.OrderController - Unhandled exception while creating order",
        "java.lang.IllegalStateException: Inventory service unavailable",
        "\tat com.example.api.OrderController.createOrder(OrderController.java:87)",
        "\tat java.base/java.lang.Thread.run(Thread.java:1583)",
        "2026-11-21 14:03:03.001 INFO [http-nio-8080-exec-4] "
        "com.example.api.OrderController - Recovered, serving cached inventory",
    ]
    outcome = parse_logback(lines)
    assert len(outcome.records) == 2
    assert "IllegalStateException" in outcome.records[0].message
    assert "OrderController.java:87" in outcome.records[0].message
    assert outcome.records[1].level == "INFO"


def test_logback_keeps_duplicate_lines():
    # Parsing keeps both copies; removing duplicates is dedupe's job.
    outcome = parse_logback([LOGBACK_LINE, LOGBACK_LINE])
    assert len(outcome.records) == 2


def test_logback_unparseable_first_line_becomes_reject():
    outcome = parse_logback(["this is not a log line", LOGBACK_LINE])
    assert len(outcome.records) == 1
    assert len(outcome.rejects) == 1
    assert outcome.rejects[0].line_number == 1
    assert outcome.rejects[0].reason  # a reason is always given


@pytest.mark.skip(reason="Week 1: syslog parser (edge cases: no year, padded day)")
def test_syslog_parses_line_without_year():
    outcome = parse_syslog(
        ["Nov 21 14:02:11 workstation sshd[1234]: Accepted password for andrew"],
        year=2026,
    )
    (record,) = outcome.records
    assert record.timestamp == "2026-11-21T14:02:11"
    assert record.source == "workstation sshd"


@pytest.mark.skip(reason="Week 1: apache parser (edge cases: '-' bytes/referrer, quoted UA with spaces)")
def test_apache_parses_combined_line_with_missing_fields():
    line = (
        '203.0.113.42 - - [21/Nov/2026:14:02:11 -0600] '
        '"GET /api/orders HTTP/1.1" 200 - - "Mozilla/5.0 (X11; Linux x86_64)"'
    )
    outcome = parse_apache([line])
    (record,) = outcome.records
    assert record.extra["status"] == 200
    assert record.extra["bytes"] is None


@pytest.mark.skip(reason="Weekend 2: JSON-lines parser (edge case: truncated line to rejects, with reason)")
def test_json_lines_malformed_goes_to_rejects():
    lines = [
        '{"timestamp": "2026-11-21T14:02:11Z", "level": "INFO", '
        '"source": "billing", "message": "Invoice 5521 generated"}',
        '{"timestamp": "2026-11-21T14:04:55Z", "level": "ERROR", "sou',
    ]
    outcome = parse_json_lines(lines)
    assert len(outcome.records) == 1
    assert len(outcome.rejects) == 1
    assert outcome.rejects[0].reason
