# DeclineCal (articles-declinecal-offshore)

Question: when offshore field production is forecast 12 months ahead with a simple decline model, do conformal prediction intervals keep their promised coverage, and does that survive a change of period?

Target venue: SPE Offshore Europe 2027 (Aberdeen, 7-9 Sept 2027), topics "Data analytics" and "Digital reservoirs / Business case". Paper proposals due 1 Feb 2027.

## Data (real, public)
Sodir (Norwegian Offshore Directorate) monthly field production, 136 fields, 1971-2026, open government data (NLOD licence).
`python fetch_sodir.py` downloads it to `data/` (git-ignored). No synthetic data is used.

## Method (`declinecal.py`)
- Target: total oil-equivalent volume of the next 12 months, forecast origins every 12 months after each field's peak (1,241 origins, 96 fields).
- Point forecasts: exponential decline, hyperbolic Arps decline (b in [0,1]), both fitted to the last 24 months, and a naive "last 12 months repeated".
- Intervals: split conformal on log(actual / forecast), alpha = 0.1, calibrated (a) on other fields (field-disjoint, 200 random halves) and (b) on earlier years (time shift, cut at 2010 and 2016).

## Measured result (results/declinecal_results.json)
| Setting | Method | Coverage (target 0.90) | Median abs. log error | Interval width (upper/lower) |
|---|---|---|---|---|
| Field-disjoint split | exp | 0.898 | 0.157 | 3.04 |
| | hyperbolic | 0.901 | 0.133 | 2.61 |
| | naive | 0.900 | 0.157 | 2.64 |
| Calibrate before 2010, test 2010+ | exp / hyp / naive | 0.832 / 0.851 / 0.864 | 0.164 / 0.144 / 0.150 | 2.45 / 2.31 / 2.40 |
| Calibrate before 2016, test 2016+ | exp / hyp / naive | 0.839 / 0.852 / 0.864 | 0.162 / 0.141 / 0.153 | 2.62 / 2.38 / 2.48 |

Reading (honest): coverage holds across fields but falls to about 0.83-0.86 under a period shift, and is lowest (0.79-0.84) for fields whose last 24 months were rising. The hyperbolic fit is the most accurate point forecast but only slightly better than repeating the last year, and all 90 % intervals are wide (roughly a factor 2.3-3 between lower and upper bound). The result is a warning about calibration under shift, not a better forecaster.

## Limits / [to be measured]
- Origins of one field are correlated; confidence intervals for the temporal coverage numbers are [to be measured] (block bootstrap over fields).
- Oil-equivalent only; separate oil, gas and water forecasts, shut-in/restart handling, and adaptive or weighted conformal methods are [to be measured].
- Comparison with published decline-curve uncertainty methods (literature check) is [to be done] before any novelty claim; no novelty claim is made.
- Public Sodir data only; no operator data.
