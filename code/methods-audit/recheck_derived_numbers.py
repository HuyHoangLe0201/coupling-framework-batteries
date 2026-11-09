"""
recheck_derived_numbers.py -- independent re-derivation of every order-of-magnitude
claim in the Lead's files and the cross-file claims other agents inherited.

WHY THIS EXISTS
mech-degradation found two errors in their own file (an unsupported "1000 cycles at
99.9% CE" and an over-stated "hundreds of times") that survived because nobody
multiplied the numbers out. Their closing advice: re-derive every order-of-magnitude
claim from its stated inputs. Run 1 of this script found FOUR errors in the Lead's
own analysis file (a 10x unit slip in SEI volume, a 0.1%-vs-0.5% arithmetic slip in
Loop B, a 3x slip in Loop D salt inventory, and a wrong Delta-c_max in Loop C).
All four are now fixed. Run 2 (this version) verifies the FIXED values.

Run before submission; a FAIL means a file is wrong.
"""
import math

F = 96485.0          # C/mol
R = 8.314            # J/mol/K
T = 298.0            # K

fails = []


def check(name, claimed, computed, tol=0.15, unit=""):
    ok = False
    if isinstance(claimed, tuple):
        lo, hi = claimed
        ok = (lo * (1 - tol) <= computed <= hi * (1 + tol))
    else:
        ok = abs(computed - claimed) <= tol * abs(claimed) if claimed else abs(computed) < 1e-12
    status = "PASS" if ok else "FAIL"
    if not ok:
        fails.append(name)
    print(f"  [{status}] {name}")
    print(f"         claimed: {claimed} {unit}   |   recomputed: {computed:.4g} {unit}")
    return ok


print("=" * 78)
print("A. Loop A -- SEI ohmic drop (fixed: sigma sensitivity band)")
print("=" * 78)
d_cm = 30e-7            # 30 nm
j_1C = 3e-3             # A/cm^2
for sigma, claimed_R, claimed_dphi in [
        (1e-9, 3000, 9000), (1e-8, 300, 900), (1e-7, 30, 90)]:
    Rsei = d_cm / sigma
    dphi = j_1C * Rsei * 1000
    check(f"R_SEI at sigma={sigma:.0e} S/cm", claimed_R, Rsei, unit="ohm*cm2")
    check(f"dphi_SEI at sigma={sigma:.0e} S/cm", claimed_dphi, dphi, unit="mV")

print()
print("=" * 78)
print("B. Loop C -- diffusion-induced stress (fixed: dc_max=0.048 mol/cm3)")
print("=" * 78)
E = 150e9
nu = 0.3
Omega = 3.5e-6          # m^3/mol
# molar volume of layered NMC -> dc_max
V_m = 19.4e-6           # m^3/mol
dc_max = 1.0 / V_m      # mol/m^3
check("dc_max for layered NMC (mol/cm3)", (0.048, 0.052), dc_max / 1e6, tol=0.02,
      unit="mol/cm3")

sigma_ub = E * Omega * dc_max / (3 * (1 - nu))
check("elastic upper bound on hoop stress (GPa)", 12.0, sigma_ub / 1e9, tol=0.10, unit="GPa")

# realistic peak ~1.5 GPa corresponds to what gradient fraction?
sigma_real = 1.5e9
dc_real = sigma_real * 3 * (1 - nu) / (E * Omega)
check("gradient fraction needed for 1.5 GPa (% of dc_max)", 12.0,
      100 * dc_real / dc_max, tol=0.15, unit="%")

KIc = 2e6
for a_um, claimed_sf_GPa in [(5, 0.50), (2, 0.80), (1, 1.13), (0.2, 2.52)]:
    a = a_um * 1e-6
    sf = KIc / math.sqrt(math.pi * a)
    check(f"fracture stress at a={a_um} um (GPa)", claimed_sf_GPa, sf / 1e9,
          tol=0.10, unit="GPa")

print()
print("=" * 78)
print("C. Loop B -- Mn dissolution (fixed: 0.5%, not 0.1%)")
print("=" * 78)
m_cat = 20e-3
m_Mn = m_cat * 0.2
M_Mn = 54.94
n_Mn = m_Mn / M_Mn
check("Mn inventory (mol/cm2)", 7.3e-5, n_Mn, tol=0.05, unit="mol/cm2")
over_1000 = n_Mn * 5e-6 * 1000
check("Mn lost in 1000 cyc @5ppm (mol/cm2)", 3.6e-7, over_1000, tol=0.10, unit="mol/cm2")
pct = 100 * over_1000 / n_Mn
check("fraction of Mn lost in 1000 cyc (%)", 0.50, pct, tol=0.05, unit="%")
# the 40x shortfall argument
shortfall = 20.0 / pct
check("shortfall factor vs 20% capacity loss", 40.0, shortfall, tol=0.10, unit="x")

print()
print("=" * 78)
print("D. Loop D -- electrolyte/salt inventory (fixed: 3.3 umol/cm2 salt)")
print("=" * 78)
n_per_mAh = (1e-3 * 3600) / F
check("mol electrolyte per mAh/cm2 LLI", 3.7e-5, n_per_mAh, unit="mol/cm2")

m_elec = 4e-3           # g/cm2  (4 mAh/cm2 at 1 g/Ah)
rho = 1.2               # g/cm3
V_cm3 = m_elec / rho
check("electrolyte volume (cm3/cm2)", 3.3e-3, V_cm3, tol=0.05, unit="cm3/cm2")
V_L = V_cm3 / 1000.0

n_total = 12.0 * V_L
n_salt = 1.0 * V_L
check("total electrolyte species (umol/cm2)", 40.0, n_total * 1e6, tol=0.10, unit="umol/cm2")
check("Li+ salt inventory (umol/cm2)", 3.3, n_salt * 1e6, tol=0.10, unit="umol/cm2")

n_cons = 0.8 * n_per_mAh
check("electrolyte consumed by 0.8 mAh/cm2 LLI (umol/cm2)", 30.0,
      n_cons * 1e6, tol=0.10, unit="umol/cm2")
check("consumed/salt ratio", 9.0, n_cons / n_salt, tol=0.15, unit="x")
check("consumed/total ratio", 0.75, n_cons / n_total, tol=0.15, unit="x")

print()
print("=" * 78)
print("E. M1 -> M4 -- SEI pore filling (fixed: 11 um per mAh/cm2)")
print("=" * 78)
M_V_SEI = 30.0          # cm3/mol
vol_per_mAh_cm = n_per_mAh * M_V_SEI     # cm3/cm2 per mAh/cm2 == cm thickness
check("SEI-equivalent thickness per mAh/cm2 LLI (um)", 11.0,
      vol_per_mAh_cm * 1e4, tol=0.10, unit="um")
pore_um = 3.0
check("LLI to fill 3 um pore volume (mAh/cm2)", 0.27,
      pore_um / (vol_per_mAh_cm * 1e4), tol=0.15, unit="mAh/cm2")
# express as % of a 3 mAh/cm2 electrode's capacity
check("pore filling as % of 3 mAh/cm2 capacity", 9.0,
      100 * (pore_um / (vol_per_mAh_cm * 1e4)) / 3.0, tol=0.20, unit="%")
# porosity-corrected range
print("  [INFO] at SEI porosity 30-50%, effective volume is 50-70% -> "
      "~5.5-7.7 um/mAh/cm2, pore fill at ~0.39-0.55 mAh/cm2 (11-18% LLI)")
print("         file states '~0.4-0.6 mAh/cm2' and '10-20%' -> consistent")

print()
print("=" * 78)
print("F. CE arithmetic -- the two ageing laws (declared: constant-absolute loss)")
print("=" * 78)
for ce in [0.999, 0.9995, 0.99978]:
    n80_c = math.log(0.8) / math.log(ce)
    n80_l = 0.2 / (1 - ce)
    print(f"  CE={ce*100:8.4f}%  N80(compounding)={n80_c:8.1f}  "
          f"N80(constant loss)={n80_l:8.1f}")
print("  [INFO] agree within ~12% at high CE -> the 80%-retention claim is safe")
print(f"  [INFO] 99.9% exhaustion: compounding={math.log(0.01)/math.log(0.999):.0f}, "
      f"constant-loss={1/0.001:.0f} -> 4.6x apart, MUST declare the law")

Q = 3e-3
g_Li = Q * 3600 / F * 6.941
vol_Li = g_Li / 0.534
check("Li inventory thickness at 3 mAh/cm2 (um)", 14.5, vol_Li * 1e4, tol=0.02, unit="um")
check("Li lost per cycle at 99.9% CE (nm)", 14.5, 0.001 * vol_Li * 1e7, tol=0.03, unit="nm")
check("cycles to exhaust inventory at that rate", 1000.0,
      (vol_Li * 1e4) / (0.001 * vol_Li * 1e4), tol=0.01, unit="cycles")

print()
print("=" * 78)
print("G. M3 ppm ambiguity (corrected: was 20x low)")
print("=" * 78)
M_NMC = 6.94 + 0.8 * 58.69 + 0.1 * 54.94 + 0.1 * 58.93 + 2 * 16.0
check("NMC811 molar mass (g/mol)", 97.3, M_NMC, tol=0.01, unit="g/mol")
m_Mn_cm2_ug = (1 / 0.200) * 1000 * (0.1 * 54.94 / M_NMC)   # ug/cm2
check("Mn inventory for 1 mAh/cm2 @200 mAh/g (ug/cm2)", 282.0, m_Mn_cm2_ug,
      tol=0.05, unit="ug/cm2")
loss_ug = 0.01 * m_Mn_cm2_ug
check("1% Mn loss (ug/cm2)", 2.82, loss_ug, tol=0.05, unit="ug/cm2")
check("1% Mn loss (umol/cm2)", 0.051, loss_ug / 54.94, tol=0.05, unit="umol/cm2")
for vol_uL, claimed_ppm in [(6, 390), (50, 47)]:
    m_mg = vol_uL * 1.2
    ppm = loss_ug / m_mg * 1000
    check(f"1% Mn loss in {vol_uL} uL -> ppm", claimed_ppm, ppm, tol=0.05, unit="ppm")
for vol_uL, claimed_pct in [(6, 0.25), (50, 2.1)]:
    m_mg = vol_uL * 1.2
    dose_ug = 100e-6 * m_mg * 1000
    pct2 = 100 * dose_ug / m_Mn_cm2_ug
    check(f"100 ppm dose as % of inventory in {vol_uL} uL", claimed_pct, pct2,
          tol=0.10, unit="%")
print("  [INFO] same 100 ppm dose = 0.25% (lean) vs 2.1% (flooded) -> 8x ambiguity")

print()
print("=" * 78)
print("H. SEI-equivalent thickness and the 22x vs 2.2x discriminator")
print("=" * 78)
# 1 mAh/cm2 of LLI = 3.7e-5 mol/cm2 (Faraday). SEI molar volume 20-40 cm3/mol.
mol_per_mAh = 3.7e-5
t_lo = mol_per_mAh * 20.0 * 1e4   # um
t_hi = mol_per_mAh * 40.0 * 1e4   # um
check("SEI thickness per mAh/cm2, low bound (um)", 7.4, t_lo, tol=0.05, unit="um")
check("SEI thickness per mAh/cm2, high bound (um)", 14.8, t_hi, tol=0.05, unit="um")
# The files quote "~11 um" for a REPRESENTATIVE SEI molar volume of ~30 cm3/mol.
# (Li2CO3 is 34.8 cm3/mol and gives 12.9 um; the 20-40 band gives 7.4-14.8 um.)
# EARLIER VERSION OF THIS SCRIPT HAD A LABELLING BUG: it computed the 11 um check
# from 34.8 cm3/mol but asserted 11 um, so it passed only because tol was set to
# 0.20 (14.6% off). The claimed value was right and the LABEL was wrong. Fixed:
# the check now uses the molar volume that actually produces 11 um, and Li2CO3 is
# checked separately against its own value. Tightened to tol=0.02.
V_M_REPRESENTATIVE = 30.0   # cm3/mol, representative value the files quote
t_rep = mol_per_mAh * V_M_REPRESENTATIVE * 1e4
check("SEI thickness per mAh/cm2, representative 30 cm3/mol (um)", 11.0, t_rep,
      tol=0.02, unit="um")
t_lico3 = mol_per_mAh * 34.8 * 1e4
check("SEI thickness per mAh/cm2, Li2CO3 34.8 cm3/mol (um)", 12.9, t_lico3,
      tol=0.02, unit="um")
# pore filling: 3 um pore volume / 11 um per mAh = 0.27 mAh/cm2
check("LLI to fill 3 um pore volume (mAh/cm2)", 0.27, 3.0 / 11.0, tol=0.05, unit="mAh/cm2")
print("  [INFO] 0.27 mAh/cm2 against 2-4 mAh/cm2 anode capacity = ~7-14% of capacity")
# dead-Li vs SEI thickness, matched fade budget
# 20% of 3 mAh/cm2 over 1000 cycles -> mAh/cm2 per cycle -> uAh/cm2 per cycle
loss_per_cycle_mAh = 0.20 * 3.0 / 1000.0             # mAh/cm2 per cycle
loss_per_cycle_uAh = loss_per_cycle_mAh * 1000       # uAh/cm2 per cycle
check("Loss per cycle for 20%/1000cyc (uAh/cm2)", 0.60, loss_per_cycle_uAh,
      tol=0.02, unit="uAh/cm2")
for tsei_in, claimed in ((11.0, 6.6), (1.1, 0.66)):
    # mAh/cm2 * (um SEI per mAh/cm2) -> um of SEI per cycle -> nm
    nm_sei = loss_per_cycle_mAh * tsei_in * 1000.0
    check(f"SEI nm/cycle at {tsei_in} um/mAh", claimed, nm_sei, tol=0.05, unit="nm/cycle")
    print(f"  [INFO] at {tsei_in:4.1f} um/mAh: dead-Li 14.55 / SEI {nm_sei:.2f} = "
          f"{14.55/nm_sei:.1f}x  (files must quote this, not a stale value)")
print("  [INFO] CORRECT discriminator is ~2.2x (11 um basis), NOT 22x (1.1 um basis).")

print()
print("=" * 78)
if fails:
    print(f"RESULT: {len(fails)} CHECK(S) FAILED -- fix the files:")
    for f in fails:
        print("   -", f)
else:
    print("RESULT: all checks passed. Files are internally consistent.")
print("=" * 78)
