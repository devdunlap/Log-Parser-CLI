"""Command-line interface: logparse parse / logparse dedupe.

Examples:
    logparse parse samples/app.log --format logback --out parsed.jsonl
    logparse parse samples/access.log --format apache --out parsed.csv --rejects rejects.txt
    logparse dedupe parsed.jsonl --out clean.jsonl
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from . import dedupe as dedupe_mod
from . import output, parsers


def _cmd_parse(args: argparse.Namespace) -> int:
    in_path = Path(args.input)
    lines = in_path.read_text(encoding="utf-8").splitlines()

    parser_fn = parsers.PARSERS[args.format]
    if args.format == "syslog":
        outcome = parser_fn(lines, year=date.today().year)
    else:
        outcome = parser_fn(lines)

    if args.out.endswith(".csv"):
        output.write_csv(outcome.records, args.out)
    else:
        output.write_jsonl(outcome.records, args.out)

    if args.rejects:
        output.write_rejects(outcome.rejects, args.rejects)

    print(
        f"lines in: {outcome.total_lines}  "
        f"parsed: {len(outcome.records)}  "
        f"rejected: {len(outcome.rejects)}"
    )
    return 0


def _cmd_dedupe(args: argparse.Namespace) -> int:
    report = dedupe_mod.dedupe_file(args.input, args.out)
    print(
        f"records in: {report.total_in}  kept: {report.kept}  "
        f"duplicates: {report.duplicates}"
    )
    for message, count in sorted(report.by_message.items()):
        print(f"  x{count}  {message}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logparse",
        description="Parse messy log files into clean structured records.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_parse = sub.add_parser("parse", help="Parse a log file into JSONL or CSV")
    p_parse.add_argument("input", help="Log file to parse")
    p_parse.add_argument(
        "--format",
        required=True,
        choices=sorted(parsers.PARSERS),
        help="Input log format",
    )
    p_parse.add_argument("--out", required=True, help="Output file (.jsonl or .csv)")
    p_parse.add_argument(
        "--rejects", help="Optional file for lines that could not be parsed"
    )
    p_parse.set_defaults(func=_cmd_parse)

    p_dedupe = sub.add_parser("dedupe", help="Flag duplicate records in a JSONL file")
    p_dedupe.add_argument("input", help="JSONL file produced by `logparse parse`")
    p_dedupe.add_argument("--out", required=True, help="Output JSONL with duplicates removed")
    p_dedupe.set_defaults(func=_cmd_dedupe)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
