"""Check the pore-filling / porosity arithmetic quoted in S2.3, and the
cycle at which the coupled model crosses the pore-fill LLI threshold.

The porosity correction has TWO defensible conventions and they move the
threshold in OPPOSITE directions. S2 must state which one it uses.
"""
import os
import sys

# Resolve the model module from this file's own location, not from the shell's cwd.
# A bare relative path made this check fail with ModuleNotFoundError when run from
# anywhere but the repo root -- it reported FAIL because of where you stood, not
# because of what the document says. Fixed alongside check_s5_sensitivity.py.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "research", "06-proposal", "_support"))
import loopA_model_v4 as m

P = m.P
n_per_mAh = 3.6 / 96485.0

print("dense SEI thickness per mAh/cm2 (V_m = 30 cm3/mol):",
      f"{n_per_mAh*30.0*1e4:.3f} um")
print("Li2CO3 end-member (34.8):", f"{n_per_mAh*34.8*1e4:.3f} um")
print("band V_m 20-40:", f"{n_per_mAh*20*1e4:.2f}", "-", f"{n_per_mAh*40*1e4:.2f}")

t_dense = n_per_mAh * 30.0 * 1e4          # um per mAh/cm2
pore = 3.0                                 # um of pore volume

print("\n--- convention A: transport-blocking, effective occupancy (1-p) ---")
print("    t_eff = t_dense * (1-p)   -> FEWER um per mAh -> MORE LLI needed")
for p in (0.30, 0.50):
    t_eff = t_dense * (1 - p)
    lli = pore / t_eff
    print(f"    p={p:.2f}: t_eff={t_eff:.2f} um/mAh  LLI_fill={lli:.3f} mAh/cm2"
          f"  ({100*lli/3.0:.1f}% of 3 mAh/cm2)")

print("\n--- convention B: geometric void-filling, t = t_dense/(1-p) ---")
print("    thicker film per mAh -> FEWER mAh needed")
for p in (0.30, 0.50):
    t_eff = t_dense / (1 - p)
    lli = pore / t_eff
    print(f"    p={p:.2f}: t_eff={t_eff:.2f} um/mAh  LLI_fill={lli:.3f} mAh/cm2"
          f"  ({100*lli/3.0:.1f}% of 3 mAh/cm2)")

print("\ndense case:", f"{pore/t_dense:.3f} mAh/cm2 ({100*(pore/t_dense)/3.0:.1f}%)")
print("manuscript range 0.3-0.6 mAh/cm2 =", f"{100*0.3/3.0:.0f}-{100*0.6/3.0:.0f}% of 3 mAh/cm2")

# When does the coupled baseline cross the pore-fill threshold?
r = m.simulate(1.0, 1.0)
LLI = r["LLI"]
knee = m.knee(LLI, r["Q0"])
for thr_name, thr in [("0.27 dense", 0.27), ("0.39", 0.39), ("0.55", 0.55), ("0.60", 0.60)]:
    idx = next((i for i, v in enumerate(LLI) if v >= thr), None)
    print(f"  coupled LLI first >= {thr_name:10s} : cycle {idx}"
          f"   (knee {knee}, lead {knee-idx if idx else None} cycles,"
          f" LLI ratio {LLI[knee]/thr:.2f})")
print("  LLI at knee / 0.27 =", f"{LLI[knee]/0.27:.2f}")
