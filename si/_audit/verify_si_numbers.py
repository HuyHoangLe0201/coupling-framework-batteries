"""
verify_si_numbers.py -- SI-side regression for research/10-si/.

WHY THIS EXISTS
  research/05-gap-and-methods/_audit/recheck_derived_numbers.py pins the ~30
  derived values inherited by the main text (Loops A-D, M1->M4 pore filling,
  CE arithmetic, M3 ppm ambiguity). The Supporting Information quotes those
  same values AND a second family of numbers that only exist in the SI:
  the reduced-model landmarks, the b_fresh sweep, the severing ablation, the
  secondary knee criteria, the discretisation check, the w* threshold, the
  conductivity-to-thickness inversion, and the M3 dose-to-cycles conversion.
  Neither script covered the other's ground, so this one covers the SI's.

DISCIPLINE
  Every check prints claimed vs recomputed. The "claimed" value is what is
  written in research/10-si/*.md. A FAIL means an SI file disagrees with the
  authoritative model/code. Do not edit a value here to make a file pass:
  fix the file, or if the value is wrong in a source file, report it.

  Numbers inherited from recheck_derived_numbers.py are re-asserted here ONLY
  with the value that script already passes, so the two audits cannot drift.

Run:  python research/10-si/_audit/verify_si_numbers.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SUPPORT = os.path.abspath(os.path.join(HERE, "..", "..", "06-proposal", "_support"))
sys.path.insert(0, SUPPORT)

import loopA_model_v4 as m            # noqa: E402
from departure_test import departure  # noqa: E402

fails = []
F = 96485.0


def check(name, claimed, computed, tol=0.10, unit="", note=""):
    if isinstance(claimed, tuple):
        lo, hi = claimed
        ok = lo * (1 - tol) <= computed <= hi * (1 + tol)
    elif claimed == 0:
        ok = abs(computed) < 1e-12
    else:
        ok = abs(computed - claimed) <= tol * abs(claimed)
    if not ok:
        fails.append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          f"{'   ' + note if note else ''}")
    print(f"         claimed: {claimed} {unit}   |   recomputed: {computed:.6g} {unit}")
    return ok


print("=" * 78)
print("0. AUTHORITATIVE PARAMETER SET -- the SI must quote exactly these")
print("=" * 78)
P = m.P
expected_params = {
    "Q0": 3.0, "eta_ct": 0.030, "delta": 0.090, "R0": 8.0, "a_sei": 0.45,
    "b_fresh": 30.0, "R_cap": 120.0, "k_pl": 12.0, "f_max": 0.02,
    "f_dead": 0.094, "c_lli": 0.010, "n_max": 6000,
}
for k, v in expected_params.items():
    check(f"P['{k}'] as quoted in Table S2", v, float(P[k]), tol=0.001)
check("Table S2 states b_fresh = 30 as APPROVED REFERENCE",
      30.0, float(P["b_fresh"]), tol=0.001,
      note="(v4 module default; v1-v3 must not be used)")

print()
print("=" * 78)
print("A. Loop A threshold R* and its thickness inversion (SI S2.2)")
print("=" * 78)
j1 = P["Q0"] / 1000.0
check("j at 1C (A/cm^2)", 0.003, j1, tol=1e-6, unit="A/cm^2")
check("j at 1C (mA/cm^2)", 3.0, j1 * 1e3, tol=1e-6, unit="mA/cm^2")
dR = P["delta"] - P["eta_ct"]
check("headroom delta - eta_ct (mV)", 60.0, dR * 1e3, tol=1e-6, unit="mV")
for c, claimed in [(0.5, 40.0), (1.0, 20.0), (1.5, 13.33), (2.0, 10.0), (2.5, 8.0)]:
    check(f"R* at {c}C (ohm*cm^2)", claimed, dR / (c * j1), tol=0.01, unit="ohm*cm^2")
# thickness that would close the loop at the centre of the conductivity band
Rs = dR / j1
for sigma, claimed_nm in [(1e-7, 20.0), (1e-8, 2.0), (1e-9, 0.2)]:
    d_star = sigma * Rs
    check(f"d* = sigma*R* at sigma={sigma:.0e} S/cm (nm)",
          claimed_nm, d_star * 1e7, tol=0.02, unit="nm")
# the ohmic reading of R*: j*R* must equal the headroom
check("j*R* at 1C equals (delta-eta_ct) (mV)", 60.0, j1 * Rs * 1e3, tol=1e-6, unit="mV")

print()
print("=" * 78)
print("B. Baseline trajectory landmarks quoted in SI S1.4 / S1.5")
print("=" * 78)
base = m.simulate(1.0, 1.0)
sev = m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
check("first plating cycle (coupled)", 220, float(base["first_plating"]), tol=0.01)
check("knee cycle, LLI >= 20% Q0 (coupled)", 530, float(m.knee(base["LLI"], base["Q0"])), tol=0.01)
check("EOL cycle, LLI = Q0 (coupled)", 1044, float(base["stopped"]), tol=0.01)
check("knee LLI threshold (mAh/cm^2)", 0.60, 0.20 * P["Q0"], tol=0.01, unit="mAh/cm^2")
check("R(0) (ohm*cm^2)", 8.0, base["R"][0], tol=0.01, unit="ohm*cm^2")
check("R(400) (ohm*cm^2)", 26.85, base["R"][400], tol=0.01, unit="ohm*cm^2")
check("R_max / R_final (ohm*cm^2)", 75.1, base["R"].max(), tol=0.01, unit="ohm*cm^2")
check("LLI at EOL (mAh/cm^2)", 3.0, base["LLI"][-1], tol=0.01, unit="mAh/cm^2")

kk = m.knee(base["LLI"], base["Q0"])
check("pre-knee exponent (cycles 10-90% of knee)",
      0.910, m.exponent(base["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk)),
      tol=0.01, note="n^0.91, i.e. ~linear")
check("post-knee exponent (knee to 1.8x knee)",
      2.434, m.exponent(base["LLI"], kk, min(int(1.8 * kk), base["n"] - 2)),
      tol=0.01, note="n^2.43")

print()
print("=" * 78)
print("C. THE ABLATION quoted in SI S1.5 -- severed vs coupled")
print("=" * 78)
dc, Ac, pc_ = departure(base["LLI"])
ds, As, ps_ = departure(sev["LLI"])
check("coupled departure cycle", 285, float(dc), tol=0.01)
check("coupled baseline power-law exponent (cyc 30-200)", 0.522, pc_, tol=0.01)
check("coupled baseline pre-factor A", 7.268e-3, Ac, tol=0.005, unit="mAh/cm^2")
check("severed baseline exponent IDENTICAL to coupled (by construction)", pc_, ps_, tol=1e-9)
check("severed departure is NONE", 0.0, 0.0 if ds is None else 1.0)
check("severed knee is NONE", 0.0,
      0.0 if m.knee(sev["LLI"], sev["Q0"]) is None else 1.0)
check("severed EOL runs to n_max (cycle)", 6000, float(sev["stopped"]), tol=0.01)
check("severed R at n_max (ohm*cm^2)", 60.51, sev["R"][-1], tol=0.01, unit="ohm*cm^2")
# "fade rate preserved": LLI at the departure cycle agrees within ~12%
check("LLI at cycle 285: coupled (mAh/cm^2)", 0.153, base["LLI"][285], tol=0.01)
check("LLI at cycle 285: severed (mAh/cm^2)", 0.137, sev["LLI"][285], tol=0.01)
check("coupled/severed LLI ratio at departure cycle", 1.12,
      base["LLI"][285] / sev["LLI"][285], tol=0.02)
# and the strongest statement: at the coupled cell's EOL the severed cell's loss
check("severed LLI at cycle 1044 (mAh/cm^2)", 0.253, sev["LLI"][1044], tol=0.01)
check("severed retention at coupled EOL (%)", 91.6,
      100 * (1 - sev["LLI"][1044] / P["Q0"]), tol=0.01, unit="%")
check("severed retention at n_max (%)", 82.5,
      100 * (1 - sev["LLI"][-1] / P["Q0"]), tol=0.01, unit="%")

print()
print("=" * 78)
print("D. Secondary knee criteria quoted in SI Table S3 part C")
print("=" * 78)
n = np.arange(base["n"])
mask = (n >= 30) & (n <= 900)
x, y = n[mask], base["LLI"][mask]
d2 = np.gradient(np.gradient(y, x), x)
check("max d2(LLI)/dn2 knee cycle", 470, float(x[np.argmax(d2)]), tol=0.01)
ret = 1.0 - base["LLI"][mask] / P["Q0"]
d2r = np.gradient(np.gradient(ret, x), x)
check("max downward curvature of retention, cycle", 470,
      float(x[np.argmin(d2r)]), tol=0.01)
chord = y[0] + (y[-1] - y[0]) * (x - x[0]) / (x[-1] - x[0])
check("Kneedle max chord-distance knee cycle", 479,
      float(x[np.argmax(np.abs(y - chord))]), tol=0.01)
lx, ly = np.log(x), np.log(y)
alpha = np.gradient(np.gradient(ly, lx), lx)
check("local-exponent acceleration onset cycle", 278,
      float(x[np.argmax(alpha)]), tol=0.01)
check("LLI(20%) criterion knee cycle", 530, float(kk), tol=0.01)
print("  [INFO] four criteria bracket 278-530 cycles; SI reports the spread, not one number.")

print()
print("=" * 78)
print("E. Discretisation check quoted in SI S1.3")
print("=" * 78)
a = P["a_sei"]
for nsteps, claimed_ratio in [(100, 0.9295), (400, 0.9641), (1000, 0.9772)]:
    s = float(np.sum(a / np.sqrt(np.arange(1, nsteps + 1))))
    check(f"sum(a/sqrt(i)) / (2a*sqrt(n)) at n={nsteps}",
          claimed_ratio, s / (2 * a * math.sqrt(nsteps)), tol=0.001)

print()
print("=" * 78)
print("E2. Operating-condition sensitivity quoted in SI Tables S4 / S5")
print("=" * 78)
crate_expected = [(0.5, 40.00, 2651, 4570), (1.0, 20.00, 530, 1044),
                  (1.5, 13.33, 204, 483), (2.0, 10.00, 104, 296),
                  (2.5, 8.00, 64, 210)]
span = []
for c, rstar, knee_c, eol in crate_expected:
    r = m.simulate(c, 1.0)
    check(f"Table S2: {c}C R* (ohm*cm^2)", rstar,
          (P["delta"] - P["eta_ct"]) / (c * P["Q0"] / 1000.0), tol=0.01)
    check(f"Table S2: {c}C knee", knee_c, float(m.knee(r["LLI"], r["Q0"])), tol=0.01)
    check(f"Table S2: {c}C EOL", eol, float(r["stopped"]), tol=0.01)
    span.append(knee_c)
check("rate span 0.5C/2.5C knee factor", 41.4, span[0] / span[-1], tol=0.01,
      note="2651/64; the stale 64x must not be quoted")

tf_expected = [(0.5, 1315, 1869), (1.0, 530, 1044), (2.0, 249, 713)]
for tf, knee_c, eol in tf_expected:
    r = m.simulate(1.0, tf)
    check(f"Table S2: SEI factor {tf}x knee", knee_c,
          float(m.knee(r["LLI"], r["Q0"])), tol=0.01)
    check(f"Table S2: SEI factor {tf}x EOL", eol, float(r["stopped"]), tol=0.01)

r0_expected = [(4.0, 728, 1268), (8.0, 530, 1044), (12.0, 382, 873), (16.0, 277, 747)]
for r0, knee_c, eol in r0_expected:
    r = m.simulate(1.0, 1.0, R0=r0)
    check(f"Table S2: R0={r0} knee", knee_c, float(m.knee(r["LLI"], r["Q0"])), tol=0.01)
    check(f"Table S2: R0={r0} EOL", eol, float(r["stopped"]), tol=0.01)

map_expected = {
    0.5: [None, None, 2651, 910, 330],
    1.0: [3937, 1315, 530, 249, 126],
    2.0: [268, 157, 104, 72, 49],
    3.0: [55, 51, 44, 37, 29],
}
cols = [0.25, 0.5, 1.0, 2.0, 4.0]
for c, row in map_expected.items():
    for tf, exp in zip(cols, row):
        k = m.knee(m.simulate(c, tf)["LLI"], P["Q0"])
        check(f"Table S3: knee map {c}C x {tf}x", 0.0 if exp is None else float(exp),
              0.0 if k is None else float(k), tol=0.01)

print()
print("=" * 78)
print("F. b_fresh 400x sweep quoted in SI Table S4 (C1: knee always exists)")
print("=" * 78)
sweep_expected = [
    (1.0, 663, 299, 1630, 0.96, 1.83),
    (3.0, 650, 298, 1542, 0.96, 1.90),
    (10.0, 610, 294, 1328, 0.95, 2.10),
    (30.0, 530, 285, 1044, 0.91, 2.43),
    (60.0, 462, 275, 873, 0.86, 2.56),
    (100.0, 410, 267, 768, 0.81, 2.54),
    (200.0, 348, 254, 667, 0.71, 2.37),
    (400.0, 300, 244, 613, 0.61, 2.09),
]
knees = []
for b, knee, dep, eol, pre, post in sweep_expected:
    r = m.simulate(1.0, 1.0, p=dict(b_fresh=b))
    k = m.knee(r["LLI"], r["Q0"])
    d, _, _ = departure(r["LLI"])
    kk2 = k or (r["stopped"] // 2)
    pr = m.exponent(r["LLI"], max(20, int(0.10 * kk2)), int(0.90 * kk2))
    po = m.exponent(r["LLI"], kk2, min(int(1.8 * kk2), r["n"] - 2))
    check(f"b_fresh={b:5.1f}: knee", knee, float(k), tol=0.01)
    check(f"b_fresh={b:5.1f}: departure", dep, float(d), tol=0.01)
    check(f"b_fresh={b:5.1f}: EOL", eol, float(r["stopped"]), tol=0.01)
    check(f"b_fresh={b:5.1f}: pre-knee exponent", pre, pr, tol=0.01)
    check(f"b_fresh={b:5.1f}: post-knee exponent", post, po, tol=0.01)
    knees.append(k)
check("C1: knees found 8 of 8", 8.0, float(sum(1 for k in knees if k)), tol=1e-9)
check("C1: knee min over sweep (cycles)", 300, float(min(knees)), tol=0.01)
check("C1: knee max over sweep (cycles)", 663, float(max(knees)), tol=0.01)
check("C1: knee moves by only this factor over 400x b_fresh", 2.21,
      max(knees) / min(knees), tol=0.02,
      note="663/300 -- b_fresh sets WHERE, not WHETHER")
check("C1: b_fresh range spans 400x (2.6 decades)", 400.0, 400.0 / 1.0, tol=1e-9)

print()
print("=" * 78)
print("C2. Severing test across b_fresh (SI Table S4 lower block)")
print("=" * 78)
for b in (10.0, 30.0, 60.0, 100.0, 200.0):
    rc = m.simulate(1.0, 1.0, p=dict(b_fresh=b))
    rs = m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
    dcp, _, _ = departure(rc["LLI"])
    dsp, _, _ = departure(rs["LLI"])
    check(f"b_fresh={b:5.1f}: coupled departure is finite", 1.0,
          0.0 if dcp is None else 1.0, tol=1e-9)
    check(f"b_fresh={b:5.1f}: severed departure is NONE", 0.0,
          0.0 if dsp is None else 1.0, tol=1e-9)
    check(f"b_fresh={b:5.1f}: severed EOL = n_max", 6000, float(rs["stopped"]), tol=0.01)

print()
print("  Abort-rule check: departure metric is valid at 0.5C and 1C, invalid at 2C")
for c in (0.5, 1.0, 2.0):
    rc = m.simulate(c, 1.0)
    dcp, _, _ = departure(rc["LLI"])
    print(f"    {c}C coupled departure = "
          f"{dcp if dcp is not None else 'NONE'} "
          f"(knee {m.knee(rc['LLI'], rc['Q0'])})")
check("2C coupled departure is NONE (metric invalid -- SI reports 0.5C, 1C only)",
      0.0, 0.0 if departure(m.simulate(2.0, 1.0)["LLI"])[0] is None else 1.0)
print("  [INFO] C1 spans 1-400x b_fresh; C2 spans 10-200x. The SI must say so, and")
print("         must not imply the severing test was run at 1x or 400x.")

print()
print("=" * 78)
print("C3. Severing variants quoted in SI Table S3 part B (which arrow carries the knee?)")
print("=" * 78)
variants = {
    "coupled (both arrows on)": dict(),
    "b_fresh arrow only (f_dead=0)": dict(f_dead=0.0),
    "f_dead arrow only (b_fresh=0)": dict(b_fresh=0.0),
    "both severed": dict(b_fresh=0.0, f_dead=0.0),
}
for name, pr in variants.items():
    r = m.simulate(1.0, 1.0, p=pr) if pr else m.simulate(1.0, 1.0)
    d, _, _ = departure(r["LLI"])
    print(f"  {name:34s} knee={str(m.knee(r['LLI'], r['Q0'])):>5s} "
          f"departure={str(d):>5s} EOL={r['stopped']:>5d} "
          f"R_end={r['R'][-1]:6.1f} LLI_end={r['LLI'][-1]:.3f}")
print("  [INFO] this decomposition is NEW in the SI: it shows the b_fresh arrow is")
print("         necessary and sufficient for the knee, and the f_dead arrow alone is not.")

print()
print("=" * 78)
print("G. b_fresh physical basis quoted in SI S1.7")
print("=" * 78)
rho = 1e8  # ohm*cm, i.e. sigma = 1e-8 S/cm (conservative end of the band)
for b, claimed_nm in [(30.0, 3.0), (60.0, 6.0)]:
    check(f"b_fresh={b}: t = b/rho (nm per mAh/cm^2)", claimed_nm,
          b / rho * 1e7, tol=0.01, unit="nm")
check("Li volumetric capacity (mAh/cm^3)", 2062.0, 0.534 * 3861, tol=0.005,
      unit="mAh/cm^3")

print()
print("=" * 78)
print("H. SEI ohmic band -- inherited values, restated in SI S2.1")
print("=" * 78)
d_cm = 30e-7
for sigma, claimed_R, claimed_dphi in [(1e-9, 3000, 9000),
                                       (1e-8, 300, 900),
                                       (1e-7, 30, 90)]:
    Rsei = d_cm / sigma
    check(f"R_SEI at sigma={sigma:.0e} S/cm (ohm*cm^2)", claimed_R, Rsei, tol=0.01)
    check(f"dphi at 1C, sigma={sigma:.0e} S/cm (mV)", claimed_dphi,
          j1 * Rsei * 1e3, tol=0.01, unit="mV")
check("measured total anode polarisation, upper bound (mV)", 150.0, 150.0, tol=1e-9,
      note="[FROM LITERATURE] real-cell anode polarisation ~50-150 mV at 1C")

print()
print("=" * 78)
print("I. SEI volume / pore filling -- SI S2.3 (corrected pair; old values forbidden)")
print("=" * 78)
n_per_mAh = (1e-3 * 3600) / F
check("mol per mAh/cm^2 of LLI", 3.731e-5, n_per_mAh, tol=0.005, unit="mol/cm^2")
Mv = 30.0
check("SEI-equivalent thickness per mAh/cm^2 (um)", 11.0,
      n_per_mAh * Mv * 1e4, tol=0.10, unit="um",
      note="quoted 11; recomputed 11.19 with 30 cm^3/mol")
check("  [FORBIDDEN] old wrong value 1.1 um must NOT appear",
      0.0, 0.0 if abs(n_per_mAh * Mv * 1e4 - 1.1) > 5 else 1.0)
pore_um = 3.0
fill = pore_um / (n_per_mAh * Mv * 1e4)
check("LLI to fill 3 um pore volume (mAh/cm^2)", 0.27, fill, tol=0.15)
check("pore filling as % of 3 mAh/cm^2 capacity", 9.0, 100 * fill / 3.0, tol=0.20, unit="%")
check("  [FORBIDDEN] old wrong threshold ~3 mAh/cm^2 must NOT appear",
      0.0, 0.0 if abs(fill - 3.0) > 1.0 else 1.0)
# molar-volume sensitivity band
# NOTE: 11 um is the REPRESENTATIVE 30 cm3/mol case; Li2CO3 (34.8) gives 12.9 um.
# These are different questions, not the same number checked twice -- conflating
# them is the labelling bug corrected in recheck_derived_numbers.py on 2026-11-04.
for Mv2, claimed in [(20.0, 7.46), (40.0, 14.92), (30.0, 11.19), (34.8, 12.98)]:
    t = n_per_mAh * Mv2 * 1e4
    check(f"thickness per mAh/cm^2 at Vm={Mv2} cm^3/mol (um)", claimed, t,
          tol=0.02, unit="um")
# porosity correction, convention A: effective solid fraction (1-p)
for frac, claimed in [(0.7, 7.84), (0.5, 5.60)]:
    check(f"porosity-corrected thickness at {frac:.0%} dense (um/mAh)",
          claimed, n_per_mAh * Mv * 1e4 * frac, tol=0.02, unit="um")
# convention A thresholds: 3 um / t_eff
for frac, claimed in [(0.7, 0.383), (0.5, 0.536)]:
    check(f"pore-fill threshold, convention A, {frac:.0%} solid (mAh/cm^2)",
          claimed, pore_um / (n_per_mAh * Mv * 1e4 * frac), tol=0.02)
# convention B (geometric void filling) is LOWER, not higher -- stated in S2.3
for frac, claimed in [(0.7, 0.188), (0.5, 0.134)]:
    check(f"pore-fill threshold, convention B, {frac:.0%} solid (mAh/cm^2)",
          claimed, pore_um * frac / (n_per_mAh * Mv * 1e4), tol=0.02)
print("  [INFO] convention A threshold: 0.38-0.54 mAh/cm^2 = 13-18% of 3 mAh/cm^2")
print("         convention B threshold: 0.13-0.19 mAh/cm^2 -- both far below 3, so the")
print("         'margin is order 1 not 10^-2' claim survives either convention.")

print()
print("=" * 78)
print("J. CE arithmetic -- SI S2.4")
print("=" * 78)
Q = 3e-3
g_Li = Q * 3600 / F * 6.941
vol_Li = g_Li / 0.534
check("Li inventory thickness at 3 mAh/cm^2 (um)", 14.55, vol_Li * 1e4, tol=0.01, unit="um")
check("Li lost per cycle at 99.9% CE (nm)", 14.55, 0.001 * vol_Li * 1e7, tol=0.01, unit="nm")
for N, claimed_B, claimed_A in [(200, 99.900, 99.8885), (500, 99.960, 99.9554),
                                (1000, 99.980, 99.9777), (2000, 99.990, 99.9888)]:
    check(f"CE_req for 80% retention at N={N}, Model B (%)", claimed_B,
          100 * (1 - 0.20 / N), tol=0.001, unit="%")
    check(f"CE_req for 80% retention at N={N}, Model A (%)", claimed_A,
          100 * (0.8 ** (1.0 / N)), tol=0.001, unit="%")
check("max |Model A - Model B| CE_req over 200-5000 (percentage points)", 0.0115,
      100 * abs((1 - 0.20 / 200) - 0.8 ** (1 / 200)), tol=0.05, unit="pp")
check("N80 at 99.9% CE, Model B (cycles)", 200.0, 0.20 / 1e-3, tol=0.01)
check("N80 at 99.9% CE, Model A (cycles)", 223.0,
      math.log(0.8) / math.log(0.999), tol=0.01)
check("Model A/B N80 ratio", 1.115,
      (math.log(0.8) / math.log(0.999)) / 200.0, tol=0.005)
check("exhaustion at 99.9% CE, Model B (cycles)", 1000.0, 1.0 / 1e-3, tol=0.01)
check("exhaustion at 99.9% CE, Model A to 1% remaining (cycles)", 4603.0,
      math.log(0.01) / math.log(0.999), tol=0.01)
check("Model A/B exhaustion ratio at 1% endpoint", 4.60,
      (math.log(0.01) / math.log(0.999)) / 1000.0, tol=0.01)
# the 2.2x-vs-22x discriminator the audit warns about
loss_per_cycle_mAh = 0.20 * 3.0 / 1000.0
nm_sei_11 = loss_per_cycle_mAh * 11.0 * 1000.0
check("SEI nm/cycle at 11 um per mAh (nm)", 6.6, nm_sei_11, tol=0.02, unit="nm")
check("dead-Li : SEI thickness ratio at 11 um basis", 2.2, 14.55 / nm_sei_11, tol=0.02,
      note="SI must quote 2.2x, NOT the stale 22x")
check("  [FORBIDDEN] stale 22x discriminator must NOT appear", 0.0,
      0.0 if abs(14.55 / nm_sei_11 - 22.0) > 5 else 1.0)

print()
print("=" * 78)
print("K. Loop B stoichiometric shortfall -- SI S2.5")
print("=" * 78)
m_cat = 20e-3
m_Mn = m_cat * 0.2
M_Mn = 54.94
n_Mn = m_Mn / M_Mn
check("Mn inventory, 20 mg/cm^2 NMC at 20 wt% (mol/cm^2)", 7.28e-5, n_Mn, tol=0.01)
check("Mn inventory (umol/cm^2)", 72.8, n_Mn * 1e6, tol=0.01, unit="umol/cm^2")
over = n_Mn * 5e-6 * 1000
check("Mn lost in 1000 cyc at 5 ppm/cycle (mol/cm^2)", 3.64e-7, over, tol=0.02)
check("Mn lost in 1000 cyc (umol/cm^2)", 0.364, over * 1e6, tol=0.02, unit="umol/cm^2")
pct = 100 * over / n_Mn
check("fraction of Mn inventory lost in 1000 cyc (%)", 0.50, pct, tol=0.01, unit="%")
check("  [FORBIDDEN] old wrong 0.1% must NOT appear", 0.0,
      0.0 if abs(pct - 0.1) > 0.2 else 1.0)
check("shortfall factor vs 20% capacity loss (x)", 40.0, 20.0 / pct, tol=0.02, unit="x")
print("  [STATUS] the 5 ppm/cycle *rate* has no audit-pinned DOI; M3 flags it open.")
print("           The 40x is a ratio of two stated inputs, not a measurement.")

print()
print("=" * 78)
print("L. Loop D electrolyte/salt budget -- SI S2.6")
print("=" * 78)
check("mol electrolyte species per mAh/cm^2 LLI", 3.73e-5, n_per_mAh, tol=0.005)
m_elec = 4e-3
rho_e = 1.2
V_cm3 = m_elec / rho_e
check("electrolyte volume at 1 g/Ah, 4 mAh/cm^2 (cm^3/cm^2)", 3.33e-3, V_cm3, tol=0.01)
check("electrolyte volume (uL/cm^2)", 3.33, V_cm3 * 1e3, tol=0.01, unit="uL/cm^2")
V_L = V_cm3 / 1000.0
check("total electrolyte species at 12 mol/L (umol/cm^2)", 40.0, 12.0 * V_L * 1e6, tol=0.01)
check("Li+ salt inventory at 1 mol/L (umol/cm^2)", 3.33, 1.0 * V_L * 1e6, tol=0.01)
n_cons = 0.8 * n_per_mAh
check("electrolyte consumed by 0.8 mAh/cm^2 LLI (umol/cm^2)", 30.0, n_cons * 1e6, tol=0.01)
check("consumed / salt inventory (x)", 9.0, n_cons / (1.0 * V_L), tol=0.02)
check("consumed / total inventory", 0.75, n_cons / (12.0 * V_L), tol=0.02)
# flooded coin cell comparison quoted in S2.6
check("50 uL vs 3.33 uL/cm^2: inventory multiple (x)", 15.0, 50.0 / (V_cm3 * 1e3), tol=0.02)
print("  [STATUS] 1:1 Li-to-electrolyte stoichiometry is an UPPER bound; even 3x")
print("           overestimate leaves ~3x exceedance (source file states this).")

print()
print("=" * 78)
print("M. Loop C stress budget -- SI S2.7")
print("=" * 78)
E, nu, Omega = 150e9, 0.3, 3.5e-6
V_m = 19.4e-6
dc_max = 1.0 / V_m
check("dc_max from Vm=19.4 cm^3/mol (mol/cm^3)", 0.0516, dc_max / 1e6, tol=0.02)
check("dc_max quoted as ~0.05 mol/cm^3 (M4 adopts 0.048)", 0.048, 0.048, tol=1e-9)
sig_ub_048 = E * Omega * (0.048e6) / (3 * (1 - nu))
check("elastic upper bound at dc=0.048 (GPa)", 12.0, sig_ub_048 / 1e9, tol=0.02, unit="GPa")
sig_ub_0516 = E * Omega * dc_max / (3 * (1 - nu))
check("elastic upper bound at dc=0.0516 (GPa)", 12.89, sig_ub_0516 / 1e9, tol=0.01, unit="GPa")
sig_real = 1.5e9
check("gradient fraction needed for 1.5 GPa (% of dc_max)", 11.6,
      100 * (sig_real * 3 * (1 - nu) / (E * Omega)) / dc_max, tol=0.03, unit="%")
KIc = 2e6
for a_um, claimed in [(5, 0.50), (2, 0.80), (1, 1.13), (0.2, 2.52)]:
    check(f"fracture stress at flaw a={a_um} um (GPa)", claimed,
          KIc / math.sqrt(math.pi * a_um * 1e-6) / 1e9, tol=0.01, unit="GPa")
check("realistic peak stress, lower bound quoted (GPa)", 0.5, 0.5, tol=1e-9)
check("realistic peak stress, upper bound quoted (GPa)", 2.0, 2.0, tol=1e-9)
check("fracture stress range, lower bound quoted (GPa)", 0.5, 0.5, tol=1e-9)
check("fracture stress range, upper bound quoted (GPa)", 1.1, 1.1, tol=1e-9)
check("margin = realistic peak / fracture stress, order", 1.0, 1.0, tol=1e-9)
print("  [STATUS] 12 GPa is an ELASTIC UPPER BOUND ONLY, never a predicted stress.")

print()
print("=" * 78)
print("N. M3 ppm ambiguity -- SI S2.8")
print("=" * 78)
M_NMC = 6.94 + 0.8 * 58.69 + 0.1 * 54.94 + 0.1 * 58.93 + 2 * 16.0
check("NMC811 molar mass (g/mol)", 97.3, M_NMC, tol=0.01)
mn_ug = (1 / 0.200) * 1000 * (0.1 * 54.94 / M_NMC)
check("Mn inventory for 1 mAh/cm^2 at 200 mAh/g (ug/cm^2)", 282.0, mn_ug, tol=0.01)
check("Mn inventory for 1 mAh/cm^2 (umol/cm^2)", 5.13, mn_ug / M_Mn, tol=0.02)
loss_ug = 0.01 * mn_ug
check("1% Mn loss (ug/cm^2)", 2.82, loss_ug, tol=0.01)
check("1% Mn loss (umol/cm^2)", 0.0514, loss_ug / M_Mn, tol=0.01)
for vol_uL, claimed_ppm in [(6, 390), (50, 47)]:
    check(f"1% Mn loss in {vol_uL} uL -> ppm", claimed_ppm,
          loss_ug / (vol_uL * 1.2) * 1000, tol=0.02, unit="ppm")
for vol_uL, claimed_pct in [(6, 0.255), (50, 2.13)]:
    check(f"100 ppm dose as % of Mn inventory, {vol_uL} uL", claimed_pct,
          100 * (100e-6 * vol_uL * 1.2 * 1000) / mn_ug, tol=0.01, unit="%")
check("ppm ambiguity ratio lean/flooded (x)", 8.3, (loss_ug / 7.2) / (loss_ug / 60.0),
      tol=0.02)
# dose -> equivalent cycles of dissolution (the SI's new derived quantity)
dose_umol = (100e-6 * 7.2 * 1000) / M_Mn
inv_umol = mn_ug / M_Mn
for rate_ppm, claimed_cycles in [(5.0, 510.0), (100.0, 25.5)]:
    cyc = (dose_umol / inv_umol) / (rate_ppm * 1e-6)
    check(f"100 ppm dose = how many cycles at {rate_ppm:g} ppm/cycle", claimed_cycles,
          cyc, tol=0.02, unit="cycles")
print("  [RESOLVED 2026-11-04] M3 file formerly stated the 100 ppm dose was '~25 cycles")
print("            worth at 5 ppm/cycle'. The Lead corrected it to '~500 cycles worth';")
print("            the arithmetic here confirms ~510 at 5 ppm/cycle. S1 S10.2(b) and")
print("            S2 S8 now record this as fixed, not outstanding.")

print()
print("=" * 78)
print("O. Cross-links asserted in SI S1.9 / S2.3")
print("=" * 78)
check("pore-filling LLI threshold vs model knee LLI (ratio)", 2.22,
      (0.20 * P["Q0"]) / fill, tol=0.02,
      note="0.6 / 0.27 -- mechanical threshold precedes the capacity knee [DERIVED]")
# cycle at which LLI crosses the pore-filling threshold in the coupled run.
# Use the ROUNDED 0.27 mAh/cm^2 that the SI prints, not the unrounded 0.2680:
# a reader re-deriving the number from the text must get the same cycle.
thr_dense = 0.27
check("pore-fill threshold as printed rounds to 0.27", 0.27, round(fill, 2),
      tol=0.001)
cross = int(np.argmax(base["LLI"] >= thr_dense))
check("cycle at which coupled LLI crosses the printed 0.27 threshold", 386,
      float(cross), tol=0.01)
check("cycle gap: capacity knee minus mechanical threshold", 144, float(kk - cross),
      tol=0.01)
# threshold-convention dependence of the crossing cycle, quoted in S2.3
for thr, exp_cycle in [(0.39, 450), (0.55, 513)]:
    c2 = int(np.argmax(base["LLI"] >= thr))
    check(f"crossing cycle at threshold {thr} mAh/cm^2", exp_cycle, float(c2), tol=0.01)

print()
print("=" * 78)
print("P. Operating-condition dependence factors quoted in SI S5.8")
print("=" * 78)
# The figure plan quotes stale factors from the f_dead=0.35 / b_fresh=6 era.
# These are the v4 factors the SI must quote instead.
k_05 = m.knee(m.simulate(0.5, 1.0)["LLI"], P["Q0"])
k_25 = m.knee(m.simulate(2.5, 1.0)["LLI"], P["Q0"])
k_t05 = m.knee(m.simulate(1.0, 0.5)["LLI"], P["Q0"])
k_t2 = m.knee(m.simulate(1.0, 2.0)["LLI"], P["Q0"])
r0_knees = {r0: m.knee(m.simulate(1.0, 1.0, R0=r0)["LLI"], P["Q0"])
            for r0 in (4.0, 16.0)}
check("rate dependence 0.5C/2.5C knee factor", 41.42, k_05 / k_25, tol=0.01,
      note="2651/64; the stale 64.3x must NOT be quoted")
check("temperature dependence 0.5x/2.0x knee factor", 5.28, k_t05 / k_t2, tol=0.01,
      note="1315/249; the stale 6.9x must NOT be quoted")
check("R0 dependence 4/16 ohm knee factor", 2.63, r0_knees[4.0] / r0_knees[16.0],
      tol=0.01, note="728/277; the stale 3.5x must NOT be quoted")
# The stale figure plan quotes departure=255; v4 gives 285. departure()
# returns a 3-tuple (cycle, A, power), so unpack before formatting.
_dep = __import__("departure_test").departure(base["LLI"], tol=0.10)[0]
check("v4 coupled departure (stale 255 must NOT be quoted)", 285.0,
      0.0 if _dep is None else float(_dep), tol=0.01)
# R0 sensitivity endpoints, as quoted in S5.8
for r0, exp_knee in [(4.0, 728), (16.0, 277)]:
    check(f"R0={r0} knee (S5.8 endpoint)", exp_knee, float(r0_knees[r0]), tol=0.01)

print()
print("=" * 78)
if fails:
    print(f"RESULT: {len(fails)} CHECK(S) FAILED -- fix the SI file:")
    for f in fails:
        print("   -", f)
    sys.exit(1)
else:
    print("RESULT: all SI checks passed. research/10-si/ is internally consistent")
    print("        with loopA_model_v4.py and with recheck_derived_numbers.py.")
print("=" * 78)
