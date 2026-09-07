"""Compare idealized photonic architectures against the target signal budget."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def compare_architectures(source: pd.DataFrame, config: dict[str, object]) -> pd.DataFrame:
    selected = source.loc[
        source["rank_within_voc"].eq(int(config["use_rank_within_voc"]))
    ]
    baseline_path = float(config["baseline_path_m"])
    required_snr = float(config["required_snr"])
    rows: list[dict[str, object]] = []
    for _, target in selected.iterrows():
        reference_ppb = float(config["reference_concentrations_ppb"][str(target["voc"])])
        baseline_target_tau = float(target["target_optical_depth"])
        baseline_background_tau = float(
            target["H2O_optical_depth"] + target["CO2_optical_depth"]
        )
        for scenario in config["scenarios"]:
            path_scale = float(scenario["effective_path_m"]) / baseline_path
            enrichment = float(scenario["target_enrichment_factor"])
            recovery = float(scenario["target_recovery_fraction"])
            residual = float(scenario["atmospheric_background_residual_fraction"])
            noise = float(scenario["relative_transmission_noise_ppm"]) * 1e-6
            target_tau = baseline_target_tau * path_scale * enrichment * recovery
            background_tau = baseline_background_tau * path_scale * residual
            target_loss = 1.0 - np.exp(-target_tau)
            snr = target_loss / noise
            lod = reference_ppb * required_snr / snr
            background_repeatability = (
                target_tau / required_snr / background_tau if background_tau > 0 else np.inf
            )
            rows.append(
                {
                    "voc": target["voc"],
                    "name": target["name"],
                    "center_cm-1": target["center_cm-1"],
                    "architecture": scenario["architecture"],
                    "scenario": scenario["scenario"],
                    "effective_path_m": scenario["effective_path_m"],
                    "target_enrichment_factor": enrichment,
                    "target_recovery_fraction": recovery,
                    "atmospheric_background_residual_fraction": residual,
                    "relative_transmission_noise_ppm": scenario[
                        "relative_transmission_noise_ppm"
                    ],
                    "reference_concentration_ppb": reference_ppb,
                    "target_attenuation_ppm": target_loss * 1e6,
                    "background_transmission": float(np.exp(-background_tau)),
                    "snr_at_reference_concentration": snr,
                    "white_noise_equivalent_lod_ppb": lod,
                    "maximum_background_tau_relative_error_ppm": (
                        background_repeatability * 1e6
                    ),
                }
            )
    return pd.DataFrame(rows)


def make_summary(table: pd.DataFrame, config: dict[str, object]) -> dict[str, object]:
    best = table.loc[table.groupby("voc")["white_noise_equivalent_lod_ppb"].idxmin()]
    return {
        "status": "idealized_architecture_scaling_comparison",
        "required_snr": config["required_snr"],
        "best_modeled_scenario_per_target": best[
            [
                "voc",
                "architecture",
                "scenario",
                "snr_at_reference_concentration",
                "white_noise_equivalent_lod_ppb",
                "background_transmission",
            ]
        ].to_dict("records"),
        "warning": config["warning"],
        "decision": "Preconcentration-assisted sensing is the only modeled route that improves target-to-atmospheric-background ratio; path enhancement alone improves white-noise SNR but not intrinsic background discrimination.",
    }


def plot_comparison(table: pd.DataFrame, output: Path) -> None:
    pivot = table.pivot(index="scenario", columns="name", values="white_noise_equivalent_lod_ppb")
    order = table["scenario"].drop_duplicates().tolist()
    pivot = pivot.reindex(order)
    ax = pivot.plot.bar(figsize=(9, 5.2), logy=True, rot=18, width=0.75)
    ax.set_ylabel("Idealized white-noise-equivalent 3σ LOD (ppbv)")
    ax.set_xlabel("")
    ax.set_title("Architecture scaling scenarios at 1 ppm relative transmission noise")
    ax.grid(axis="y", alpha=0.2, which="both")
    ax.legend(title="Target", frameon=False)
    ax.figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    ax.figure.savefig(output, dpi=220)
    plt.close(ax.figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/architecture_scenarios_v0.1.json")
    )
    parser.add_argument("--output", type=Path, default=Path("results/architecture_comparison.csv"))
    parser.add_argument(
        "--summary", type=Path, default=Path("results/architecture_comparison_summary.json")
    )
    parser.add_argument(
        "--figure", type=Path, default=Path("results/figures/architecture_comparison.png")
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = pd.read_csv(config["source_table"])
    result = compare_architectures(source, config)
    summary = make_summary(result, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_comparison(result, args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
