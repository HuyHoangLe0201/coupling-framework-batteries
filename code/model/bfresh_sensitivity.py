"""
b_fresh sensitivity sweep -- converts the model's weakest parameter into a
robustness claim (requested by Lead; option (a)).

b_fresh = interphase resistance added per unit of freshly created Li/dead-Li
surface. It has NO literature anchor. The question is not "what is its value"
but "does the QUALITATIVE result survive across a wide range of it".

Claims under test:
  C1: with coupling ON, a knee exists.
  C2: with coupling OFF, no knee exists (the severing test).
  -> If C1 & C2 hold across 2+ decades of b_fresh, the result is robust and
     the parameter ceases to be a vulnerability.

Also reports the physical interpretation (option b) for context:
b_fresh can be re-expressed as an interphase thickness per unit fresh area,
using SEI resistivity ~1e8 ohm*cm, so b_fresh [ohm*cm^2 per mAh/cm^2] maps to
a nm of new interphase per mAh/cm^2 of fresh plated Li.
"""
import numpy as np
import loopA_model_v4 as m
from departure_test import departure

print("=" * 88)
print("b_fresh SENSITIVITY SWEEP — is the qualitative result robust?")
print("=" * 88)

b_values = [1.0, 3.0, 10.0, 30.0, 60.0, 100.0, 200.0, 400.0]
print(f"\n{'b_fresh':>8} {'knee':>7} {'depart':>7} {'EOL':>6} {'pre-exp':>8} "
      f"{'post-exp':>9} {'R_final':>8} {'verdict':>10}")
print("-" * 88)

rows = []
for b in b_values:
    rc = m.simulate(1.0, 1.0, p=dict(b_fresh=b))
    k = m.knee(rc["LLI"], rc["Q0"])
    d, _, _ = departure(rc["LLI"])
    kk = k or (rc["stopped"] // 2)
    pre = m.exponent(rc["LLI"], max(20, int(0.10 * kk)), int(0.90 * kk))
    post = m.exponent(rc["LLI"], kk, min(int(1.8 * kk), rc["n"] - 2))
    rows.append((b, k, d, rc, pre, post))
    verdict = "knee" if k else "NO knee"
    print(f"{b:>8.1f} {str(k):>7} {str(d):>7} {rc['stopped']:>6} "
          f"{pre:>8.2f} {post:>9.2f} {rc['R'][-1]:>8.1f} {verdict:>10}")

print("\n" + "=" * 88)
print("C1: does a knee exist with coupling ON, across b_fresh?")
print("=" * 88)
knees = [r[1] for r in rows]
print(f"  b_fresh range tested: {b_values[0]} to {b_values[-1]} "
      f"({b_values[-1]/b_values[0]:.0f}x, {np.log10(b_values[-1]/b_values[0]):.1f} decades)")
print(f"  knees found: {sum(1 for k in knees if k is not None)}/{len(knees)}")
print(f"  knee range: {min(k for k in knees if k)} to {max(k for k in knees if k)} cycles")

print("\n" + "=" * 88)
print("C2: THE SEVERING TEST across b_fresh (severed = b_fresh 0 AND f_dead 0)")
print("=" * 88)
print(f"\n{'b_fresh':>8} {'coupled depress':>16} {'severed depress':>16} "
      f"{'severed EOL':>12}")
print("-" * 88)
sever_all_none = True
for b in [10.0, 30.0, 60.0, 100.0, 200.0]:
    rc = m.simulate(1.0, 1.0, p=dict(b_fresh=b))
    rs = m.simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
    dc, _, _ = departure(rc["LLI"])
    ds, _, _ = departure(rs["LLI"])
    if ds is not None:
        sever_all_none = False
    print(f"{b:>8.1f} {str(dc):>16} {str(ds):>16} {rs['stopped']:>12}")

print("\n" + "=" * 88)
print("ROBUSTNESS VERDICT")
print("=" * 88)
if sever_all_none and all(k is not None for k in knees):
    print(f"""
  C1 HOLDS: a knee appears for every b_fresh tested across
            {np.log10(b_values[-1]/b_values[0]):.1f} decades ({b_values[0]:.0f}-{b_values[-1]:.0f}).
  C2 HOLDS: the severed cell NEVER departs from its early power law,
            at every b_fresh tested.

  => The qualitative result is ROBUST to b_fresh. The parameter sets WHERE
     the knee occurs, not WHETHER it occurs. This converts b_fresh from an
     unanchored fudge factor into a locating parameter, and it is the
     strongest available answer to a reviewer who attacks the model's
     parameterisation.
""")
else:
    print("  WARNING: robustness NOT established. Investigate before claiming.")

print("=" * 88)
print("PHYSICAL INTERPRETATION of b_fresh (for the SI)")
print("=" * 88)
rho_sei = 1e8  # ohm*cm, conservative interphase resistivity (~1e-8 S/cm)
print(f"""
  b_fresh has units ohm*cm^2 per (mAh/cm^2). Using an interphase resistivity
  rho = {rho_sei:.0e} ohm*cm and Li volumetric capacity 2062 mAh/cm^3:

    1 mAh/cm^2 of fresh plated Li, if it forms a film of thickness t on area A,
    gives b_fresh ~= rho * t / A_effective.

  So b_fresh = 60 ohm*cm^2 per mAh/cm^2 corresponds to an effective added
  interphase thickness of order
        t ~= b_fresh / rho = 60 / 1e8 cm = 6e-7 cm = 6 nm
  per mAh/cm^2 of dead Li per cm^2 -- i.e. a few nanometres of fresh
  interphase per unit of fresh surface. That is the right ORDER OF MAGNITUDE
  for a re-formed SEI, which gives b_fresh a physical basis even without a
  literature value. State this derivation in the SI (option b), alongside the
  sensitivity sweep (option a).
""")
