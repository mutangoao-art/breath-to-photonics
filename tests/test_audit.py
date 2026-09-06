from pathlib import Path

import pandas as pd

from breath_to_photonics.audit import build_audit, match_fields


def test_match_fields_recognizes_common_schema_names() -> None:
    matched = match_fields(["Participant ID", "Diagnosis", "Study Cohort", "VOC Peak Area"])
    assert "Diagnosis" in matched["diagnosis"]
    assert "Study Cohort" in matched["cohort"]
    assert "VOC Peak Area" in matched["compound"]
    assert "VOC Peak Area" in matched["signal"]


def test_build_audit_records_shape_and_gate(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {
            "participant_id": [1, 2],
            "diagnosis": ["asthma", "not-asthma"],
            "cohort": ["discovery", "validation"],
            "sample_type": ["breath", "ambient air"],
            "compound": ["example-a", "example-a"],
            "peak_area": [3.0, None],
        }
    )
    frame.to_csv(tmp_path / "example.csv", index=False)
    audit = build_audit(tmp_path)
    assert audit["supported_file_count"] == 1
    assert audit["tables"][0]["rows"] == 2
    assert audit["tables"][0]["missing_fraction"]["peak_area"] == 0.5
    assert audit["provisional_gate"]["status"] == "pass"

