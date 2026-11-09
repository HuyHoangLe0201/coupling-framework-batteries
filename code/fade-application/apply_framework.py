#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply the framework's knee-to-EOL test to published fade curves.

The Perspective states that the framework is "testable on any published fade
curve that has been decomposed" and never runs the test.  This script runs the
part that does not require refitting anyone's data.

A false start worth recording
-----------------------------
The first version of this script compared the model's EOL/knee ratio with the
published one and reported a clear FAILURE (model 1.97, data 1.26).  That
comparison was wrong, and wrong in exactly the way the manuscript corrects
elsewhere.  The model's `knee()` function defines the knee as LLI >= 0.20 Q0,
which is 80 % retention -- and 80 % retention is the *published definition of
end of life*.  So the comparison set the model's end of life against the data's
end of life and called the mismatch a failed prediction.  SI S1.6 also warns
that no literature cycle number should be compared numerically with the model's,
because the model is unfitted and its loop gain is a placeholder.

What is actually testable is a dimensionless ratio: a common scale factor
cancels.  But the ratio still depends on which of the five knee definitions is
used, and the literature does not use one definition consistently either.  The
honest result is that the test is inconclusive, and this script is written to
show that rather than to pick the branch that looks better.

Data
----
`knee_eol.csv`: knee point and end of life for 303 cells from 17 published
studies, tabulated from the original figures by

    Attia et al., J. Electrochem. Soc. 169, 060517 (2022),
    doi:10.1149/1945-7111/ac6d13

and taken from github.com/tinosulzer/kneepoint-review
(code/data/knee_point_EOL_linreg_data.csv).  End of life is 80 % of nominal
capacity in every source.  The numbers are the original authors' readings of
published figures, not independent measurements.

Usage:  python apply_framework.py [knee_eol.csv]
"""
import csv
import json
import os
import statistics as st
import sys

MODEL = {"knee_onset": (278, 285), "knee_late": (470, 479),
         "knee_lli20": (530,), "eol_80pct": 530, "capacity_zero": 1044}


def load(path):
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        try:
            k, e = float(r["knee_point"]), float(r["EOL"])
        except (ValueError, KeyError):
            continue
        if k > 0 and e > 0:
            out.append((r["name_plot_dict_key"], k, e))
    return out


def model_ratios():
    """EOL at 80 % retention (the published definition) over each model knee."""
    return {
        "onset (departure / local exponent)":
            [MODEL["eol_80pct"] / k for k in MODEL["knee_onset"]],
        "late (2nd derivative / Kneedle)":
            [MODEL["eol_80pct"] / k for k in MODEL["knee_late"]],
        "LLI >= 0.20 Q0 (manuscript's knee)":
            [MODEL["eol_80pct"] / k for k in MODEL["knee_lli20"]],
    }


def main(path):
    rows = load(path)
    n = len(rows)
    studies = len(set(r[0] for r in rows))
    sane = [r for r in rows if r[1] <= r[2]]
    ratios = sorted(e / k for _, k, e in sane)

    print("=" * 70)
    print("The framework's knee-to-EOL test, run on published fade curves")
    print("=" * 70)
    print(f"\ndata:    {os.path.basename(path)}")
    print(f"cells:   {n} from {studies} published studies")
    print(f"EOL:     80 % of nominal capacity in every source")
    print(f"knee:    median {st.median([r[1] for r in rows]):.0f}, "
          f"range {min(r[1] for r in rows):.0f}-{max(r[1] for r in rows):.0f}")

    print("\n-- The literature does not agree on what a knee is --")
    inv = n - len(sane)
    print(f"  cells with knee AFTER end of life: {inv}/{n} = {100*inv/n:.0f} %")
    print("  Not a data error: the studies detect the knee by different")
    print("  algorithms, and on a curve already past 80 % retention the detected")
    print("  inflection can fall later than the 80 % crossing.  Any claim that")
    print("  the knee is one well-defined object has to survive this.")

    print("\n-- Published ratio --")
    print(f"  median EOL/knee:    {st.median(ratios):.2f}")
    print(f"  interquartile:      {ratios[len(ratios)//4]:.2f}-{ratios[3*len(ratios)//4]:.2f}")
    # least squares
    xs = [r[1] for r in sane]
    ys = [r[2] for r in sane]
    mx, my = st.mean(xs), st.mean(ys)
    sl = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
    ic = my - sl*mx
    ss = sum((y-ml)**2 for y, ml in zip(ys, [sl*x+ic for x in xs]))
    r2 = 1 - ss / sum((y-my)**2 for y in ys)
    print(f"  least squares:      EOL = {sl:.2f} x knee + {ic:.0f}  (R2 = {r2:.3f}, n = {len(sane)})")

    print("\n-- Model ratio, by knee definition --")
    print(f"  model end of life (80 % retention) = cycle {MODEL['eol_80pct']}")
    print(f"  (model capacity = 0 at cycle {MODEL['capacity_zero']}; that is cell")
    print("   death, not the published EOL, and is not used in this comparison)")
    for name, vals in model_ratios().items():
        rng = f"{min(vals):.2f}" if len(vals) == 1 else f"{min(vals):.2f}-{max(vals):.2f}"
        print(f"    {name:38s} ratio {rng}")

    print("\n-- Verdict --")
    lo = min(min(v) for v in model_ratios().values())
    hi = max(max(v) for v in model_ratios().values())
    print(f"  model ratio spans {lo:.2f}-{hi:.2f} across five knee definitions.")
    print(f"  published IQR is {ratios[len(ratios)//4]:.2f}-{ratios[3*len(ratios)//4]:.2f}, which lies inside that span.")
    print("  Depending on the definition adopted, the framework is either")
    print("  consistent with the data or above it.  A test whose outcome is")
    print("  fixed by the definition of its own central object has no")
    print("  discriminating power, so the result is INCONCLUSIVE.")
    print("  Reporting either branch as confirmation would repeat the error the")
    print("  manuscript corrects elsewhere.")

    print("\n-- What the comparison does establish --")
    print(f"  The knee-to-EOL interval exists, but it is short: the median")
    print(f"  published cell reaches 80 % retention at {st.median(ratios):.2f} x its knee")
    print("  cycle, not the ~2 x the model gives under its onset definitions.")
    print("  A proposed use of the knee as a warning signal is therefore")
    print("  operating on roughly a quarter of a knee-to-knee interval.")

    print("\n-- Not established --")
    print("  Whether the *coupling* explains the observed knees.  That needs the")
    print("  decomposition the Perspective asks for (LLI, LAM, KL as functions of")
    print("  cycle for individual cells).  The knee/EOL tabulation carries none,")
    print("  so the most informative test is deferred.  This is the largest open")
    print("  item, and SI S1.13 says so.")

    return {"n": n, "studies": studies, "n_sane": len(sane),
            "n_knee_after_eol": inv,
            "median_ratio": st.median(ratios),
            "iqr": [ratios[len(ratios)//4], ratios[3*len(ratios)//4]],
            "fit": {"slope": sl, "intercept": ic, "r2": r2},
            "model_ratios": {k: [round(x, 2) for x in v]
                             for k, v in model_ratios().items()},
            "verdict": "inconclusive"}


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    res = main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "knee_eol.csv"))
    with open(os.path.join(here, "framework_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("\nwrote framework_results.json")
