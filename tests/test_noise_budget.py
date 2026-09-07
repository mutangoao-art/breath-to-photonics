import pandas as pd
import pytest

from breath_to_photonics.noise_budget import calculate_budget


def test_noise_budget_scales_lod_with_noise() -> None:
    source = pd.DataFrame(
        {
            "voc": ["Toluene", "Toluene"],
            "name": ["toluene", "toluene"],
            "center_cm-1": [1030.75, 728.0],
            "target_optical_depth": [1e-6, 2e-6],
            "H2O_optical_depth": [0.001, 0.2],
            "CO2_optical_depth": [0.002, 0.3],
            "rank_within_voc": [1, 2],
        }
    )
    config = {
        "use_rank_within_voc": 1,
        "required_snr": 3,
        "reference_concentrations_ppb": {"Toluene": 0.89},
        "relative_transmission_noise_ppm_scenarios": [0.1, 1.0],
    }
    result = calculate_budget(source, config)
    assert len(result) == 2
    assert result.iloc[1]["white_noise_equivalent_lod_ppb"] == pytest.approx(
        10 * result.iloc[0]["white_noise_equivalent_lod_ppb"]
    )
    assert result.iloc[0]["maximum_relative_transmission_noise_ppm"] == pytest.approx(1 / 3)
