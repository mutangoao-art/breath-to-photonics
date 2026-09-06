"""Partial quantitative Beer-Lambert screen using NIST absorption coefficients."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .spectra import read_jcamp


EXPECTED_Y_UNITS = "(MICROMOL/MOL)-1M-1 (BASE 10)"


def transmission(coefficient_per_ppm_m: float, concentration_ppb: float, path_m: float) -> float:
    """Return base-10 Beer-Lambert transmission for a coefficient in ppm^-1 m^-1."""
    absorbance = coefficient_per_ppm_m * (concentration_ppb / 1000.0) * path_m
    return 10.0 ** (-absorbance)


def path_for_attenuation(
    coefficient_per_ppm_m: float, concentration_ppb: float, attenuation_fraction: float
) -> float:
    """Return the path needed to reach a specified fractional intensity loss."""
    if coefficient_per_ppm_m <= 0 or concentration_ppb <= 0:
        return float("inf")
    target_absorbance = -np.log10(1.0 - attenuation_fraction)
    return float(target_absorbance / (coefficient_per_ppm_m * concentration_ppb / 1000.0))


def summarize_target(root: Path, item: dict[str, object], config: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    headers, frame = read_jcamp(root / str(item["file"]))
    if headers.get("$NIST SOURCE", "").upper() != "QUANT-IR":
        raise ValueError(f"{item['file']} is not labelled as NIST QUANT-IR")
    if headers.get("YUNITS", "").upper() != EXPECTED_Y_UNITS:
        raise ValueError(f"Unexpected quantitative units in {item['file']}: {headers.get('YUNITS')}")

    center = float(item["window_center_cm-1"])
    half_width = float(config["window_half_width_cm-1"])
    window = frame.loc[frame["wavenumber_cm-1"].between(center - half_width, center + half_width)].copy()
    positive = window["absorbance"].clip(lower=0.0)
    peak_coefficient = float(positive.max())
    mean_coefficient = float(positive.mean())
    reference_ppb = float(config["reference_concentration_ppb"])
    reference_path = float(config["reference_path_m"])
    target_loss = float(config["target_attenuation_fraction"])

    summary = {
        "voc": item["voc"],
        "name": item["name"],
        "cas": item["cas"],
        "window_center_cm-1": center,
        "window_half_width_cm-1": half_width,
        "resolution_cm-1": float(headers["RESOLUTION"]),
        "peak_coefficient_per_ppm_m": peak_coefficient,
        "window_mean_coefficient_per_ppm_m": mean_coefficient,
        "reference_ppb": reference_ppb,
        "reference_path_m": reference_path,
        "peak_attenuation_fraction": 1.0 - transmission(peak_coefficient, reference_ppb, reference_path),
        "window_mean_attenuation_fraction": 1.0 - transmission(mean_coefficient, reference_ppb, reference_path),
        "path_m_for_target_attenuation_peak": path_for_attenuation(peak_coefficient, reference_ppb, target_loss),
        "path_m_for_target_attenuation_window_mean": path_for_attenuation(mean_coefficient, reference_ppb, target_loss),
    }
    rows = []
    for concentration in config["concentrations_ppb"]:
        for path_m in config["path_lengths_m"]:
            rows.append(
                {
                    "voc": item["voc"],
                    "name": item["name"],
                    "center_cm-1": center,
                    "concentration_ppb": float(concentration),
                    "path_m": float(path_m),
                    "peak_attenuation_fraction": 1.0 - transmission(peak_coefficient, float(concentration), float(path_m)),
                    "window_mean_attenuation_fraction": 1.0 - transmission(mean_coefficient, float(concentration), float(path_m)),
                }
            )
    return summary, rows


def plot_detectability(summaries: list[dict[str, object]], concentrations: list[float], output: Path) -> None:
    paths = np.logspace(-1, 3, 300)
    fig, axes = plt.subplots(1, len(summaries), figsize=(10, 4), sharey=True, squeeze=False)
    for ax, summary in zip(axes[0], summaries):
        coefficient = float(summary["peak_coefficient_per_ppm_m"])
        for concentration in concentrations:
            loss = 1.0 - np.power(10.0, -coefficient * (concentration / 1000.0) * paths)
            ax.plot(paths, loss * 100.0, label=f"{concentration:g} ppb")
        ax.axhline(1.0, color="black", linestyle="--", linewidth=0.8, label="1% attenuation")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"{summary['name']} at {summary['window_center_cm-1']:.0f} cm$^{{-1}}$")
        ax.set_xlabel("Optical path (m)")
        ax.grid(alpha=0.2, which="both")
    axes[0, 0].set_ylabel("Peak attenuation (%)")
    axes[0, -1].legend(frameon=False, fontsize=8)
    fig.suptitle("NIST QUANT-IR Beer–Lambert bounds (target-only; no breath matrix)")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def run(root: Path, config: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
    summaries = []
    rows: list[dict[str, object]] = []
    for item in config["covered_targets"]:
        summary, target_rows = summarize_target(root, item, config)
        summaries.append(summary)
        rows.extend(target_rows)
    output_summary = {
        "status": "partial_target_only_bound",
        "quantitative_coverage": f"{len(summaries)}/{len(summaries) + len(config['uncovered_targets'])}",
        "covered_targets": summaries,
        "uncovered_targets": config["uncovered_targets"],
        "warning": "Target-only Beer-Lambert bounds are not LODs and exclude H2O, CO2, other VOCs, noise, drift, and sampling losses.",
    }
    return pd.DataFrame(rows), output_summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectra_root", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/quantitative_manifest_v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/quantitative_detectability.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/quantitative_summary.json"))
    parser.add_argument("--figure", type=Path, default=Path("results/figures/quantitative_detectability.png"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    table, summary = run(args.spectra_root, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_detectability(summary["covered_targets"], [float(value) for value in config["concentrations_ppb"]], args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
