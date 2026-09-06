"""Audit public dataset files before modelling.

The audit is intentionally schema-agnostic: public repositories often change
filenames or column spelling. It records evidence instead of silently guessing.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


TABLE_SUFFIXES = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".json"}
FIELD_HINTS = {
    "sample_id": ("sample", "subject", "participant", "patient", "id"),
    "diagnosis": ("asthma", "diagnosis", "disease", "case", "status", "label"),
    "cohort": ("cohort", "site", "study", "batch", "discovery", "validation"),
    "sample_type": ("breath", "ambient", "air", "blank", "sample_type", "matrix"),
    "pairing": ("pair", "matched", "ambient_id", "background_id"),
    "compound": ("compound", "metabolite", "voc", "cas", "feature", "analyte"),
    "signal": ("intensity", "abundance", "area", "peak", "signal", "concentration"),
}


@dataclass(frozen=True)
class TableAudit:
    path: str
    format: str
    rows: int | None
    columns: int | None
    column_names: list[str]
    matched_fields: dict[str, list[str]]
    missing_fraction: dict[str, float]
    error: str | None = None


def discover_files(root: Path) -> list[Path]:
    """Return supported data files below *root* in stable order."""
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TABLE_SUFFIXES)


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".tsv", ".txt"}:
        return pd.read_csv(path, sep=None, engine="python")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported table format: {suffix}")


def match_fields(columns: Iterable[object]) -> dict[str, list[str]]:
    """Map conceptual requirements to columns whose names provide evidence."""
    names = [str(column) for column in columns]
    lowered = {name: name.casefold().replace("-", "_").replace(" ", "_") for name in names}
    return {
        field: [name for name, normalized in lowered.items() if any(hint in normalized for hint in hints)]
        for field, hints in FIELD_HINTS.items()
    }


def inspect_table(path: Path, base: Path | None = None) -> TableAudit:
    """Read one table and summarize its schema and missingness."""
    display_path = str(path.relative_to(base)) if base and path.is_relative_to(base) else str(path)
    try:
        frame = _read_table(path)
        columns = [str(column) for column in frame.columns]
        missing = {str(column): round(float(value), 6) for column, value in frame.isna().mean().items()}
        return TableAudit(
            path=display_path,
            format=path.suffix.lower().lstrip("."),
            rows=int(frame.shape[0]),
            columns=int(frame.shape[1]),
            column_names=columns,
            matched_fields=match_fields(columns),
            missing_fraction=missing,
        )
    except Exception as exc:  # preserve the failure as audit evidence
        return TableAudit(
            path=display_path,
            format=path.suffix.lower().lstrip("."),
            rows=None,
            columns=None,
            column_names=[],
            matched_fields={},
            missing_fraction={},
            error=f"{type(exc).__name__}: {exc}",
        )


def build_audit(root: Path) -> dict[str, object]:
    files = discover_files(root)
    tables = [inspect_table(path, root) for path in files]
    evidence = {
        field: sorted({column for table in tables for column in table.matched_fields.get(field, [])})
        for field in FIELD_HINTS
    }
    required = ("diagnosis", "cohort", "sample_type", "compound", "signal")
    return {
        "root": str(root.resolve()),
        "supported_file_count": len(files),
        "readable_table_count": sum(table.error is None for table in tables),
        "requirement_evidence": evidence,
        "provisional_gate": {
            "status": "pass" if all(evidence[key] for key in required) else "needs_review",
            "note": "Column-name evidence is provisional; values and sample pairing require manual verification.",
        },
        "tables": [asdict(table) for table in tables],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory containing downloaded public data")
    parser.add_argument("--output", type=Path, default=Path("results/data_audit.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Audited {audit['supported_file_count']} files; result: {args.output}")


if __name__ == "__main__":
    main()

