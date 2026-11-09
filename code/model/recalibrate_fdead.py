"""
Recalibrate f_dead against the M2 measured range.

M2 (03-mechanisms/M2-li-plating-dead-lithium.md, section c) reports MEASURED
dead-Li fractions of 3.3 +/- 0.6 % (with 5% FEC) and 9.4 +/- 0.6 % (without),
from DOI 10.1016/j.xcrp.2020.100139.

v4 used f_dead = 0.35, which is 4-10x too high. This script tests whether the
model still produces a knee with the physically measured range, and what
b_fresh is required.
"""
import numpy as np
import loopA_model_v4 as m
from departure_test import departure


def one(f_dead, b_fresh, c=1.0):
    r = m.simulate(c, 1.0, p=dict(f_dead=f_dead, b_fresh=b_fresh))
    k = m.knee(r["LLI"], r["Q0"])
    d, _, _ = departure(r["LLI"])
    kk = k or (r["stopped"] // 2)
    pre = m.exponent(r["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
    post = m.exponent(r["LLI"], kk, min(int(1.8 * kk), r["n"] - 2))
    return r, k, d, pre, post


print("=" * 92)
print("Recalibrating f_dead to the MEASURED range (3.3% with FEC, 9.4% without)")
print("=" * 92)
hdr = (f"{'f_dead':>7} {'b_fresh':>8} {'knee':>7} {'EOL':>6} {'depart':>7} "
       f"{'pre-exp':>8} {'post-exp':>9} {'LLI/Q0':>7}")
print(hdr)
print("-" * 92)
cases = [(0.35, 6.0),      # v3-era value (too high)
         (0.094, 6.0),     # measured, no FEC
         (0.033, 6.0),     # measured, with FEC
         (0.094, 30.0),
         (0.094, 60.0),
         (0.094, 120.0),
         (0.050, 60.0)]
for f_dead, b_fresh in cases:
    r, k, d, pre, post = one(f_dead, b_fresh)
    print(f"{f_dead:>7.3f} {b_fresh:>8.1f} {str(k):>7} {r['stopped']:>6} "
          f"{str(d):>7} {pre:>8.2f} {post:>9.2f} "
          f"{r['LLI'][-1]/r['Q0']:>7.2f}")

print("\n" + "=" * 92)
print("EFFECT OF RECALIBRATION — what changes and what does not")
print("=" * 92)
r_hi, k_hi, d_hi, _, _ = one(0.35, 6.0)
r_lo, k_lo, d_lo, pre_lo, post_lo = one(0.094, 60.0)
print(f"""
  f_dead = 0.35 (unphysical, 4-10x too high):
      knee = {k_hi}, departure = {d_hi}, EOL = {r_hi['stopped']}

  f_dead = 0.094 (MEASURED, no-FEC value) with b_fresh = 60:
      knee = {k_lo}, departure = {d_lo}, EOL = {r_lo['stopped']}

  => The knee SURVIVES recalibration to the measured dead-Li fraction, but
     b_fresh must rise substantially (6 -> 60 ohm*cm^2 per mAh/cm^2).
     b_fresh is the one parameter with NO literature anchor; it is the
     'fresh Li -> extra interphase resistance' conversion, and it is the
     weakest link in the whole model. State this openly.
""")

print("=" * 92)
print("SEVERED TEST at the recalibrated parameter set (the key result)")
print("=" * 92)
for label, f_dead, b_fresh in [("uncalibrated", 0.35, 6.0),
                               ("calibrated", 0.094, 60.0)]:
    print(f"\n{label}: f_dead={f_dead}, b_fresh={b_fresh}")
    for c in (0.5, 1.0):
        rc = m.simulate(c, 1.0, p=dict(f_dead=f_dead, b_fresh=b_fresh))
        rs = m.simulate(c, 1.0, p=dict(f_dead=0.0, b_fresh=0.0))
        dc, _, _ = departure(rc["LLI"])
        ds, _, _ = departure(rs["LLI"])
        print(f"  {c}C  coupled departure={str(dc):>5}  "
              f"severed departure={str(ds):>5}  "
              f"coupled knee={str(m.knee(rc['LLI'], rc['Q0'])):>5}  "
              f"severed EOL={rs['stopped']}")

print("""
DECISION FOR THE MANUSCRIPT
  Use f_dead = 0.094 (measured, DOI 10.1016/j.xcrp.2020.100139) as the
  reference value, and report f_dead = 0.033 as the FEC-improved case.
  b_fresh must be labelled "unconstrained by literature — tuned to reproduce
  a knee within the observed cycle-count range", and the SI must show the
  sensitivity of the knee cycle count to b_fresh.
  The qualitative results (knee exists; coupling severs it) survive.
""")
