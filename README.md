# logparse

Parse messy log files into clean structured records. `logparse` reads
Logback/Java, syslog, Apache access, and JSON-ish logs, and writes JSON
lines or CSV in one shared record shape - and it can flag the duplicate
entries that quietly inflate alert counts.

```bash
logparse parse samples/app.log --format logback --out parsed.jsonl
logparse dedupe parsed.jsonl --out clean.jsonl
```

## Why it exists

Production logs are messy: four formats, multi-line stack traces,
truncated lines, and - the quiet killer - the same error written twice
because a logger was configured to propagate to two appenders. Those
duplicates count toward alert thresholds and page people for nothing.
This tool is the fix in miniature: give the logs structure, keep the
lines that fail to parse (in a rejects file, with reasons), and make
duplication visible and countable instead of hidden.

## How to run it

```bash
git clone <this repo>
cd log-parser-cli
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest            # test suite
logparse parse samples/app.log --format logback --out parsed.jsonl --rejects rejects.txt
```

One example per format:

```bash
logparse parse samples/app.log       --format logback --out parsed.jsonl
logparse parse samples/syslog.log    --format syslog  --out parsed.jsonl
logparse parse samples/access.log    --format apache  --out parsed.csv
logparse parse samples/malformed.log --format json    --out parsed.jsonl --rejects rejects.txt
```

## Design decisions

<!-- Fill in as you build; short paragraphs, your reasoning, not a diary. -->
- Why one shared record shape for every format:
- Why the regexes are compiled once, with named groups:
- Why rejects are a file with reasons instead of stderr noise:
- Why dedupe is a separate command, not a parse flag:

## How this was built

This project was built spec-first with Claude Code as the coding
assistant. What was delegated, what was reviewed and changed by hand,
and where the model got things wrong are documented in
[CLAUDE.md](CLAUDE.md) - that record is part of the work, not a footnote.

## What it does not do (yet)

- No live tailing / streaming input.
- No database load - loading this output into Postgres is Project 2
  (Ops Data API), and the record shape here is that project's first
  table by design.
- Syslog timestamps carry no year; the current year is assumed.

## Status

Scaffolded Nov 22, 2026. Parsers land in order: logback (Weekend 1),
syslog + apache (week 1 evenings), JSON-ish + dedupe (Weekend 2).
See CLAUDE.md for the build log.
