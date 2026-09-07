# Application materials

These drafts describe the project accurately as a completed computational feasibility study. Replace bracketed text only when tailoring the outreach paragraph to a specific laboratory.

## CV entry — compact version

**From Breathomics to Photonic Targets — Independent Research Project**

Built a reproducible Python workflow linking clinical breathomics with quantitative mid-IR sensor feasibility. Audited a 346-visit public GC-MS release, prevented discovery/validation leakage, and found 0/142 VOCs meeting a locked cross-cohort replication rule. Integrated NIST and HITRAN spectroscopy, Beer–Lambert and noise models, and a nine-gate go/no-go framework; identified preconcentration as the only conditionally testable route and designed a 115-run benchtop validation protocol.

## CV bullets — technical version

- Audited public asthma breathomics data spanning 112 participants and 346 visits; detected three discovery/validation participant overlaps and implemented participant-level, leakage-aware validation across 142 VOC features.
- Tested a predeclared cross-cohort replication rule and reported a null primary result without promoting exploratory candidates to biomarkers.
- Curated experimental NIST gas-phase spectra and quantitative QUANT-IR data, then modelled HITRAN H2O/CO2 interference, resolution loss, optical noise, multipass/cavity architectures, and preconcentration mass balance.
- Converted the evidence into versioned go/no-go criteria and an automated evaluator for a 115-run recovery, humidity, blank, carryover, breakthrough, and atmospheric-residual protocol; maintained 29 passing software tests.

## Personal or research statement paragraph

In my independent project *From Breathomics to Photonic Targets*, I investigated a question that sits between biomarker discovery and optical instrumentation: when is a clinically reported volatile organic compound sufficiently reproducible and measurable to justify sensor development? I audited a public asthma breathomics release, discovered participant overlap between nominal discovery and validation datasets, and implemented a locked participant-level replication analysis. None of 142 VOCs replicated, so I treated all subsequent candidates as exploratory rather than forcing a diagnostic conclusion. I then connected experimental gas-phase spectra, quantitative absorption data, HITRAN water and carbon-dioxide interference, and instrument noise models in a versioned decision framework. The resulting negative feasibility decision showed me that useful engineering research is not only about building a device; it is also about identifying unsupported assumptions early and designing the smallest experiment that can change the decision.

## Prospective-advisor outreach paragraph

I believe this project could let me contribute to your group beyond bringing a general interest in [LAB RESEARCH AREA]. I have developed a reproducible workflow that connects clinical biomarker evidence to spectroscopic and instrument-level feasibility, including leakage-aware cohort validation, quantitative interference modelling, and explicit go/no-go criteria. Applied to asthma breath VOCs, it identified why a seemingly promising direct optical route should not yet proceed and converted the remaining uncertainty into a staged benchtop protocol. For your work on [SPECIFIC LAB PROJECT OR PAPER], I could help test candidate targets and sensing assumptions before costly fabrication or integration, while making negative or conditional results reproducible and experimentally actionable.

## Short interview answer — “Tell me about this project”

I wanted to know whether published asthma breath biomarkers were actually ready to become photonic sensor targets. I built an evidence chain from public GC-MS data to gas-phase spectra, atmospheric interference, and instrument noise. The most important result was negative: none of 142 VOCs replicated across the locked cohorts, and even the exploratory targets had severe water and carbon-dioxide interference. Instead of hiding that result, I formalized the reasons not to build the diagnostic device and designed the smallest benchtop experiment that could test the remaining preconcentration route. The project taught me how to make engineering decisions under imperfect biological evidence.

## Portfolio caption

An end-to-end feasibility study connecting asthma breathomics to mid-infrared photonic sensing. The project demonstrates data auditing, independent-cohort validation, quantitative spectroscopy, physics-based sensor modelling, and evidence-gated experimental design. Its primary contribution is a defensible no-go decision for premature diagnostic hardware and a testable route for limited methods validation.

## Claims to avoid

- “Discovered an asthma biomarker.” No VOC passed the locked replication rule.
- “Developed an asthma diagnostic sensor.” No optical hardware was built or validated.
- “Achieved a 0.03 ppbv detection limit.” This is an idealized model result, not a measured LOD.
- “Identified interference-free windows.” The quantitative screen found no clean single window in the downloaded range.
- “Confirmed the five compounds.” Compound-level authentic-standard status remains unresolved.

## Tailoring checklist

Before using the outreach paragraph:

1. cite one specific recent project or paper from the laboratory;
2. name the lab problem this workflow could help solve;
3. describe the concrete contribution—validation, spectroscopy, modelling, or experiment design;
4. remove any technique the target laboratory does not use;
5. keep the negative result, but lead with the decision process and research value.
