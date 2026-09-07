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

1. Expand and refine the quantitative H2O/CO2 model. HITRAN lines, a 296 K first-pass screen, and an alternative-window search over 650–1250 cm⁻¹ are complete; no viable single window emerged. Remaining work includes other spectral ranges, temperature scaling, line mixing, and water continuum.
2. Expand concentration evidence beyond the initial small asthma study. A first cross-study audit is complete and shows strong ambient sensitivity; robust asthma distributions and explicit non-detect modelling remain open.
3. Resolve compound-level authentic-standard status. The public-evidence audit is complete: all five named candidates satisfy the study's reported NIST/retention-index framework, but the public release does not map individual compounds to MSI Level 1 versus Level 2. See `docs/CHEMICAL_IDENTITY_AUDIT_2026-09-07.md`.
4. Refine the instrument noise/drift model. Direct multipass, cavity-enhanced and preconcentration-assisted scenarios have now been compared. Only preconcentration improves target-to-atmospheric-background contrast; wavelength drift, 1/f noise, averaging time and sampling losses remain open. See `docs/NOISE_AND_DRIFT_BUDGET_2026-09-07.md` and `docs/ARCHITECTURE_COMPARISON_2026-09-07.md`.
5. Validate the preconcentrator experimentally. A mass-balance and timing screen identifies a 500 mL to 5 mL, 80% recovery reference design. A locked 115-run protocol and automated acceptance evaluator are complete. Physical execution remains open, and the current unfilled plan correctly returns `not_evaluable`. See `docs/PRECONCENTRATOR_MASS_BALANCE_2026-09-07.md`, `docs/BENCHTOP_VALIDATION_PROTOCOL_2026-09-07.md`, and `docs/BENCHTOP_EVALUATOR_2026-09-07.md`.
6. Stop or redesign the target-selection claim if no clinically replicated and physically measurable target emerges. A defensible negative feasibility result remains an acceptable endpoint.

The next step requires laboratory hardware and certified standards: execute the benchtop protocol beginning with system blanks and the 500 mL recovery block. Before hardware is available, useful work should shift to a consolidated decision report rather than adding unsupported model detail. Expanding the spectral search remains useful only if a candidate clears both clinical replication and chemical-identity gates.
