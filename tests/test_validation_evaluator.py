import json
from pathlib import Path

from breath_to_photonics.preconcentrator import sample_amount_pmol
from breath_to_photonics.validation_evaluator import evaluate
from breath_to_photonics.validation_protocol import generate_run_plan


def completed_passing_plan():
    config = json.loads(Path("configs/benchtop_validation_v0.1.json").read_text())
    plan = generate_run_plan(config)
    plan["actual_sample_flow_ml_min"] = plan["sample_flow_ml_min"]
    plan["actual_sample_volume_ml"] = plan["sample_volume_ml"]
    plan["actual_relative_humidity_percent"] = plan["relative_humidity_percent"]
    plan["actual_temperature_K"] = 296.0
    plan["actual_pressure_atm"] = 1.0
    plan["actual_desorption_volume_ml"] = 5.0
    for index, row in plan.iterrows():
        per_ppb = sample_amount_pmol(1, row["sample_volume_ml"], 1, 296)
        input_ppb = row["input_concentration_ppb"]
        primary_ppb = input_ppb * 0.8 if input_ppb > 0 else 0.005
        for prefix in ("toluene", "butanone"):
            primary = primary_ppb * per_ppb
            plan.loc[index, f"{prefix}_primary_pmol"] = primary
            plan.loc[index, f"{prefix}_secondary_pmol"] = (
                primary * 0.02 / 0.98 if row["phase"] == "breakthrough" else 0.0
            )
    for column in (
        "H2O_CO2_tau_pre_1030_75_cm-1",
        "H2O_CO2_tau_pre_939_20_cm-1",
    ):
        plan[column] = 1.0
    for column in (
        "H2O_CO2_tau_post_1030_75_cm-1",
        "H2O_CO2_tau_post_939_20_cm-1",
    ):
        plan[column] = 0.005
    return plan, config


def test_blank_template_is_not_evaluable() -> None:
    config = json.loads(Path("configs/benchtop_validation_v0.1.json").read_text())
    result, summary = evaluate(generate_run_plan(config), config)
    assert result.empty
    assert summary["overall_decision"] == "not_evaluable"
    assert summary["missing_counts"]


def test_completed_plan_passes() -> None:
    plan, config = completed_passing_plan()
    result, summary = evaluate(plan, config)
    assert summary["overall_decision"] == "pass"
    assert summary["failed_metric_count"] == 0
    assert result["passed"].all()


def test_high_blank_fails_both_targets() -> None:
    plan, config = completed_passing_plan()
    blank_index = plan.index[plan["phase"].eq("system_blank")][0]
    per_ppb = sample_amount_pmol(1, plan.loc[blank_index, "sample_volume_ml"], 1, 296)
    plan.loc[blank_index, "toluene_primary_pmol"] = 0.03 * per_ppb
    _, summary = evaluate(plan, config)
    assert summary["overall_decision"] == "conditional_pass"
    assert summary["target_pass"] == {"Toluene": False, "X2_Butanone": True}
