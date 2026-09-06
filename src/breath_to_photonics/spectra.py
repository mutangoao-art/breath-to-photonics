"""Parse and compare NIST JCAMP-DX gas-phase reference spectra."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def read_jcamp(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    """Parse the simple NIST XYDATA=(X++(Y..Y)) representation."""
    headers: dict[str, str] = {}
    data_lines: list[str] = []
    in_data = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("##"):
            key, _, value = line[2:].partition("=")
            headers[key.strip().upper()] = value.strip()
            in_data = key.strip().upper() == "XYDATA"
        elif in_data and line.strip() and not line.startswith("$"):
            data_lines.append(line)
    if headers.get("STATE", "").casefold() != "gas":
        raise ValueError(f"{path.name} is not labelled as a gas-phase spectrum")
    if headers.get("XUNITS", "").upper() not in {"1/CM", "CM-1"}:
        raise ValueError(f"{path.name} does not use wavenumber units")

    delta_x = float(headers["DELTAX"]) * float(headers.get("XFACTOR", "1"))
    y_factor = float(headers.get("YFACTOR", "1"))
    x_factor = float(headers.get("XFACTOR", "1"))
    xs: list[float] = []
    ys: list[float] = []
    for line in data_lines:
        # JCAMP AFFN permits adjacent signed values such as ``491496-1278016``.
        tokens = re.findall(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?", line)
        values = [float(value) for value in tokens]
        start = values[0] * x_factor
        for index, value in enumerate(values[1:]):
            xs.append(start + index * delta_x)
            ys.append(value * y_factor)
    frame = pd.DataFrame({"wavenumber_cm-1": xs, "absorbance": ys})
    expected = int(headers["NPOINTS"])
    if len(frame) != expected:
        raise ValueError(f"Expected {expected} points in {path.name}, parsed {len(frame)}")
    return headers, frame


def summarize_spectra(spectra_root: Path, manifest: list[dict[str, str]]) -> tuple[pd.DataFrame, dict[str, object]]:
    peak_rows = []
    coverage = []
    for item in manifest:
        headers, frame = read_jcamp(spectra_root / item["file"])
        normalized = frame["absorbance"] / frame["absorbance"].max()
        peaks, properties = find_peaks(normalized.to_numpy(), prominence=0.08, distance=8)
        order = peaks[np.argsort(properties["prominences"])[::-1]][:5]
        for rank, index in enumerate(order, start=1):
            peak_rows.append(
                {
                    "voc": item["voc"],
                    "name": item["name"],
                    "cas": item["cas"],
                    "rank": rank,
                    "wavenumber_cm-1": round(float(frame.iloc[index]["wavenumber_cm-1"]), 1),
                    "wavelength_um": round(10000 / float(frame.iloc[index]["wavenumber_cm-1"]), 3),
                    "relative_absorbance": round(float(normalized.iloc[index]), 4),
                }
            )
        coverage.append(
            {
                "voc": item["voc"],
                "state": headers["STATE"],
                "y_units": headers["YUNITS"],
                "points": int(headers["NPOINTS"]),
                "range_cm-1": [float(headers["MINX"]), float(headers["MAXX"])],
            }
        )
    return pd.DataFrame(peak_rows), {
        "spectra_count": len(coverage),
        "all_gas_phase": all(entry["state"].casefold() == "gas" for entry in coverage),
        "coverage": coverage,
        "limitation": "NIST WebBook spectra support qualitative band-location comparison. Different measurement conditions and absent concentration/path metadata prevent cross-compound sensitivity or LOD comparison.",
    }


def plot_spectra(spectra_root: Path, manifest: list[dict[str, str]], output: Path) -> None:
    fig, axes = plt.subplots(len(manifest), 1, figsize=(8, 8.5), sharex=True)
    for ax, item in zip(axes, manifest):
        _, frame = read_jcamp(spectra_root / item["file"])
        normalized = frame["absorbance"] / frame["absorbance"].max()
        ax.plot(frame["wavenumber_cm-1"], normalized, linewidth=1, color="#1565c0")
        ax.set_ylabel(item["name"], rotation=0, ha="right", va="center", fontsize=8)
        ax.set_ylim(-0.03, 1.05)
        ax.grid(alpha=0.15)
    axes[0].set_title("Experimental NIST gas-phase IR spectra\n(normalized within compound; amplitudes are not comparable)")
    axes[-1].set_xlabel("Wavenumber (cm$^{-1}$)")
    axes[-1].invert_xaxis()
    fig.text(0.02, 0.5, "Normalized absorbance", rotation=90, va="center")
    fig.tight_layout(rect=(0.08, 0, 1, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectra_root", type=Path)
    parser.add_argument("--manifest", type=Path, default=Path("configs/spectral_manifest_v0.1.json"))
    parser.add_argument("--peaks", type=Path, default=Path("results/spectral_peaks.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/spectral_summary.json"))
    parser.add_argument("--figure", type=Path, default=Path("results/figures/nist_gas_spectra.png"))
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    peaks, summary = summarize_spectra(args.spectra_root, manifest)
    args.peaks.parent.mkdir(parents=True, exist_ok=True)
    peaks.to_csv(args.peaks, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_spectra(args.spectra_root, manifest, args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
