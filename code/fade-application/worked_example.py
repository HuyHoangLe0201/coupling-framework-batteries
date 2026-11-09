# -*- coding: utf-8 -*-
"""Worked example for the Perspective: apply the Section 2 prescription to one
public dataset and report what happens, including where it fails.

Source data: Harris, S. J. et al., "Failure statistics for commercial
lithium-ion batteries: A study of 24 pouch cells", J. Power Sources 342,
589-597 (2017), doi:10.1016/j.jpowsour.2016.12.083.
24 commercial pouch cells cycled at 10 C, 100 % depth of discharge; the file
carries normalised capacity retention per cycle (593 cycles each).

The manuscript's Section 2 prescribes: with f = 1 - CE, retention obeys
Q(N)/Q0 = 1 - f*N, so downward curvature measures df/dN, the coupling
strength. Fit f(N) = f0 + alpha*N and report alpha.

This script does exactly that on the 24 cells and reports:
  1. the per-cell alpha and its sign,
  2. how much of the curvature a single constant f can explain (RMSE linear
     vs quadratic),
  3. the window sensitivity of the alpha sign, which is the honest limitation.

Run:  python worked_example.py
Out:  worked_example_results.json
"""
import json
import os

import numpy as np
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "harris2017.xlsx")
OUT = os.path.join(HERE, "worked_example_results.json")

# Analysis window: the fit is done where retention sits between these bounds.
# The early cycles are dominated by formation and by the noise of a 10 C
# protocol, so a lower bound is needed; the upper bound is 1.0 (fresh cell).
WINDOWS = [(0.95, 1.00), (0.90, 1.00), (0.85, 1.00), (0.80, 1.00)]
PRIMARY = (0.90, 1.00)


def _require(path, label):
    """Fail with the fix, not a traceback: the dataset is not redistributed."""
    if not os.path.isfile(path):
        raise SystemExit(
            "missing dataset: {}\n"
            "  {}\n"
            "This file is third-party published data and is not redistributed in\n"
            "this repository. See raw/README-DATA.md (or run fetch_data.py --urls)\n"
            "for its source, then place it at the path above.".format(path, label))


def load_series():
    """Return [(name, cycles, retention)] for every cell with >50 points."""
    _require(SRC, "Harris et al. 2017, 24 pouch cells at 10 C (sheet ZP2A)")
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["ZP2A"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header, data = rows[0], rows[1:]

    seen, series = set(), []
    for j in range(1, len(header)):
        name = header[j]
        if name in seen:
            continue
        seen.add(name)
        cyc, ret = [], []
        for r in data:
            if r[0] is None or r[j] is None:
                continue
            try:
                c, v = float(r[0]), float(r[j])
            except (TypeError, ValueError):
                continue
            if v != v:  # NaN
                continue
            cyc.append(c)
            ret.append(v)
        if len(cyc) > 50:
            series.append((name, np.array(cyc), np.array(ret)))
    return series


def fit_alpha(cycles, ret, lo, hi):
    """Fit f(N) = f0 + alpha*N to the per-cycle loss over the window.

    f(N) is estimated as the negative finite difference of retention, which is
    the per-cycle loss. Returns alpha, or None if the window is too small.
    """
    n = cycles[1:]
    loss = -np.diff(ret)
    mask = (ret[1:] >= lo) & (ret[1:] <= hi)
    if mask.sum() < 25:
        return None
    design = np.vstack([np.ones(mask.sum()), n[mask]]).T
    coef, _, _, _ = np.linalg.lstsq(design, loss[mask], rcond=None)
    return float(coef[1])


def linear_vs_quadratic(cycles, ret):
    """How well does a single constant f explain the retention curve?"""
    fbar = (1.0 - ret[-1]) / cycles[-1]
    rmse_lin = float(np.sqrt(np.mean((ret - (1.0 - fbar * cycles)) ** 2)))

    design = np.vstack([np.ones(len(cycles)), cycles, cycles ** 2]).T
    cf, _, _, _ = np.linalg.lstsq(design, ret, rcond=None)
    pred2 = cf[0] + cf[1] * cycles + cf[2] * cycles ** 2
    rmse_quad = float(np.sqrt(np.mean((ret - pred2) ** 2)))
    return rmse_lin, rmse_quad, float(cf[2])


def main():
    series = load_series()
    print("cells loaded: %d" % len(series))

    per_cell = []
    for name, c, r in series:
        a = fit_alpha(c, r, *PRIMARY)
        if a is None:
            continue
        rl, rq, a2 = linear_vs_quadratic(c, r)
        per_cell.append(dict(name=name, alpha=a, rmse_linear=rl,
                             rmse_quadratic=rq, quad_coef=a2,
                             n_points=int(len(c)),
                             min_retention=float(r.min())))

    alphas = np.array([p["alpha"] for p in per_cell])
    print("\n== primary window %.2f-%.2f ==" % PRIMARY)
    print("cells analysed      : %d" % len(per_cell))
    print("alpha median        : %.3e per cycle" % np.median(alphas))
    print("alpha > 0           : %d / %d" % (int((alphas > 0).sum()), len(alphas)))
    print("alpha range         : %.2e to %.2e" % (alphas.min(), alphas.max()))

    rl = np.array([p["rmse_linear"] for p in per_cell])
    rq = np.array([p["rmse_quadratic"] for p in per_cell])
    a2 = np.array([p["quad_coef"] for p in per_cell])
    print("\nconstant-f RMSE median  : %.4f" % np.median(rl))
    print("quadratic RMSE median   : %.4f" % np.median(rq))
    print("quadratic better        : %d / %d" % (int((rq < rl).sum()), len(rl)))
    print("quadratic coef < 0      : %d / %d" % (int((a2 < 0).sum()), len(a2)))

    print("\n== window sensitivity of the sign of alpha ==")
    windows = {}
    for lo, hi in WINDOWS:
        vals = [fit_alpha(c, r, lo, hi) for _, c, r in series]
        vals = np.array([v for v in vals if v is not None])
        windows["%.2f-%.2f" % (lo, hi)] = dict(
            n=int(len(vals)), positive=int((vals > 0).sum()),
            median=float(np.median(vals)))
        print("  %.2f-%.2f : n=%2d  alpha>0 in %2d/%2d  median %.2e"
              % (lo, hi, len(vals), int((vals > 0).sum()), len(vals),
                 np.median(vals)))

    result = dict(
        source="Harris et al., J. Power Sources 342, 589-597 (2017)",
        doi="10.1016/j.jpowsour.2016.12.083",
        protocol="10 C, 100 % depth of discharge, 24 commercial pouch cells",
        primary_window=PRIMARY,
        n_cells=len(per_cell),
        alpha_median=float(np.median(alphas)),
        alpha_positive=int((alphas > 0).sum()),
        alpha_min=float(alphas.min()),
        alpha_max=float(alphas.max()),
        rmse_linear_median=float(np.median(rl)),
        rmse_quadratic_median=float(np.median(rq)),
        quadratic_better=int((rq < rl).sum()),
        quadratic_coef_negative=int((a2 < 0).sum()),
        window_sensitivity=windows,
        per_cell=per_cell,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    print("\nwrote %s" % os.path.basename(OUT))


if __name__ == "__main__":
    main()
