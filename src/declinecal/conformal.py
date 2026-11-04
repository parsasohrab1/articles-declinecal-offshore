"""Split-conformal bounds for a decline-curve forecast.

Calibration wells are fitted on their first n_fit months; the log error of the forecast at each lead month h is stored.
For a new well the forecast is multiplied by exp(lower) and exp(upper), the (alpha/2) and (1 - alpha/2) conformal quantiles of the stored
errors at that lead (per-lead calibration, so the bounds widen with the lead if the errors do)."""
import numpy as np
from .arps import arps, fit_arps


def lead_errors(wells, n_fit, horizon):
    """wells: list of 1-D arrays of monthly rates. Returns an array (n_wells, horizon) of log(actual / forecast)."""
    E = []
    for q in wells:
        q = np.asarray(q, float)
        if len(q) < n_fit + horizon:
            continue
        p = fit_arps(np.arange(n_fit), q[:n_fit]); t = np.arange(n_fit, n_fit + horizon)
        f = arps(t, *p); a = q[n_fit:n_fit + horizon]
        E.append(np.where(a > 0, np.log(np.maximum(a, 1e-12) / f), np.nan))
    return np.array(E)


def _quantiles(col, alpha):
    col = np.sort(col[~np.isnan(col)]); n = len(col)
    kl = int(np.floor((n + 1) * alpha / 2)); ku = int(np.ceil((n + 1) * (1 - alpha / 2)))
    lo = col[kl - 1] if kl >= 1 else -np.inf
    hi = col[ku - 1] if ku <= n else np.inf
    return lo, hi


def calibrate(wells, n_fit, horizon, alpha=0.1):
    E = lead_errors(wells, n_fit, horizon)
    if len(E) < 20:
        raise ValueError("at least 20 calibration wells are needed for a 90% interval")
    return {"n_fit": n_fit, "horizon": horizon, "alpha": alpha, "n_wells": int(len(E)), "bounds": [list(_quantiles(E[:, h], alpha)) for h in range(horizon)]}


def forecast_with_bounds(q_history, cal):
    q = np.asarray(q_history, float)[: cal["n_fit"]]
    p = fit_arps(np.arange(len(q)), q); t = np.arange(cal["n_fit"], cal["n_fit"] + cal["horizon"]); f = arps(t, *p)
    lo = np.array([b[0] for b in cal["bounds"]]); hi = np.array([b[1] for b in cal["bounds"]])
    return {"params": p, "forecast": f, "lower": f * np.exp(lo), "upper": f * np.exp(hi)}


def coverage(wells, cal):
    """Share of (well, lead) actuals inside the bounds, and the mean width of the log interval."""
    inside, widths = [], []
    for q in wells:
        q = np.asarray(q, float)
        if len(q) < cal["n_fit"] + cal["horizon"]:
            continue
        r = forecast_with_bounds(q, cal); a = q[cal["n_fit"]:cal["n_fit"] + cal["horizon"]]
        inside += list((a >= r["lower"]) & (a <= r["upper"])); widths += list(np.log(r["upper"] / r["lower"]))
    return {"coverage": float(np.mean(inside)), "mean_log_width": float(np.mean(widths)), "n": int(len(inside))}
