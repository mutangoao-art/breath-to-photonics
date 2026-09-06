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

Downloaded NIST JCAMP files are cached under `data/raw/spectra/nist/` and excluded from Git. Their identity, CAS number, phase and source URL are recorded in `configs/spectral_manifest_v0.1.json`.

Gas-phase water (CAS 7732-18-5) and carbon dioxide (CAS 124-38-9) JCAMP records are also cached in that directory. Their provenance and their role as qualitative interferents are recorded in `configs/interference_manifest_v0.1.json`.

## Quantitative spectral references

- Source: NIST Quantitative Infrared Database, https://webbook.nist.gov/chemistry/quant-ir/
- Local location: `data/raw/spectra/nist-quant/` (excluded from Git)
- Selected format: gas-phase absorption coefficient, Boxcar apodization, nominal 2 cm⁻¹ entry (JCAMP metadata report 1.929 cm⁻¹)
- Covered exploratory targets: 2-butanone and toluene
- Not present in the NIST Quantitative IR species table: decane, 2-heptanone, and 1,4-dichlorobenzene
- Coefficient units: `(micromol/mol)-1 m-1 (base 10)`, so concentration in ppm and path in metres can be used directly in the NIST Beer–Lambert convention
- Coverage and scenario assumptions are locked in `configs/quantitative_manifest_v0.1.json`

## Breath concentration anchor

- Source: Huzar et al., *Needle Trap Device-GC-MS for Characterization of Lung Diseases Based on Breath VOC Profiles*, Molecules 2021, 26, 1787
- DOI: https://doi.org/10.3390/molecules26061787
- Relevant values: asthma-subgroup mean (SD) 2-butanone 1.26 (0.80) ppbv and toluene 0.89 (0.60) ppbv
- Detection frequencies in asthma samples: 87.5% and 50.0%, respectively
- Limitation: asthma subgroup n=8; these values anchor an engineering scenario and are not treated as population reference intervals
