# BRS – Business Requirements Specification (DeclineCal)

## 1. Business problem
Production forecasts of offshore wells are usually given as one decline curve without a statement of how wrong it can be. Reserve bookings, field development plans and offtake commitments need a range whose coverage is known.

## 2. Business objectives
| ID | Objective |
|----|-----------|
| BO-1 | State for every forecast a lower and an upper bound with a measured coverage (for example 90%) |
| BO-2 | Show whether the stated coverage holds on wells that were not used for calibration, and warn when it does not |
| BO-3 | Let a reservoir or production engineer reproduce the bounds from the well histories alone, without a black-box model |

## 3. Stakeholders
Reservoir and production engineers (forecasts), asset managers (plans and commitments), reserves auditors (coverage evidence).

## 4. Scope
In scope: monthly rate histories of oil or gas wells, hyperbolic (Arps) decline, per-lead conformal bounds. Out of scope: reservoir simulation, pressure or water-cut modelling, economic evaluation, any claim of reserves.

## 5. Constraints and assumptions
- The coverage guarantee holds when the new well is exchangeable with the calibration wells; a regime change after the fitting window (water breakthrough, choke change, workover) breaks it, which the evaluation shows.
- At least 20 calibration wells are required for a 90% interval.
- Real field data are not part of the repository.

## 6. Success measures (to be measured on field data)
Measured coverage on held-out wells within 0.03 of the target; bounds narrower than a naive fixed percentage band at equal coverage.
