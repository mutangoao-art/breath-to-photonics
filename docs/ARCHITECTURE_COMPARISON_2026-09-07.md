# Photonic architecture comparison — 2026-09-07

## Decision

Path enhancement alone is not the preferred next prototype route. A preconcentration-assisted optical measurement is more defensible because it can enrich the VOC while removing most H2O and CO2. This improves chemical contrast, whereas a longer multipass cell or enhancement cavity scales target and atmospheric absorption together.

This remains an engineering scenario comparison, not a validated instrument design. No architecture should proceed to hardware for an asthma claim until a target passes clinical replication and authentic-standard identity gates.

## Compared scenarios

All scenarios use the best windows found in the available 650–1250 cm⁻¹ HITRAN range and assume 1 ppm relative transmission noise so that scaling effects can be compared directly.

| Architecture scenario | Effective path | Target enrichment and recovery | Atmospheric residual |
|---|---:|---:|---:|
| Direct multipass baseline | 10 m | 1×, 100% | 100% |
| Direct multipass, idealized | 100 m | 1×, 100% | 100% |
| Cavity enhanced, idealized | 1000 m | 1×, 100% | 100% |
| Preconcentration assisted | 10 m | 100×, 80% | 1% |

The 100× enrichment, 80% recovery, 1% residual and fixed-noise values are explicit sensitivity assumptions. They are not claimed as measured performance.

## Results

| Target and scenario | Target attenuation | Background transmission | Idealized 3σ LOD | Background optical-depth tolerance |
|---|---:|---:|---:|---:|
| Toluene, 10 m direct | 1.06 ppm | 99.25% | 2.52 ppbv | 46.6 ppm relative |
| Toluene, 100 m direct | 10.58 ppm | 92.71% | 0.252 ppbv | 46.6 ppm relative |
| Toluene, 1000 m cavity | 105.81 ppm | 46.93% | 0.0252 ppbv | 46.6 ppm relative |
| Toluene, preconcentration | 84.65 ppm | 99.992% | 0.0315 ppbv | 372,928 ppm relative |
| 2-Butanone, 10 m direct | 1.56 ppm | 99.03% | 2.42 ppbv | 53.4 ppm relative |
| 2-Butanone, 100 m direct | 15.65 ppm | 90.70% | 0.242 ppbv | 53.4 ppm relative |
| 2-Butanone, 1000 m cavity | 156.46 ppm | 37.69% | 0.0242 ppbv | 53.4 ppm relative |
| 2-Butanone, preconcentration | 125.17 ppm | 99.990% | 0.0302 ppbv | 427,591 ppm relative |

Under the fixed-noise assumption, the 1000 m cavity produces the lowest white-noise-equivalent LOD because its path multiplier is 100×, compared with an 80× net target gain in the preconcentration scenario. However, its H2O/CO2 background absorbs approximately 53% or 62% of incident light and the required relative background repeatability is unchanged.

The preconcentration scenario reduces atmospheric optical depth by 100× while increasing recovered target abundance by 80×. It therefore improves the target-to-atmospheric-background ratio by 8000× and greatly relaxes the background subtraction requirement. Actual performance will depend on analyte-specific capture, breakthrough, desorption, carryover and water management.

## Relation to published demonstrations

- An 18 m mid-infrared multipass instrument has demonstrated 1 ppb precision for CO with 10 s averaging. This verifies that compact multipass trace-gas instruments can be sensitive, but CO line spectroscopy is not directly transferable to broad, weak VOC fingerprints: https://doi.org/10.1364/AO.36.008042
- Mid-infrared optical-feedback cavity-enhanced spectroscopy has reported a noise-equivalent absorption coefficient of 3 × 10⁻⁹ cm⁻¹ at 1 s and a 35 pptv N2O limit under reduced pressure. This establishes cavity capability for favorable narrow-line gases, not these two VOCs in humid breath: https://doi.org/10.1364/OL.35.003607
- A Stirling-cooled three-stage preconcentrator coupled to GC-FID/MS reported 0.01–0.09 ppbv LODs across 116 VOCs. It supports the concentration regime assumed here while also showing that the demonstrated solution uses dehydration, trapping, focusing and chromatographic separation rather than direct optics: https://doi.org/10.1021/acsomega.5c01166

## Recommendation

If the project continues toward hardware, the next design should be a hybrid concept:

1. paired background and breath sampling;
2. water/CO2 removal with analyte-specific recovery validation;
3. modest preconcentration rather than extreme optical path alone;
4. spectral or temporal separation before optical readout;
5. certified 2-butanone and toluene standards to measure recovery, carryover and cross-sensitivity.

The appropriate next calculation is a preconcentrator mass balance and timing model covering sample volume, enrichment factor, recovery, trap capacity, desorption volume and cycle time.

