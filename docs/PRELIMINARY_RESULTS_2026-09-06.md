# Preliminary cross-cohort results — 2026-09-06

## Primary result

The v0.1 rules were locked in `configs/analysis_v0.1.json` before candidate effects were inspected. B2 was used for discovery. B1 was used for validation after removing ID36, ID52, and ID53 because those participants also appeared in B2. Repeated visits were averaged within participant.

- Discovery: 62 participants.
- Validation: 49 previously unseen participants.
- Tested: 142 VOCs.
- Primary discovery candidates: 1.
- Candidates meeting the locked replication rule: 0.

D-menthone passed the discovery rule (Hedges g = -0.94; FDR q = 0.097) but reversed direction in validation (g = +0.21). It therefore failed replication.

This is a useful negative result: the current processed data do not support claiming a cross-cohort asthma VOC biomarker under the locked criteria.

## Exploratory follow-up

Eighteen VOCs had the same effect direction and an absolute Hedges g of at least 0.20 in both cohorts. This criterion was added only after the primary result and is explicitly exploratory. None passed the primary multiple-testing and replication rule.

The strongest direction-consistent effects by the smaller absolute cohort effect were:

| VOC | Discovery g | Validation g | Interpretation |
|---|---:|---:|---|
| 3-methylpentane | -0.56 | -0.51 | lower adjusted signal in asthma |
| ethyl butanoate | -0.46 | -0.65 | lower adjusted signal in asthma |
| 1-pentanol | +0.35 | +0.66 | higher adjusted signal in asthma |
| azetidine | +0.30 | +0.55 | higher adjusted signal in asthma |
| 3-methylbutan-1-ol | +0.30 | +0.64 | higher adjusted signal in asthma |

These are feasibility hypotheses for the spectral-mapping stage, not validated biomarkers. Chemical identity confidence and availability of quantitative gas-phase IR spectra must be checked before any hardware recommendation.

## Limits

- The supplied B1/B2 matrices are already background-adjusted, filtered, imputed, and normalized by the original authors.
- The current analysis tests association, not diagnostic performance or causality.
- Welch tests and standardized mean differences do not model all possible clinical covariates.
- Chemical names are GC-MS annotations and require identity-quality review.
- Multiple-testing correction leaves no replicated candidate under the primary rule.

