import json
from pathlib import Path

import pytest

from breath_to_photonics.window_search import search_windows


def test_window_search_returns_ranked_candidates_when_raw_data_exist() -> None:
    hitran_root = Path("data/raw/hitran")
    target_root = Path("data/raw/spectra/nist-quant")
    if not (hitran_root / "6a9e3e2d/6a9e3e2d.par").exists():
        pytest.skip("Downloaded raw spectra are unavailable")
    hitran_config = json.loads(Path("configs/hitran_interference_v0.1.json").read_text())
    search_config = json.loads(Path("configs/alternative_window_search_v0.1.json").read_text())
    table, summary = search_windows(hitran_root, target_root, hitran_config, search_config)
    assert summary["status"] == "alternative_window_search_at_296K"
    assert set(table.loc[table["rank_within_voc"].eq(1), "voc"]) == {"Toluene", "X2_Butanone"}
    assert table["background_transmission"].between(0, 1).all()
