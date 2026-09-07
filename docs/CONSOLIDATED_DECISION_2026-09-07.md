# Consolidated project decision — 2026-09-07

## Decision

The computational phase produced a useful and reproducible **negative feasibility result**.

- Do **not** build or present a photonic instrument for asthma diagnosis from the current target set.
- A small benchtop preconcentrator study is conditionally justified as a measurement-method experiment only.
- If certified standards, gas-handling hardware, and laboratory safety approval are unavailable, stopping here is a scientifically valid outcome.

This decision is generated from the versioned thresholds in `configs/decision_gates_v0.1.json`. The machine-readable outputs are `results/decision_gates.csv` and `results/decision_summary.json`.

## Why the result is valid

“Negative” does not mean that the analysis failed. The clinical files passed structural audit after three overlapping participants were removed from validation, the analysis rule was locked before target selection, experimental gas-phase reference spectra were verified, and every later calculation preserves the distinction between measured evidence and simulated performance.

The result is effective at answering the project question: the present evidence chain does not support choosing a molecular target and committing to diagnostic hardware. It prevents an expensive build from being based on a cohort-specific statistical signal or an optically unsuitable window.

## Decision gates

| Gate | Status | Evidence | Consequence |
|---|---|---|---|
| Public clinical data integrity | Pass | Required files and matching passed; three overlapping participants were excluded | The release is usable for the locked analysis |
| Cross-cohort clinical replication | Fail | 0 of 142 VOCs met the replication rule | No current VOC is a validated asthma biomarker |
| Experimental gas-phase reference | Pass | Five exploratory VOCs have verified NIST gas-phase spectra | Band positions can be studied |
| Quantitative target spectra | Partial | Compatible QUANT-IR data exist for 2 of 5 candidates | Quantitative modelling is limited to 2-butanone and toluene |
| Compound-level identity | Blocked | Authentic-standard/MSI Level 1 status is unresolved for all five | No molecular target should be frozen for hardware |
| Clean atmospheric window | Fail | Best modelled H2O+CO2/target optical-depth ratio is about 6,236:1 | No clean single window exists in 650–1250 cm⁻¹ under the stated model |
| Direct 10 m detection | Fail | Maximum target signal is 1.56 ppm; 3σ requires less than 0.522 ppm noise | Direct transmission is unsupported at literature-mean concentrations |
| Preconcentration route | Conditional | Idealized 80× net enrichment and about 0.030–0.032 ppbv LOD | Plausible on paper, but recovery and water removal are unmeasured |
| Benchtop validation | Pending | The unfilled 115-run plan evaluates as `not_evaluable` | Measurements are required before optical integration |

## What is established and what is not

Established:

- the audited public-data structure and the overlap-mitigated analysis population;
- absence of a replicated VOC under the locked v0.1 rule;
- verified gas-phase band locations for five exploratory compounds;
- quantitative bounds for two compounds under explicit assumptions;
- severe H2O/CO2 interference in the downloaded HITRAN range;
- an executable benchtop protocol and acceptance evaluator.

Not established:

- an asthma biomarker or diagnostic classifier;
- authentic-standard confirmation for any of the five target identities;
- a clean, selective spectral window;
- real preconcentrator recovery, humidity tolerance, breakthrough, blanks, or carryover;
- an experimentally demonstrated optical limit of detection.

## Allowed next step

Proceed only if the work is framed as a benchtop methods validation with no asthma-diagnostic claim. Start with the least expensive stopping block:

1. verify system blanks and flow/volume accuracy;
2. run certified-standard recovery at 500 mL for 2-butanone and toluene;
3. stop immediately if blanks exceed 0.02 ppbv, recovery falls outside 70–130%, or RSD exceeds 20%;
4. only after that, continue to humidity, breakthrough, carryover, and atmospheric-residual tests;
5. do not integrate photonic hardware until the complete evaluator returns `pass` or a scientifically reviewed `conditional_pass`.

The complete locked protocol remains 115 runs. The staged start above is a cost-control checkpoint, not a replacement for the full acceptance test.

## Reopening the diagnostic-hardware decision

The decision may be reconsidered only when all three upstream blockers change:

1. at least one VOC replicates in an independent clinical cohort under a predeclared rule;
2. that compound is confirmed with an authentic standard in the relevant analytical workflow;
3. a quantitative sensing route passes interference, noise, and benchtop acceptance gates.

Additional simulations alone cannot satisfy these conditions.
