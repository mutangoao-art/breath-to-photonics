# Status and roadmap — 2026-09-06

## Original plan versus current state

| Original stage | Status | What happened |
|---|---|---|
| Audit the clinical release and ambient-air matching | Complete | RADicA files passed structural checks; MaskBG/S1/S2 matching was confirmed |
| Correct breath signals using matched ambient air | Complete via source release | The supplied B1/B2 matrices were already background-adjusted, filtered, imputed, and normalized by the authors |
| Discovery selection and untouched-cohort validation | Complete | Participant overlap was removed from validation; no VOC passed the locked replication rule |
| Match candidates to experimental gas-phase IR spectra | Complete for five exploratory VOCs | Work continued as feasibility analysis because there was no primary replicated candidate |
| Rank targets by reproducibility, interference, and measurement complexity | Not valid as a final ranking | A qualitative screen and partial quantitative bounds exist, but clinical replication is null and quantitative spectral coverage is only 2/5 |

## Data-driven adjustments

These changes were responses to observed evidence rather than parts of the initial idealized sequence:

1. Three B1/B2 participant overlaps were discovered and removed from validation to prevent leakage.
2. Because the locked primary analysis returned zero replicated VOCs, subsequent VOCs are labelled exploratory rather than validated targets.
3. Liquid-phase spectra were rejected; only verified gas-phase records were retained.
4. H2O/CO2 screening began as normalized shape comparison because the reference records were not quantitatively comparable.
5. NIST QUANT-IR covered only 2-butanone and toluene, so detectability modelling is explicitly partial rather than filled with estimated coefficients.
6. The arbitrary 100 ppb demonstration was replaced with small-study asthma means of 1.26 ppbv and 0.89 ppbv. This shifted the estimated 1% peak-attenuation paths from tens or hundreds of metres to kilometres.

## Remaining work

Highest-priority scientific gaps are:

1. Obtain or generate quantitative H2O and CO2 absorption at breath-relevant temperature, pressure, and humidity. Target-only instrument-resolution convolution is complete; interferent line data still require HITRAN access.
2. Expand concentration evidence beyond the initial small asthma study. A first cross-study audit is complete and shows strong ambient sensitivity; robust asthma distributions and explicit non-detect modelling remain open.
3. Audit GC-MS identity confidence for the exploratory annotations using retention indices and reference-standard evidence.
4. Define an instrument noise/drift model and compare direct multipass, cavity-enhanced, and preconcentration-assisted architectures.
5. Stop or redesign the target-selection claim if no clinically replicated and physically measurable target emerges. A defensible negative feasibility result remains an acceptable endpoint.

The next recommended implementation step is the remaining part of item 1. HITRAN currently requires an account/API key; the code should keep external line data cached, versioned by metadata, and excluded from Git.
