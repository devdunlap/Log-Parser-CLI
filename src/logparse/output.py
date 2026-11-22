"""Writers for parsed records: JSON lines and CSV."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .records import LogRecord

_BASE_COLUMNS = ["timestamp", "level", "source", "message"]


def write_jsonl(records: list[LogRecord], out_path: str | Path) -> None:
    with open(out_path, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def write_csv(records: list[LogRecord], out_path: str | Path) -> None:
    extra_keys = sorted({key for r in records for key in r.extra})
    columns = _BASE_COLUMNS + extra_keys
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for record in records:
            row = {col: getattr(record, col) for col in _BASE_COLUMNS}
            row.update({key: record.extra.get(key) for key in extra_keys})
            writer.writerow(row)


def write_rejects(rejects, out_path: str | Path) -> None:
    with open(out_path, "w", encoding="utf-8") as fh:
        for reject in rejects:
            fh.write(f"line {reject.line_number}: {reject.reason}\t{reject.raw}\n")
