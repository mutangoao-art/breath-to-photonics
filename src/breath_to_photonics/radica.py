"""Dataset-specific validation for the public RADicA release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


RAW = "RADicA_VOC_raw_peak_data.csv"
META = "RADicA_VOC_metadata.csv"
B1 = "RADicA_BG_adjusted_B1_outl_removed.csv"
B2 = "RADicA_BG_adjusted_B2_outl_removed.csv"
IDENTIFIERS = {"Unnamed: 0", "ID", "Diagnosis", "Sample", "CoreVisit"}


def _participant_counts(frame: pd.DataFrame) -> dict[str, int]:
    return {str(key): int(value) for key, value in frame.groupby("Diagnosis")["ID"].nunique().items()}


def audit_radica(root: Path) -> dict[str, object]:
    paths = {name: root / name for name in (RAW, META, B1, B2)}
    missing_files = [name for name, path in paths.items() if not path.exists()]
    if missing_files:
        return {"status": "fail", "missing_files": missing_files}

    raw = pd.read_csv(paths[RAW])
    meta = pd.read_csv(paths[META])
    b1 = pd.read_csv(paths[B1])
    b2 = pd.read_csv(paths[B2])

    sample_sets = meta.groupby(["ID", "CoreVisit"])["Sample"].agg(lambda x: set(x.dropna()))
    required_samples = {"MaskBG", "S1", "S2"}
    complete_pairs = int((sample_sets == required_samples).sum())
    voc_b1 = set(b1.columns) - IDENTIFIERS
    voc_b2 = set(b2.columns) - IDENTIFIERS
    overlapping_participants = sorted(set(b1["ID"]) & set(b2["ID"]))
    checks = {
        "required_files_present": True,
        "diagnosis_has_two_classes": meta["Diagnosis"].nunique() == 2,
        "all_id_visits_have_background_and_two_breath_replicates": complete_pairs == len(sample_sets),
        "processed_cohorts_have_identical_voc_columns": voc_b1 == voc_b2,
        "processed_data_have_no_missing_voc_values": not (b1[list(voc_b1)].isna().any().any() or b2[list(voc_b2)].isna().any().any()),
        "processed_cohorts_have_disjoint_participants": not overlapping_participants,
    }
    return {
        "status": "pass" if all(checks.values()) else "needs_review",
        "checks": checks,
        "raw": {
            "rows": int(raw.shape[0]),
            "voc_columns": int(raw.shape[1] - 3),
            "batches": {str(k): int(v) for k, v in raw["Batch"].value_counts().sort_index().items()},
            "missing_voc_fraction": float(raw.iloc[:, 3:].isna().mean().mean()),
        },
        "metadata": {
            "rows": int(meta.shape[0]),
            "participants": int(meta["ID"].nunique()),
            "participants_by_diagnosis": _participant_counts(meta),
            "id_visit_groups": int(len(sample_sets)),
            "complete_background_breath_triplets": complete_pairs,
        },
        "processed_cohorts": {
            "B1": {"rows": int(len(b1)), "participants": int(b1["ID"].nunique()), "participants_by_diagnosis": _participant_counts(b1)},
            "B2": {"rows": int(len(b2)), "participants": int(b2["ID"].nunique()), "participants_by_diagnosis": _participant_counts(b2)},
            "shared_voc_columns": int(len(voc_b1 & voc_b2)),
            "overlapping_participants": overlapping_participants,
        },
        "interpretation": "Required data are present, but B1/B2 are not participant-independent. The three overlapping participants must be assigned wholly to one analysis partition or excluded before validation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/radica_audit.json"))
    args = parser.parse_args()
    result = audit_radica(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"RADicA gate: {result['status']} -> {args.output}")


if __name__ == "__main__":
    main()
