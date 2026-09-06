# From Breathomics to Photonic Targets

This project asks one engineering question:

> Which asthma-associated breath volatile organic compounds (VOCs) are reproducible across independent cohorts and also plausible targets for compact mid-infrared sensing?

The first milestone is deliberately narrow: download and audit the public RADicA breathomics release before choosing any statistical model.

## Planned evidence chain

1. Audit the clinical breathomics files, metadata, licence, cohorts, labels, compounds, missing values, and ambient-air matching.
2. Correct breath signals using matched ambient-air samples.
3. Select candidates in a discovery cohort and test effect direction in an untouched validation cohort.
4. Match validated candidates to experimental gas-phase IR reference spectra.
5. rank candidates by clinical reproducibility, spectral selectivity against H2O/CO2, and measurement complexity.

The project will keep three evidence types separate:

- patient breath GC-MS data: which VOCs may be clinically relevant;
- experimental pure-gas IR spectra: where compounds absorb;
- physics-based simulations: how humidity, CO2, resolution, noise, and drift may affect a sensor.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m breath_to_photonics.audit data/raw --output results/data_audit.json
pytest
```

Raw public data are not committed. See `data/SOURCES.md` for provenance and download status.

## Current status

Project scaffold and reusable data-audit pipeline are in place. The paper and author code confirm a promising public schema, while the current network receives HTTP 403 from Figshare. Dataset eligibility is not assumed until the downloaded files pass the generated audit. See `docs/DATA_AUDIT_2026-09-06.md`.
