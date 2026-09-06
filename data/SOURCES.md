# Data sources and provenance

## Primary clinical dataset

- Name: RADicA untreated symptomatic asthma breath VOC dataset
- Repository: Figshare
- DOI: https://doi.org/10.6084/m9.figshare.29504333
- Intended use: participant-level VOC signals, asthma/not-asthma labels, independent cohorts, and matched ambient-air samples
- Local location: `data/raw/radica/`
- Paper data statement: metabolomic data and associated metadata are public; additional anonymised clinical data require an approved request and data-access agreement
- Author analysis code: https://github.com/aturlo/RADicA-breath-VOC-analysis
- Expected public filenames confirmed by the author code: `RADicA_VOC_raw_peak_data.csv` and `RADicA_VOC_metadata.csv`
- Local location: `data/raw/radica/` (manually downloaded; excluded from Git)
- Status: required structures are present; split design needs review because three participants overlap B1/B2; see `docs/DATA_AUDIT_2026-09-06.md`

No eligibility claim is made until `results/data_audit.json` confirms the actual public files and fields.

## Fallback clinical dataset

- Name: Kuo Clinical Breathomics Dataset
- DOI: https://doi.org/10.6084/m9.figshare.23522490.v6
- Intended use only if the primary release lacks critical participant-level fields

## Spectral references (later milestone)

- NIST Chemistry WebBook gas-phase IR spectra: experimental reference spectra
- NIST Quantitative Infrared Database: quantitative absorption coefficients when available
- HITRAN/HAPI: line parameters used to generate physics-based synthetic spectra for small molecules and interferents
