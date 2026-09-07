# Preconcentrator mass balance and timing — 2026-09-07

## Reference design

The reference scenario collects 500 mL of breath at 200 mL/min, recovers 80% of the target and transfers it into 5 mL of carrier gas. The geometric volume ratio is 100× and the net concentration enrichment is 80×.

At the literature asthma means, the ideal-gas mass balance gives:

| Quantity | Toluene | 2-Butanone |
|---|---:|---:|
| Breath concentration | 0.89 ppbv | 1.26 ppbv |
| Recovered amount | 14.7 pmol | 20.8 pmol |
| Recovered mass | 1.35 ng | 1.50 ng |
| Desorbed concentration | 71.2 ppbv | 100.8 ppbv |
| 10 m target attenuation | 84.6 ppm | 125 ppm |
| Idealized 3σ optical LOD at 1 ppm noise | 0.0315 ppbv | 0.0302 ppbv |

The estimated cycle is 20.5 minutes: 2.5 minutes collection, 8 minutes dry purge, 5 minutes desorption and transfer, and 5 minutes reset. This corresponds to a theoretical maximum of 23 cycles in an eight-hour period before calibration, blanks, failures and operator overhead.

## Sensitivity scenarios

| Scenario | Net enrichment | Cycle time | Toluene LOD | 2-butanone LOD |
|---|---:|---:|---:|---:|
| 500 mL, 10 mL desorption, 50% recovery | 25× | 20.5 min | 0.101 ppbv | 0.0966 ppbv |
| 500 mL, 5 mL desorption, 80% recovery | 80× | 20.5 min | 0.0315 ppbv | 0.0302 ppbv |
| 1 L, 5 mL desorption, 80% recovery | 160× | 23 min | 0.0158 ppbv | 0.0151 ppbv |
| 2 L, 5 mL desorption, 80% recovery | 320× | 28 min | 0.00789 ppbv | 0.00755 ppbv |

Increasing sample volume improves the idealized LOD almost linearly while adding only collection time in this model. That is an optimistic bound. Larger volumes increase water load, sorbent competition, breakthrough risk and total non-target VOC mass.

## What the calculation establishes

The earlier 100×/80%-recovery architecture scenario is physically equivalent to collecting 500 mL and transferring the recovered analyte into 5 mL. The required target mass is only at the low-ng level, so target mass alone is unlikely to set trap capacity. Capacity must instead be assessed against total water and total VOC loading.

The calculation does not establish that either compound will actually achieve 80% recovery. Toluene and 2-butanone differ in volatility, polarity and sorbent interaction, so recovery, breakthrough and desorption must be measured separately.

## Experimental gate

Before refining the photonic readout, a benchtop trap experiment should measure:

1. recovery at 0.1, 1 and 10 ppbv using certified standards;
2. breakthrough at 0.5, 1 and 2 L humid-gas volumes;
3. residual water and CO2 after purge;
4. blank level and carryover after desorption;
5. repeatability across at least seven replicate cycles;
6. recovered concentration or mass using an independent reference method.

The preferred starting condition is the 500 mL reference design. It matches the RADicA sampling volume, keeps collection time short and already provides adequate idealized optical signal. Scaling to 1–2 L should occur only if measured recovery and blank performance are insufficient.

## Assumptions and provenance

- The RADicA protocol collected 500 mL at 200 mL/min and used an 8 minute nitrogen purge: https://pmc.ncbi.nlm.nih.gov/articles/PMC13338015/
- Its two thermal-desorption stages used 3 and 2 minute desorption intervals; the model combines these into a 5 minute transfer allowance.
- A three-stage cooled preconcentration study used 500 mL breath injection and reported sub-0.1 ppbv LODs, while emphasizing dehydration, trapping and focusing: https://doi.org/10.1021/acsomega.5c01166
- Five minutes of reset time is an engineering allowance, not a value reported by either study.
- The calculation assumes ideal gas behavior and complete mixing in the 5 mL desorption volume.

