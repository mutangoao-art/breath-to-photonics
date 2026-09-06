# NIST spectral audit — 2026-09-06

## Scope

The primary clinical replication rule yielded no validated VOC. Spectral work therefore proceeds only as an explicitly exploratory feasibility screen. It must not be interpreted as sensor-target validation.

Five direction-consistent exploratory VOCs were matched to standard chemical identities and experimental gas-phase IR spectra in the NIST Chemistry WebBook:

| RADicA column | Standard identity | CAS | NIST phase | Strong relative band from this record |
|---|---|---|---|---:|
| `X2_Butanone` | 2-butanone | 78-93-3 | gas | 1730 cm-1 (5.780 µm) |
| `Decane` | decane | 124-18-5 | gas | 2934 cm-1 (3.408 µm) |
| `X2_Heptanone` | 2-heptanone | 110-43-0 | gas | 2942 and 1730 cm-1 (3.399 and 5.780 µm) |
| `Toluene` | toluene | 108-88-3 | gas | 726 cm-1 (13.774 µm) |
| `Benzene._1.4_dichloro_` | 1,4-dichlorobenzene | 106-46-7 | gas | 1094 cm-1 (9.141 µm) |

The detected bands are algorithmic peaks from normalized reference spectra, not proposed final detection wavelengths.

## Important rejection

The first NIST records inspected for 3-methylpentane, ethyl butanoate, and 3-methyl-1-butanol were labelled liquid or liquid-neat. They were not used as breath gas spectra. This prevents a common but serious phase-mismatch error.

## What these spectra can support

- confirming that an experimental gas-phase reference spectrum exists;
- comparing qualitative band positions within the recorded spectral range;
- identifying regions worth checking against water and carbon dioxide interference.

## What they cannot support yet

- comparing sensitivity between compounds, because spectra were acquired under different conditions;
- calculating ppm-level concentration or limit of detection without quantitative absorption coefficients, concentration, and path length;
- claiming selectivity in humid breath before adding H2O and CO2 spectra;
- claiming that a GC-MS annotation is definitively identified without annotation-confidence evidence.

The next technical gate is quantitative interference analysis using compatible absorption-coefficient data, preferably from NIST Quantitative IR, PNNL, or a documented HITRAN-based simulation where the molecule is covered.

