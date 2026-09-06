"""Create compact figures for the locked candidate analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    data = pd.read_csv(args.table)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    exploratory = data["exploratory_direction_consistent"].astype(bool)
    ax.scatter(data["discovery_hedges_g"], data["validation_hedges_g"], s=20, alpha=0.35, color="#607d8b")
    ax.scatter(
        data.loc[exploratory, "discovery_hedges_g"],
        data.loc[exploratory, "validation_hedges_g"],
        s=34,
        alpha=0.9,
        color="#00796b",
        label="direction-consistent exploratory set",
    )
    primary = data["discovery_candidate"].astype(bool)
    ax.scatter(
        data.loc[primary, "discovery_hedges_g"],
        data.loc[primary, "validation_hedges_g"],
        s=70,
        marker="x",
        linewidth=2,
        color="#c62828",
        label="primary discovery candidate",
    )
    lim = max(1.05, float(np.nanmax(np.abs(data[["discovery_hedges_g", "validation_hedges_g"]].to_numpy()))) * 1.08)
    ax.plot([-lim, lim], [-lim, lim], linestyle="--", color="black", linewidth=0.8, alpha=0.5)
    ax.axhline(0, color="grey", linewidth=0.6)
    ax.axvline(0, color="grey", linewidth=0.6)
    ax.set(xlim=(-lim, lim), ylim=(-lim, lim), xlabel="Discovery B2 Hedges g", ylabel="Validation B1 Hedges g")
    ax.set_title("Cross-cohort VOC effect reproducibility")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.output_dir / "cross_cohort_effects.png", dpi=220)
    plt.close(fig)

    ranked = data.assign(min_abs_g=data[["discovery_hedges_g", "validation_hedges_g"]].abs().min(axis=1))
    ranked = ranked.loc[ranked["direction_agrees"]].nlargest(12, "min_abs_g").sort_values("min_abs_g")
    y = np.arange(len(ranked))
    fig, ax = plt.subplots(figsize=(7.2, 5.5))
    ax.scatter(ranked["discovery_hedges_g"], y + 0.12, label="Discovery B2", color="#1565c0")
    ax.scatter(ranked["validation_hedges_g"], y - 0.12, label="Validation B1", color="#ef6c00")
    ax.axvline(0, color="grey", linewidth=0.7)
    ax.set_yticks(y, ranked["voc"].str.replace("_", " ", regex=False), fontsize=8)
    ax.set_xlabel("Hedges g (Asthma minus Not Asthma)")
    ax.set_title("Direction-consistent exploratory effects\n(no VOC met the primary replication rule)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(args.output_dir / "exploratory_consistent_effects.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()

