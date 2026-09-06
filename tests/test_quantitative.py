import pytest

from breath_to_photonics.quantitative import path_for_attenuation, transmission


def test_transmission_uses_base_ten_absorbance_and_ppb_conversion() -> None:
    assert transmission(0.01, concentration_ppb=100.0, path_m=10.0) == pytest.approx(10**-0.01)


def test_path_for_attenuation_round_trips() -> None:
    coefficient = 0.002
    concentration = 50.0
    path_m = path_for_attenuation(coefficient, concentration, attenuation_fraction=0.01)
    assert 1.0 - transmission(coefficient, concentration, path_m) == pytest.approx(0.01)
