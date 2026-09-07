# Quantitative HITRAN interference baseline — 2026-09-07

## Data validation

The manual HITRAN2024 download is valid and contains:

- 94,240 fixed-width line records;
- 9,013 H2O lines and 85,227 CO2 lines;
- the requested 650.000776–1249.989269 cm⁻¹ range;
- multiple selected natural isotopologues for both molecules;
- the field definition and complete bibliography supplied with the download.

All four downloaded files are preserved under `data/raw/hitran/6a9e3e2d/` and excluded from Git.

## Baseline assumptions

This first calculation deliberately stays at the HITRAN line-intensity reference temperature of 296 K. It uses 1 atm total pressure, a 10 m optical path, 5% H2O, 4% CO2, 2 cm⁻¹ Gaussian instrument FWHM, and Lorentz air/self pressure broadening. Target concentrations remain the literature asthma means: 0.89 ppbv toluene and 1.26 ppbv 2-butanone.

These mole fractions are transparent engineering assumptions rather than measurements from RADicA. The baseline does not yet include 310 K line-strength scaling, Doppler broadening, line mixing, water continuum, or non-Voigt line shapes.

## Results at the candidate centers

| Window | Dominant interferent | Interferent optical depth | Target optical depth | Interferent/target ratio | Baseline transmission |
|---|---|---:|---:|---:|---:|
| Toluene, 726 cm⁻¹ | CO2 | 1.302 | 7.53×10⁻⁶ | 173,010 | 27.2% |
| 2-butanone, 1174 cm⁻¹ | H2O | 0.2256 | 7.78×10⁻⁶ | 29,001 | 79.8% |

Both previously selected windows fail this first quantitative interference screen. At 726 cm⁻¹, the simplified CO2 baseline absorbs most of the light before the ppbv toluene contribution is considered. At 1174 cm⁻¹, the water optical depth is approximately 29,000 times the target optical depth.

This reverses the qualitative normalized-spectrum impression that 726 cm⁻¹ was relatively clean. Independent normalization removed the real concentration difference between percent-level interferents and ppbv targets.

## Interpretation boundary

The result is strong enough to reject both centers as obviously clean windows, but the exact ratios are not final performance predictions. In particular, simple Lorentz far wings can overestimate CO2 absorption where line mixing or sub-Lorentz behaviour matters. Temperature scaling and the water continuum may also change the baseline. Those refinements are required before quoting residuals or detector dynamic-range requirements.

The appropriate next action is not to optimize hardware around these two centers. It is to search the full quantitative target spectra for alternative sub-windows after applying a more complete interferent model, and to retain the possibility that neither exploratory VOC is viable.

## Reproduction

```bash
PYTHONPATH=src python -m breath_to_photonics.hitran_interference \
  data/raw/hitran data/raw/spectra/nist-quant
```

Machine-readable outputs are `results/hitran_interference_windows.csv` and `results/hitran_interference_summary.json`.
