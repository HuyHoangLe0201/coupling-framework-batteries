"""
fig3_data.py -- the ONLY place Figure 3's numbers come from.

Every array this module returns is produced by calling
research/06-proposal/_support/loopA_model_v4.py. Nothing is transcribed from a
document, and nothing is fitted, smoothed or invented. If the model changes, the
figure changes; that is the point.

The expected values are asserted here AND re-asserted independently by
figure-spec-check.py, so a silent model edit cannot slip through as a plausible
new curve.
"""

import os
import sys
import numpy as np

# Resolve the model relative to THIS file, not the caller's CWD. Two layouts are
# supported because the working tree and the published repository differ in where
# the model sits; a third would be a layout change, and that should be a loud
# failure rather than a silent re-derivation.
_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    # working tree: research/11-figures/ next to research/06-proposal/_support/
    os.path.join(_HERE, "..", "06-proposal", "_support"),
    # published repository: figures/ next to code/model/
    os.path.join(_HERE, "..", "code", "model"),
]
_MODEL_DIR = None
for _c in _CANDIDATES:
    _c = os.path.normpath(_c)
    if os.path.isfile(os.path.join(_c, "loopA_model_v4.py")):
        _MODEL_DIR = _c
        break
if _MODEL_DIR is None:
    raise RuntimeError(
        "authoritative model not found in any of {} . Figure 3 must not fall back "
        "to a copy or a re-derivation.".format([os.path.normpath(c) for c in _CANDIDATES]))
if _MODEL_DIR not in sys.path:
    sys.path.insert(0, _MODEL_DIR)
import loopA_model_v4 as m

P = m.P

# Milestones the documents quote; asserted immediately so a drift is loud.
EXPECT = {
    "knee_1c": 530,
    "eol_1c": 1044,
    "first_plating": 220,
    "pre_exponent": 0.910,
    "post_exponent": 2.434,
}


def baseline():
    return m.simulate(1.0, 1.0)


def severed():
    """Severed control: both feedback arrows removed, baseline SEI kept."""
    return m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))


def check_milestones():
    b = baseline()
    kk = m.knee(b["LLI"], b["Q0"])
    pre = m.exponent(b["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
    post = m.exponent(b["LLI"], kk, min(int(1.8 * kk), b["n"] - 2))
    got = {
        "knee_1c": kk,
        "eol_1c": b["stopped"],
        "first_plating": b["first_plating"],
        "pre_exponent": round(pre, 3),
        "post_exponent": round(post, 3),
    }
    bad = {k: (EXPECT[k], got[k]) for k in EXPECT
           if abs(float(EXPECT[k]) - float(got[k])) > 5e-3}
    if bad:
        raise AssertionError(
            "model milestones drifted from the documented values: "
            + ", ".join("{}: expected {} got {}".format(k, e, g)
                        for k, (e, g) in bad.items())
        )
    s = severed()
    if m.knee(s["LLI"], s["Q0"]) is not None:
        raise AssertionError("severed control now has a knee -- the central "
                             "result of Figure 3 no longer holds")
    return got


def rate_sweep():
    """(c_rate, knee, eol) for C-rates quoted in S1 Table S3."""
    out = []
    for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
        r = m.simulate(c, 1.0)
        out.append((c, m.knee(r["LLI"], r["Q0"]), r["stopped"]))
    return out


def t_sweep():
    out = []
    for tf in [0.5, 1.0, 2.0]:
        r = m.simulate(1.0, tf)
        out.append((tf, m.knee(r["LLI"], r["Q0"]), r["stopped"]))
    return out


def r0_sweep():
    out = []
    for r0 in [4.0, 8.0, 12.0, 16.0]:
        r = m.simulate(1.0, 1.0, R0=r0)
        out.append((r0, m.knee(r["LLI"], r["Q0"]), r["stopped"]))
    return out


def operating_map(c_rates=(0.5, 1.0, 2.0, 3.0),
                  t_factors=(0.25, 0.5, 1.0, 2.0, 4.0)):
    """Knee cycle count on a C-rate x SEI-growth-factor grid.

    None means 'no knee within n_max cycles'. That null is a RESULT (the severed
    limit reproduced by slow rates), so it is returned explicitly, never masked
    to a large number.
    """
    rows = []
    for c in c_rates:
        row = []
        for tf in t_factors:
            k = m.knee(m.simulate(c, tf)["LLI"], P["Q0"])
            row.append(k)
        rows.append(row)
    return list(c_rates), list(t_factors), rows


def threshold_locus(c_rates):
    """R* = (delta - eta_ct)/j in ohm cm^2, straight from the model's j."""
    out = []
    for c in c_rates:
        j = c * P["Q0"] / 1000.0
        out.append((c, (P["delta"] - P["eta_ct"]) / j))
    return out


def composition(stacked_count=None):
    """Coupled-cell loss composition for the sub-panel of Fig 3a.

    The reduced model tracks TWO quantities only: LLI and interphase resistance R.
    It does NOT decompose into three channels. We therefore plot what the model
    actually contains -- LLI and the interphase growth it is coupled to -- and
    label it as such. Plotting a three-way LLI/LAM/KL stacked area would require
    inventing LAM and KL, which this figure must never do.
    """
    b = baseline()
    n = np.arange(b["n"])
    return n, b["LLI"], b["R"]
