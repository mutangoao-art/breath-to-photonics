"""Quantitative H2O/CO2 baseline from downloaded HITRAN 160-character lines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

from .quantitative import transmission
from .resolution import broaden
from .spectra import read_jcamp


BOLTZMANN_J_K = 1.380649e-23
PASCAL_PER_ATM = 101325.0


def read_hitran_160(path: Path) -> pd.DataFrame:
    """Read fields needed for a 296 K pressure-broadened screen."""
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), start=1):
        if len(line) < 67:
            raise ValueError(f"Short HITRAN record at line {line_number}")
        rows.append(
            {
                "molecule_id": int(line[0:2]),
                "isotopologue_id": line[2:3],
                "wavenumber_cm-1": float(line[3:15]),
                "line_intensity_cm_molecule-1": float(line[15:25]),
                "gamma_air_cm-1_atm-1": float(line[35:40]),
                "gamma_self_cm-1_atm-1": float(line[40:45]),
                "delta_air_cm-1_atm-1": float(line[59:67]),
            }
        )
    return pd.DataFrame(rows)


def lorentz_cross_section(
    lines: pd.DataFrame,
    grid: np.ndarray,
    mole_fraction: float,
    pressure_atm: float,
    wing_cm1: float,
) -> np.ndarray:
    """Return summed 296 K Lorentz cross-section in cm2/molecule."""
    output = np.zeros_like(grid)
    lo = float(grid.min()) - wing_cm1
    hi = float(grid.max()) + wing_cm1
    selected = lines.loc[lines["wavenumber_cm-1"].between(lo, hi)]
    air_fraction = 1.0 - mole_fraction
    numeric = selected[
        [
            "wavenumber_cm-1",
            "line_intensity_cm_molecule-1",
            "gamma_air_cm-1_atm-1",
            "gamma_self_cm-1_atm-1",
            "delta_air_cm-1_atm-1",
        ]
    ].to_numpy()
    for line_center, intensity, gamma_air, gamma_self, delta_air in numeric:
        gamma = pressure_atm * (gamma_air * air_fraction + gamma_self * mole_fraction)
        center = line_center + pressure_atm * air_fraction * delta_air
        output += intensity * gamma / (np.pi * ((grid - center) ** 2 + gamma**2))
    return output


def instrument_convolve(values: np.ndarray, step_cm1: float, fwhm_cm1: float) -> np.ndarray:
    sigma_points = fwhm_cm1 / (2.0 * np.sqrt(2.0 * np.log(2.0))) / step_cm1
    return gaussian_filter1d(values, sigma=sigma_points)


def number_density_cm3(mole_fraction: float, pressure_atm: float, temperature_K: float) -> float:
    return mole_fraction * pressure_atm * PASCAL_PER_ATM / (BOLTZMANN_J_K * temperature_K) / 1e6


def run(
    hitran_root: Path,
    target_root: Path,
    config: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, object], dict[str, pd.DataFrame]]:
    lines = read_hitran_160(hitran_root / config["hitran_file"])
    step = float(config["grid_step_cm-1"])
    pressure = float(config["pressure_atm"])
    temperature = float(config["temperature_K"])
    path_cm = float(config["path_length_m"]) * 100.0
    fwhm = float(config["instrument_fwhm_cm-1"])
    wing = float(config["line_wing_cm-1"])
    fractions = config["mole_fractions"]
    molecule_ids = {"H2O": 1, "CO2": 2}
    rows = []
    plot_frames = {}
    for item in config["windows"]:
        center = float(item["center_cm-1"])
        grid = np.arange(center - 40.0, center + 40.0 + step / 2.0, step)
        frame = pd.DataFrame({"wavenumber_cm-1": grid})
        interferent_tau = np.zeros_like(grid)
        center_index = int(np.argmin(np.abs(grid - center)))
        center_values = {}
        for gas, molecule_id in molecule_ids.items():
            fraction = float(fractions[gas])
            cross_section = lorentz_cross_section(
                lines.loc[lines["molecule_id"].eq(molecule_id)],
                grid,
                fraction,
                pressure,
                wing,
            )
            cross_section = instrument_convolve(cross_section, step, fwhm)
            tau = cross_section * number_density_cm3(fraction, pressure, temperature) * path_cm
            frame[f"{gas}_optical_depth"] = tau
            interferent_tau += tau
            center_values[gas] = float(tau[center_index])

        headers, target = read_jcamp(target_root / item["target_quant_file"])
        target_values = target["absorbance"].clip(lower=0.0).to_numpy()
        target_values = broaden(
            target_values,
            float(headers["DELTAX"]),
            float(headers["RESOLUTION"]),
            fwhm,
        )
        target_coefficient = np.interp(grid, target["wavenumber_cm-1"], target_values)
        target_absorbance_base10 = (
            target_coefficient
            * float(item["target_concentration_ppb"])
            / 1000.0
            * float(config["path_length_m"])
        )
        target_tau = np.log(10.0) * target_absorbance_base10
        frame["target_optical_depth"] = target_tau
        frame["interferent_transmission"] = np.exp(-interferent_tau)
        frame["combined_transmission"] = np.exp(-(interferent_tau + target_tau))
        target_center_tau = float(target_tau[center_index])
        interferent_center_tau = float(interferent_tau[center_index])
        rows.append(
            {
                "voc": item["voc"],
                "name": item["name"],
                "center_cm-1": center,
                "target_concentration_ppb": float(item["target_concentration_ppb"]),
                "H2O_optical_depth_at_center": center_values["H2O"],
                "CO2_optical_depth_at_center": center_values["CO2"],
                "target_optical_depth_at_center": target_center_tau,
                "interferent_to_target_optical_depth_ratio": (
                    interferent_center_tau / target_center_tau if target_center_tau > 0 else float("inf")
                ),
                "interferent_transmission_at_center": float(np.exp(-interferent_center_tau)),
                "target_only_attenuation_at_center": 1.0
                - transmission(
                    float(target_coefficient[center_index]),
                    float(item["target_concentration_ppb"]),
                    float(config["path_length_m"]),
                ),
            }
        )
        plot_frames[item["voc"]] = frame
    table = pd.DataFrame(rows)
    summary = {
        "status": "quantitative_baseline_at_296K",
        "download_id": config["download_id"],
        "hitran_line_count": int(len(lines)),
        "molecule_line_counts": {
            "H2O": int(lines["molecule_id"].eq(1).sum()),
            "CO2": int(lines["molecule_id"].eq(2).sum()),
        },
        "conditions": {
            "temperature_K": temperature,
            "pressure_atm": pressure,
            "path_length_m": float(config["path_length_m"]),
            "instrument_fwhm_cm-1": fwhm,
            "mole_fractions": fractions,
        },
        "limitations": config["limitations"],
    }
    return table, summary, plot_frames


def plot_windows(table: pd.DataFrame, frames: dict[str, pd.DataFrame], output: Path) -> None:
    fig, axes = plt.subplots(len(table), 1, figsize=(9, 6.5), squeeze=False)
    for ax, (_, row) in zip(axes[:, 0], table.iterrows()):
        frame = frames[row["voc"]]
        ax.plot(frame["wavenumber_cm-1"], frame["H2O_optical_depth"], label="H2O", color="#00897b")
        ax.plot(frame["wavenumber_cm-1"], frame["CO2_optical_depth"], label="CO2", color="#ef6c00")
        ax.plot(frame["wavenumber_cm-1"], frame["target_optical_depth"], label=row["name"], color="#1565c0")
        ax.axvline(row["center_cm-1"], color="black", linestyle="--", linewidth=0.8)
        ax.set_yscale("log")
        ax.set_ylabel("Optical depth")
        ax.set_title(f"{row['name']}: {row['center_cm-1']:.0f} cm$^{{-1}}$")
        ax.invert_xaxis()
        ax.grid(alpha=0.15)
        ax.legend(frameon=False, ncol=3)
    axes[-1, 0].set_xlabel("Wavenumber (cm$^{-1}$)")
    fig.suptitle("HITRAN interferent baseline versus exploratory VOC target (296 K, 10 m)")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hitran_root", type=Path)
    parser.add_argument("target_root", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/hitran_interference_v0.1.json"))
    parser.add_argument("--output", type=Path, default=Path("results/hitran_interference_windows.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/hitran_interference_summary.json"))
    parser.add_argument("--figure", type=Path, default=Path("results/figures/hitran_interference.png"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    table, summary, frames = run(args.hitran_root, args.target_root, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_windows(table, frames, args.figure)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
