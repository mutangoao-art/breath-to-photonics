"""Evaluate loss of quantitative target signal as instrumental resolution broadens."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

from .quantitative import EXPECTED_Y_UNITS, path_for_attenuation, transmission
from .spectra import read_jcamp


def broaden(
    values: np.ndarray,
    spacing_cm1: float,
    source_fwhm_cm1: float,
    target_fwhm_cm1: float,
) -> np.ndarray:
    """Gaussian-broaden a uniformly sampled spectrum to a coarser target FWHM."""
    if target_fwhm_cm1 < source_fwhm_cm1:
        raise ValueError("Target resolution cannot be finer than the source spectrum")
    added_fwhm = np.sqrt(max(0.0, target_fwhm_cm1**2 - source_fwhm_cm1**2))
    sigma_points = added_fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0))) / spacing_cm1
    return gaussian_filter1d(values, sigma=sigma_points) if sigma_points > 0 else values.copy()


def evaluate(root: Path, config: dict[str, object]) -> pd.DataFrame:
    rows = []
    half_width = float(config["window_half_width_cm-1"])
    target_loss = float(config["target_attenuation_fraction"])
    path_m = float(config["reference_path_m"])
    for item in config["covered_targets"]:
        headers, frame = read_jcamp(root / item["file"])
        if headers.get("YUNITS", "").upper() != EXPECTED_Y_UNITS:
            raise ValueError(f"Unexpected quantitative units in {item['file']}")
        source_resolution = float(headers["RESOLUTION"])
        spacing = float(np.median(np.diff(frame["wavenumber_cm-1"])))
        center = float(item["window_center_cm-1"])
        concentration = float(item["evidence_reference_ppb"])
        in_window = frame["wavenumber_cm-1"].between(center - half_width, center + half_width).to_numpy()
        coefficients = frame["absorbance"].clip(lower=0.0).to_numpy()
        for resolution in config["instrument_resolutions_cm-1"]:
            broadened = broaden(coefficients, spacing, source_resolution, float(resolution))
            peak = float(broadened[in_window].max())
            rows.append(
                {
                    "voc": item["voc"],
                    "name": item["name"],
                    "center_cm-1": center,
                    "instrument_resolution_cm-1": float(resolution),
                    "peak_coefficient_per_ppm_m": peak,
                    "evidence_reference_ppb": concentration,
                    "attenuation_at_reference_path_fraction": 1.0
                    - transmission(peak, concentration, path_m),
                    "path_m_for_target_attenuation": path_for_attenuation(
                        peak, concentration, target_loss
                    ),
                }
            )
    result = pd.DataFrame(rows)
    minimum_resolution = min(config["instrument_resolutions_cm-1"])
    baseline = result.loc[
        result["instrument_resolution_cm-1"].eq(minimum_resolution)
    ].set_index("voc")
    result["peak_retained_fraction"] = result.apply(
        lambda row: row["peak_coefficient_per_ppm_m"]
        / baseline.loc[row["voc"], "peak_coefficient_per_ppm_m"],
        axis=1,
    )
    return result


def plot_resolution(table: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for name, group in table.groupby("name"):
        axes[0].plot(
            group["instrument_resolution_cm-1"],
            group["peak_retained_fraction"] * 100,
            marker="o",
            label=name,
        )
        axes[1].plot(
            group["instrument_resolution_cm-1"],
            group["path_m_for_target_attenuation"] / 1000,
            marker="o",
            label=name,
        )
    axes[0].set_ylabel("Peak coefficient retained (%)")
    axes[1].set_ylabel("Path for 1% peak attenuation (km)")
    for ax in axes:
        ax.set_xlabel("Instrument resolution FWHM (cm$^{-1}$)")
        ax.grid(alpha=0.2)
        ax.legend(frameon=False)
    fig.suptitle("Resolution sensitivity at literature asthma mean concentrations")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectra_root", type=Path)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/quantitative_manifest_v0.1.json")
    )
    parser.add_argument("--output", type=Path, default=Path("results/resolution_sensitivity.csv"))
    parser.add_argument(
        "--figure", type=Path, default=Path("results/figures/resolution_sensitivity.png")
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    table = evaluate(args.spectra_root, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    plot_resolution(table, args.figure)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
