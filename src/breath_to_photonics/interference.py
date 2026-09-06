"""Shape-only screen for spectral overlap with H2O, CO2, and other VOCs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from .spectra import read_jcamp


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    maximum = float(output["absorbance"].max())
    output["relative_absorbance"] = output["absorbance"] / maximum if maximum > 0 else 0.0
    return output


def window_max(frame: pd.DataFrame, center: float, half_width: float) -> float:
    values = frame.loc[
        frame["wavenumber_cm-1"].between(center - half_width, center + half_width), "relative_absorbance"
    ]
    return float(values.max()) if not values.empty else float("nan")


def screen_windows(root: Path, config: dict[str, object]) -> pd.DataFrame:
    targets = {
        item["voc"]: (item, normalize(read_jcamp(root / item["file"])[1]))
        for item in config["targets"]
    }
    interferents = {
        item["name"]: normalize(read_jcamp(root / item["file"])[1])
        for item in config["interferents"]
    }
    half_width = float(config["window_half_width_cm-1"])
    prominence = float(config["minimum_peak_prominence"])
    rows = []
    for voc, (metadata, spectrum) in targets.items():
        peaks, properties = find_peaks(spectrum["relative_absorbance"].to_numpy(), prominence=prominence, distance=8)
        for peak_index, peak_prominence in zip(peaks, properties["prominences"]):
            center = float(spectrum.iloc[peak_index]["wavenumber_cm-1"])
            target_strength = window_max(spectrum, center, half_width)
            h2o = window_max(interferents["water vapour"], center, half_width)
            co2 = window_max(interferents["carbon dioxide"], center, half_width)
            cross = max(
                window_max(other_spectrum, center, half_width)
                for other_voc, (_, other_spectrum) in targets.items()
                if other_voc != voc
            )
            denominator = 0.05 + max(h2o, co2, cross)
            rows.append(
                {
                    "voc": voc,
                    "name": metadata["name"],
                    "cas": metadata["cas"],
                    "center_cm-1": round(center, 1),
                    "center_um": round(10000 / center, 3),
                    "target_relative_max": round(target_strength, 4),
                    "h2o_relative_max": round(h2o, 4),
                    "co2_relative_max": round(co2, 4),
                    "other_voc_relative_max": round(cross, 4),
                    "peak_prominence": round(float(peak_prominence), 4),
                    "shape_separation_proxy": round(target_strength / denominator, 4),
                }
            )
    result = pd.DataFrame(rows)
    result["rank_within_voc"] = result.groupby("voc")["shape_separation_proxy"].rank(method="first", ascending=False).astype(int)
    return result.sort_values(["voc", "rank_within_voc"])


def plot_best_windows(root: Path, config: dict[str, object], windows: pd.DataFrame, output: Path) -> None:
    best = windows.loc[windows["rank_within_voc"].eq(1)].copy()
    interferents = {
        item["name"]: normalize(read_jcamp(root / item["file"])[1])
        for item in config["interferents"]
    }
    target_lookup = {item["voc"]: item for item in config["targets"]}
    half_width = float(config["window_half_width_cm-1"])
    fig, axes = plt.subplots(len(best), 1, figsize=(8, 9), squeeze=False)
    for ax, (_, row) in zip(axes[:, 0], best.iterrows()):
        item = target_lookup[row["voc"]]
        target = normalize(read_jcamp(root / item["file"])[1])
        center = float(row["center_cm-1"])
        view_width = max(120.0, half_width * 3)
        for label, frame, colour, width in (
            (item["name"], target, "#1565c0", 1.8),
            ("H2O", interferents["water vapour"], "#00897b", 1.0),
            ("CO2", interferents["carbon dioxide"], "#ef6c00", 1.0),
        ):
            section = frame.loc[frame["wavenumber_cm-1"].between(center - view_width, center + view_width)]
            ax.plot(section["wavenumber_cm-1"], section["relative_absorbance"], label=label, color=colour, linewidth=width)
        ax.axvspan(center - half_width, center + half_width, color="#90caf9", alpha=0.18)
        ax.set_ylabel(item["name"], rotation=0, ha="right", va="center", fontsize=8)
        ax.set_ylim(-0.03, 1.05)
        ax.invert_xaxis()
    axes[0, 0].legend(frameon=False, ncol=3, fontsize=8)
    axes[0, 0].set_title("Best shape-separation window per exploratory VOC\n(normalized reference spectra; qualitative screen only)")
    axes[-1, 0].set_xlabel("Wavenumber (cm$^{-1}$)")
    fig.text(0.015, 0.5, "Within-compound normalized absorbance", rotation=90, va="center")
    fig.tight_layout(rect=(0.08, 0, 1, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectra_root", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/interference_manifest_v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/interference_windows.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/interference_summary.json"))
    parser.add_argument("--figure", type=Path, default=Path("results/figures/interference_windows.png"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    windows = screen_windows(args.spectra_root, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    windows.to_csv(args.output, index=False)
    best = windows.loc[windows["rank_within_voc"].eq(1)]
    summary = {
        "status": "qualitative_only",
        "targets_screened": int(best.shape[0]),
        "window_half_width_cm-1": config["window_half_width_cm-1"],
        "best_windows": best[["voc", "center_cm-1", "center_um", "shape_separation_proxy"]].to_dict("records"),
        "warning": "Scores compare normalized spectral shapes, not concentration-weighted absorbance. They cannot establish selectivity, sensitivity, or LOD.",
    }
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_best_windows(args.spectra_root, config, windows, args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
