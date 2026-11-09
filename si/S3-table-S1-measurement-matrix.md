# S3. Table S1, the mechanism × measurement matrix, and the reporting checklist

## S3.1 Structure of the matrix

A capacity-fade curve is a single scalar that integrates every loss mechanism at once. It cannot, on its
own, answer all of the three questions a degradation paper addresses:

1. Loss-term identity. Which of Li inventory, active material, and kinetics moved (a quantity question).
2. Electrode attribution. Which electrode is responsible (a location question).
3. Mechanism family. Which mechanism family is responsible (a chemistry question).

The matrix below maps each measurement onto the questions above. It is required because a fade curve
reported as evidence for a mechanism typically answers none of them, and because the order in which
measurements are applied may matter more than the measurements themselves. Every technique in Table S1 is
established; none is novel. Indexing them by question and by loop is what makes the table a diagnostic
plan rather than a list.

**Verdict legend.** ✔ clean separation · ◐ partial, or requires a differential experiment · ✘ cannot
separate. A ✘ is information: it tells the reader which claims this measurement cannot support, an
element such lists usually omit.

**Loop column.** Which of the four feedback loops (A: plating/dead Li/SEI; B: dissolution/crossover;
C: fracture/stress; D: electrolyte/salt inventory) the measurement is diagnostic of. A blank means the
measurement constrains the balance but not a specific loop.

---

## S3.2 Table S1. Mechanism × measurement matrix

| # | Measurement | What it separates | What it *cannot* separate | Verdict | Q | Loop |
|---|---|---|---|---|---|---|
| 1 | dQ/dV, dV/dQ, incremental capacity (ICA/DVA) | Li-inventory loss (peak *shifts*) vs active-material loss (peak *area* shrinks); the canonical LLI/LAM decomposition | Cannot distinguish *where* Li was lost (SEI vs dead Li vs isolated pocket), nor *which* electrode lost AM | ◐ for Q1; ✘ for Q2, Q3 | 1 | — |
| 2 | High-precision coulometry (HPC), CE titration | Parasitic current per cycle to ~0.001 % precision; reversible vs irreversible inefficiency; the most sensitive early-warning signal | Cannot say whether the parasitic current is SEI (M1) or dead-Li corrosion (M2) — both appear as CE < 1 | ✔ for Q1 magnitude; ✘ for Q3 | 1 | A |
| 3 | Voltage-relaxation profile (VRP) / OCV relaxation | Reversible plating specifically: a voltage plateau during relaxation is the signature of stripping Li⁰ | Cannot quantify dead (isolated) Li; a plateau's absence does not mean plating did not occur irreversibly | ✔ for *reversible* M2 only | 1, 3 | A |
| 4 | EIS / distribution of relaxation times (DRT) | Electrode-resolved time constants: SEI vs charge-transfer vs diffusion; DRT resolves overlapping arcs without equivalent-circuit guessing | Attribution of a specific arc to M3 vs M1 is model-dependent; reconstruction-layer and CEI impedance overlap in frequency | ◐ for Q2; ✘ for Q3 | 2 | A, B, D |
| 5 | Three-electrode / multi-reference cell | Directly resolves anode from cathode overpotential and impedance, the cleanest answer to Q2 | Destructive to the cell format; RE placement artefacts; not applicable to commercial cells | ✔ for Q2 | 2 | — |
| 6 | Half-cell reconstruction (coin-cell rebuild) | Rebuilds each electrode against fresh Li counter, separating anode-limited from cathode-limited fade after the fact; the standard post-hoc complement to dV/dQ | Destructive; the rebuild itself perturbs the electrode (new SEI, new pressure, air exposure); cannot distinguish mechanisms within an electrode | ✔ for Q2 | 2 | — |
| 7 | Operando XRD / neutron diffraction | Lattice-parameter evolution, phase fractions (spinel/rock-salt), Li staging in graphite; distinguishes *structural* AM loss from loss of electrochemically active Li | Does not see amorphous or surface-confined species; poor at the few-nm SRL scale | ✔ for Q1 (structural), ◐ for Q3 | 1, 3 | C, B |
| 8 | Neutron depth profiling / neutron imaging | Spatially resolved Li density, including inactive Li; bulk-sensitive and non-destructive | Modest spatial resolution; not element-specific for TM | ◐ | 1, 2 | — |
| 9 | ICP-MS / ICP-OES (electrolyte or anode digest) | Total dissolved TM, element-resolved, the *only* direct proof of M3 mass loss | Only total amount, not rate or timing; destructive | ✔ for Q3 (M3 vs not-M3); ✘ for timing | 3 | B |
| 10 | LA-ICP-OES / µXRF mapping | Spatially resolved TM deposition on anode and Li distribution | Semi-quantitative; chemical state invisible | ✔ for Q3 location | 2, 3 | B |
| 11 | XPS (anode, cathode) | Chemical state of deposited TM, SEI/CEI composition, F 1s speciation | Surface-only; quantification unreliable; air-sensitive | ◐ | 3 | B, C |
| 12 | DEMS (O₂, CO₂, CO) | Lattice oxygen loss (the M3 trigger), solvent oxidation; time- and potential-resolved | O₂ partly consumed by solvent before detection, so O₂ yield ≠ lattice O lost; cannot identify which cation left | ✔ for the oxygen channel; ✘ for TM | 3 | B |
| 13 | Operando ¹⁹F NMR + EPR | HF and Mn²⁺ concentration *simultaneously in time*, the best existing probe of the acid–dissolution loop | Requires specialized hardware; not for commercial sealed cells | ✔ for Q3 (M3 chemistry) | 3 | B |
| 14 | Isothermal microcalorimetry / electrochemical calorimetry | Parasitic heat flux, an independent, non-electrical measure of parasitic current, so it separates *chemical* from *transport* inefficiency | Cannot assign heat to a specific mechanism without complementary data | ◐ | 1 | — |
| 15 | Stack-pressure / dilatometry | Irreversible vs reversible expansion; mechanical coupling (M4), and via pressure the M4→M3 arrow | Indirect; requires pressure-controlled hardware | ◐ | 2, 3 | C |
| 16 | ARC (accelerating rate calorimetry) | Thermal-onset signature; dead-Li and plating detection via rest-time-dependent onset | A safety probe, not a mechanism separator; destructive | ✘ for Q1–Q3; ✔ for safety context | — | A |
| 17 | Isotope labeling (⁶Li/⁷Li, ¹⁸O) | Provenance tracking, where Li and O actually went; the only method distinguishing *native* from *re-deposited* species | Expensive, low-throughput, rarely applied to full cells | ✔ for provenance, but underused | 3 | A, B |
| 18 | Titration gas chromatography (TGC) | Separates unreacted metallic Li⁰ (dead Li) from Li⁺ in the SEI, the definitive M1-vs-M2 discriminator | Destructive; ex situ; requires cell teardown; no Li⁰ to titrate in graphite/Li-ion cells | ✔ — see S3.3 | 3 | A |
| 19 | ⁷Li in situ / operando NMR | Dead Li vs SEI Li vs bulk Li, non-destructively; also Li site occupancy for voltage fade | Requires NMR-accessible cell; overlapping shifts need modeling | ✔ | 1, 3 | A |
| 20 | Cryo-EM / STEM-EELS | Nanoscale morphology and phase of dead Li and of the SRL | Local only; no statistics; extreme care needed | ◐ | 3 | A, C |

*Notes.* [a] Row 6 (half-cell reconstruction) is included to reach 20 rows: it answers question 2, locating
the loss on the anode or the cathode, and is the standard complement to row 1 in the literature. [b] Q = the question from S3.1 that the measurement primarily answers.
[c] “Loop” is the assignment adopted here, not one taken from the source literature; where a measurement
constrains two loops, both are listed. [d] The six rows that carry Loop A (2, 3, 4, 18, 19, 20) are exactly the ones a
Loop-A test plan needs; there is no single measurement that resolves Loop A, which is the matrix's
principal negative finding.

What the matrix shows that a list would not. Score every row on question 3 (chemical identity — *which
mechanism family*), which is the question the field most wants answered:

| Chemistry capability | Count | Rows |
|---|---|---|
| ✔ clean — directly identifies chemical species or state | 6 | 9, 10, 13, 17, 18, 19 |
| ◐ partial — indirect, or only for one sub-case | 5 | 3, 7, 11, 12, 20 |
| ✘ cannot — explicitly fails on chemistry | 4 | 1, 2, 4, 16 |
|, silent, answers Q1/Q2 only, says nothing about chemistry | 5 | 5, 6, 8, 14, 15 |

So only 6 of 20 techniques cleanly answer the chemistry question, and 9 either only partly answer it or
cannot answer it at all. That asymmetry is the empirical case for the decision tree in S4: because no
single measurement settles the chemistry question, the productive strategy is ordering measurements so
each eliminates a branch, rather than seeking one definitive probe. The matrix provides the evidence and the tree
the response.

---

## S3.3 The best single diagnostic for SEI versus dead Li

**TGC, per Fang et al.** `[FROM LITERATURE: 10.1038/s41586-019-1481-z]`, reinforced by operando ⁷Li NMR
when the cell cannot be destroyed.

The chemistry is the reason it works and should be stated rather than cited as a black box: unreacted
metallic Li⁰ reacts with a protic reagent (water or an alcohol) to evolve H₂ quantitatively, while Li⁺
bound in the SEI (Li₂CO₃, LiF, ROCO₂Li, Li₂O) does not. Measuring evolved H₂ by GC therefore gives a
direct, calibration-free count of Li⁰ atoms; subtracting that from total inactive Li yields the SEI-bound
Li⁺ fraction.

The result is central: in Li-metal cells, unreacted metallic Li⁰, not
SEI-bound Li⁺, dominates inactive lithium. That re-partitions the two most-studied mechanism families.
The SEI is not primarily a lithium sink but primarily a *transport barrier*, and dead lithium, not
interphase, is where most of the stranded inventory sits in these cells.

The two families remain parallel members of the loop rather than one being a downstream product of the
other: Loop A closes through M2 → M1 (dead lithium carries fresh interphase) and through M1 → M2
(interphase raises the overpotential that drives plating). What TGC settles is which family dominates in a
given cell, not the direction of the arrow between them.

**Practical caveats to state.** TGC requires teardown and is post-mortem, not operando. It is not applicable to graphite/Li-ion cells, where all Li is either intercalated or in the SEI — there is no Li⁰ to
titrate. For those cells the equivalent discriminator is high-precision coulometry plus three-electrode
reconstruction, which localizes the loss to the anode but does not split SEI from dead Li. That
residual gap is stated in S4.11 item 1 and is the most significant acknowledged limit of the tree.

---

## S3.4 The 20-item reporting checklist

The biggest reporting gap in this literature is not a missing technique — it is that results are not
comparable across papers, because the quantities that set a mechanism's rate are not reported.
Dissolution in “ppm” and fade in “% per 100 cycles” are not physical quantities until the cell's
normalization is known; S2.8 quantifies that ambiguity at 8.3× for a single cell-design change. The
checklist provides the response, in three tiers.

### Tier 1: required for an interpretable number

| # | Item | Why it is Tier 1 |
|---|---|---|
| 1 | Cathode: composition, morphology (polycrystalline vs single-crystal), particle-size distribution, loading (mg cm⁻²), density/porosity, areal capacity (mAh cm⁻²) | Sets M3 and M4 susceptibility; without areal capacity no current density is defined |
| 2 | Anode: type, loading, porosity, areal capacity | Sets N/P and which mechanism's loss is masked |
| 3 | N/P ratio | Determines whether the cell is anode- or cathode-limited, hence which loss is visible |
| 4 | Electrolyte: salt, concentration, solvent ratio, additive identity and wt%, total mass or volume per cell, and electrolyte-to-active-material ratio | Without this, ppm values are uninterpretable, the 8.3× ambiguity of S2.8 |
| 5 | Water and HF content of the as-assembled cell, with method (coulometric Karl Fischer / acid–base titration) | The solvent spec is not the cell content; both drive Loop B |
| 6 | Cell format and stack pressure | Coin vs pouch vs cylindrical changes pressure history; pressure changes both M4 cracking and M2 plating |
| 7 | Voltage window, C-rate (charge and discharge), temperature, aging protocol (CC-CV vs CC, rest periods, depth of discharge) | Sets *R*\* (S2.2); without it a knee position is not comparable |
| 8 | Cycle number at which fade is quoted, plus the full trajectory | A single endpoint hides the knee, which is the object of study |
| 9 | Formation protocol | First-cycle irreversible loss is often a large fraction of total “degradation” and is protocol-dependent |

### Tier 2: required when a mechanism is claimed

| # | Item | Why it is Tier 2 |
|---|---|---|
| 10 | Loss decomposition (LLI / LAM / polarization) with the method used | “Capacity fade” alone does not answer question 1 |
| 11 | Coulombic efficiency at ≥4 significant figures, SOC window, number of cycles averaged | CE below 4 s.f. cannot discriminate the Loop-A rates of S2.4 |
| 12 | Reference-cycle protocol before/after aging (rate, window, temperature) | Otherwise fade is confounded with rate-capability loss |
| 13 | Impedance spectra with the equivalent circuit or DRT used, and the frequency range | An arc without its deconvolution is not an assignment |
| 14 | Post-mortem sampling plan: electrode, location (edge vs center), number of samples, how the cell was opened | Air exposure is the classic artefact in TM analysis |
| 15 | Detection limits for ICP-MS/XPS/DEMS | “Below detection” is a result only if the limit is stated |

### Tier 3: recommended for reuse

| # | Item | Why it is Tier 3 |
|---|---|---|
| 16 | Raw or minimally processed data for reference cycles and impedance spectra (supplementary) | Lets others re-run the decomposition |
| 17 | Cell-level metadata for physics-based modeling: separator thickness, current-collector foils, tab configuration | Needed to reproduce any transport model |
| 18 | The claim-to-measurement mapping: explicitly, which measurement supports which mechanistic claim | The item most often skipped, and the one that would most improve the field — it forces authors to notice when a claim rests on a fade curve alone |
| 19 | Negative results: mechanisms ruled out, and by what measurement | The tree's value depends on eliminations being reported |
| 20 | Whether fade was path-dependent (rate history, rest, temperature) | Path dependence is the normal case; a single aging protocol underdetermines the mechanism |

### Suggested template sentence for a methods section

> “Cell build: [cathode composition, morphology, loading mg cm⁻², areal capacity mAh cm⁻²] ‖ [anode,
> loading, areal capacity], N/P = [x], electrolyte [salt, conc., solvent ratio, additives wt%],
> electrolyte mass [mg] (E/AM = [x] g Ah⁻¹), separator [type, thickness], cell format [coin/pouch], stack
> pressure [MPa]. Water [ppm, method]; HF [mg L⁻¹, method]. Formation: [protocol]. Aging: [protocol,
> voltage window, C-rate, T]. Reference cycle: [C/20, window, T]. Loss decomposition by [method]; CE
> precision [± x %].“

The checklist is applied to the present work as well as to others. A methods paragraph that omits items
4, 5, or 11 does not meet the standard the checklist sets.

---

## S3.5 Coverage of the four loops

| Loop | Diagnostic measurements (row numbers) | Coverage |
|---|---|---|
| A — plating → dead Li → SEI → η → plating | 2 (HPC/CE), 3 (VRP), 4 (EIS/DRT), 18 (TGC), 19 (⁷Li NMR), 20 (cryo-EM), 16 (ARC, safety) | Strong on *detecting* plating; weak on the feedback arrow (whether dead Li actually raises *R*) |
| B — dissolution → anode poisoning → η → dissolution | 4, 9 (ICP-MS), 10 (LA-ICP), 11 (XPS), 12 (DEMS), 13 (¹⁹F NMR/EPR), 17 (isotopes) | Strong on *detecting* dissolution; weak on turnover — no routine measurement gives the catalytic turnover number S2.5 requires |
| C — fracture → fresh surface → SEI/dissolution | 4, 7 (XRD), 11, 15 (pressure/dilatometry), 20 | Adequate for *detecting* fracture; fresh-surface quantification is indirect only |
| D — electrolyte/salt depletion | 4, plus a flooding differential (not a row — it is an *experiment design*, not a technique) | Weakest loop. No matrix row measures salt inventory directly; Loop D is diagnosed by elimination and by the flooding test |

**The gap this exposes.** Table S1 is most complete exactly where the argument is least constrained. The matrix detects
mechanisms well (plating, dissolution, fracture) but detects coupling, the operative claim —
poorly. No row measures “the arrow from dead Li to interphase resistance,” and
no row measures the catalytic turnover of Loop B or the salt inventory of Loop D. That is why the decision
tree (S4) terminates in B7, loop identification, which is not a measurement but a *perturbation
protocol*: it infers coupling from the sensitivity of the knee to a driving variable, because coupling
itself is not directly measurable with current techniques. The checklist's item 18 (claim-to-measurement
mapping) and item 19 (negative results) are what make that inference auditable.

A consequence for the scope of the claim. Table S1 is not a complete diagnostic toolkit. It provides a
sequencing of established techniques that resolves mechanism, plus one perturbation protocol that tests
coupling. A stronger claim would exceed what the matrix supports, as its ✘
marks are there to prevent.
