"""Mass-balance and cycle-time scenarios for a breath VOC preconcentrator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


GAS_CONSTANT_J_MOL_K = 8.314462618
PASCAL_PER_ATM = 101325.0


def sample_amount_pmol(
    concentration_ppb: float,
    volume_ml: float,
    pressure_atm: float,
    temperature_K: float,
) -> float:
    """Return analyte amount in an ideal-gas sample."""
    total_moles = pressure_atm * PASCAL_PER_ATM * volume_ml * 1e-6 / (
        GAS_CONSTANT_J_MOL_K * temperature_K
    )
    return total_moles * concentration_ppb * 1e-9 * 1e12


def calculate_mass_balance(source: pd.DataFrame, config: dict[str, object]) -> pd.DataFrame:
    selected = source.loc[
        source["rank_within_voc"].eq(int(config["use_rank_within_voc"]))
    ]
    required_snr = float(config["required_snr"])
    noise_fraction = float(config["relative_transmission_noise_ppm"]) * 1e-6
    path_scale = float(config["optical_path_m"]) / float(config["baseline_path_m"])
    rows: list[dict[str, object]] = []
    for _, target in selected.iterrows():
        voc = str(target["voc"])
        reference_ppb = float(config["reference_concentrations_ppb"][voc])
        molar_mass = float(config["molar_masses_g_mol"][voc])
        for scenario in config["scenarios"]:
            sample_volume = float(scenario["sample_volume_ml"])
            desorption_volume = float(scenario["desorption_volume_ml"])
            recovery = float(scenario["recovery_fraction"])
            geometric_enrichment = sample_volume / desorption_volume
            net_enrichment = geometric_enrichment * recovery
            sampled_pmol = sample_amount_pmol(
                reference_ppb,
                sample_volume,
                float(config["pressure_atm"]),
                float(config["temperature_K"]),
            )
            recovered_pmol = sampled_pmol * recovery
            recovered_mass_ng = recovered_pmol * molar_mass / 1000.0
            desorbed_ppb = reference_ppb * net_enrichment
            target_tau = float(target["target_optical_depth"]) * path_scale * net_enrichment
            attenuation = 1.0 - np.exp(-target_tau)
            snr = attenuation / noise_fraction
            lod = reference_ppb * required_snr / snr
            collection_time = sample_volume / float(scenario["sample_flow_ml_min"])
            cycle_time = (
                collection_time
                + float(config["purge_time_min"])
                + float(config["desorption_and_transfer_time_min"])
                + float(config["reset_time_min"])
            )
            rows.append(
                {
                    "voc": voc,
                    "name": target["name"],
                    "scenario": scenario["scenario"],
                    "sample_volume_ml": sample_volume,
                    "sample_flow_ml_min": scenario["sample_flow_ml_min"],
                    "collection_time_min": collection_time,
                    "desorption_volume_ml": desorption_volume,
                    "recovery_fraction": recovery,
                    "geometric_enrichment_factor": geometric_enrichment,
                    "net_enrichment_factor": net_enrichment,
                    "sampled_target_pmol": sampled_pmol,
                    "recovered_target_pmol": recovered_pmol,
                    "recovered_target_mass_ng": recovered_mass_ng,
                    "desorbed_concentration_ppb": desorbed_ppb,
                    "target_attenuation_ppm": attenuation * 1e6,
                    "snr_at_reference_concentration": snr,
                    "white_noise_equivalent_lod_ppb": lod,
                    "cycle_time_min": cycle_time,
                    "maximum_cycles_per_8h": 480.0 / cycle_time,
                }
            )
    return pd.DataFrame(rows)


def make_summary(table: pd.DataFrame, config: dict[str, object]) -> dict[str, object]:
    reference = table.loc[table["scenario"].eq("reference design")]
    return {
        "status": "preconcentrator_mass_balance_and_timing_screen",
        "reference_design": reference[
            [
                "voc",
                "sample_volume_ml",
                "desorption_volume_ml",
                "recovery_fraction",
                "net_enrichment_factor",
                "recovered_target_pmol",
                "recovered_target_mass_ng",
                "desorbed_concentration_ppb",
                "white_noise_equivalent_lod_ppb",
                "cycle_time_min",
            ]
        ].to_dict("records"),
        "warning": config["warning"],
        "decision": "A 500 mL to 5 mL, 80% recovery cycle reproduces the prior 80x net-gain scenario in about 20.5 minutes, but analyte recovery and water management are now the dominant experimental unknowns.",
    }


def plot_scenarios(table: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2), layout="constrained")
    for name, group in table.groupby("name", sort=False):
        ax.plot(
            group["cycle_time_min"],
            group["white_noise_equivalent_lod_ppb"],
            marker="o",
            linewidth=1.5,
            label=name,
        )
    for _, group in table.groupby("scenario", sort=False):
        row = group.loc[group["white_noise_equivalent_lod_ppb"].idxmax()]
        is_rightmost = row["cycle_time_min"] == table["cycle_time_min"].max()
        ax.annotate(
            f"{row['net_enrichment_factor']:.0f}× net",
            (row["cycle_time_min"], row["white_noise_equivalent_lod_ppb"]),
            xytext=((-6 if is_rightmost else 6), 6),
            textcoords="offset points",
            fontsize=8,
            ha="right" if is_rightmost else "left",
        )
    ax.set_yscale("log")
    ax.set_xlabel("Estimated cycle time (min)")
    ax.set_ylabel("Idealized white-noise-equivalent 3σ LOD (ppbv)")
    ax.set_title("Preconcentrator sample-volume and recovery scenarios")
    ax.grid(alpha=0.2, which="both")
    ax.legend(frameon=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/preconcentrator_v0.1.json")
    )
    parser.add_argument("--output", type=Path, default=Path("results/preconcentrator.csv"))
    parser.add_argument(
        "--summary", type=Path, default=Path("results/preconcentrator_summary.json")
    )
    parser.add_argument(
        "--figure", type=Path, default=Path("results/figures/preconcentrator.png")
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = pd.read_csv(config["source_table"])
    result = calculate_mass_balance(source, config)
    summary = make_summary(result, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_scenarios(result, args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
