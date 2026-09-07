"""Search quantitative target spectra for lower-interference HITRAN windows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from .hitran_interference import (
    instrument_convolve,
    lorentz_cross_section,
    number_density_cm3,
    read_hitran_160,
)
from .resolution import broaden
from .spectra import read_jcamp


def search_windows(
    hitran_root: Path,
    target_root: Path,
    hitran_config: dict[str, object],
    search_config: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, object]]:
    lines = read_hitran_160(hitran_root / hitran_config["hitran_file"])
    lo, hi = [float(value) for value in search_config["search_range_cm-1"]]
    step = float(hitran_config["grid_step_cm-1"])
    grid = np.arange(lo, hi + step / 2.0, step)
    pressure = float(hitran_config["pressure_atm"])
    temperature = float(hitran_config["temperature_K"])
    path_m = float(hitran_config["path_length_m"])
    path_cm = path_m * 100.0
    fwhm = float(hitran_config["instrument_fwhm_cm-1"])
    wing = float(hitran_config["line_wing_cm-1"])
    fractions = hitran_config["mole_fractions"]

    optical_depths = {}
    for gas, molecule_id in {"H2O": 1, "CO2": 2}.items():
        fraction = float(fractions[gas])
        cross_section = lorentz_cross_section(
            lines.loc[lines["molecule_id"].eq(molecule_id)],
            grid,
            fraction,
            pressure,
            wing,
        )
        cross_section = instrument_convolve(cross_section, step, fwhm)
        optical_depths[gas] = (
            cross_section
            * number_density_cm3(fraction, pressure, temperature)
            * path_cm
        )
    interferent_tau = optical_depths["H2O"] + optical_depths["CO2"]
    background_transmission = np.exp(-interferent_tau)

    rows = []
    floor = float(search_config["score_floor_optical_depth"])
    for item in hitran_config["windows"]:
        headers, target = read_jcamp(target_root / item["target_quant_file"])
        target_values = broaden(
            target["absorbance"].clip(lower=0.0).to_numpy(),
            float(headers["DELTAX"]),
            float(headers["RESOLUTION"]),
            fwhm,
        )
        coefficient = np.interp(grid, target["wavenumber_cm-1"], target_values)
        target_tau = (
            np.log(10.0)
            * coefficient
            * float(item["target_concentration_ppb"])
            / 1000.0
            * path_m
        )
        prominence = float(search_config["minimum_relative_peak_prominence"]) * float(coefficient.max())
        distance = max(1, int(float(search_config["minimum_peak_spacing_cm-1"]) / step))
        peaks, properties = find_peaks(coefficient, prominence=prominence, distance=distance)
        for peak, peak_prominence in zip(peaks, properties["prominences"]):
            score = target_tau[peak] * background_transmission[peak] / (interferent_tau[peak] + floor)
            rows.append(
                {
                    "voc": item["voc"],
                    "name": item["name"],
                    "center_cm-1": round(float(grid[peak]), 3),
                    "center_um": round(10000.0 / float(grid[peak]), 4),
                    "target_optical_depth": float(target_tau[peak]),
                    "H2O_optical_depth": float(optical_depths["H2O"][peak]),
                    "CO2_optical_depth": float(optical_depths["CO2"][peak]),
                    "background_transmission": float(background_transmission[peak]),
                    "target_peak_prominence": float(peak_prominence),
                    "search_score": float(score),
                }
            )
    result = pd.DataFrame(rows)
    result["rank_within_voc"] = result.groupby("voc")["search_score"].rank(
        ascending=False, method="first"
    ).astype(int)
    result = result.sort_values(["voc", "rank_within_voc"])
    maximum_rank = int(search_config["maximum_rank_per_target"])
    result = result.loc[result["rank_within_voc"].le(maximum_rank)].copy()
    best = result.loc[result["rank_within_voc"].eq(1)]
    summary = {
        "status": "alternative_window_search_at_296K",
        "search_range_cm-1": [lo, hi],
        "best_windows": best[
            [
                "voc",
                "center_cm-1",
                "center_um",
                "target_optical_depth",
                "H2O_optical_depth",
                "CO2_optical_depth",
                "background_transmission",
                "search_score",
            ]
        ].to_dict("records"),
        "warning": search_config["warning"],
    }
    return result, summary


def plot_candidates(table: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(
        len(table["voc"].unique()),
        1,
        figsize=(9, 6.5),
        squeeze=False,
        layout="constrained",
    )
    for ax, (voc, group) in zip(axes[:, 0], table.groupby("voc", sort=False)):
        scatter = ax.scatter(
            group["center_cm-1"],
            group["target_optical_depth"],
            c=group["background_transmission"],
            s=90 / np.sqrt(group["rank_within_voc"]),
            cmap="viridis",
            vmin=0,
            vmax=1,
        )
        best = group.loc[group["rank_within_voc"].eq(1)].iloc[0]
        ax.annotate(
            f"best proxy: {best['center_cm-1']:.1f} cm$^{{-1}}$",
            (best["center_cm-1"], best["target_optical_depth"]),
            xytext=(8, 8),
            textcoords="offset points",
        )
        ax.set_yscale("log")
        ax.set_ylabel("Target optical depth")
        ax.set_title(group.iloc[0]["name"])
        ax.grid(alpha=0.15)
        ax.invert_xaxis()
    axes[-1, 0].set_xlabel("Candidate peak center (cm$^{-1}$)")
    fig.colorbar(
        scatter,
        ax=axes[:, 0],
        label="H2O + CO2 background transmission",
        pad=0.03,
        shrink=0.9,
    )
    fig.suptitle("Alternative-window search proxy (296 K baseline, 10 m)")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hitran_root", type=Path)
    parser.add_argument("target_root", type=Path)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/alternative_window_search_v0.1.json")
    )
    parser.add_argument("--output", type=Path, default=Path("results/alternative_windows.csv"))
    parser.add_argument(
        "--summary", type=Path, default=Path("results/alternative_windows_summary.json")
    )
    parser.add_argument(
        "--figure", type=Path, default=Path("results/figures/alternative_windows.png")
    )
    args = parser.parse_args()
    search_config = json.loads(args.config.read_text(encoding="utf-8"))
    hitran_config = json.loads(Path(search_config["hitran_config"]).read_text(encoding="utf-8"))
    table, summary = search_windows(args.hitran_root, args.target_root, hitran_config, search_config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_candidates(table, args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
