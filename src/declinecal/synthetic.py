"""Synthetic wells for tests ONLY (labelled): Arps decline with multiplicative log-normal noise, between-well parameter spread and an optional rate step."""
import numpy as np
from .arps import arps


def make_wells(n, months=48, noise=0.08, seed=0, break_month=None, break_factor=1.0):
    rng = np.random.default_rng(seed); t = np.arange(months); out = []
    for _ in range(n):
        qi = rng.lognormal(np.log(1000), 0.4); di = rng.uniform(0.03, 0.12); b = rng.uniform(0.3, 1.4)
        q = arps(t, qi, di, b) * np.exp(rng.normal(0, noise, months))
        if break_month is not None:
            q = np.where(t >= break_month, q * break_factor, q)   # regime change after the fitting window (e.g. water breakthrough, choke change)
        out.append(q)
    return out
