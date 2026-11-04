"""Tests on SYNTHETIC wells generated here; they check the logic, they are not results."""
import numpy as np
from declinecal import arps, conformal, synthetic


def test_fit_recovers_noise_free_parameters():
    t = np.arange(36); q = arps.arps(t, 900.0, 0.07, 0.8); qi, di, b = arps.fit_arps(t, q)
    assert abs(qi - 900) / 900 < 0.02 and abs(di - 0.07) < 0.01 and np.allclose(arps.arps(t, qi, di, b), q, rtol=0.02)


def test_coverage_is_near_nominal_on_exchangeable_wells():
    cal = conformal.calibrate(synthetic.make_wells(300, seed=1), n_fit=18, horizon=12, alpha=0.1)
    cov = conformal.coverage(synthetic.make_wells(300, seed=2), cal)
    assert 0.85 <= cov["coverage"] <= 0.95


def test_bounds_widen_with_the_lead_month():
    cal = conformal.calibrate(synthetic.make_wells(300, seed=3), n_fit=18, horizon=12)
    w = [b[1] - b[0] for b in cal["bounds"]]; assert w[-1] > w[0]


def test_coverage_falls_when_a_regime_change_follows_the_fitting_window():
    cal = conformal.calibrate(synthetic.make_wells(300, seed=4), n_fit=18, horizon=12)
    same = conformal.coverage(synthetic.make_wells(200, seed=5), cal)["coverage"]
    shifted = conformal.coverage(synthetic.make_wells(200, seed=5, break_month=20, break_factor=0.6), cal)["coverage"]
    assert shifted < same - 0.05


def test_too_few_calibration_wells_are_refused():
    import pytest
    with pytest.raises(ValueError):
        conformal.calibrate(synthetic.make_wells(10), n_fit=18, horizon=12)
