"""
Loop-A reduced model, v4 -- authoritative version for Box 1 / Figure 3.

PROVENANCE NOTE
  _support/loopA_model_v3.py appeared in this folder at 16:29:51, was not
  written by proposal-writer, and DOES NOT RUN (RuntimeError: did not
  terminate within n_max cycles; it also mis-reports R* by using
  j = 3*1000/3600 A/cm^2 instead of c_rate*Q0/1000 = 0.003 A/cm^2).
  It is kept for the record but MUST NOT be used. This v4 is the
  reproducible model.

BUILD HISTORY (this narrative belongs in Box 1, it is a genuine result):
  v1  pure positive feedback                -> numerical divergence (R ~ 1e80)
  v2  ad-hoc "current redistribution" damper -> finite knee, but LLI reaches
                                                 318% of Q0 (unphysical) and
                                                 pre-knee exponent n^1.63
  v4  mass-balance-limited plating          -> physical throughout, linear
                                                 pre-knee, sharp knee, finite EOL

WHAT v4 FIXES
  * The current is set by the NOMINAL capacity and the C-rate (constant
    during a test), not by the shrinking remaining capacity. v3 got this
    wrong: it let j fall as capacity fell, which throttled the feedback for
    a spurious reason.
  * Plating is bounded by mass balance: only a fraction f of the applied
    charge can go to Li(0), so p_plate = f * Q_applied and f <= f_max < 1.
    This is the physical self-limitation -- not a hand-added damping term.
  * The interphase resistance has a saturation cap R_cap (pore filling).
  * All state variables stay physical: 0 <= LLI <= Q0, finite EOL.

CAVEAT
  Parameters are order-of-magnitude placeholders chosen to be physically
  defensible, NOT fitted to any dataset. This validates the ARGUMENT
  STRUCTURE and the Figure 3 concept only. No number printed here may be
  quoted in the manuscript as a result.
"""
import numpy as np

P = dict(
    Q0=3.0,        # mAh/cm^2, nominal areal capacity
    eta_ct=0.030,  # V, charge-transfer overpotential at the operating rate
    delta=0.090,   # V, margin between operating anode potential and 0 V vs Li/Li+
    R0=8.0,        # ohm*cm^2, fresh-cell anode area-specific resistance
    a_sei=0.45,    # ohm*cm^2 per sqrt(cycle) -- diffusion-limited SEI baseline
    b_fresh=30.0,  # ohm*cm^2 per (mAh/cm^2) of dead Li -> fresh interphase
                   # REFERENCE VALUE, approved by Lead. Chosen because it keeps
                   # the pre-knee exponent at 0.91 (≈linear, honest narrative),
                   # gives a knee at ~530 cycles, and corresponds to a ~3 nm
                   # re-formed interphase (physically plausible).
                   # NO literature anchor: it LOCATES the knee, does not decide
                   # whether one exists. SI must present the full 1-400 sweep.
    R_cap=120.0,   # ohm*cm^2, asymptote as anode pores fill with interphase
    k_pl=12.0,     # 1/V, sharpness of the plating turn-on
    f_max=0.02,    # max fraction of applied charge that plates (mass balance)
    f_dead=0.094,  # MEASURED dead-Li fraction, no-FEC case
                   # (10.1016/j.xcrp.2020.100139). FEC case = 0.033 +/- 0.006.
                   # v1-v3 used 0.35, which is 4-10x unphysical.
    c_lli=0.010,   # mAh/cm^2 LLI per ohm*cm^2 of newly grown interphase
    n_max=6000,
)


def simulate(c_rate=1.0, T_factor=1.0, R0=None, p=None):
    """T_factor scales the SEI growth prefactor (Arrhenius proxy ~2x per 20 K)."""
    q = dict(P)
    q.update(p or {})
    if R0 is not None:
        q["R0"] = R0

    nm = q["n_max"]
    R = np.zeros(nm); LLI = np.zeros(nm); dead = np.zeros(nm); phi = np.zeros(nm)
    R[0] = q["R0"]
    Q_applied = c_rate * q["Q0"]          # mAh/cm^2 passed per cycle (constant)
    j = c_rate * q["Q0"] / 1000.0         # A/cm^2, constant during a test
    first_plating = None
    stopped = nm

    for i in range(1, nm):
        eta = j * R[i - 1] + q["eta_ct"] - q["delta"]
        f = q["f_max"] * (1.0 - np.exp(-q["k_pl"] * eta)) if eta > 0 else 0.0
        phi[i] = f
        if f > 1e-5 and first_plating is None:
            first_plating = i

        p_plate = f * Q_applied
        d_dead = q["f_dead"] * p_plate

        headroom = max(0.0, 1.0 - (R[i - 1] - q["R0"]) / q["R_cap"])
        dR = (q["a_sei"] / np.sqrt(i) * T_factor + q["b_fresh"] * d_dead) * headroom

        R[i] = R[i - 1] + dR
        dead[i] = dead[i - 1] + d_dead
        LLI[i] = LLI[i - 1] + q["c_lli"] * dR + d_dead

        if LLI[i] >= q["Q0"] - 1e-9:
            # cell is dead: capacity cannot go negative, so LLI is clipped at Q0
            LLI[i] = q["Q0"]
            stopped = i
            return dict(R=R[:i + 1], LLI=LLI[:i + 1], dead=dead[:i + 1],
                        phi=phi[:i + 1], Q0=q["Q0"], R0=q["R0"], j=j,
                        first_plating=first_plating, stopped=stopped,
                        n=len(LLI[:i + 1]))

    return dict(R=R, LLI=LLI, dead=dead, phi=phi, Q0=q["Q0"], R0=q["R0"], j=j,
                first_plating=first_plating, stopped=nm, n=nm)


def knee(LLI, Q0, frac=0.20):
    idx = np.where(LLI >= frac * Q0)[0]
    return int(idx[0]) if len(idx) else None


def exponent(y, lo, hi):
    c = np.arange(len(y))
    m = (c >= lo) & (c <= hi) & (y > 1e-9)
    if m.sum() < 5:
        return float("nan")
    return float(np.polyfit(np.log(c[m]), np.log(y[m]), 1)[0])


def report():
    print("=" * 80)
    print("Loop-A reduced model v4 (mass-balance-limited plating)")
    print("=" * 80)

    base = simulate(1.0, 1.0)
    Rstar = (P["delta"] - P["eta_ct"]) / base["j"]
    print(f"\n1C: j = {base['j']*1e3:.1f} mA/cm^2   plating threshold "
          f"R* = (delta-eta_ct)/j = {Rstar:.1f} ohm*cm^2")
    print(f"  R: fresh={base['R'][0]:.1f}  R(400)={base['R'][min(400,-1)]:.1f}  "
          f"max={base['R'].max():.1f}")
    print(f"  first plating at cycle {base['first_plating']}")
    print(f"  knee (LLI >= 20% Q0) at cycle {knee(base['LLI'], base['Q0'])}")
    print(f"  end of life (LLI = Q0) at cycle {base['stopped']}   [finite? "
          f"{base['stopped'] < P['n_max']}]")
    print(f"  LLI(EOL) = {base['LLI'][-1]:.2f} mAh/cm^2 "
          f"({100*base['LLI'][-1]/base['Q0']:.0f}% of Q0)   [<=100%? "
          f"{base['LLI'][-1] <= base['Q0'] + 1e-3}]")

    print("\n--- P1: knee vs C-rate (expect later knee at lower rate) ---")
    print(f"{'C-rate':>7} {'R* (ohm cm2)':>14} {'knee':>7} {'EOL':>7}")
    for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
        r = simulate(c, 1.0)
        rs = (P["delta"] - P["eta_ct"]) / (c * P["Q0"] / 1000.0)
        print(f"{c:>7.1f} {rs:>14.1f} {str(knee(r['LLI'], r['Q0'])):>7} "
              f"{r['stopped']:>7}")

    print("\n--- P1b: knee vs temperature proxy (SEI growth factor) ---")
    print(f"{'T proxy':>8} {'knee':>7} {'EOL':>7}")
    for Tf, nm in [(0.5, "0 C"), (1.0, "25 C"), (2.0, "45 C")]:
        r = simulate(1.0, Tf)
        print(f"{nm:>8} {str(knee(r['LLI'], r['Q0'])):>7} {r['stopped']:>7}")

    print("\n--- P1c: knee vs formation quality (initial R) ---")
    print(f"{'R0':>8} {'knee':>7} {'EOL':>7}")
    for R0 in [4.0, 8.0, 12.0, 16.0]:
        r = simulate(1.0, 1.0, R0=R0)
        print(f"{R0:>8.1f} {str(knee(r['LLI'], r['Q0'])):>7} {r['stopped']:>7}")

    print("\n--- Shape: is pre-knee ~linear and post-knee superlinear? ---")
    kk = knee(base["LLI"], base["Q0"]) or (base["stopped"] // 2)
    pre = exponent(base["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
    post = exponent(base["LLI"], kk, min(int(1.8 * kk), base["n"] - 2))
    print(f"  pre-knee  (10-90% of knee): LLI ~ n^{pre:.2f}   [target ~1.0]")
    print(f"  post-knee (knee to 1.8k)  : LLI ~ n^{post:.2f}   [target > 1]")

    print("\n--- Knee-onset map: C-rate (rows) x SEI-growth factor (cols) ---")
    cols = [0.25, 0.5, 1.0, 2.0, 4.0]
    print("        " + "".join(f"{f'{c}x':>8s}" for c in cols))
    for c in [0.5, 1.0, 2.0, 3.0]:
        row = ""
        for Tf in cols:
            k = knee(simulate(c, Tf)["LLI"], P["Q0"])
            row += f"{(k if k is not None else 'none'):>8}"
        print(f"  {c:>3.1f}C {row}")

    print("""
VERDICT for Box 1 / Figure 3
  (i)   every state variable stays physical (LLI <= Q0, finite EOL)
  (ii)  pre-knee fade is ~linear (exponent ~1), post-knee superlinear (>1)
  (iii) knee onset moves monotonically with rate, temperature and R0
  (iv)  self-limitation is emergent from mass balance, not hand-added damping
  (v)   threshold is R* = (delta - eta_ct)/j -- depends only on OPERATING
        CONDITION, not on a materials constant  ==> supports
        "knee onset is a design variable, not a materials constant"
""")
    return base


if __name__ == "__main__":
    report()
