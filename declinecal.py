"""DeclineCal: do calibrated intervals for 12-month-ahead offshore field production hold when the decline model is simple?

Real data: Sodir monthly field production (136 fields, 1971-2026). Target: total oil-equivalent volume of the next 12 months.
Point forecasts: exponential decline, hyperbolic (Arps, b in [0,1]) fitted to the last 24 months, and the naive 'last 12 months repeated'.
Intervals: split conformal on the log ratio log(actual/forecast), calibrated on OTHER fields (field-disjoint) and, separately, on EARLIER years (time shift).
Reports empirical coverage overall and per regime. Negative results are kept.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

H, W = 12, 24      # forecast horizon and fitting window (months)
ALPHA = 0.1


def load(path="data/sodir_field_production_monthly.csv"):
    d = pd.read_csv(path, encoding="utf-8-sig")
    d["t"] = d.prfYear * 12 + d.prfMonth - 1
    d = d.rename(columns={"prfInformationCarrier": "field", "prfPrdOeNetMillSm3": "oe"})
    return {f: g.sort_values("t")[["t", "oe"]].reset_index(drop=True) for f, g in d.groupby("field")}


def arps(t, qi, D, b):
    return qi / np.power(1.0 + b * D * t, 1.0 / b) if b > 1e-6 else qi * np.exp(-D * t)


def fit_forecast(y, kind):
    """y: last W monthly values. Returns forecast of the next H months (array) or None."""
    t = np.arange(len(y), dtype=float)
    q0 = max(y[:3].mean(), 1e-9)
    try:
        if kind == "exp":
            p, _ = curve_fit(lambda t, qi, D: arps(t, qi, D, 0.0), t, y, p0=[q0, 0.02], bounds=([0, -0.2], [10 * q0, 1.0]), maxfev=4000)
            return arps(np.arange(len(y), len(y) + H, dtype=float), p[0], p[1], 0.0)
        p, _ = curve_fit(arps, t, y, p0=[q0, 0.03, 0.5], bounds=([0, 0, 1e-3], [10 * q0, 1.0, 1.0]), maxfev=6000)
        return arps(np.arange(len(y), len(y) + H, dtype=float), *p)
    except Exception:
        return None


def build(fields):
    rows = []
    for f, g in fields.items():
        if len(g) < W + H + 24 or (np.diff(g.t) != 1).any():
            continue
        y = g.oe.values
        peak = int(np.argmax(y))
        for o in range(max(W, peak + 12), len(y) - H + 1, 12):    # origins every 12 months, after the peak
            past, fut = y[o - W:o], y[o:o + H]
            if past.min() <= 0 or fut.sum() <= 0:
                continue
            fe, fh = fit_forecast(past, "exp"), fit_forecast(past, "hyp")
            if fe is None or fh is None or fe.sum() <= 0 or fh.sum() <= 0:
                continue
            slope = np.polyfit(np.arange(W), np.log(past), 1)[0]        # recent log-trend per month
            rows.append(dict(field=f, year=int(g.t.iloc[o] // 12), actual=float(fut.sum()), exp=float(fe.sum()), hyp=float(fh.sum()),
                             naive=float(past[-H:].sum()), trend=float(slope), up=bool(slope > 0.0)))
    return pd.DataFrame(rows)


def conformal_q(scores, alpha=ALPHA):
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return float(np.sort(scores)[min(k, n) - 1])


def evaluate(df, cal, test, method):
    s = np.abs(np.log(cal.actual / cal[method]))
    q = conformal_q(s.values)
    r = np.log(test.actual / test[method])
    cover = (np.abs(r) <= q)
    return dict(n_cal=int(len(cal)), n_test=int(len(test)), q=q, coverage=float(cover.mean()), median_abs_log_err=float(np.abs(r).median()),
                width_ratio=float(np.exp(2 * q)),
                coverage_trend_up=float(cover[test.up].mean()) if test.up.any() else None, n_trend_up=int(test.up.sum()),
                coverage_trend_down=float(cover[~test.up].mean()), n_trend_down=int((~test.up).sum()))


def main():
    df = build(load())
    out = {"n_origins": int(len(df)), "n_fields": int(df.field.nunique()), "alpha": ALPHA, "H": H, "W": W, "field_disjoint": {}, "temporal": {}}
    rng = np.random.default_rng(0)
    methods = ["exp", "hyp", "naive"]
    for m in methods:      # field-disjoint split, 200 random repeats
        res = []
        for _ in range(200):
            fl = df.field.unique(); rng.shuffle(fl)
            cal_f = set(fl[: len(fl) // 2])
            res.append(evaluate(df, df[df.field.isin(cal_f)], df[~df.field.isin(cal_f)], m))
        out["field_disjoint"][m] = {k: float(np.mean([r[k] for r in res if r[k] is not None])) for k in ("coverage", "median_abs_log_err", "width_ratio", "coverage_trend_up", "coverage_trend_down")}
        out["field_disjoint"][m]["coverage_sd"] = float(np.std([r["coverage"] for r in res]))
    for cut in (2010, 2016):   # calibrate on origins before cut, test on origins from cut on (time shift)
        out["temporal"][str(cut)] = {m: evaluate(df, df[df.year < cut], df[df.year >= cut], m) for m in methods}
    Path("results").mkdir(exist_ok=True)
    Path("results/declinecal_results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
