"""
extract_si_numbers.py -- DIAGNOSTIC HELPER (not part of the SI deliverable).

Prints every derived quantity quoted in research/10-si/*.md so that each
number in the SI can be copied from program output rather than recalled.
The authoritative check is research/10-si/_audit/verify_si_numbers.py.

Run: python research/10-si/_audit/extract_si_numbers.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SUPPORT = os.path.abspath(os.path.join(HERE, "..", "..", "06-proposal", "_support"))
sys.path.insert(0, SUPPORT)

import loopA_model_v4 as m            # noqa: E402
from departure_test import departure, powerlaw_fit  # noqa: E402

P = m.P
print("=" * 78)
print("0. Parameter set actually in force (loopA_model_v4.P)")
print("=" * 78)
for k, v in P.items():
    print(f"  {k:10s} = {v}")

print()
print("=" * 78)
print("1. Baseline (1C, b_fresh=30) trajectory landmarks")
print("=" * 78)
base = m.simulate(1.0, 1.0)
sev = m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
jj = base["j"]
Rstar = (P["delta"] - P["eta_ct"]) / jj
print(f"  j (1C)                 = {jj*1e3:.3f} mA/cm^2 = {jj:.5f} A/cm^2")
print(f"  R* at 1C               = {Rstar:.2f} ohm*cm^2")
print(f"  first plating (coupled)= {base['first_plating']}")
print(f"  knee  (LLI>=20% Q0)    = {m.knee(base['LLI'], base['Q0'])}")
print(f"  EOL   (LLI=Q0)         = {base['stopped']}")
print(f"  knee threshold LLI     = {0.20*P['Q0']:.3f} mAh/cm^2")
print(f"  R(0)={base['R'][0]:.2f}  R(400)={base['R'][400]:.2f}  R_max={base['R'].max():.2f}")
dc, Ac, pc = departure(base["LLI"])
ds, As, ps_ = departure(sev["LLI"])
print(f"  coupled: fit A={Ac:.4e} p={pc:.4f} departure={dc}")
print(f"  severed: fit A={As:.4e} p={ps_:.4f} departure={ds} "
      f"knee={m.knee(sev['LLI'], sev['Q0'])} EOL={sev['stopped']} "
      f"R_end={sev['R'][-1]:.2f}")

print("\n  cycle :  coupled LLI   severed LLI   coupled R   severed R")
for n in (200, 285, 400, 530, 698, 1000, 1044, 2000, 4000, 5999):
    ic = base["LLI"][min(n, base["n"] - 1)]
    isv = sev["LLI"][min(n, sev["n"] - 1)]
    rc = base["R"][min(n, base["n"] - 1)]
    rsv = sev["R"][min(n, sev["n"] - 1)]
    print(f"  {n:5d} :  {ic:10.3f}     {isv:10.3f}    {rc:7.2f}     {rsv:7.2f}")

kc = base["knee"] if False else m.knee(base["LLI"], base["Q0"])
kk = m.knee(base["LLI"], base["Q0"])
pre = m.exponent(base["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
post = m.exponent(base["LLI"], kk, min(int(1.8 * kk), base["n"] - 2))
pres = m.exponent(sev["LLI"], max(20, int(0.10 * (sev["stopped"] // 2))),
                  int(0.90 * (sev["stopped"] // 2)))
print(f"\n  pre-knee exponent (coupled)  = {pre:.3f}")
print(f"  post-knee exponent (coupled) = {post:.3f}")
print(f"  severed exponent (10-90% of 3000) = {pres:.3f}")

print()
print("=" * 78)
print("2. C-rate, temperature proxy, R0 tables (as printed by v4.report)")
print("=" * 78)
print(f"{'C-rate':>7} {'R*':>7} {'knee':>7} {'EOL':>7}")
for c in (0.5, 1.0, 1.5, 2.0, 2.5):
    r = m.simulate(c, 1.0)
    rs = (P["delta"] - P["eta_ct"]) / (c * P["Q0"] / 1000.0)
    print(f"{c:>7.1f} {rs:>7.2f} {str(m.knee(r['LLI'], r['Q0'])):>7} {r['stopped']:>7}")
print(f"\n{'T proxy':>7} {'knee':>7} {'EOL':>7}")
for tf in (0.5, 1.0, 2.0):
    r = m.simulate(1.0, tf)
    print(f"{tf:>7.1f} {str(m.knee(r['LLI'], r['Q0'])):>7} {r['stopped']:>7}")
print(f"\n{'R0':>7} {'knee':>7} {'EOL':>7}")
for r0 in (4.0, 8.0, 12.0, 16.0):
    r = m.simulate(1.0, 1.0, R0=r0)
    print(f"{r0:>7.1f} {str(m.knee(r['LLI'], r['Q0'])):>7} {r['stopped']:>7}")

print("\nKnee-onset map, C-rate (rows) x SEI-growth factor (cols)")
cols = [0.25, 0.5, 1.0, 2.0, 4.0]
print("        " + "".join(f"{str(c)+'x':>8s}" for c in cols))
for c in (0.5, 1.0, 2.0, 3.0):
    row = ""
    for tf in cols:
        k = m.knee(m.simulate(c, tf)["LLI"], P["Q0"])
        row += f"{(k if k is not None else 'none'):>8}"
    print(f"  {c:>3.1f}C {row}")

print()
print("=" * 78)
print("3. b_fresh sweep (1-400x)")
print("=" * 78)
print(f"{'b_fresh':>8} {'knee':>6} {'depart':>7} {'EOL':>6} {'pre':>6} {'post':>6} "
      f"{'R_end':>7}")
for b in (1.0, 3.0, 10.0, 30.0, 60.0, 100.0, 200.0, 400.0):
    r = m.simulate(1.0, 1.0, p=dict(b_fresh=b))
    k = m.knee(r["LLI"], r["Q0"])
    d, _, _ = departure(r["LLI"])
    kk2 = k or (r["stopped"] // 2)
    pr = m.exponent(r["LLI"], max(20, int(0.10 * kk2)), int(0.90 * kk2))
    po = m.exponent(r["LLI"], kk2, min(int(1.8 * kk2), r["n"] - 2))
    print(f"{b:>8.1f} {str(k):>6} {str(d):>7} {r['stopped']:>6} "
          f"{pr:>6.2f} {po:>6.2f} {r['R'][-1]:>7.1f}")

print("\nC2 severing test across b_fresh (severed = b_fresh 0 AND f_dead 0)")
for b in (10.0, 30.0, 60.0, 100.0, 200.0):
    rc = m.simulate(1.0, 1.0, p=dict(b_fresh=b))
    rs = m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
    dcp, _, _ = departure(rc["LLI"])
    dsp, _, _ = departure(rs["LLI"])
    print(f"  b={b:5.1f} coupled departure={str(dcp):>5} "
          f"severed departure={str(dsp):>5} severed EOL={rs['stopped']}")

print("\nAbort-rate check: departure at 0.5C and 1C only (2C is invalid)")
for c in (0.5, 1.0, 2.0):
    rc = m.simulate(c, 1.0)
    rs = m.simulate(c, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
    dcp, _, _ = departure(rc["LLI"])
    dsp, _, _ = departure(rs["LLI"])
    print(f"  {c:>3.1f}C coupled departure={str(dcp):>5} "
          f"severed departure={str(dsp):>5} "
          f"coupled knee={str(m.knee(rc['LLI'], rc['Q0'])):>5}")

print()
print("=" * 78)
print("4. Discretisation check: sum(a/sqrt(i)) vs 2a*sqrt(n)")
print("=" * 78)
a = P["a_sei"]
for n in (100, 400, 1000):
    s = float(np.sum(a / np.sqrt(np.arange(1, n + 1))))
    print(f"  n={n:5d}: sum={s:8.4f}   2a*sqrt(n)={2*a*np.sqrt(n):8.4f}   "
          f"ratio={s/(2*a*np.sqrt(n)):.4f}")

print()
print("=" * 78)
print("5. b_fresh physical interpretation (thickness per unit dead Li)")
print("=" * 78)
for b in (30.0, 60.0):
    for rho in (1e8,):
        print(f"  b={b:5.1f}, rho={rho:.0e} ohm*cm -> t = b/rho = "
              f"{b/rho:.2e} cm = {b/rho*1e7:.1f} nm")
print("  Li volumetric capacity 2062 mAh/cm^3 (rho_Li 0.534 g/cm3 x 3861 mAh/g)")

print()
print("=" * 78)
print("6. Numbers inherited from recheck_derived_numbers.py (restated)")
print("=" * 78)
print("  SEI: d=30nm, j=3mA/cm2 -> sigma 1e-9/1e-8/1e-7 S/cm -> "
      "R 3000/300/30 ohm cm2 -> dphi 9000/900/90 mV")
print("  SEI volume: 3.7e-5 mol per mAh/cm2 x 30 cm3/mol = 1.1e-3 cm3/cm2 "
      "= 11 um per mAh/cm2")
print("  pore fill: 3/11 = 0.2727 mAh/cm2 = 8.93% of 3 mAh/cm2")
print("  CE: 14.55 um inventory at 3 mAh/cm2; 14.55 nm/cycle at 99.9%")
print("  Loop B: 0.5% Mn over 1000 cyc vs 20% loss -> 40x shortfall")
print("  Loop D: 3.3 umol/cm2 Li+ vs 30 umol/cm2 -> 8.96x")
print("  Loop C: elastic UB 12.89 GPa (quoted 12); realiz. 0.5-2 GPa vs "
      "frac 0.5-1.1 GPa")
print("  M3: 390/47 ppm; 0.25%/2.1% of inventory")
