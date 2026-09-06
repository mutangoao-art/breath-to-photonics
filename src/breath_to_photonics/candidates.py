"""Participant-level discovery and locked-cohort validation of VOC effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


NON_VOC = {"Unnamed: 0", "ID", "Diagnosis", "Sample", "CoreVisit"}


def hedges_g(case: np.ndarray, control: np.ndarray) -> float:
    """Bias-corrected standardized mean difference: case minus control."""
    case = np.asarray(case, dtype=float)
    control = np.asarray(control, dtype=float)
    n1, n0 = len(case), len(control)
    if n1 < 2 or n0 < 2:
        return float("nan")
    pooled_var = ((n1 - 1) * case.var(ddof=1) + (n0 - 1) * control.var(ddof=1)) / (n1 + n0 - 2)
    if pooled_var <= 0:
        return 0.0
    d = (case.mean() - control.mean()) / np.sqrt(pooled_var)
    correction = 1 - 3 / (4 * (n1 + n0) - 9)
    return float(correction * d)


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    """Benjamini-Hochberg adjusted p-values, preserving the input index."""
    values = p_values.to_numpy(dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted = ranked * len(values) / np.arange(1, len(values) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    output = np.empty_like(adjusted)
    output[order] = np.clip(adjusted, 0, 1)
    return pd.Series(output, index=p_values.index)


def participant_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Collapse repeated visits so each participant contributes once."""
    vocs = [column for column in frame.columns if column not in NON_VOC]
    diagnoses = frame.groupby("ID")["Diagnosis"].nunique()
    if (diagnoses > 1).any():
        raise ValueError("A participant has inconsistent diagnosis labels")
    compact = pd.concat([frame[["ID", "Diagnosis"]].copy(), frame[vocs].copy()], axis=1)
    return compact.groupby(["ID", "Diagnosis"], as_index=False)[vocs].mean()


def cohort_effects(frame: pd.DataFrame) -> pd.DataFrame:
    vocs = [column for column in frame.columns if column not in {"ID", "Diagnosis"}]
    rows = []
    for voc in vocs:
        case = frame.loc[frame["Diagnosis"].eq("Asthma"), voc].dropna().to_numpy()
        control = frame.loc[frame["Diagnosis"].eq("Not Asthma"), voc].dropna().to_numpy()
        test = stats.ttest_ind(case, control, equal_var=False)
        rows.append(
            {
                "voc": voc,
                "n_asthma": len(case),
                "n_not_asthma": len(control),
                "mean_asthma": float(case.mean()),
                "mean_not_asthma": float(control.mean()),
                "hedges_g": hedges_g(case, control),
                "welch_p": float(test.pvalue),
            }
        )
    result = pd.DataFrame(rows)
    result["fdr_q"] = benjamini_hochberg(result["welch_p"])
    return result


def bootstrap_ci(
    frame: pd.DataFrame, vocs: list[str], iterations: int, seed: int
) -> dict[str, tuple[float, float, float]]:
    """Participant-stratified bootstrap CI and direction stability for Hedges g."""
    rng = np.random.default_rng(seed)
    outputs: dict[str, tuple[float, float, float]] = {}
    for voc in vocs:
        case = frame.loc[frame["Diagnosis"].eq("Asthma"), voc].dropna().to_numpy()
        control = frame.loc[frame["Diagnosis"].eq("Not Asthma"), voc].dropna().to_numpy()
        observed = hedges_g(case, control)
        boot = np.array(
            [
                hedges_g(rng.choice(case, len(case), replace=True), rng.choice(control, len(control), replace=True))
                for _ in range(iterations)
            ]
        )
        stability = float(np.mean(np.sign(boot) == np.sign(observed))) if observed != 0 else 0.5
        outputs[voc] = (float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975)), stability)
    return outputs


def run_analysis(data_root: Path, config: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
    discovery_raw = pd.read_csv(data_root / str(config["discovery_file"]))
    validation_raw = pd.read_csv(data_root / str(config["validation_file"]))
    overlap = sorted(set(discovery_raw["ID"]) & set(validation_raw["ID"]))
    validation_raw = validation_raw.loc[~validation_raw["ID"].isin(overlap)].copy()

    discovery = participant_table(discovery_raw)
    validation = participant_table(validation_raw)
    discovery_effects = cohort_effects(discovery).add_prefix("discovery_").rename(columns={"discovery_voc": "voc"})
    validation_effects = cohort_effects(validation).add_prefix("validation_").rename(columns={"validation_voc": "voc"})
    results = discovery_effects.merge(validation_effects, on="voc", validate="one_to_one")
    results["discovery_candidate"] = (
        results["discovery_fdr_q"].le(float(config["discovery_fdr_threshold"]))
        & results["discovery_hedges_g"].abs().ge(float(config["discovery_absolute_hedges_g_threshold"]))
    )
    results["direction_agrees"] = np.sign(results["discovery_hedges_g"]) == np.sign(results["validation_hedges_g"])
    results["replicated"] = (
        results["discovery_candidate"]
        & results["direction_agrees"]
        & results["validation_hedges_g"].abs().ge(float(config["validation_absolute_hedges_g_threshold"]))
    )
    results["exploratory_direction_consistent"] = (
        results["direction_agrees"]
        & results["discovery_hedges_g"].abs().ge(0.20)
        & results["validation_hedges_g"].abs().ge(0.20)
    )

    selected_vocs = results.loc[results["discovery_candidate"], "voc"].tolist()
    if selected_vocs:
        ci_discovery = bootstrap_ci(discovery, selected_vocs, int(config["bootstrap_iterations"]), int(config["random_seed"]))
        ci_validation = bootstrap_ci(validation, selected_vocs, int(config["bootstrap_iterations"]), int(config["random_seed"]) + 1)
        for prefix, values in (("discovery", ci_discovery), ("validation", ci_validation)):
            results[f"{prefix}_g_ci_low"] = results["voc"].map(lambda voc: values.get(voc, (np.nan,) * 3)[0])
            results[f"{prefix}_g_ci_high"] = results["voc"].map(lambda voc: values.get(voc, (np.nan,) * 3)[1])
            results[f"{prefix}_direction_stability"] = results["voc"].map(lambda voc: values.get(voc, (np.nan,) * 3)[2])

    results = results.sort_values(
        ["replicated", "discovery_candidate", "discovery_fdr_q", "discovery_hedges_g"],
        ascending=[False, False, True, False],
    ).reset_index(drop=True)
    summary = {
        "status": "complete",
        "overlapping_participants_removed_from_validation": overlap,
        "discovery_participants": int(discovery["ID"].nunique()),
        "validation_participants": int(validation["ID"].nunique()),
        "tested_vocs": int(len(results)),
        "discovery_candidates": int(results["discovery_candidate"].sum()),
        "replicated_candidates": int(results["replicated"].sum()),
        "exploratory_direction_consistent_vocs": int(results["exploratory_direction_consistent"].sum()),
        "warning": "Exploratory observational effects are not validated biomarkers or causal findings.",
    }
    return results, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/analysis_v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/candidate_effects.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/candidate_summary.json"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    results, summary = run_analysis(args.data_root, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
