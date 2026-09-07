import json
from pathlib import Path

from breath_to_photonics.validation_protocol import generate_run_plan


def test_locked_plan_counts_and_carryover_order() -> None:
    config = json.loads(Path("configs/benchtop_validation_v0.1.json").read_text())
    plan = generate_run_plan(config)
    assert len(plan) == 115
    assert plan["run_id"].is_unique
    assert plan["phase"].value_counts().to_dict() == {
        "recovery_precision": 63,
        "breakthrough": 18,
        "carryover": 14,
        "background_residual": 14,
        "system_blank": 6,
    }
    carryover = plan.loc[plan["phase"].eq("carryover")]
    assert carryover["condition"].tolist() == ["high_challenge", "immediate_blank"] * 7


def test_plan_is_reproducible() -> None:
    config = json.loads(Path("configs/benchtop_validation_v0.1.json").read_text())
    first = generate_run_plan(config)
    second = generate_run_plan(config)
    assert first.equals(second)
