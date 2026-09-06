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


def test_read_jcamp_accepts_cm_minus_one_and_adjacent_signed_values(tmp_path: Path) -> None:
    path = tmp_path / "quantitative.jdx"
    path.write_text(
        "\n".join(
            [
                "##STATE=gas",
                "##XUNITS=cm-1",
                "##YUNITS=(micromol/mol)-1m-1 (base 10)",
                "##XFACTOR=1",
                "##YFACTOR=0.01",
                "##DELTAX=1",
                "##NPOINTS=3",
                "##XYDATA=(X++(Y..Y))",
                "100 2-1 3",
                "##END=",
            ]
        ),
        encoding="utf-8",
    )
    _, frame = read_jcamp(path)
    assert frame["absorbance"].round(3).tolist() == [0.02, -0.01, 0.03]
