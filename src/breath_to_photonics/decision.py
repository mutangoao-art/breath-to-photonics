"""Consolidate project evidence into explicit continuation and stop gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_sources(config: dict[str, object]) -> dict[str, object]:
    loaded: dict[str, object] = {}
    for name, filename in config["sources"].items():
        path = Path(filename)
        loaded[name] = pd.read_csv(path) if path.suffix == ".csv" else json.loads(path.read_text())
    return loaded


def build_gates(data: dict[str, object], config: dict[str, object]) -> pd.DataFrame:
    audit = data["radica_audit"]
    candidates = data["candidate_summary"]
    spectra = data["spectral_summary"]
    quantitative = data["quantitative_summary"]
    identity = data["identity_confidence"]
    windows = data["alternative_windows"]
    noise = data["noise_budget"]
    precon = data["preconcentrator"]
    bench = data["benchtop_evaluation"]
    policy = config["policy"]

    audit_checks = audit["checks"]
    usable = all(
        audit_checks[key]
        for key in (
            "required_files_present",
            "diagnosis_has_two_classes",
            "all_id_visits_have_background_and_two_breath_replicates",
            "processed_cohorts_have_identical_voc_columns",
            "processed_data_have_no_missing_voc_values",
        )
    ) and len(candidates["overlapping_participants_removed_from_validation"]) == 3

    best = windows.loc[windows["rank_within_voc"].eq(1)].copy()
    best["interferent_ratio"] = (
        best["H2O_optical_depth"] + best["CO2_optical_depth"]
    ) / best["target_optical_depth"]
    minimum_ratio = float(best["interferent_ratio"].min())
    unresolved = int(identity["exact_msi_level_publicly_resolvable"].str.lower().ne("yes").sum())
    maximum_direct_snr = max(
        float(target["target_attenuation_ppm"]) for target in noise["targets"]
    )
    reference_lods = [
        float(target["white_noise_equivalent_lod_ppb"])
        for target in precon["reference_design"]
    ]

    rows = [
        {
            "gate": "public_clinical_data_integrity",
            "status": "pass" if usable else "fail",
            "evidence": "Required files, labels, matched triplets and processed matrices passed; three overlapping participants were removed from validation.",
            "implication": "The public release is usable for the locked analysis after overlap mitigation.",
            "source": "results/radica_audit.json; results/candidate_summary.json",
        },
        {
            "gate": "cross_cohort_clinical_replication",
            "status": "pass" if candidates["replicated_candidates"] >= policy["minimum_replicated_clinical_targets"] else "fail",
            "evidence": f"{candidates['replicated_candidates']} of {candidates['tested_vocs']} tested VOCs met the locked replication rule.",
            "implication": "No current VOC can be called a validated asthma biomarker.",
            "source": "results/candidate_summary.json",
        },
        {
            "gate": "experimental_gas_phase_reference",
            "status": "pass" if spectra["all_gas_phase"] and spectra["spectra_count"] == 5 else "partial",
            "evidence": f"Verified gas-phase NIST spectra exist for {spectra['spectra_count']} exploratory candidates.",
            "implication": "Band-location analysis is supported, but amplitudes are not mutually quantitative.",
            "source": "results/spectral_summary.json",
        },
        {
            "gate": "quantitative_target_spectra",
            "status": "partial",
            "evidence": f"Compatible NIST QUANT-IR coverage is {quantitative['quantitative_coverage']}.",
            "implication": "Only 2-butanone and toluene can enter the current quantitative model.",
            "source": "results/quantitative_summary.json",
        },
        {
            "gate": "compound_level_identity_confirmation",
            "status": "pass" if unresolved <= policy["maximum_identity_unresolved_targets_for_hardware_lock"] else "blocked",
            "evidence": f"Authentic-standard/MSI Level 1 status is unresolved for {unresolved} of {len(identity)} exploratory targets.",
            "implication": "A molecular target must not be frozen for hardware without standard confirmation.",
            "source": "results/identity_confidence.csv",
        },
        {
            "gate": "clean_atmospheric_window",
            "status": "pass" if minimum_ratio <= policy["maximum_interferent_to_target_ratio_for_clean_window"] else "fail",
            "evidence": f"The best modeled H2O+CO2 to target optical-depth ratio is {minimum_ratio:,.0f}:1.",
            "implication": "No clean single window was found in the downloaded 650–1250 cm-1 range.",
            "source": "results/alternative_windows.csv",
        },
        {
            "gate": "direct_10m_optical_detection",
            "status": "pass" if maximum_direct_snr >= policy["required_snr"] else "fail",
            "evidence": f"At 1 ppm relative transmission noise, the largest 10 m target SNR is {maximum_direct_snr:.2f}, below the required {policy['required_snr']:.0f}.",
            "implication": "Direct 10 m transmission is not supported at the literature mean concentrations.",
            "source": "results/noise_budget_summary.json",
        },
        {
            "gate": "preconcentration_assisted_feasibility",
            "status": "conditional",
            "evidence": f"The 500 mL to 5 mL, 80% recovery scenario predicts idealized LODs of {min(reference_lods):.3f}–{max(reference_lods):.3f} ppbv.",
            "implication": "The route is physically plausible on paper, but recovery and water removal dominate uncertainty.",
            "source": "results/preconcentrator_summary.json",
        },
        {
            "gate": "benchtop_validation",
            "status": "pending" if bench["overall_decision"] == "not_evaluable" else bench["overall_decision"],
            "evidence": f"Current evaluator decision: {bench['overall_decision']}.",
            "implication": "Certified-standard hardware measurements are required before optical integration.",
            "source": "results/benchtop_evaluation_summary.json",
        },
    ]
    return pd.DataFrame(rows)


def summarize(gates: pd.DataFrame) -> dict[str, object]:
    statuses = gates["status"].value_counts().to_dict()
    return {
        "status": "consolidated_project_decision",
        "gate_counts": statuses,
        "diagnostic_hardware_decision": "do_not_build_for_asthma_diagnosis",
        "methods_prototype_decision": "conditional_small_benchtop_validation_only",
        "reason": "Clinical replication failed, compound-level standard confirmation is unresolved, and no clean atmospheric window was found. A limited preconcentrator experiment can still test the measurement concept without making a diagnostic claim.",
        "next_action": "Run system blanks and the 500 mL certified-standard recovery block if laboratory hardware and safety approvals are available; otherwise stop at the documented negative feasibility result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/decision_gates_v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/decision_gates.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/decision_summary.json"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    gates = build_gates(load_sources(config), config)
    summary = summarize(gates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    gates.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
