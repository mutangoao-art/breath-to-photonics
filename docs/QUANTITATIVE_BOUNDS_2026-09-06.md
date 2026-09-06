# Partial quantitative detectability bounds — 2026-09-06

## Result

The NIST Quantitative Infrared Database contains compatible gas-phase absorption-coefficient spectra for two of the five exploratory targets: 2-butanone and toluene. It does not list decane, 2-heptanone, or 1,4-dichlorobenzene. Quantitative coverage is therefore **2/5**, and no values were imputed for the missing compounds.

The selected records are primary gas standards measured at 23 °C and 101.3 kPa, using Boxcar apodization with JCAMP-reported resolution of 1.929 cm⁻¹. NIST expresses the base-10 coefficient in ppm⁻¹ m⁻¹, giving

\[
T(\tilde\nu)=10^{-a(\tilde\nu)cL},
\]

where `a` is the absorption coefficient, `c` is concentration in ppm, and `L` is optical path in metres.

## Scenario bounds

The concentration grid from 1–1000 ppb is a sensitivity sweep, **not a claim about physiological concentration**. Using 100 ppb and a 10 m path as a transparent reference scenario:

| Target/window | Peak coefficient (ppm⁻¹ m⁻¹) | Peak attenuation | Window-mean attenuation | Path for 1% peak attenuation |
|---|---:|---:|---:|---:|
| 2-butanone, 1174 cm⁻¹ | 2.6863×10⁻⁴ | 0.0618% | 0.0463% | 162.5 m |
| Toluene, 726 cm⁻¹ | 7.8370×10⁻⁴ | 0.1803% | 0.0503% | 55.7 m |

The peak calculation is an optimistic narrow-channel bound. Across each ±20 cm⁻¹ window, the mean response is smaller; a real filter, laser linewidth, or spectrometer response must be convolved with the coefficient spectrum.

## Engineering interpretation

At this scenario point, neither target produces a 1% loss in a 10 m path. Toluene is the stronger narrow-feature case, but its clinical status remains exploratory and non-replicated. A compact instrument would probably need effective-path enhancement, stronger concentration evidence, or a signal-extraction method capable of resolving sub-percent changes. This is a design constraint, not yet a hardware recommendation.

## What remains missing

These are target-only Beer–Lambert bounds, not limits of detection. They exclude:

- quantitative H2O and CO2 absorption under humid-breath conditions;
- cross-absorption from other breath VOCs;
- actual target concentration distributions in asthma and control breath;
- collection and preconcentration losses;
- source linewidth, detector noise, baseline drift, and calibration error.

NIST also cautions that point intensities can be misleading across instrumental line shapes and recommends integrated features for comparisons. The next model should convolve target coefficients and HITRAN H2O/CO2 spectra to a declared instrument response and use evidence-backed concentration distributions.

## Provenance and reproduction

The coefficient definition, uncertainties, excluded atmospheric-interference regions, and species table are documented by the [NIST Quantitative Infrared Database](https://webbook.nist.gov/chemistry/quant-ir/). Raw JCAMP records are cached locally but excluded from Git; filenames and assumptions are recorded in `configs/quantitative_manifest_v0.1.json`.

```bash
PYTHONPATH=src python -m breath_to_photonics.quantitative data/raw/spectra/nist-quant
```
