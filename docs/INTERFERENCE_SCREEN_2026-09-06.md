# Qualitative H2O/CO2 interference screen — 2026-09-06

## Scope

The locked cross-cohort analysis produced no replicated primary VOC candidate. This screen therefore covers five **exploratory** VOCs for which an experimental gas-phase NIST spectrum was verified; it is not a validation of asthma biomarkers or sensor targets.

Each target spectrum was normalized independently and compared with independently normalized gas-phase water and carbon-dioxide NIST spectra. Candidate centers are target peaks, and each inspected window spans ±20 cm⁻¹. The reported shape-separation proxy penalizes overlap with H2O, CO2, and the other screened VOCs.

## Best shape-only windows

| Exploratory VOC | Center (cm⁻¹) | Center (µm) | Shape proxy | Interpretation |
|---|---:|---:|---:|---|
| 1,4-dichlorobenzene | 1094 | 9.141 | 8.3195 | Lowest normalized overlap in this small comparison |
| Toluene | 726 | 13.774 | 7.8678 | Low normalized overlap in this small comparison |
| 2-butanone | 1174 | 8.518 | 1.0908 | Moderate shape separation |
| Decane | 2934 | 3.408 | 0.9524 | Strong cross-VOC ambiguity in the C–H region |
| 2-heptanone | 2942 | 3.399 | 0.9524 | Strong cross-VOC ambiguity in the C–H region |

The 1,4-dichlorobenzene and toluene windows look least overlapped in normalized shape, but this does **not** mean they are the best sensor targets. Decane and 2-heptanone both select the crowded approximately 3.4 µm hydrocarbon C–H region, where the screened VOC spectra overlap strongly. The 2-butanone window at 1174 cm⁻¹ is intermediate under this proxy.

## Strict limitation

The NIST records were collected under different and incompletely harmonized conditions. Independent normalization discards absolute absorption strength, and the comparison is not weighted by realistic breath concentrations, optical path length, instrument resolution, noise, or humidity. Consequently, these scores cannot support claims about practical selectivity, sensitivity, ppm-level response, or limit of detection.

## Next evidence gate

Before choosing a photonic architecture, replace the shape-only proxy with compatible quantitative absorption data: quantitative target coefficients where available, HITRAN/HAPI line-by-line H2O and CO2 simulations, and defensible breath concentration ranges. Then simulate transmission at realistic path lengths and resolution and test whether any window remains identifiable under noise and drift.

Reproduce this stage with:

```bash
PYTHONPATH=src python -m breath_to_photonics.interference data/raw/spectra/nist
```
