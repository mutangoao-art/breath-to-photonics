# RADicA data audit — 2026-09-06

## Gate result: data usable, split design needs revision

The user manually downloaded the four public files after automated Figshare access returned HTTP 403. They are stored under `data/raw/radica/` and excluded from Git. All required structures are present, but the dataset-specific audit correctly returns `needs_review` because B1 and B2 are not fully participant-independent.

Observed release summary:

- raw peak table: 1,548 rows and 312 VOC columns across batches 1–6;
- metadata: 1,038 rows, 112 participants (68 asthma; 44 not asthma);
- 346 participant-visit groups, all containing one matched room-air sample and two breath replicates;
- processed B1: 91 participant-visits from 52 participants (33 asthma; 19 not asthma);
- processed B2: 105 participant-visits from 62 participants (37 asthma; 25 not asthma);
- B1 and B2 have the same 142 processed VOC columns;
- three participants overlap: ID36, ID52, and ID53 have CV1 in B1 and CV2 in B2;
- the supplied processed VOC matrices contain no missing values.

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

## What still must be checked before statistical selection

- exact file version and licence;
- chemical annotation fields, names, and CAS identifiers;
- detection-limit encoding versus true absence;
- duplicate samples and repeated visits;
- whether the two campaigns can legitimately be treated as discovery and validation cohorts for the proposed question.

## Decision

Keep RADicA as the primary dataset. Do not treat B1 and B2 as independent without adjustment. Before inspecting candidate effects, assign each overlapping participant wholly to one partition or exclude those participants, lock which cohort is discovery versus validation, decide whether to use the author-adjusted matrices or reproduce preprocessing, and document how repeated visits will be handled.
