"""
Departure-from-baseline test: does SEVERING the coupling abolish the knee?

This is the single strongest evidence for the paper's thesis (requested by Lead).
Metric:
  1. fit  LLI ~ A * n^p  on a baseline window (cycles 30..200)
  2. extrapolate that power law to all n
  3. departure = first cycle where LLI exceeds (1+tol) * extrapolation

Expected: loop ON -> a departure cycle exists (a knee).
          loop OFF -> departure = None (fades along its own power law forever).

"Loop OFF" = sever both feedback arrows while keeping baseline SEI growth:
   b_fresh = 0  (dead Li does NOT create extra interphase resistance)
   f_dead  = 0  (plated Li is NOT electrically isolated -> no inventory loss)

This shows the knee is not a fast-ageing artefact: knee and fade rate are
INDEPENDENT axes.
"""
import numpy as np
from loopA_model_v4 import P, simulate, knee


def powerlaw_fit(LLI, lo=30, hi=200):
    n = np.arange(len(LLI))
    m = (n >= lo) & (n <= hi) & (LLI > 1e-12)
    if m.sum() < 8:
        return None
    p, logA = np.polyfit(np.log(n[m]), np.log(LLI[m]), 1)
    return float(np.exp(logA)), float(p)


def departure(LLI, tol=0.10, lo=30, hi=200, search_from=200):
    fit = powerlaw_fit(LLI, lo, hi)
    if fit is None:
        return None, None, None
    A, pw = fit
    n = np.arange(len(LLI))
    base = A * np.power(np.maximum(n, 1), pw)
    m = (n >= search_from) & (LLI > (1 + tol) * base)
    idx = np.where(m)[0]
    return (int(idx[0]) if len(idx) else None), A, pw


print("=" * 80)
print("DEPARTURE-FROM-BASELINE TEST: is the knee caused by the coupling?")
print("=" * 80)

coupled = simulate(1.0, 1.0)
severed = simulate(1.0, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))

for name, r in [("COUPLED (loop ON)", coupled), ("SEVERED (loop OFF)", severed)]:
    d, A, pw = departure(r["LLI"])
    print(f"\n{name}")
    print(f"  baseline fit (cyc 30-200): LLI = {A:.3e} * n^{pw:.2f}")
    print(f"  first plating: {r['first_plating']}")
    print(f"  knee (LLI>=20% Q0): {knee(r['LLI'], r['Q0'])}")
    print(f"  end of life (LLI=Q0): {r['stopped']}")
    print(f"  >>> DEPARTURE from baseline: {d if d is not None else 'NONE'}")
    print(f"  R final = {r['R'][-1]:.1f} ohm*cm^2")

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)
dc, _, _ = departure(coupled["LLI"])
ds, _, _ = departure(severed["LLI"])
if dc is not None and ds is None:
    print(f"""
  *** KEY RESULT ***
  Coupled cell departs from its own early power law at cycle {dc}.
  Severed cell NEVER departs (no knee), even though it still fades.
  => Severing the coupling does not merely DELAY the knee: it ABOLISHES it.
  => The knee is therefore not an artefact of a fast fade rate. Knee and
     fade rate are INDEPENDENT axes, which is exactly the paper's thesis:
     the knee is a topological consequence of the coupling, not a kinetic
     accident.
""")
else:
    print(f"  Coupled departure={dc}, severed departure={ds}.")
    print("  Result is weaker than hoped; investigate before using in the paper.")

print("\n--- Does the same hold at other C-rates? ---")
print(f"{'C-rate':>7} {'coupled dep.':>13} {'severed dep.':>13} "
      f"{'coupled knee':>13} {'severed EOL':>12}")
for c in [0.5, 1.0, 2.0]:
    rc = simulate(c, 1.0)
    rs = simulate(c, 1.0, p=dict(b_fresh=0.0, f_dead=0.0))
    dcp, _, _ = departure(rc["LLI"])
    dsp, _, _ = departure(rs["LLI"])
    print(f"{c:>7.1f} {str(dcp):>13} {str(dsp):>13} "
          f"{str(knee(rc['LLI'], rc['Q0'])):>13} {rs['stopped']:>12}")

print("\nNOTE for the manuscript: the {'NONE'} outcome for the severed cell is")
print("the load-bearing observation. Report it as 'under this reduced model, a")
print("cell whose coupling is severed never leaves its early power law', not as")
print("a claim about real cells.")
