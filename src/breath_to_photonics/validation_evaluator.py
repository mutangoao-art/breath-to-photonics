"""Evaluate completed benchtop runs against the locked acceptance criteria."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .preconcentrator import sample_amount_pmol


TARGET_COLUMNS = {
    "Toluene": ("toluene_primary_pmol", "toluene_secondary_pmol"),
    "X2_Butanone": ("butanone_primary_pmol", "butanone_secondary_pmol"),
}
ACTUAL_COLUMNS = [
    "actual_sample_flow_ml_min",
    "actual_sample_volume_ml",
    "actual_relative_humidity_percent",
    "actual_temperature_K",
    "actual_pressure_atm",
    "actual_desorption_volume_ml",
]
TAU_COLUMNS = [
    "H2O_CO2_tau_pre_1030_75_cm-1",
    "H2O_CO2_tau_post_1030_75_cm-1",
    "H2O_CO2_tau_pre_939_20_cm-1",
    "H2O_CO2_tau_post_939_20_cm-1",
]


def required_measurements(plan: pd.DataFrame) -> dict[str, int]:
    """Count missing fields without treating missing measurements as zero."""
    missing: dict[str, int] = {}
    for column in ACTUAL_COLUMNS:
        missing[column] = int(pd.to_numeric(plan[column], errors="coerce").isna().sum())
    for primary, _ in TARGET_COLUMNS.values():
        missing[primary] = int(pd.to_numeric(plan[primary], errors="coerce").isna().sum())
    breakthrough = plan["phase"].eq("breakthrough")
    for _, secondary in TARGET_COLUMNS.values():
        missing[secondary] = int(
            pd.to_numeric(plan.loc[breakthrough, secondary], errors="coerce").isna().sum()
        )
    background = plan["phase"].eq("background_residual")
    for column in TAU_COLUMNS:
        missing[column] = int(
            pd.to_numeric(plan.loc[background, column], errors="coerce").isna().sum()
        )
    return {key: value for key, value in missing.items() if value > 0}


def _metric(
    rows: list[dict[str, object]],
    target: str,
    metric: str,
    condition: str,
    value: float,
    lower: float | None,
    upper: float | None,
) -> None:
    passed = bool(
        np.isfinite(value)
        and (lower is None or value >= lower)
        and (upper is None or value <= upper)
    )
    rows.append(
        {
            "target": target,
            "metric": metric,
            "condition": condition,
            "value": value,
            "lower_limit": lower,
            "upper_limit": upper,
            "passed": passed,
        }
    )


def evaluate(plan: pd.DataFrame, config: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
    missing = required_measurements(plan)
    if missing:
        return pd.DataFrame(
            columns=[
                "target", "metric", "condition", "value",
                "lower_limit", "upper_limit", "passed",
            ]
        ), {
            "status": "pending_missing_measurements",
            "overall_decision": "not_evaluable",
            "missing_counts": missing,
            "completed_required_fields": False,
        }

    numeric = ACTUAL_COLUMNS + TAU_COLUMNS
    for primary, secondary in TARGET_COLUMNS.values():
        numeric.extend([primary, secondary])
    data = plan.copy()
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    criteria = config["acceptance_criteria"]
    metrics: list[dict[str, object]] = []
    for target, (primary, secondary) in TARGET_COLUMNS.items():
        amount_per_ppb = data.apply(
            lambda row: sample_amount_pmol(
                1.0,
                row["actual_sample_volume_ml"],
                row["actual_pressure_atm"],
                row["actual_temperature_K"],
            ),
            axis=1,
        )
        data[f"{target}_input_equivalent_ppb"] = data[primary] / amount_per_ppb
        introduced = amount_per_ppb * data["input_concentration_ppb"]
        data[f"{target}_recovery_percent"] = 100.0 * data[primary] / introduced.replace(0, np.nan)

        recovery = data.loc[data["phase"].eq("recovery_precision")]
        grouped = recovery.groupby(
            ["input_concentration_ppb", "relative_humidity_percent"], sort=True
        )
        recovery_means: dict[tuple[float, float], float] = {}
        for (concentration, humidity), group in grouped:
            values = group[f"{target}_recovery_percent"]
            mean = float(values.mean())
            rsd = float(values.std(ddof=1) / mean * 100.0)
            condition = f"{concentration:g} ppbv, {humidity:g}% RH"
            recovery_means[(float(concentration), float(humidity))] = mean
            _metric(
                metrics,
                target,
                "mean_recovery_percent",
                condition,
                mean,
                float(criteria["recovery_percent_range"][0]),
                float(criteria["recovery_percent_range"][1]),
            )
            _metric(
                metrics,
                target,
                "recovery_rsd_percent",
                condition,
                rsd,
                None,
                float(criteria["recovery_rsd_percent_max"]),
            )
            if float(concentration) == min(config["calibration_concentrations_ppb"]):
                mdl = float(
                    group[f"{target}_input_equivalent_ppb"].std(ddof=1)
                    * float(config["low_level_mdl_multiplier_for_seven_replicates"])
                )
                _metric(
                    metrics,
                    target,
                    "seven_replicate_low_level_mdl_ppb",
                    condition,
                    mdl,
                    None,
                    float(criteria["white_noise_equivalent_lod_ppb_max"]),
                )

        for concentration in config["calibration_concentrations_ppb"]:
            dry = recovery_means[(float(concentration), 0.0)]
            for humidity in config["calibration_relative_humidity_percent"]:
                if float(humidity) == 0.0:
                    continue
                bias = abs(recovery_means[(float(concentration), float(humidity))] / dry - 1.0) * 100
                _metric(
                    metrics,
                    target,
                    "humidity_bias_percent",
                    f"{concentration:g} ppbv, {humidity:g}% RH versus dry",
                    bias,
                    None,
                    float(criteria["humidity_bias_percent_max"]),
                )

        blanks = data.loc[data["phase"].eq("system_blank")]
        for _, row in blanks.iterrows():
            _metric(
                metrics,
                target,
                "system_blank_ppb",
                str(row["run_id"]),
                float(row[f"{target}_input_equivalent_ppb"]),
                None,
                float(criteria["blank_ppb_max"]),
            )

        carryover = data.loc[data["phase"].eq("carryover")].reset_index(drop=True)
        for index in range(0, len(carryover), 2):
            challenge = carryover.iloc[index]
            blank = carryover.iloc[index + 1]
            percent = float(blank[primary] / challenge[primary] * 100.0)
            _metric(
                metrics,
                target,
                "carryover_percent",
                f"{challenge['run_id']} to {blank['run_id']}",
                percent,
                None,
                float(criteria["carryover_percent_of_previous_max"]),
            )
            _metric(
                metrics,
                target,
                "post_challenge_blank_ppb",
                str(blank["run_id"]),
                float(blank[f"{target}_input_equivalent_ppb"]),
                None,
                float(criteria["blank_ppb_max"]),
            )

        breakthrough = data.loc[data["phase"].eq("breakthrough")]
        for _, row in breakthrough.iterrows():
            total = row[primary] + row[secondary]
            percent = float(row[secondary] / total * 100.0)
            volume = float(row["sample_volume_ml"])
            upper = (
                float(criteria["breakthrough_percent_at_500ml_max"])
                if volume == 500.0
                else float(criteria["breakthrough_percent_at_1000ml_max"])
                if volume == 1000.0
                else None
            )
            if upper is not None:
                _metric(
                    metrics,
                    target,
                    "breakthrough_percent",
                    str(row["run_id"]),
                    percent,
                    None,
                    upper,
                )

    background = data.loc[data["phase"].eq("background_residual")]
    for suffix in ("1030_75", "939_20"):
        ratios = (
            background[f"H2O_CO2_tau_post_{suffix}_cm-1"]
            / background[f"H2O_CO2_tau_pre_{suffix}_cm-1"]
        )
        for run_id, value in zip(background["run_id"], ratios):
            _metric(
                metrics,
                "system",
                "post_treatment_background_tau_fraction",
                f"{run_id}, {suffix.replace('_', '.')} cm-1",
                float(value),
                None,
                float(criteria["post_treatment_background_optical_depth_fraction_max"]),
            )

    for _, row in data.iterrows():
        flow_error = abs(row["actual_sample_flow_ml_min"] / row["sample_flow_ml_min"] - 1) * 100
        volume_error = abs(row["actual_sample_volume_ml"] / row["sample_volume_ml"] - 1) * 100
        _metric(
            metrics, "system", "sample_flow_error_percent", str(row["run_id"]),
            float(flow_error), None, float(criteria["sample_flow_error_percent_max"]),
        )
        _metric(
            metrics, "system", "sample_volume_error_percent", str(row["run_id"]),
            float(volume_error), None, float(criteria["sample_volume_error_percent_max"]),
        )

    result = pd.DataFrame(metrics)
    system_pass = bool(result.loc[result["target"].eq("system"), "passed"].all())
    target_pass = {
        target: bool(result.loc[result["target"].eq(target), "passed"].all() and system_pass)
        for target in TARGET_COLUMNS
    }
    passed_count = sum(target_pass.values())
    decision = "pass" if passed_count == 2 else "conditional_pass" if passed_count == 1 else "fail"
    summary = {
        "status": "evaluation_complete",
        "overall_decision": decision,
        "target_pass": target_pass,
        "system_pass": system_pass,
        "metric_count": int(len(result)),
        "failed_metric_count": int((~result["passed"]).sum()),
    }
    return result, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_plan", type=Path, nargs="?", default=Path("results/benchtop_run_plan.csv"))
    parser.add_argument(
        "--config", type=Path, default=Path("configs/benchtop_validation_v0.1.json")
    )
    parser.add_argument("--output", type=Path, default=Path("results/benchtop_evaluation.csv"))
    parser.add_argument(
        "--summary", type=Path, default=Path("results/benchtop_evaluation_summary.json")
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    plan = pd.read_csv(args.run_plan, keep_default_na=True)
    result, summary = evaluate(plan, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
