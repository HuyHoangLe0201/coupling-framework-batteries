"""
probe_stale_numbers.py -- DIAGNOSTIC ONLY (not part of the SI).

Purpose: box1-model-spec.md quotes a baseline of knee=413, EOL=698,
departure=255 and a b_fresh=60 "reference" row (knee 462, departure 275,
EOL 873). The authoritative v4 script with the approved b_fresh=30 gives
knee=530, EOL=1044, departure=285, and the same b_fresh=60 row as the spec
(knee 462, departure 275, EOL 873). So the sweep table in the spec is
consistent with v4, but its BASELINE numbers are not. This script searches
for a parameter set that reproduces 413/698/255, so the discrepancy can be
reported precisely rather than vaguely.

Run: python research/10-si/_audit/probe_stale_numbers.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUPPORT = os.path.abspath(os.path.join(HERE, "..", "..", "06-proposal", "_support"))
sys.path.insert(0, SUPPORT)

import loopA_model_v4 as m            # noqa: E402
from departure_test import departure  # noqa: E402


def row(tag, **p):
    r = m.simulate(1.0, 1.0, p=p) if p else m.simulate(1.0, 1.0)
    d, _, _ = departure(r["LLI"])
    print(f"{tag:28s} knee={str(m.knee(r['LLI'], r['Q0'])):>5s} "
          f"EOL={r['stopped']:>5d} depart={str(d):>5s} "
          f"R_final={r['R'][-1]:7.1f}  LLI/Q0={r['LLI'][-1]/r['Q0']:.2f}")


print("TARGET from box1-model-spec.md S4/S5: knee=413 EOL=698 depart=255\n")

print("--- baseline candidates ---")
row("v4 as shipped (b=30)")
row("b_fresh=60", b_fresh=60.0)
row("f_dead=0.35 b=6 (v3-era)", f_dead=0.35, b_fresh=6.0)
row("f_dead=0.35 b=30", f_dead=0.35, b_fresh=30.0)
row("f_dead=0.35 b=60", f_dead=0.35, b_fresh=60.0)

print("\n--- sweep over b_fresh, f_dead=0.094 (v4 default) ---")
for b in [30, 45, 60, 75, 90, 110, 130, 150]:
    row(f"b_fresh={b}", b_fresh=float(b))

print("\n--- sweep over R_cap ---")
for rc in [120, 200, 300, 600, 1e9]:
    row(f"R_cap={rc}", R_cap=float(rc))

print("\n--- sweep over c_lli ---")
for c in [0.006, 0.008, 0.010, 0.012, 0.015, 0.020]:
    row(f"c_lli={c}", c_lli=c)

print("\n--- sweep over a_sei ---")
for a in [0.45, 0.6, 0.8, 1.0, 1.2]:
    row(f"a_sei={a}", a_sei=a)

print("\n--- sweep over f_max / k_pl ---")
for fm in [0.01, 0.02, 0.04, 0.08]:
    row(f"f_max={fm}", f_max=fm)
for kp in [6, 12, 24, 48]:
    row(f"k_pl={kp}", k_pl=kp)

print("""
INTERPRETATION
  If no single-parameter change reproduces 413/698/255, the spec's baseline
  block is a stale pre-recalibration run (the f_dead=0.35 era), not a
  reproducible output of loopA_model_v4.py. The b_fresh=60 row in the same
  spec DOES reproduce (462/873/275), which proves the table was partly
  regenerated and the baseline partly not.
""")
