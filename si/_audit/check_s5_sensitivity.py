"""Verify the R0 sensitivity claim in S5.8, and the stale-vs-v4 ratio table.

The SI now quotes v4 R0 sensitivity (728 -> 277) and the three dependence factors.
Those must be recomputed, not inferred, because they were appended late.

Note on the section number: this check was written when the stale-value audit
trail was S5.7. On 2026-11-04 the figure spec was restructured from four figures
to one three-panel figure, which inserted a new S5.7 (build defects found in the
rendered PDF) and pushed the audit trail to S5.8. The numbers checked here did
not change; only the section that carries them did.
"""
import os
import sys

# Resolve the model module from this file's own location, not from the shell's cwd.
# This used to be a bare relative path ("research/06-proposal/_support"), so the check
# failed with ModuleNotFoundError when run from anywhere but the repo root -- a gate that
# reports FAIL because of where you stood, not because of what the document says. Same
# defect was fixed in check_pore_filling.py and verify_s3_counts.py.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "research", "06-proposal", "_support"))
import loopA_model_v4 as m

P = m.P
print("=== v4 R0 sensitivity (knee vs R0) ===")
knees = {}
for R0 in (4.0, 8.0, 12.0, 16.0):
    r = m.simulate(1.0, 1.0, R0=R0)
    k = m.knee(r["LLI"], r["Q0"])
    knees[R0] = k
    print(f"  R0={R0:5.1f}  knee={k:5d}  EOL={r['stopped']:5d}")

print("\n=== dependence factors, v4 ===")
k_05 = m.knee(m.simulate(0.5, 1.0)["LLI"], P["Q0"])
k_25 = m.knee(m.simulate(2.5, 1.0)["LLI"], P["Q0"])
k_t05 = m.knee(m.simulate(1.0, 0.5)["LLI"], P["Q0"])
k_t2 = m.knee(m.simulate(1.0, 2.0)["LLI"], P["Q0"])
rate = k_05 / k_25
temp = k_t05 / k_t2
r0f = knees[4.0] / knees[16.0]
print(f"  rate  0.5C/2.5C : {k_05}/{k_25} = {rate:.1f}")
print(f"  temp  0.5x/2.0x : {k_t05}/{k_t2} = {temp:.1f}")
print(f"  R0    4/16 ohm  : {knees[4.0]}/{knees[16.0]} = {r0f:.1f}")

print("\n=== stale-parameter claims (must NOT be quoted) ===")
stale_rate = 2314 / 36
stale_temp = 1167 / 170
stale_r0 = 606 / 173
print(f"  stale rate 2314/36 = {stale_rate:.1f}")
print(f"  stale temp 1167/170 = {stale_temp:.1f}")
print(f"  stale R0   606/173 = {stale_r0:.1f}")

claimed = dict(rate=41.4, temp=5.3, r0=2.6)
got = dict(rate=round(rate, 1), temp=round(temp, 1), r0=round(r0f, 1))
print(f"\nSI S5.8 claims {claimed}")
print(f"recomputed      {got}")
ok = all(abs(got[k] - claimed[k]) <= 0.11 for k in claimed)
print("MATCH" if ok else "MISMATCH -- fix SI S5.8")
assert ok
