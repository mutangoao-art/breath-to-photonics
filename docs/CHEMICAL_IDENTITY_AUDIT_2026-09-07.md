# Chemical identity audit — 2026-09-07

## Decision

The five exploratory VOC names have stronger support than name-only library guesses, but their exact compound-level MSI identification grades cannot be recovered from the public release. They remain **provisional identities for sensor design** until authentic-standard confirmation is documented for each target.

This does not invalidate the completed clinical or spectral feasibility calculations. It limits their interpretation: the calculations apply to the named molecules **if the RADicA annotations are correct**.

## What the study establishes

The RADicA paper reports an in-house library of 313 VOCs and the following identification procedure:

- NIST 2023 mass spectral library similarity score threshold of 80;
- retention-index agreement within ±20, based on C5–C15 alkane standards;
- up to two qualifier ions in addition to the quantifier ion;
- MSI Level 1 for 60 compounds confirmed with authentic chemical standards;
- MSI Level 2 for 247 compounds meeting the spectral and retention-index criteria without authentic-standard confirmation;
- MSI Level 3 for six unresolved compounds represented by molecular formulas or ambiguous analogues.

The five audited candidates have explicit chemical names rather than unknown molecular-formula labels. On the information reported by the paper, they are therefore consistent with Level 1 or Level 2, not the described Level 3 class.

## What is absent from the public release

The following evidence was checked on 2026-09-07:

1. `RADicA_VOC_raw_peak_data.csv` contains compound-name columns but no retention time, measured or predicted retention index, spectral similarity score, qualifier-ion ratios, standard identifier, or MSI level.
2. `RADicA_VOC_metadata.csv` contains participant and sample metadata, not chemical-identification metadata.
3. The four Europe PMC supplementary files describe downstream statistical results and methods but do not provide a compound-to-MSI-level or compound-to-standard mapping.
4. The paper-linked GitHub repository, `https://github.com/aturlo/RADicA`, had no commits visible on its default `main` branch when checked.

Consequently, the aggregate statement “60 compounds are Level 1” cannot be used to label any of the five candidates as standard-confirmed. Assigning individual Level 1 grades would be inference, not reported evidence.

## Audited candidates

| RADicA field | Standard identity | CAS | Publicly defensible study grade | Sensor-design status |
|---|---|---:|---|---|
| `X2_Butanone` | 2-butanone | 78-93-3 | MSI Level 1 or 2; exact grade unresolved | provisional |
| `Toluene` | toluene | 108-88-3 | MSI Level 1 or 2; exact grade unresolved | provisional |
| `Decane` | decane | 124-18-5 | MSI Level 1 or 2; exact grade unresolved | provisional |
| `X2_Heptanone` | 2-heptanone | 110-43-0 | MSI Level 1 or 2; exact grade unresolved | provisional |
| `Benzene._1.4_dichloro_` | 1,4-dichlorobenzene | 106-46-7 | MSI Level 1 or 2; exact grade unresolved | provisional |

The machine-readable record is `results/identity_confidence.csv`.

## Engineering consequence

No photonic architecture should be optimized around a candidate solely because its NIST infrared spectrum is available. Before freezing a molecular target, require one of:

1. the relevant RADicA in-house library record showing authentic-standard confirmation under the same TD-GC-MS method; or
2. a new targeted confirmation run using a certified standard, matching retention time/index and quantifier/qualifier ions in representative breath and background matrices.

For 2-butanone and toluene, this identity gate is additional to the already observed barriers: neither is clinically replicated under the locked analysis, both occur in ambient air, and the quantitative HITRAN model found atmospheric optical depth thousands of times larger than target optical depth in the searched windows.

## Sources

- RADicA paper and GC-MS identification method: https://pmc.ncbi.nlm.nih.gov/articles/PMC13338015/
- Public RADicA data DOI: https://doi.org/10.6084/m9.figshare.29504333
- Paper-linked code repository: https://github.com/aturlo/RADicA
- MSI reporting framework cited by the study: https://doi.org/10.1007/s11306-007-0082-2

