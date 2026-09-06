# Instrument-resolution sensitivity — 2026-09-06

## Purpose

This step tests how much of the optimistic target peak survives when the approximately 1.929 cm⁻¹ NIST QUANT-IR spectra are broadened to coarser instrument resolutions. It completes the resolution component of the planned quantitative model while H2O/CO2 line data remain unavailable locally.

The model applies the additional Gaussian broadening required to reach 2, 5, 10, and 20 cm⁻¹ full width at half maximum. It conserves integrated spectral area. It does not claim that a particular laser, filter, or spectrometer has a Gaussian line shape.

## Results

| Target | Resolution | Peak retained | Path for 1% peak attenuation |
|---|---:|---:|---:|
| 2-butanone | 2 cm⁻¹ | 100.0% | 12.90 km |
| 2-butanone | 20 cm⁻¹ | 85.6% | 15.06 km |
| Toluene | 2 cm⁻¹ | 100.0% | 6.26 km |
| Toluene | 20 cm⁻¹ | 34.2% | 18.27 km |

The 2-butanone feature around 1174 cm⁻¹ is relatively broad and loses about 14% of its peak coefficient by 20 cm⁻¹. The toluene feature around 726 cm⁻¹ is much more resolution-sensitive: at 5 cm⁻¹ only about 60% remains, and at 20 cm⁻¹ about 34% remains. Toluene's apparent advantage at the native resolution largely disappears in a coarse instrument.

## HITRAN access boundary

The existing NIST water and CO2 reference spectra cannot be made quantitative because their records lack the concentration and optical-path metadata needed to scale absorbance. HITRAN provides the necessary line-by-line parameters and HAPI can calculate absorption and instrumental convolution, but the current official HAPI page states that downloading requires a free account API key.

No substitute values were inferred from the normalized NIST plots. The next exact step is to obtain H2O and CO2 line data for the two narrow spectral regions, cache them under `data/raw/`, then combine target and interferent optical depths under declared temperature, pressure, humidity, CO2 fraction, and instrument response.

## Reproduction

```bash
PYTHONPATH=src python -m breath_to_photonics.resolution data/raw/spectra/nist-quant
```

The full numeric result is in `results/resolution_sensitivity.csv`.
