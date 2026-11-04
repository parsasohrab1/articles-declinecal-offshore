# SRS – Software Requirements Specification (DeclineCal)

1. Purpose: forecast the monthly rate of a well for the next H months with lower and upper bounds whose coverage is calibrated on other wells.
2. Users: reservoir and production engineers; integration by an asset data team.
3. Inputs: monthly rate histories (one array per well, positive numbers, at least n_fit months); calibration wells (at least 20).

| ID | Requirement | Where |
|----|-------------|-------|
| FR-01 | Fit q(t) = qi / (1 + b di t)^(1/b) to the first n_fit months by least squares on log rates, with bounds on qi, di, b | `arps.fit_arps` |
| FR-02 | Refuse to fit fewer than 4 positive rates | `arps.fit_arps` |
| FR-03 | For each calibration well, fit on the first n_fit months and store the log error of the forecast at each lead month | `conformal.lead_errors` |
| FR-04 | Compute per-lead lower and upper conformal quantiles at level alpha; refuse fewer than 20 calibration wells | `conformal.calibrate` |
| FR-05 | Return forecast, lower and upper bounds for a new well | `conformal.forecast_with_bounds` |
| FR-06 | Report measured coverage and mean log width on held-out wells | `conformal.coverage` |
| FR-07 | Provide a synthetic well generator for tests only | `synthetic.make_wells` |

4. Non-functional: pure Python with numpy and scipy; a fit takes milliseconds; no network access; deterministic for fixed inputs.
5. Out of scope: reservoir simulation, economics, reserves classification; patent-covered functions of the product are not implemented in this repository.
6. Acceptance: `pytest` passes (5 tests on synthetic wells); on real wells the measured coverage must be within 0.03 of the target (not yet measured).
