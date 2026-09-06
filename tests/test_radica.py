from pathlib import Path

from breath_to_photonics.radica import audit_radica


def test_audit_reports_missing_required_files(tmp_path: Path) -> None:
    result = audit_radica(tmp_path)
    assert result["status"] == "fail"
    assert "RADicA_VOC_metadata.csv" in result["missing_files"]

