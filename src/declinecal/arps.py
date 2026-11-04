"""Arps decline curve q(t) = qi / (1 + b di t)^(1/b) (b in (0, 2]) and its fit to monthly rates."""
import numpy as np
from scipy.optimize import least_squares


def arps(t, qi, di, b):
    t = np.asarray(t, float)
    return qi / (1.0 + b * di * t) ** (1.0 / b)


def fit_arps(t, q):
    """Least squares on log rates (so that all rates count equally). Returns (qi, di, b)."""
    t = np.asarray(t, float); q = np.asarray(q, float); ok = q > 0; t, q = t[ok], q[ok]
    if len(q) < 4:
        raise ValueError("at least 4 positive rates are needed")
    x0 = [q[0], 0.05, 1.0]
    r = least_squares(lambda p: np.log(arps(t, *p)) - np.log(q), x0, bounds=([1e-9, 1e-6, 0.05], [np.inf, 5.0, 2.0]))
    return tuple(float(v) for v in r.x)
