# -*- coding: utf-8 -*-
"""Direct sweep of the operating margin delta, the parameter the thesis is about.

WHY THIS EXISTS
  The Perspective claims the knee is a design variable because each loop closes
  on an OPERATING MARGIN. The reduced Loop-A model of Box 1 has exactly one
  parameter that is that margin: delta in (S1.2),

      eta(n) = j*R(n-1) + eta_ct - delta,

  the gap between the anode's equilibrium potential and 0 V vs Li/Li+. The
  threshold for plating is R* = (delta - eta_ct)/j. Every sweep in SI S1.7 and
  S1.9 varies the LOOP GAIN (b_fresh), the SEI rate (T_factor) and the C-rate,
  but none varies delta. C-rate is not a clean substitute: it enters eta through
  j and simultaneously changes Q_applied in (S1.4), so a C-rate sweep mixes the
  margin effect with the plated-charge effect.

  This script closes that gap. delta is swept at fixed C-rate, fixed Q0, fixed
  b_fresh, so j and Q_applied are constant and the only thing moving is the
  operating margin. The result is the direct test of the central claim.

  It is reported next to the gain sweep so the two can be compared on equal
  footing: which variable actually sets where the knee lands?

Run:   python margin_sweep.py
Out:   margin_sweep_results.json
"""
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from loopA_model_v4 import P, simulate, knee, exponent  # noqa: E402

OUT = os.path.join(HERE, "margin_sweep_results.json")

# delta is the margin between the anode's operating potential and 0 V vs Li/Li+,
# reference 0.090 V. The sweep is confined to the range in which the departure
# detector's pre-loop baseline (cycles 30-200, see SI S1.5) is not contaminated
# by plating. Below delta = 0.090 V plating starts before cycle 200, so the
# "early power law" is no longer pre-loop and the knee number is not comparable
# with the reference case. That is a real limit of the analysis, not a choice:
# the clean window is only delta = 0.090-0.120 V, a factor of 1.33. The
# contaminated rows are reported too, marked, rather than quietly dropped.
DELTAS_CLEAN = [0.120, 0.115, 0.110, 0.105, 0.100, 0.095, 0.090]
DELTAS_CONTAMINATED = [0.085, 0.080, 0.070, 0.060, 0.050, 0.040, 0.030]
DELTAS = DELTAS_CLEAN + DELTAS_CONTAMINATED

# The gain sweep of SI S1.7, repeated here so both appear in one artefact.
GAINS = [1.0, 3.0, 10.0, 30.0, 60.0, 100.0, 200.0, 400.0]


def _knee_at(rows, delta):
    """Knee at an arbitrary delta, by simulation (small linear grid)."""
    r = simulate(1.0, 1.0, p={"delta": delta})
    k = knee(r["LLI"], r["Q0"])
    return k if k is not None else float("nan")


def run_delta(delta):
    """Simulate at 1C with only delta changed."""
    r = simulate(1.0, 1.0, p={"delta": delta})
    j = r["j"]
    Rstar = (delta - P["eta_ct"]) / j
    k = knee(r["LLI"], r["Q0"])
    fp = r["first_plating"]
    clean = fp is not None and fp > 200
    return dict(delta=delta, Rstar=Rstar, knee=k, eol=r["stopped"],
                first_plating=fp, baseline_clean=clean,
                n=r["n"], converged=(k is not None))


def run_gain(b):
    """Simulate at 1C with only b_fresh changed (the SI S1.7 axis)."""
    r = simulate(1.0, 1.0, p={"b_fresh": b})
    k = knee(r["LLI"], r["Q0"])
    return dict(gain=b, knee=k, eol=r["stopped"])


def main():
    print("=" * 78)
    print("Operating-margin sweep, delta at fixed C-rate, Q0 and b_fresh")
    print("=" * 78)
    print("j is held at %.4f A/cm2 for every row, so Q_applied is constant."
          % (1.0 * P["Q0"] / 1000.0))
    print("\n%8s %10s %8s %8s %9s %s"
          % ("delta(V)", "R*(ohmcm2)", "knee", "EOL", "plating@", "baseline"))
    rows = []
    for d in DELTAS:
        row = run_delta(d)
        rows.append(row)
        print("%8.3f %10.1f %8s %8d %9s %s"
              % (d, row["Rstar"],
                 row["knee"] if row["knee"] is not None else "none",
                 row["eol"], row["first_plating"],
                 "clean" if row["baseline_clean"] else "CONTAMINATED"))

    conv = [r for r in rows if r["converged"] and r["baseline_clean"]]
    print("\n--- Delta effect, clean window only (delta %.3f-%.3f V) ---"
          % (conv[-1]["delta"], conv[0]["delta"]))
    if len(conv) >= 2:
        hi, lo = conv[0], conv[-1]
        span = hi["delta"] / lo["delta"]
        shift = hi["knee"] / lo["knee"]
        print("delta %.3f -> %.3f V (factor %.2f): knee %d -> %d (factor %.2f)"
              % (hi["delta"], lo["delta"], span, hi["knee"], lo["knee"], shift))
        print("A 10 %% tighter margin (%.3f -> %.3f V) moves the knee %.2fx."
              % (hi["delta"], hi["delta"] / 1.10, hi["knee"] / _knee_at(rows, hi["delta"] / 1.10)))
        print("Compare: a 400x change in loop gain moves the knee 2.21x (S1.7).")

    gain_rows = [run_gain(b) for b in GAINS]
    print("\n--- Gain effect, same model, for comparison (SI S1.7) ---")
    print("%10s %8s %8s" % ("b_fresh", "knee", "EOL"))
    for g in gain_rows:
        print("%10.1f %8s %8s" % (g["gain"], g["knee"], g["eol"]))
    gspan = GAINS[-1] / GAINS[0]
    gshift = gain_rows[0]["knee"] / gain_rows[-1]["knee"]
    print("gain %.0f -> %.0f (factor %.0f): knee %d -> %d (factor %.2f)"
          % (GAINS[0], GAINS[-1], gspan, gain_rows[0]["knee"],
             gain_rows[-1]["knee"], gshift))

    result = dict(
        note=("delta is the only parameter in the model that is the operating "
              "margin of the thesis; it had never been swept"),
        c_rate=1.0, Q0=P["Q0"], j=1.0 * P["Q0"] / 1000.0,
        b_fresh_fixed=P["b_fresh"], eta_ct_fixed=P["eta_ct"],
        delta_sweep=rows,
        gain_sweep=gain_rows,
        delta_span=conv[0]["delta"] / conv[-1]["delta"] if len(conv) >= 2 else None,
        delta_knee_shift=conv[0]["knee"] / conv[-1]["knee"] if len(conv) >= 2 else None,
        gain_span=gspan, gain_knee_shift=gshift,
    )
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    print("\nwrote %s" % os.path.basename(OUT))
    return result


if __name__ == "__main__":
    main()
