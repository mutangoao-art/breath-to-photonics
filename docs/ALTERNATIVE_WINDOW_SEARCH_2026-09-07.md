# Alternative spectral-window search — 2026-09-07

## Question

After the original 726 and 1174 cm⁻¹ centers failed the quantitative H2O/CO2 baseline, can another target peak within the downloaded 650–1250 cm⁻¹ range materially reduce interference?

The search evaluates peaks in the quantitative 2 cm⁻¹ NIST target spectra. Its ranking proxy rewards target optical depth and background transmission while penalizing combined H2O/CO2 optical depth. Conditions and limitations remain those of the 296 K HITRAN baseline.

## Best alternatives in the downloaded range

| Target | Alternative center | Background transmission | Target optical depth | Interferent/target ratio |
|---|---:|---:|---:|---:|
| Toluene | 1030.75 cm⁻¹ (9.7017 µm) | 99.25% | 1.06×10⁻⁶ | approximately 7,150 |
| 2-butanone | 939.20 cm⁻¹ (10.6474 µm) | 99.03% | 1.56×10⁻⁶ | approximately 6,240 |

These alternatives are substantially less opaque than the original centers: most incident light remains after the assumed 10 m background path. However, the interferent optical depth is still thousands of times larger than the ppbv target optical depth. They are therefore better *search candidates*, not viable sensor windows.

The tradeoff is visible in both cases. Moving away from the strongest interference also moves to weaker target absorption. A high background transmission by itself does not solve the dynamic-range and subtraction problem.

## Decision

No clean single window has emerged for either exploratory VOC within 650–1250 cm⁻¹. The result does not prove that all mid-IR regions fail, because the HITRAN download does not cover the complete NIST target spectra. The next defensible options are:

1. download H2O/CO2 lines covering the remaining quantitative target bands, especially the carbonyl and C–H regions;
2. test multi-window fitting rather than one-channel peak sensing;
3. stop promoting either compound if the expanded search remains background-dominated.

The ranking score is heuristic and must not be described as selectivity, sensitivity, or limit of detection.

## Reproduction

```bash
PYTHONPATH=src python -m breath_to_photonics.window_search \
  data/raw/hitran data/raw/spectra/nist-quant
```
