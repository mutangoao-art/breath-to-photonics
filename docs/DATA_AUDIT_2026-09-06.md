# RADicA data audit — 2026-09-06

## Gate result: pending download, promising schema

The primary dataset has not yet passed the field-level eligibility gate because the Figshare API, DOI landing page, and bulk-download endpoint returned HTTP 403 from the current execution network. No HTML error page was saved as data.

## What is independently verified

From the paper's Data Availability Statement:

- metabolomic data and associated metadata are public at DOI `10.6084/m9.figshare.29504333`;
- additional anonymised clinical data require sponsor approval and a data-access agreement;
- the analysis code is public.

From the author's public analysis scripts:

- raw input filenames are `RADicA_VOC_raw_peak_data.csv` and `RADicA_VOC_metadata.csv`;
- the raw peak table contains at least `Sample`, `Acq_Date_Time`, and `Batch` plus VOC peak-area columns;
- sample names distinguish blanks, external standards, room-air background (`B1`), and two breath replicates (`S1`, `S2`);
- batches 1–4 and 5–6 are processed as two data-collection campaigns;
- metadata contain at least `Sample_ID`, `CoreVisit`, `ID`, `Analysis_date`, and `Diagnosis`;
- room air and breath replicates are joined by participant and core visit;
- zero peak areas are treated as missing in the published pipeline;
- the published correction models log breath signal against log background signal and diagnosis.

## What still must be checked in the downloaded release

- exact file version and licence;
- participant counts by cohort and diagnosis;
- whether every breath sample has a usable matched room-air sample;
- chemical annotation fields, names, and CAS identifiers;
- detection-limit encoding versus true absence;
- duplicate samples and repeated visits;
- whether public diagnosis metadata are sufficient for our independent validation design;
- whether the two campaigns can legitimately be treated as discovery and validation cohorts for the proposed question.

## Decision

Keep RADicA as the primary candidate, but do not begin candidate-VOC statistics until the actual files pass the automated and manual checks above. If access remains blocked or essential fields are absent, switch to the documented Kuo fallback and revise the scientific claim accordingly.

