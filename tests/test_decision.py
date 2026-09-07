import json
from pathlib import Path

from breath_to_photonics.decision import build_gates, load_sources, summarize


def test_current_decision_gates_are_explicit() -> None:
    config = json.loads(Path("configs/decision_gates_v0.1.json").read_text())
    gates = build_gates(load_sources(config), config).set_index("gate")
    assert gates.loc["public_clinical_data_integrity", "status"] == "pass"
    assert gates.loc["cross_cohort_clinical_replication", "status"] == "fail"
    assert gates.loc["compound_level_identity_confirmation", "status"] == "blocked"
    assert gates.loc["clean_atmospheric_window", "status"] == "fail"
    assert gates.loc["benchtop_validation", "status"] == "pending"


def test_current_overall_decision_separates_diagnostic_and_methods_work() -> None:
    config = json.loads(Path("configs/decision_gates_v0.1.json").read_text())
    summary = summarize(build_gates(load_sources(config), config))
    assert summary["diagnostic_hardware_decision"] == "do_not_build_for_asthma_diagnosis"
    assert summary["methods_prototype_decision"] == "conditional_small_benchtop_validation_only"
