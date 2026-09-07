import pandas as pd
import pytest

from breath_to_photonics.preconcentrator import calculate_mass_balance, sample_amount_pmol


def test_sample_amount_scales_with_volume_and_concentration() -> None:
    base = sample_amount_pmol(1, 500, 1, 296)
    assert sample_amount_pmol(2, 500, 1, 296) == pytest.approx(2 * base)
    assert sample_amount_pmol(1, 1000, 1, 296) == pytest.approx(2 * base)


def test_mass_balance_enrichment_and_cycle_time() -> None:
    source = pd.DataFrame(
        {
            "voc": ["Toluene"], "name": ["toluene"], "rank_within_voc": [1],
            "target_optical_depth": [1e-6],
        }
    )
    config = {
        "use_rank_within_voc": 1, "baseline_path_m": 10, "optical_path_m": 10,
        "required_snr": 3, "relative_transmission_noise_ppm": 1,
        "temperature_K": 296, "pressure_atm": 1, "purge_time_min": 8,
        "desorption_and_transfer_time_min": 5, "reset_time_min": 5,
        "reference_concentrations_ppb": {"Toluene": 1},
        "molar_masses_g_mol": {"Toluene": 92.14},
        "scenarios": [{
            "scenario": "test", "sample_volume_ml": 500, "sample_flow_ml_min": 200,
            "desorption_volume_ml": 5, "recovery_fraction": 0.8,
        }],
    }
    row = calculate_mass_balance(source, config).iloc[0]
    assert row["geometric_enrichment_factor"] == 100
    assert row["net_enrichment_factor"] == 80
    assert row["cycle_time_min"] == 20.5
    assert row["recovered_target_pmol"] == pytest.approx(0.8 * row["sampled_target_pmol"])
