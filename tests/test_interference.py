import pandas as pd

from breath_to_photonics.interference import normalize, window_max


def test_window_max_uses_requested_interval() -> None:
    frame = normalize(pd.DataFrame({"wavenumber_cm-1": [90, 100, 110, 140], "absorbance": [0.0, 2.0, 1.0, 4.0]}))
    assert window_max(frame, center=100, half_width=10) == 0.5
