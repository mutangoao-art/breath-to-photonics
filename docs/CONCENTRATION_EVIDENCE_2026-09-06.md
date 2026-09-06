# Cross-study breath concentration evidence — 2026-09-06

## Finding

The available quantitative evidence supports a low-ppbv engineering regime, but it does not provide a stable asthma-specific concentration distribution.

- Huzar et al. reported asthma-subgroup means of 1.26 ppbv for 2-butanone and 0.89 ppbv for toluene. The subgroup contained eight people; detection frequencies were 87.5% and 50%, respectively.
- Buszewski et al. reported healthy-control ranges of 1.35–3.18 ppb for 2-butanone and 1.45–37.21 ppb for toluene. These show that upper exposure-driven values can be much higher, especially for toluene, but they are not asthma reference intervals.
- Barker et al. measured mean toluene of 0.29 ppb in healthy children's breath and 0.80 ppb in ambient air, producing a negative breath-minus-ambient value.
- Mochalski et al. found room-air 2-butanone significantly higher than breath in healthy adults, while toluene levels in breath and room air were comparable.

The last two findings matter more than a wider numerical range: both candidate signals can be dominated by environmental exposure. A sensor measuring a single absolute breath channel could therefore detect room history rather than disease biology.

## Modelling decision

The current 0.5–40 ppb sweep is retained because it spans the extracted literature values. The Huzar asthma means remain the central engineering anchors, but are not treated as population estimates. No meta-analytic pooling is performed because populations, sampling media, preconcentration, background handling, and summary statistics differ.

For future feasibility tests, the minimum valid sampling architecture should include:

1. paired inhaled/room-air measurement or another validated background estimate;
2. a breath-minus-ambient or alveolar-gradient output;
3. explicit handling of non-detects rather than zero substitution;
4. collection timing and storage controls.

This strengthens the current negative feasibility signal: achieving adequate optical sensitivity is necessary but not sufficient, because background subtraction must resolve a much smaller biological difference between two larger measurements.

## Sources

- [Huzar et al., 2021](https://doi.org/10.3390/molecules26061787)
- [Buszewski et al., 2012](https://doi.org/10.1007/s00216-012-6102-8)
- [Barker et al., 2006](https://doi.org/10.1183/09031936.06.00085105)
- [Mochalski et al., 2013](https://doi.org/10.1039/c3an36756h)

Structured evidence is stored in `results/concentration_evidence.csv`.
