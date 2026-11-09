"""
dissolution_sensitivity.py -- Package E: sensitivity of the Loop B "catalytic, not
stoichiometric" argument to the Mn dissolution rate, which is the single weakest
input in the whole dossier.

WHY THIS EXISTS
--------------
The manuscript's central quantitative claim is a ~40x shortfall: at a nominal
5 ppm/cycle, only ~0.5% of the cathode's Mn inventory leaves over 1000 cycles,
whereas the cell loses ~20% of its capacity. That gap is the *entire* justification
for calling the M3->anode coupling catalytic rather than stoichiometric.

The 5 ppm/cycle is NOT measured by us and NOT well established in the dossier.
The only source for any ppm/cycle range is Bhandari & Bhattacharya, J. Electrochem.
Soc. 2016, 164, A106-A127, DOI 10.1149/2.0101614jes, and the dossier records
1-10 ppm/cycle (mild) but tens-to-hundreds ppm/cycle (aggressive). If the operative
rate is at the aggressive end, the shortfall shrinks and the claim weakens.

This script therefore does three things:
  1. Reproduces the dossier's 40x at 5 ppm/cycle (acceptance criterion), using
     EXACTLY the inputs in quantitative-coupling-analysis.md section 4.
  2. Sweeps the rate and finds the crossover where the argument flips.
  3. Adds a SECOND, independent comparison that the dossier's 40x omits: the
     mole-for-mole (Mn lost vs Li lost) shortfall. The dossier's 40x compares
     "% of Mn inventory" against "% of capacity" as if the two inventories were
     equal. They are not: on a molar basis the Mn inventory is ~54% of the Li
     inventory, so the *molar* shortfall is LARGER (~74x), not smaller.

CROSS-CHECKED AGAINST
---------------------
_audit/recheck_derived_numbers.py section C, which asserts:
    Mn inventory            = 7.3e-5 mol/cm2
    Mn lost in 1000 cyc @5ppm = 3.6e-7 mol/cm2
    fraction lost           = 0.50 %
    shortfall               = 40.0
This script must reproduce all four, or it FAILs.

INPUTS -- held fixed, per the task. Every one is traceable.
----------------------------------------------------------
  cathode loading        20 mg/cm2      section 4 input ("take a cathode loading of...")
  Mn mass fraction       ~0.2           section 4 input (representative of Mn-rich NMC111)
  M(Mn)                  54.94 g/mol    IUPAC standard atomic weight
  areal capacity         3.6 mAh/cm2    section 4 input (of the same electrode)
  capacity loss          20 % / 1000 cyc section 4 input
  F                      96485 C/mol    fundamental

NOTE ON THE UNIT. "ppm/cycle" is only defined relative to a stated reference, and
section 4 defines it relative to the cathode's Mn INVENTORY (its own arithmetic
"5 ppm/cycle x 1000 cycles = 5000 ppm = 0.5%" only works on that basis). That
convention is used throughout. It is NOT necessarily the convention of the cited
literature -- see the unit-ambiguity section at the end.
"""

F = 96485.0  # C/mol

# ---------------------------------------------------------------- inputs
M_CAT_MG_CM2 = 20.0       # mg/cm2, cathode loading                 [section 4 input]
MN_MASS_FRACTION = 0.20   # -, Mn fraction by mass                  [section 4 input]
M_MN = 54.94              # g/mol                                   [IUPAC]
Q_AREAL_MAH_CM2 = 3.6     # mAh/cm2, areal capacity                 [section 4 input]
CAP_LOSS_FRAC = 0.20      # -, fractional capacity loss             [section 4 input]
N_CYCLES = 1000

# ---------------------------------------------------------------- derived inventories
m_Mn_mg_cm2 = M_CAT_MG_CM2 * MN_MASS_FRACTION          # mg/cm2
n_Mn = (m_Mn_mg_cm2 * 1e-3) / M_MN                     # mol/cm2
# Li inventory implied by the areal capacity (all capacity treated as Li-limited)
n_Li = (Q_AREAL_MAH_CM2 * 1e-3 * 3600.0) / F           # mol/cm2
n_Li_lost = CAP_LOSS_FRAC * n_Li                       # mol/cm2 at 20 % loss

print("=" * 78)
print("INPUTS AND DERIVED INVENTORIES")
print("=" * 78)
print(f"  cathode loading            {M_CAT_MG_CM2:g} mg/cm2")
print(f"  Mn mass fraction           {MN_MASS_FRACTION:g}")
print(f"  Mn mass loading            {m_Mn_mg_cm2:g} mg/cm2")
print(f"  M(Mn)                      {M_MN:g} g/mol")
print(f"  -> Mn inventory            {n_Mn:.4g} mol/cm2")
print(f"  areal capacity             {Q_AREAL_MAH_CM2:g} mAh/cm2")
print(f"  -> Li inventory            {n_Li:.4g} mol/cm2")
print(f"  capacity loss / 1000 cyc   {100*CAP_LOSS_FRAC:g} %  ->  {n_Li_lost:.4g} mol/cm2 of Li")
print(f"  NOTE: Mn inventory is {100*n_Mn/n_Li:.1f} % of the Li inventory "
      f"(ratio Li/Mn = {n_Li/n_Mn:.3f}).")
print()

# ---------------------------------------------------------------- sweep
RATES = [1, 5, 10, 50, 100, 200]


def sweep(rate_ppm):
    """Return a dict of all quantities at a given dissolution rate (ppm/cycle).

    ppm/cycle is taken as a fraction of the cathode Mn inventory per cycle.
    """
    frac_per_cycle = rate_ppm * 1e-6
    frac_over_life = frac_per_cycle * N_CYCLES
    n_lost = n_Mn * frac_over_life                    # mol/cm2
    # (i) the dossier's convention: like-percentage comparison
    shortfall_pct = (100.0 * CAP_LOSS_FRAC) / (100.0 * frac_over_life)
    # (ii) mole-for-mole: every departing Mn destroys exactly one Li+
    shortfall_molar = n_Li_lost / n_lost
    return dict(
        rate=rate_ppm,
        frac_over_life=frac_over_life,
        n_lost=n_lost,
        pct_mn=100.0 * frac_over_life,
        shortfall_pct=shortfall_pct,
        shortfall_molar=shortfall_molar,
        # how many Li+ each Mn must catalytically destroy for the gap to be closed
        turnover_needed=shortfall_molar,
    )


rows = [sweep(r) for r in RATES]
d5 = sweep(5)          # the nominal case, used by several blocks below

print("=" * 78)
print("SWEEP: RATE vs SHORTFALL")
print("=" * 78)
print(f"{'rate':>6} {'Mn lost':>10} {'% Mn inv':>9} {'Mn lost':>12} "
      f"{'shortfall':>10} {'shortfall':>10} {'TO needed':>10} {'TO per':>9}")
print(f"{'(ppm/cyc)':>6} {'(mol/cm2)':>10} {'/1000cyc':>9} {'(umol/cm2)':>12} "
      f"{'(pct-basis)':>10} {'(molar)':>10} {'(Li per Mn)':>10} {'cycle':>9}")
print("-" * 78)
for d in rows:
    print(f"{d['rate']:>6g} {d['n_lost']:>10.2e} {d['pct_mn']:>9.3g} "
          f"{d['n_lost']*1e6:>12.4g} {d['shortfall_pct']:>10.3g} "
          f"{d['shortfall_molar']:>10.3g} {d['turnover_needed']:>10.3g} "
          f"{d['turnover_needed']/N_CYCLES:>9.3g}")
print()
print("  'TO needed' = how many Li+ each departing Mn must catalytically destroy")
print("  (over the whole 1000 cycles) for the gap to close without invoking any")
print("  other mechanism. 'TO per cycle' is that divided by 1000. This is the")
print("  quantity the catalytic reading must make plausible, and it is modest:")
print("  even at 1 ppm/cycle a single Mn must catalyse only "
      f"{rows[0]['turnover_needed']/N_CYCLES:.2f} Li per cycle.")
print()
print("  KEY ROBUSTNESS PROPERTY: as the rate RISES the shortfall shrinks, but the")
print("  turnover DEMAND shrinks by the same factor. So the catalytic hypothesis")
print("  does not become harder to defend at high rates -- it becomes easier to")
print("  satisfy while explaining less. The claim is therefore not fragile to rate")
print("  uncertainty in the way a single '40x' quotation implies; what is fragile")
print("  is the SIZE of the amplification, not its existence.")
print()

print("-" * 78)
print(f"{'rate':>6} {'1:1 Mn->Li':>12} {'% of 20% fade':>14} {'verdict':>32}")
print(f"{'(ppm/cyc)':>6} {'coverage':>12} {'(molar)':>14}")
print("-" * 78)
for d in rows:
    coverage = 100.0 / d['shortfall_molar']          # % of Li loss met 1:1 by Mn
    if d['shortfall_molar'] >= 10:
        verdict = "catalytic amplification required"
    elif d['shortfall_molar'] > 2:
        verdict = "amplification still required"
    elif d['shortfall_molar'] > 1.2:
        verdict = "amplification marginal"
    else:
        verdict = "stoichiometry ALONE suffices"
    print(f"{d['rate']:>6g} {coverage:>11.1f}% {coverage:>13.1f}% {verdict:>32}")
print()
print("  Read this column, not the naive 'pct-basis' one: moles are conserved and")
print("  percentages of different inventories are not. '1:1 coverage' is the")
print("  fraction of the Li loss that departing Mn could account for if each Mn")
print("  destroyed exactly one Li+. At 200 ppm/cycle it is still only "
      f"{100.0/rows[-1]['shortfall_molar']:.0f}%.")
print()
print("  NOTE the pct-basis column above (40x at 5 ppm) is the dossier's stated")
print("  convention and is reproducible, but it compares a fraction of the Mn")
print("  inventory with a fraction of capacity. Because the Mn inventory is only")
print(f"  {100*n_Mn/n_Li:.0f}% of the Li inventory, the pct-basis number UNDERSTATES the")
print("  mole-for-mole shortfall by that factor:")
print(f"     5 ppm/cycle: pct-basis 40x  vs  molar {d5['shortfall_molar']:.1f}x")
print("  Both are >1, so the qualitative conclusion is unchanged -- but the")
print("  manuscript should quote the molar number, or state its basis.")
print()

# ---------------------------------------------------------------- acceptance checks
print("=" * 78)
print("ACCEPTANCE CHECKS -- must match recheck_derived_numbers.py section C")
print("=" * 78)
fails = []


def check(name, claimed, computed, tol=0.05, unit=""):
    ok = abs(computed - claimed) <= tol * abs(claimed)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"         expected: {claimed:g} {unit}   |   computed: {computed:.4g} {unit}")
    if not ok:
        fails.append(name)
    return ok


check("Mn inventory (mol/cm2)", 7.3e-5, n_Mn, unit="mol/cm2")
check("Mn lost in 1000 cyc @5ppm (mol/cm2)", 3.6e-7, d5["n_lost"], unit="mol/cm2")
check("fraction of Mn inventory lost @5ppm (%)", 0.50, d5["pct_mn"], unit="%")
check("shortfall factor vs 20% loss @5ppm (pct basis)", 40.0, d5["shortfall_pct"],
      unit="x")
print()

# ---------------------------------------------------------------- crossover
print("=" * 78)
print("CROSSOVER: WHERE DOES STOICHIOMETRY ALONE SUFFICE?")
print("=" * 78)
# (i) pct-basis: 20 / (0.1 r) = 1  ->  r = 200
r_c_pct = (100.0 * CAP_LOSS_FRAC) / (100.0 * 1e-6 * N_CYCLES)
# (ii) molar: n_Li_lost = n_Mn * r*1e-6*N  ->  r = n_Li_lost/(n_Mn*1e-6*N)
r_c_molar = n_Li_lost / (n_Mn * 1e-6 * N_CYCLES)
print(f"  (i)  pct-basis crossover      r_c = {r_c_pct:.1f} ppm/cycle")
print(f"       -> implied Mn inventory loss over 1000 cyc = "
      f"{100*r_c_pct*1e-6*N_CYCLES:.1f} %")
print(f"  (ii) molar (1 Mn : 1 Li)      r_c = {r_c_molar:.1f} ppm/cycle")
print(f"       -> implied Mn inventory loss over 1000 cyc = "
      f"{100*r_c_molar*1e-6*N_CYCLES:.1f} %")
print()
print("  Interpretation: above r_c the Mn that leaves is, by itself, enough to")
print("  account for the observed 20% capacity loss, and no catalytic amplification")
print("  is required. The molar (ii) figure is the physically correct 1:1 test; the")
print("  pct-basis (i) figure is the dossier's convention and is a like-percentage")
print("  shortcut that implicitly assumes Mn inventory == Li inventory.")
print()

# ---------------------------------------------------------------- plausibility bound
print("=" * 78)
print("IS THE REQUIRED CATALYSIS PHYSICALLY PLAUSIBLE? (turnover frequency)")
print("=" * 78)
CYCLE_SECONDS = 2 * 3600.0     # 2 h per cycle (0.5C); the dossier's 20%/1000cyc basis
print(f"  Assuming {CYCLE_SECONDS/3600:g} h per cycle, the demanded turnover frequency is:")
print()
print(f"{'rate':>8} {'Li per Mn':>12} {'Li per Mn':>12} {'TOF':>14} {'time per':>14}")
print(f"{'(ppm/cyc)':>8} {'per cycle':>12} {'per 1000cyc':>12} {'(1/s)':>14} {'event':>14}")
print("-" * 78)
for d in rows:
    to_per_cycle = d['turnover_needed'] / N_CYCLES
    tof = to_per_cycle / CYCLE_SECONDS
    period = CYCLE_SECONDS / to_per_cycle
    print(f"{d['rate']:>8g} {to_per_cycle:>12.3g} {d['turnover_needed']:>12.3g} "
          f"{tof:>14.2e} {period:>13.0f}s")
print()
print("  A homogeneous/heterogeneous catalyst with TOF ~1e-5 s^-1 is an extremely")
print("  UNdemanding requirement: it is roughly one turnover event per day per Mn")
print("  site. For comparison, typical catalytic TOFs span 1e-2 to 1e7 s^-1, and")
print("  even a slow surface reaction at a graphite interphase runs far above 1e-5")
print("  s^-1. So the catalytic reading is NOT implausible on kinetic grounds at any")
print("  rate in the sweep. What the 40x gap does NOT do is prove that catalysis")
print("  occurs -- it only shows that direct stoichiometry cannot account for the")
print("  fade, which is a necessary, not a sufficient, condition for the catalytic")
print("  reading. The sufficient evidence is a dose-response measurement (does the")
print("  parasitic current rise after a controlled TM dose?), which the dossier")
print("  identifies as not yet cleanly done.")
print()

# ---------------------------------------------------------------- plausibility bound
print("=" * 78)
print("SELF-CONSISTENCY BOUND ON THE *SUSTAINED* RATE")
print("=" * 78)
print("  Material loss over the full 1000 cycles cannot exceed a plausible LAM")
print("  budget; a cell that has lost 20% capacity while still cycling has not lost")
print("  a third of its cathode Mn. Sustained rates implied by LAM ceilings:")
print()
print(f"{'assumed LAM ceiling':>20} {'max sustained rate':>20} {'shortfall (molar)':>19}")
print("-" * 78)
for lam in (0.02, 0.05, 0.10, 0.20):
    r_max = lam / (1e-6 * N_CYCLES)
    s = sweep(r_max)["shortfall_molar"]
    print(f"{100*lam:>19.0f}% {r_max:>20.1f} {s:>19.2f}")
print()
print("  => Even a 20% Mn-inventory LAM (which would itself be a dominant,")
print("     easily measured degradation mode) only reaches the crossover.")
print("     For any LAM ceiling below ~20%, the shortfall stays > 1 and the")
print("     catalytic interpretation is required.")
print()

# ---------------------------------------------------------------- composition note
print("=" * 78)
print("SIDE SENSITIVITY -- cathode composition (NOT in the main table)")
print("=" * 78)
print("  The 0.2 Mn mass fraction is representative of Mn-rich NMC111 / LMO. For")
print("  Ni-rich NMC811 the Mn inventory is ~3.6x smaller, which ENLARGES the")
print("  shortfall. Computed for reference only -- inputs are otherwise unchanged.")
MN_FRAC_811 = 0.056  # mass fraction of Mn in LiNi0.8Mn0.1Co0.1O2 (5.494/97.28 g/mol)
n_Mn_811 = (M_CAT_MG_CM2 * MN_FRAC_811 * 1e-3) / M_MN
n_lost_811 = n_Mn_811 * 5e-6 * N_CYCLES
print(f"    NMC811 Mn inventory       {n_Mn_811:.3g} mol/cm2 "
      f"(ratio Mn-rich/NMC811 = {n_Mn/n_Mn_811:.2f}x)")
print(f"    shortfall @5ppm (molar)   {n_Li_lost/n_lost_811:.1f}x  "
      f"(vs {d5['shortfall_molar']:.1f}x for Mn-rich)")
print()

# ---------------------------------------------------------------- unit ambiguity
print("=" * 78)
print("UNIT AMBIGUITY -- the rate and its units are entangled")
print("=" * 78)
print("  Measured dissolution is often reported as a Mn CONCENTRATION in the")
print("  electrolyte (ppm by mass), not as a fraction of the cathode Mn inventory")
print("  per cycle. Those two are NOT interconvertible without the electrolyte")
print("  mass and cathode loading: M3 shows the SAME 1% Mn-loss event reads")
print("  ~390 ppm in a lean coin cell (6 uL) but ~47 ppm in a flooded cell")
print("  (50 uL) -- an ~8x design-dependent ambiguity in what one 'ppm' means.")
print("  So if a cited 'ppm/cycle' is an electrolyte-concentration rate rather than")
print("  an inventory-fraction rate, converting it to the basis used in this table")
print("  carries up to ~8x uncertainty ON TOP of the 1-200 ppm/cycle rate range.")
print("  Mitigation: the manuscript must state the basis explicitly. A rate quoted")
print("  as 'ppm of Mn inventory per cycle' is design-independent and is the only")
print("  form that can be compared across cell formats.")
print()

print("=" * 78)
if fails:
    print(f"RESULT: {len(fails)} CHECK(S) FAILED")
    for f in fails:
        print("   -", f)
    raise SystemExit(1)
print("RESULT: all acceptance checks passed.")
print("  40x reproduced at 5 ppm/cycle (dossier convention).")
print(f"  Molar shortfall at 5 ppm/cycle: {d5['shortfall_molar']:.1f}x")
print(f"  Crossover: {r_c_pct:.0f} ppm/cycle (pct basis), "
      f"{r_c_molar:.0f} ppm/cycle (molar).")
print("=" * 78)
