# Benchtop preconcentrator validation protocol — 2026-09-07

## Scope and decision rule

This protocol tests whether a 500 mL to 5 mL breath-VOC preconcentrator can provide sufficiently reproducible recovery and atmospheric-background removal for later optical measurements of toluene and 2-butanone.

It is a research go/no-go protocol, not a regulatory validated method and not a protocol for collecting human samples. Begin with certified gas mixtures and synthetic humidified gas. Human breath testing requires separate ethics, biosafety and clinical sampling approval.

Proceed to optical integration only if **both targets pass every primary criterion** at 0.1, 1 and 10 ppbv. A failed target is removed rather than rescued by post-hoc threshold changes.

## Safety prerequisites

Do not begin until the laboratory supervisor has approved a written risk assessment covering compressed gas, heated desorption, flammable VOCs, ventilation and exhaust disposal.

- Use a certified dilute gas standard in an inert balance gas. Do not prepare standards by evaporating neat toluene or 2-butanone unless the laboratory already has an approved chemical-handling procedure.
- Locate cylinders and dilution hardware in approved ventilated space with secured cylinders, compatible regulators and verified leak checks.
- Route trap and optical-cell exhaust to an approved extraction system; do not vent into the room.
- Keep ignition sources away from standards and desorption hardware.
- Obtain and follow the supplier SDS. Use laboratory-required eye protection, coat and gloves, and provide spill and eyewash procedures.
- Verify that hot surfaces, valves, sorbent and seals are compatible with the maximum desorption temperature.

NIOSH identifies 2-butanone as a Class IB flammable liquid and lists eye, skin, respiratory and central-nervous-system effects. OSHA identifies central-nervous-system and irritation hazards for toluene. Occupational limits are not design targets: the test system should remain closed and externally exhausted.

## Required equipment

- certified mixed standard containing toluene and 2-butanone, with certificate and uncertainty;
- hydrocarbon-free zero air or high-purity inert dilution gas;
- calibrated mass-flow controllers or equivalent dynamic dilution system;
- humidity generator and traceable dew-point or humidity measurement;
- primary sorbent trap and identical secondary breakthrough trap;
- thermal desorber with measured desorption volume;
- reference quantification method capable of ≤0.02 ppbv blanks and ≤0.1 ppbv LOD;
- pressure, temperature and flow logging;
- independent water/CO2 measurement before and after treatment;
- data sheet based on `results/benchtop_run_plan.csv`.

## Pre-run qualification

1. Record standard lot, certificate, expiry, balance gas and regulator identity.
2. Calibrate flow at the intended 200 mL/min setpoint. Error must be ≤5%.
3. Verify accumulated 500 mL sample volume within ±5%.
4. Leak-test all lines at operating pressure and temperature.
5. Condition the trap until three consecutive system blanks meet ≤0.02 ppbv for both targets.
6. Verify desorption volume at 5.0 mL within ±5% or record the measured value and regenerate the mass balance.
7. Confirm that the reference instrument passes its own calibration and continuing-check requirements.

## Locked run sequence

The generated plan contains 115 runs:

| Phase | Runs | Purpose |
|---|---:|---|
| Start/end system blanks | 6 | demonstrate initial cleanliness and terminal drift/carryover |
| Recovery and precision | 63 | 0.1, 1 and 10 ppbv × 0, 50 and 90% RH × 7 replicates |
| Breakthrough | 18 | 0.5, 1 and 2 L × 50 and 90% RH × 3 replicates, using a secondary trap |
| Carryover | 14 | seven 10 ppbv/90% RH challenges, each immediately followed by a blank |
| Atmospheric residual | 14 | zero air at 50 and 90% RH × 7 replicates, with H2O/CO2 optical-depth measurement |

Recovery and breakthrough conditions are reproducibly randomized using seed `20260907`. Challenge and blank runs remain adjacent so carryover can be calculated.

For every run, record actual rather than nominal flow, volume, RH, temperature, pressure, collection time, purge time, desorption temperature/time/volume, target result, secondary-trap result, H2O/CO2 result and any deviation.

## Calculations

### Recovery

`recovery (%) = measured recovered amount / introduced amount × 100`

Calculate separately for each target, concentration and humidity. Report mean, SD, RSD and confidence interval. Do not substitute missing or censored measurements with zero.

### Humidity bias

For each concentration, compare mean recovery at 50 and 90% RH with the dry condition. Report the relative difference and its uncertainty.

### Breakthrough

`breakthrough (%) = secondary-trap amount / (primary + secondary amount) × 100`

Analyze both traps. A low primary-trap result without the secondary trap cannot distinguish poor recovery from breakthrough.

### Carryover

`carryover (%) = blank amount after challenge / preceding challenge recovered amount × 100`

Also apply the absolute blank requirement; passing a percentage criterion after a large challenge is not sufficient.

### Atmospheric residual

Measure H2O and CO2 optical depth before and after the complete treatment path at 1030.75 and 939.20 cm⁻¹. Calculate the post/pre optical-depth ratio and cycle-to-cycle residual SD.

## Primary acceptance criteria

| Metric | Acceptance criterion |
|---|---:|
| Mean recovery | 70–130% for each target/condition |
| Recovery precision | RSD ≤20% |
| Humidity bias | ≤20% relative to dry recovery |
| White-noise-equivalent LOD | ≤0.1 ppbv |
| System/method blank | ≤0.02 ppbv per target |
| Carryover | ≤1% of preceding challenge and ≤0.02 ppbv |
| Breakthrough at 500 mL | ≤5% |
| Breakthrough at 1 L | ≤10% |
| Treated H2O/CO2 optical depth | ≤1% of untreated humid-gas value |
| Flow and volume accuracy | each within ±5% |

The 2 L condition is exploratory and does not need to pass for the 500 mL reference design. If 500 mL passes but 1 L fails, retain the 500 mL design and document the capacity boundary.

## Stop conditions

Stop the sequence and investigate before continuing if:

- a leak, unexpected pressure rise, uncontrolled heating or exhaust failure occurs;
- blanks exceed 0.02 ppbv twice consecutively;
- carryover exceeds 5% after a challenge;
- the secondary trap exceeds 20% of total target at 500 mL;
- measured humidity or flow leaves its allowed band;
- the reference method's continuing calibration check fails.

Do not delete failed runs. Record the deviation, corrective action and complete pre/post-conditioning blanks before restarting.

## Interpretation

- **Pass:** both targets meet all primary criteria; proceed to coupled trap–optical-cell testing.
- **Conditional pass:** only one target passes; continue only with that molecule and update all target-selection claims.
- **Fail:** neither target passes, or treated H2O/CO2 remains above the optical budget; stop this preconcentration design and reassess sorbent/dehydration strategy.

Even a technical pass does not establish an asthma biomarker. Clinical replication and compound-level authentic-standard identity remain independent gates.

## Sources

- EPA Method TO-15A, including humidified matrix matching, calibration and blank principles: https://www.epa.gov/sites/default/files/2019-12/documents/to-15a_vocs.pdf
- RADicA sampling and TD-GC-MS conditions: https://pmc.ncbi.nlm.nih.gov/articles/PMC13338015/
- NIOSH Pocket Guide for 2-butanone: https://www.cdc.gov/niosh/npg/npgd0069.html
- OSHA toluene exposure and hazard information: https://www.osha.gov/toluene/occupational-exposure-limits

