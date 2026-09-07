"""Translate target optical depths into measurement and background-stability requirements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_budget(table: pd.DataFrame, config: dict[str, object]) -> pd.DataFrame:
    """Return noise scenarios for the selected alternative window of each target."""
    selected = table.loc[
        table["rank_within_voc"].eq(int(config["use_rank_within_voc"]))
    ].copy()
    required_snr = float(config["required_snr"])
    rows: list[dict[str, object]] = []
    for _, item in selected.iterrows():
        target_tau = float(item["target_optical_depth"])
        background_tau = float(item["H2O_optical_depth"] + item["CO2_optical_depth"])
        target_loss = 1.0 - np.exp(-target_tau)
        maximum_noise = target_loss / required_snr
        maximum_background_tau_error = target_tau / required_snr
        maximum_background_relative_error = maximum_background_tau_error / background_tau
        for noise_ppm in config["relative_transmission_noise_ppm_scenarios"]:
            noise_fraction = float(noise_ppm) * 1e-6
            reference_ppb = float(config["reference_concentrations_ppb"][str(item["voc"])])
            concentration_lod = reference_ppb * required_snr * noise_fraction / target_loss
            rows.append(
                {
                    "voc": item["voc"],
                    "name": item["name"],
                    "center_cm-1": item["center_cm-1"],
                    "reference_concentration_ppb": reference_ppb,
                    "target_attenuation_fraction": target_loss,
                    "target_attenuation_ppm": target_loss * 1e6,
                    "required_snr": required_snr,
                    "maximum_relative_transmission_noise_ppm": maximum_noise * 1e6,
                    "background_optical_depth": background_tau,
                    "maximum_background_optical_depth_error": maximum_background_tau_error,
                    "maximum_background_optical_depth_relative_error_ppm": (
                        maximum_background_relative_error * 1e6
                    ),
                    "assumed_relative_transmission_noise_ppm": float(noise_ppm),
                    "white_noise_equivalent_lod_ppb": concentration_lod,
                }
            )
    return pd.DataFrame(rows)


def summarize(table: pd.DataFrame, config: dict[str, object]) -> dict[str, object]:
    unique = table.drop_duplicates("voc")
    return {
        "status": "instrument_noise_and_background_repeatability_screen",
        "required_snr": float(config["required_snr"]),
        "targets": unique[
            [
                "voc",
                "center_cm-1",
                "target_attenuation_ppm",
                "maximum_relative_transmission_noise_ppm",
                "maximum_background_optical_depth_relative_error_ppm",
            ]
        ].to_dict("records"),
        "interpretation": config["interpretation"],
        "warning": "These values are necessary idealized precision requirements, not demonstrated instrument performance or validated limits of detection.",
    }


def plot_budget(table: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.8), layout="constrained")
    for _, group in table.groupby("name", sort=False):
        line = ax.plot(
            group["assumed_relative_transmission_noise_ppm"],
            group["white_noise_equivalent_lod_ppb"],
            marker="o",
            label=group.iloc[0]["name"],
        )[0]
        ax.axhline(
            group.iloc[0]["reference_concentration_ppb"],
            linestyle="--",
            linewidth=0.8,
            alpha=0.6,
            color=line.get_color(),
            label=f"{group.iloc[0]['name']} reference mean",
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Relative transmission noise (ppm, 1σ equivalent)")
    ax.set_ylabel("White-noise-equivalent 3σ LOD (ppbv)")
    ax.set_title("Idealized optical noise requirement at best searched windows")
    ax.grid(alpha=0.2, which="both")
    ax.legend(frameon=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/noise_budget_v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/noise_budget.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/noise_budget_summary.json"))
    parser.add_argument("--figure", type=Path, default=Path("results/figures/noise_budget.png"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = pd.read_csv(config["source_table"])
    result = calculate_budget(source, config)
    summary = summarize(result, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_budget(result, args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
