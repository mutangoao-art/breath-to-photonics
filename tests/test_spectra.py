from pathlib import Path

from breath_to_photonics.spectra import read_jcamp


def test_read_jcamp_expands_xydata(tmp_path: Path) -> None:
    path = tmp_path / "example.jdx"
    path.write_text(
        "\n".join(
            [
                "##TITLE=Example",
                "##STATE=gas",
                "##XUNITS=1/CM",
                "##YUNITS=ABSORBANCE",
                "##XFACTOR=1",
                "##YFACTOR=0.1",
                "##DELTAX=2",
                "##NPOINTS=3",
                "##XYDATA=(X++(Y..Y))",
                "100 1 2 3",
                "##END=",
            ]
        ),
        encoding="utf-8",
    )
    headers, frame = read_jcamp(path)
    assert headers["STATE"] == "gas"
    assert frame["wavenumber_cm-1"].tolist() == [100.0, 102.0, 104.0]
    assert frame["absorbance"].round(3).tolist() == [0.1, 0.2, 0.3]

