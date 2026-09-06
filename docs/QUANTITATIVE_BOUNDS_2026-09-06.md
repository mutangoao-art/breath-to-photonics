# Partial quantitative detectability bounds — 2026-09-06

## Result

The NIST Quantitative Infrared Database contains compatible gas-phase absorption-coefficient spectra for two of the five exploratory targets: 2-butanone and toluene. It does not list decane, 2-heptanone, or 1,4-dichlorobenzene. Quantitative coverage is therefore **2/5**, and no values were imputed for the missing compounds.

The selected records are primary gas standards measured at 23 °C and 101.3 kPa, using Boxcar apodization with JCAMP-reported resolution of 1.929 cm⁻¹. NIST expresses the base-10 coefficient in ppm⁻¹ m⁻¹, giving

\[
T(\tilde\nu)=10^{-a(\tilde\nu)cL},
\]

where `a` is the absorption coefficient, `c` is concentration in ppm, and `L` is optical path in metres.

## Concentration calibration

A small independent breath study reported quantitative asthma-subgroup means of 1.26 ppbv (SD 0.80; detected in 87.5% of asthma samples) for 2-butanone and 0.89 ppbv (SD 0.60; detected in 50%) for toluene. Its asthma subgroup contained only eight people, so these values are engineering anchors rather than robust population distributions. The source study used calibrated needle-trap GC-MS and reported an LOQ of 0.003 ppbv for both compounds.

Using those asthma means and a 10 m path:

| Target/window | Peak coefficient (ppm⁻¹ m⁻¹) | Peak attenuation | Window-mean attenuation | Path for 1% peak attenuation |
|---|---:|---:|---:|---:|
| 2-butanone, 1174 cm⁻¹ | 2.6863×10⁻⁴ | 0.000780% | 0.000583% | 12.90 km |
| Toluene, 726 cm⁻¹ | 7.8370×10⁻⁴ | 0.00161% | 0.000448% | 6.26 km |

The peak calculation is an optimistic narrow-channel bound. Across each ±20 cm⁻¹ window, the mean response is smaller; a real filter, laser linewidth, or spectrometer response must be convolved with the coefficient spectrum.

## Engineering interpretation

At these literature means, neither target approaches a 1% loss in a 10 m path; the peak-only paths for that loss are kilometres long. Toluene is the stronger narrow-feature case, but its clinical status remains exploratory and non-replicated, and its 50% detection frequency reinforces the risk of exposure and sampling effects. Direct, unenhanced absorption therefore looks implausible at these concentrations. Cavity enhancement, preconcentration, or a substantially lower-noise technique would need explicit quantitative evaluation. This is a design constraint, not yet a hardware recommendation.

## What remains missing

These are target-only Beer–Lambert bounds, not limits of detection. They exclude:

- quantitative H2O and CO2 absorption under humid-breath conditions;
- cross-absorption from other breath VOCs;
- actual target concentration distributions in asthma and control breath;
- collection and preconcentration losses;
- source linewidth, detector noise, baseline drift, and calibration error.

NIST also cautions that point intensities can be misleading across instrumental line shapes and recommends integrated features for comparisons. The next model should convolve target coefficients and HITRAN H2O/CO2 spectra to a declared instrument response and use evidence-backed concentration distributions.

## Provenance and reproduction

The coefficient definition, uncertainties, excluded atmospheric-interference regions, and species table are documented by the [NIST Quantitative Infrared Database](https://webbook.nist.gov/chemistry/quant-ir/). The concentration anchor comes from [Huzar et al. (2021)](https://doi.org/10.3390/molecules26061787). Raw JCAMP records are cached locally but excluded from Git; filenames and assumptions are recorded in `configs/quantitative_manifest_v0.1.json`.

```bash
PYTHONPATH=src python -m breath_to_photonics.quantitative data/raw/spectra/nist-quant
```
