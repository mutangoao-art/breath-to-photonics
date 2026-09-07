# Noise and background-repeatability budget — 2026-09-07

## Purpose

This screen converts the best windows found within 650–1250 cm⁻¹ into minimum optical measurement requirements. It answers a narrower question than an instrument design: how stable would an ideal 10 m transmission measurement need to be for a 3σ observation at the literature asthma mean?

## Assumptions

- target and HITRAN optical depths are taken from the 296 K, 1 atm, 5% H2O, 4% CO2, 10 m and 2 cm⁻¹ baseline;
- selected windows are 1030.75 cm⁻¹ for toluene and 939.20 cm⁻¹ for 2-butanone;
- target concentrations are 0.89 and 1.26 ppbv, respectively;
- required signal-to-noise ratio is 3;
- target attenuation is treated as linear in concentration in this low-optical-depth regime;
- the background-repeatability calculation limits the residual error in combined H2O/CO2 optical depth to one third of target optical depth.

## Results

| Target | Target attenuation at 10 m | Maximum 1σ relative transmission noise | Maximum relative error in background optical depth | Idealized 3σ LOD at 1 ppm noise |
|---|---:|---:|---:|---:|
| Toluene | 1.06 ppm | 0.353 ppm | 46.6 ppm | 2.52 ppbv |
| 2-Butanone | 1.56 ppm | 0.522 ppm | 53.4 ppm | 2.42 ppbv |

At 1 ppm relative transmission noise, both idealized limits of detection exceed the literature asthma means. Reducing the white-noise equivalent to 0.1 ppm would lower the idealized 3σ limits to about 0.25 ppbv, but this still excludes systematic and correlated errors.

The background requirement is also stringent. The combined H2O/CO2 optical-depth baseline would need to reproduce to roughly 47–53 parts per million of its own value between background and breath measurements. This is not a requirement on water mole fraction alone; wavelength error, temperature, pressure, line-shape error and humidity changes can all contribute to the residual.

## Interpretation

These are necessary but not sufficient performance bounds. They do not establish a practical detection limit and do not include:

- wavelength drift across structured H2O/CO2 absorption;
- detector nonlinearity, etalons, source drift or correlated 1/f noise;
- uncertain breath temperature, pressure and humidity;
- sampling loss and adsorption;
- other breath VOCs;
- benefits or penalties from multi-line spectral fitting and averaging time.

The result therefore strengthens the negative feasibility evidence. A direct 10 m single-window measurement would require sub-ppm relative transmission precision plus exceptionally repeatable background correction, even before clinical replication and chemical-identity gates are satisfied.

## Outputs

- `results/noise_budget.csv`: all assumed noise scenarios and equivalent concentration limits;
- `results/noise_budget_summary.json`: compact target requirements;
- `results/figures/noise_budget.png`: equivalent LOD versus relative transmission noise;
- `configs/noise_budget_v0.1.json`: locked assumptions.

