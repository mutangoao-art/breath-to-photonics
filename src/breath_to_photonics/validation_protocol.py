"""Generate the locked benchtop preconcentrator validation run plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _base_row(config: dict[str, object]) -> dict[str, object]:
    return {
        "target_standard": "+".join(config["targets"]),
        "sample_flow_ml_min": config["default_sample_flow_ml_min"],
        "secondary_trap_required": False,
        "acceptance_metric": "",
        "actual_sample_flow_ml_min": np.nan,
        "actual_sample_volume_ml": np.nan,
        "actual_relative_humidity_percent": np.nan,
        "actual_temperature_K": np.nan,
        "actual_pressure_atm": np.nan,
        "actual_desorption_volume_ml": np.nan,
        "toluene_primary_pmol": np.nan,
        "toluene_secondary_pmol": np.nan,
        "butanone_primary_pmol": np.nan,
        "butanone_secondary_pmol": np.nan,
        "H2O_CO2_tau_pre_1030_75_cm-1": np.nan,
        "H2O_CO2_tau_post_1030_75_cm-1": np.nan,
        "H2O_CO2_tau_pre_939_20_cm-1": np.nan,
        "H2O_CO2_tau_post_939_20_cm-1": np.nan,
        "deviation_or_note": "",
    }


def generate_run_plan(config: dict[str, object]) -> pd.DataFrame:
    rng = np.random.default_rng(int(config["random_seed"]))
    rows: list[dict[str, object]] = []

    def add_system_blanks(count: int, location: str) -> None:
        for replicate in range(1, count + 1):
            rows.append(
                {
                    **_base_row(config),
                    "phase": "system_blank",
                    "condition": location,
                    "replicate": replicate,
                    "input_concentration_ppb": 0.0,
                    "relative_humidity_percent": 0.0,
                    "sample_volume_ml": config["default_sample_volume_ml"],
                    "acceptance_metric": "blank_ppb",
                }
            )

    add_system_blanks(int(config["system_blank_replicates_start"]), "sequence_start")

    calibration = []
    for concentration in config["calibration_concentrations_ppb"]:
        for humidity in config["calibration_relative_humidity_percent"]:
            for replicate in range(1, int(config["calibration_replicates"]) + 1):
                calibration.append(
                    {
                        **_base_row(config),
                        "phase": "recovery_precision",
                        "condition": f"{concentration:g}ppb_{humidity:g}RH",
                        "replicate": replicate,
                        "input_concentration_ppb": concentration,
                        "relative_humidity_percent": humidity,
                        "sample_volume_ml": config["default_sample_volume_ml"],
                        "acceptance_metric": "recovery_and_rsd",
                    }
                )
    rows.extend(calibration[index] for index in rng.permutation(len(calibration)))

    breakthrough = []
    for volume in config["breakthrough_volumes_ml"]:
        for humidity in config["breakthrough_relative_humidity_percent"]:
            for replicate in range(1, int(config["breakthrough_replicates"]) + 1):
                breakthrough.append(
                    {
                        **_base_row(config),
                        "phase": "breakthrough",
                        "condition": f"{volume:g}mL_{humidity:g}RH",
                        "replicate": replicate,
                        "input_concentration_ppb": config["breakthrough_concentration_ppb"],
                        "relative_humidity_percent": humidity,
                        "sample_volume_ml": volume,
                        "secondary_trap_required": True,
                        "acceptance_metric": "secondary_trap_percent",
                    }
                )
    rows.extend(breakthrough[index] for index in rng.permutation(len(breakthrough)))

    for pair in range(1, int(config["carryover_pairs"]) + 1):
        for condition, concentration in (
            ("high_challenge", config["carryover_challenge_ppb"]),
            ("immediate_blank", 0.0),
        ):
            rows.append(
                {
                    **_base_row(config),
                    "phase": "carryover",
                    "condition": condition,
                    "replicate": pair,
                    "input_concentration_ppb": concentration,
                    "relative_humidity_percent": config[
                        "carryover_relative_humidity_percent"
                    ],
                    "sample_volume_ml": config["default_sample_volume_ml"],
                    "acceptance_metric": "carryover_percent" if concentration == 0 else "challenge",
                }
            )

    background = []
    for humidity in config["background_residual_relative_humidity_percent"]:
        for replicate in range(1, int(config["background_residual_replicates"]) + 1):
            background.append(
                {
                    **_base_row(config),
                    "phase": "background_residual",
                    "condition": f"zero_air_{humidity:g}RH",
                    "replicate": replicate,
                    "input_concentration_ppb": 0.0,
                    "relative_humidity_percent": humidity,
                    "sample_volume_ml": config["default_sample_volume_ml"],
                    "acceptance_metric": "post_treatment_background_optical_depth",
                }
            )
    rows.extend(background[index] for index in rng.permutation(len(background)))
    add_system_blanks(int(config["system_blank_replicates_end"]), "sequence_end")

    plan = pd.DataFrame(rows)
    plan.insert(0, "run_id", [f"BV-{index:03d}" for index in range(1, len(plan) + 1)])
    return plan


def summarize(plan: pd.DataFrame, config: dict[str, object]) -> dict[str, object]:
    return {
        "status": "locked_benchtop_validation_plan",
        "total_runs": int(len(plan)),
        "runs_by_phase": plan["phase"].value_counts(sort=False).to_dict(),
        "acceptance_criteria": config["acceptance_criteria"],
        "warning": config["warning"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/benchtop_validation_v0.1.json")
    )
    parser.add_argument("--output", type=Path, default=Path("results/benchtop_run_plan.csv"))
    parser.add_argument(
        "--summary", type=Path, default=Path("results/benchtop_run_plan_summary.json")
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    plan = generate_run_plan(config)
    summary = summarize(plan, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plan.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
