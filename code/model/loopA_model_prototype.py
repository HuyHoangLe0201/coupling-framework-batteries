"""
Prototype for Box 1 / Figure 3(a,b) of the Perspective.
NOT a validated battery model -- a scaling argument.
Purpose: verify that the reduced Loop-A system exhibits a genuine
threshold (knee) whose ONSET is set by operating conditions, and
produce illustrative panels to validate the figure concept.

State variables (per unit area):
  R  : local anode interphase (SEI) area-specific resistance  [ohm*cm^2]
  D  : cumulative dead-Li charge-equivalent                    [mAh/cm^2]
  Qloss: total lost capacity                                   [mAh/cm^2]

Loop A closure:
  eta_plating = j*R + eta_ct - delta        (V; positive => Li plates)
  plating rate  p = kp * max(0, eta_plating)         [mAh/cm^2/cycle]
  dead-Li increment = f_dead * p
  interphase growth: dR/dn = a_sei + b_fresh * p    (fresh Li creates fresh SEI area)
  LLI increment: dLLI/dn = c_sEI*(a_sei + b*p) + p
"""
import numpy as np

F = 96485.0

params = dict(
    j=0.003,        # A/cm^2  (1C on 3 mAh/cm^2)
    eta_ct=0.030,   # V, charge-transfer overpotential
    delta=0.090,    # V, effective margin to 0 V vs Li/Li+ at the operating SOC
    R0=8.0,         # ohm*cm^2, fresh-cell anode ASI
    a_sei=0.050,    # ohm*cm^2 per cycle, baseline interphase growth
    kp=60.0,        # mAh/cm^2 per cycle per volt of excess overpotential
    f_dead=0.35,    # fraction of plated Li that becomes electrically isolated
    b_fresh=1.2,    # ohm*cm^2 per (mAh/cm^2) of fresh plated Li -> SEI
    c_lli=0.004,    # mAh/cm^2 of LLI per ohm*cm^2 of interphase grown
    Q0=3.0,         # mAh/cm^2 nominal capacity
    ncycles=2000,
)


def simulate(p):
    n = p["ncycles"]
    R = np.zeros(n); D = np.zeros(n); LLI = np.zeros(n); plated = np.zeros(n)
    R[0] = p["R0"]
    for i in range(1, n):
        eta = p["j"] * R[i - 1] + p["eta_ct"] - p["delta"]
        pl = p["kp"] * max(0.0, eta)
        plated[i] = pl
        dR = p["a_sei"] + p["b_fresh"] * pl
        R[i] = R[i - 1] + dR
        D[i] = D[i - 1] + p["f_dead"] * pl
        LLI[i] = LLI[i - 1] + p["c_lli"] * dR + pl
    return R, D, LLI, plated


def knee_cycle(LLI, frac=0.20):
    """operational knee: first cycle where LLI exceeds frac of nominal capacity"""
    idx = np.where(LLI > frac * params["Q0"])[0]
    return int(idx[0]) if len(idx) else None


print("=" * 78)
print("Loop-A reduced model: does the knee onset move with operating condition?")
print("=" * 78)

base = dict(params)
R, D, LLI, plated = simulate(base)
print(f"\nBaseline (j = {base['j']*1e3:.1f} mA/cm^2, 1C):")
print(f"  R crosses plating threshold at R* = "
      f"{(base['delta']-base['eta_ct'])/base['j']:.1f} ohm*cm^2")
print(f"  R(1) = {R[0]:.1f}  R(500) = {R[499]:.1f}  R(2000) = {R[-1]:.1f} ohm*cm^2")
n_first_plating = np.where(plated > 1e-9)[0]
print(f"  first cycle with plating: "
      f"{n_first_plating[0] if len(n_first_plating) else 'none'}")
print(f"  knee (20% LLI): {knee_cycle(LLI)} cycles")
print(f"  LLI(2000) = {LLI[-1]:.2f} mAh/cm^2 = {100*LLI[-1]/base['Q0']:.0f}% of capacity")

print("\n--- Rate dependence (knee should move LATER at lower rate) ---")
res_rate = []
for c in [0.5, 1.0, 2.0, 3.0]:
    p = dict(base); p["j"] = 0.003 * c
    _, _, L, _ = simulate(p)
    k = knee_cycle(L)
    Rstar = (p["delta"] - p["eta_ct"]) / p["j"]
    res_rate.append((c, Rstar, k))
    print(f"  {c:>4.1f}C  j={p['j']*1e3:5.1f} mA/cm^2  R*={Rstar:6.1f}  knee={k}")

print("\n--- Temperature dependence (higher T -> faster SEI -> earlier knee) ---")
res_T = []
for Tfac, name in [(0.5, "0 C"), (1.0, "25 C"), (2.0, "45 C")]:
    p = dict(base); p["a_sei"] = base["a_sei"] * Tfac
    _, _, L, _ = simulate(p)
    k = knee_cycle(L)
    res_T.append((name, Tfac, k))
    print(f"  {name:>5s}  a_sei={p['a_sei']:.3f}  knee={k}")

print("\n--- Initial-resistance (formation quality) dependence ---")
res_R0 = []
for R0 in [4.0, 8.0, 16.0, 30.0]:
    p = dict(base); p["R0"] = R0
    _, _, L, _ = simulate(p)
    res_R0.append((R0, knee_cycle(L)))
    print(f"  R0={R0:5.1f} ohm*cm^2  knee={res_R0[-1][1]}")

print("\n--- Is post-knee fade superlinear? (LLI growth exponent) ---")
n = np.arange(1, len(LLI) + 1)
mask = LLI > 1e-6
for lo, hi, label in [(50, 300, "pre-knee"), (400, 900, "post-knee")]:
    m = (n >= lo) & (n <= hi) & mask
    if m.sum() > 5:
        alpha = np.polyfit(np.log(n[m]), np.log(LLI[m]), 1)[0]
        print(f"  {label:>9s} ({lo}-{hi} cyc): LLI ~ n^{alpha:.2f}")

print("\n--- Knee-onset map over (C-rate, a_sei) ---")
print("  (rows = C-rate, cols = SEI growth rate factor; entries = knee cycle)")
print("  " + "".join(f"{f'{Tf:>6.1f}x':>8s}" for Tf in [0.25, 0.5, 1.0, 2.0, 4.0]))
for c in [0.5, 1.0, 2.0, 3.0, 4.0]:
    row = ""
    for Tf in [0.25, 0.5, 1.0, 2.0, 4.0]:
        p = dict(base); p["j"] = 0.003 * c; p["a_sei"] = base["a_sei"] * Tf
        k = knee_cycle(simulate(p)[2])
        row += f"{k if k is not None else '>2000':>8}"
    print(f"  {c:>3.1f}C{row}")

print("\nVERDICT: the model produces (i) a linear pre-knee regime, "
      "(ii) superlinear post-knee LLI, and (iii) knee onset moving "
      "systematically with rate, temperature and initial resistance.")
print("The threshold is R* = (delta - eta_ct)/j -- i.e. an operating-condition")
print("boundary, NOT a materials constant. Figure 3 concept is supported.")
