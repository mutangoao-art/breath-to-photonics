# Benchtop validation evaluator — 2026-09-07

## Purpose

`breath_to_photonics.validation_evaluator` converts a completed copy of `results/benchtop_run_plan.csv` into individual acceptance checks and an overall `pass`, `conditional_pass`, `fail`, or `not_evaluable` decision.

The evaluator uses the locked thresholds in `configs/benchtop_validation_v0.1.json`. It does not silently replace missing measurements with nominal values or zero.

## Required measurements

Every run requires actual flow, actual volume, actual RH, temperature, pressure, desorption volume and primary-trap result for both targets. Breakthrough runs additionally require both secondary-trap results. Atmospheric-residual runs require pre- and post-treatment H2O/CO2 optical depth at both selected windows.

Optional deviation notes do not block evaluation, but all experimental deviations should be recorded.

## Calculated checks

For each target, the evaluator calculates:

- mean recovery and RSD for every concentration/humidity block;
- humidity bias relative to the matching dry block;
- a seven-replicate low-level MDL estimate using `3.143 × SD` of input-equivalent concentration;
- system blank concentration;
- carryover as a percentage of the immediately preceding challenge and as an absolute blank concentration;
- secondary-trap breakthrough percentage at 500 mL and 1 L.

System checks include:

- post/pre H2O/CO2 optical-depth fraction at 1030.75 and 939.20 cm⁻¹;
- actual flow error relative to the run setpoint;
- actual volume error relative to the run setpoint.

The 2 L breakthrough block remains exploratory and is reported in the source records but is not used as a locked pass/fail condition.

## Decision logic

- `pass`: both targets and all system checks pass;
- `conditional_pass`: exactly one target passes and all system checks pass;
- `fail`: neither target passes or a shared system check fails;
- `not_evaluable`: one or more required measurements are missing.

All individual results are retained in `results/benchtop_evaluation.csv`; the summary decision and missing-field counts are stored in `results/benchtop_evaluation_summary.json`.

## Usage

After entering measurements in a copy of the locked run plan:

```bash
PYTHONPATH=src python -m breath_to_photonics.validation_evaluator path/to/completed_run_plan.csv
```

Use `--output` and `--summary` to preserve separate evaluations for different experiment dates. Do not overwrite the locked empty run plan with experimental measurements.

## Current state

Running the evaluator against the unfilled template correctly returns `not_evaluable`. This is the expected project state until physical experiments are completed.

