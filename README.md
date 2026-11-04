# DeclineCal – calibrated confidence bounds for offshore production forecasts

Fits an Arps decline curve to the first months of a well and returns the forecast with **conformal lower and upper bounds** that were calibrated on other wells, so that the stated coverage (for example 90%) is measured and not assumed.

**Maturity: TRL 4** (laboratory validation on synthetic wells; no real field data yet). See [docs/TRL.md](docs/TRL.md). Requirements: [docs/SRS.md](docs/SRS.md) and [docs/BRS.md](docs/BRS.md).

```bash
pip install -e ".[dev]"
pytest -q
```

```python
from declinecal import conformal
cal = conformal.calibrate(calibration_wells, n_fit=18, horizon=12, alpha=0.1)   # wells: arrays of monthly rates
r = conformal.forecast_with_bounds(new_well_rates, cal)                         # r["forecast"], r["lower"], r["upper"]
conformal.coverage(test_wells, cal)                                             # measured coverage and width
```

Modules: `arps.py` (curve and fit), `conformal.py` (per-lead calibration, bounds, coverage), `synthetic.py` (wells for tests only).
