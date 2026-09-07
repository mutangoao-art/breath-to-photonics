from pathlib import Path

import numpy as np
import pytest

from breath_to_photonics.hitran_interference import (
    lorentz_cross_section,
    number_density_cm3,
    read_hitran_160,
)


def test_read_hitran_160_extracts_fixed_width_fields(tmp_path: Path) -> None:
    one_line = (
        f"{1:2d}{1:1d}{1000.0:12.6f}{2e-20:10.3E}{1.0:10.3E}"
        f"{0.07:5.4f}{0.1:5.3f}{0.0:10.4f}{0.7:4.2f}{0.0:8.6f}"
    ).ljust(160)
    path = tmp_path / "one.par"
    path.write_text(one_line + "\n", encoding="ascii")
    frame = read_hitran_160(path)
    assert frame.iloc[0]["molecule_id"] == 1
    assert frame.iloc[0]["wavenumber_cm-1"] == 1000.0


def test_lorentz_profile_has_expected_integrated_area() -> None:
    import pandas as pd

    lines = pd.DataFrame(
        {
            "wavenumber_cm-1": [1000.0],
            "line_intensity_cm_molecule-1": [2e-20],
            "gamma_air_cm-1_atm-1": [0.1],
            "gamma_self_cm-1_atm-1": [0.1],
            "delta_air_cm-1_atm-1": [0.0],
        }
    )
    grid = np.linspace(990, 1010, 20001)
    cross_section = lorentz_cross_section(lines, grid, 0.01, 1.0, 25.0)
    assert np.trapezoid(cross_section, grid) == pytest.approx(2e-20, rel=0.01)


def test_number_density_is_positive() -> None:
    assert number_density_cm3(0.05, 1.0, 296.0) > 0
