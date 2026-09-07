import pandas as pd
import pytest

from breath_to_photonics.architecture import compare_architectures


def test_path_and_enrichment_scale_low_optical_depth_lod() -> None:
    source = pd.DataFrame(
        {
            "voc": ["Toluene"],
            "name": ["toluene"],
            "center_cm-1": [1030.75],
            "target_optical_depth": [1e-6],
            "H2O_optical_depth": [0.001],
            "CO2_optical_depth": [0.002],
            "rank_within_voc": [1],
        }
    )
    base = {
        "architecture": "test",
        "target_recovery_fraction": 1,
        "atmospheric_background_residual_fraction": 1,
        "relative_transmission_noise_ppm": 1,
    }
    config = {
        "use_rank_within_voc": 1,
        "baseline_path_m": 10,
        "required_snr": 3,
        "reference_concentrations_ppb": {"Toluene": 1},
        "scenarios": [
            {**base, "scenario": "base", "effective_path_m": 10, "target_enrichment_factor": 1},
            {**base, "scenario": "10x path", "effective_path_m": 100, "target_enrichment_factor": 1},
            {**base, "scenario": "10x enrichment", "effective_path_m": 10, "target_enrichment_factor": 10},
        ],
    }
    result = compare_architectures(source, config).set_index("scenario")
    assert result.loc["10x path", "white_noise_equivalent_lod_ppb"] == pytest.approx(
        result.loc["10x enrichment", "white_noise_equivalent_lod_ppb"]
    )
    assert result.loc["10x path", "white_noise_equivalent_lod_ppb"] == pytest.approx(
        result.loc["base", "white_noise_equivalent_lod_ppb"] / 10, rel=1e-5
    )


def test_path_does_not_change_background_ratio() -> None:
    source = pd.DataFrame(
        {
            "voc": ["Toluene"], "name": ["toluene"], "center_cm-1": [1000],
            "target_optical_depth": [1e-6], "H2O_optical_depth": [0.001],
            "CO2_optical_depth": [0.001], "rank_within_voc": [1],
        }
    )
    common = {
        "architecture": "test", "target_enrichment_factor": 1,
        "target_recovery_fraction": 1, "atmospheric_background_residual_fraction": 1,
        "relative_transmission_noise_ppm": 1,
    }
    config = {
        "use_rank_within_voc": 1, "baseline_path_m": 10, "required_snr": 3,
        "reference_concentrations_ppb": {"Toluene": 1},
        "scenarios": [
            {**common, "scenario": "10m", "effective_path_m": 10},
            {**common, "scenario": "100m", "effective_path_m": 100},
        ],
    }
    result = compare_architectures(source, config)
    assert result.iloc[0]["maximum_background_tau_relative_error_ppm"] == pytest.approx(
        result.iloc[1]["maximum_background_tau_relative_error_ppm"]
    )
