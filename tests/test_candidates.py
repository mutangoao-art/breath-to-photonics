import numpy as np
import pandas as pd

from breath_to_photonics.candidates import benjamini_hochberg, hedges_g, participant_table


def test_hedges_g_has_expected_direction() -> None:
    assert hedges_g(np.array([3, 4, 5]), np.array([1, 2, 3])) > 0


def test_bh_is_monotonic_in_sorted_p_values() -> None:
    adjusted = benjamini_hochberg(pd.Series([0.01, 0.03, 0.02]))
    ordered = adjusted.iloc[np.argsort([0.01, 0.03, 0.02])].to_numpy()
    assert np.all(np.diff(ordered) >= 0)


def test_participant_table_averages_repeated_visits() -> None:
    frame = pd.DataFrame(
        {"ID": ["A", "A", "B"], "Diagnosis": ["Asthma", "Asthma", "Not Asthma"], "voc": [1.0, 3.0, 4.0]}
    )
    output = participant_table(frame)
    assert output.loc[output["ID"].eq("A"), "voc"].item() == 2.0

