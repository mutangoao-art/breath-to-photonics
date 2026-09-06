import numpy as np
import pytest

from breath_to_photonics.resolution import broaden


def test_broadening_preserves_area_and_reduces_peak() -> None:
    values = np.zeros(1001)
    values[500] = 1.0
    broadened = broaden(
        values, spacing_cm1=0.1, source_fwhm_cm1=2.0, target_fwhm_cm1=10.0
    )
    assert broadened.sum() == pytest.approx(values.sum())
    assert broadened.max() < values.max()


def test_broadening_rejects_finer_target_resolution() -> None:
    with pytest.raises(ValueError, match="finer"):
        broaden(
            np.ones(10), spacing_cm1=1.0, source_fwhm_cm1=2.0, target_fwhm_cm1=1.0
        )
