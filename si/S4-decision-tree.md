# S4. The diagnostic decision tree — branches B0–B7

## S4.1 Scope of the tree

A faded cell arrives at the bench with no label. Deciding which mechanism caused the fade, and then
whether that mechanism is coupled to another, means choosing among roughly twenty techniques, each of
which constrains a different part of the problem. The order in which they are applied is the substance of
this section.

The decision tree below is a sequencing of established measurements, not a new diagnostic. Every
technique in it appears in Table S1 and none is novel. The contribution is the order: each step names
one measurement, the *discriminating outcome*, and the mechanism that outcome implies, so that a reader
starting from a faded cell can reach a mechanism assignment (or an explicit “confounded”) without having to
hold the whole technique set in mind.

The tree does not attempt the following:

1. It does not start from a mechanism. Beginning with the hypothesis “M3” invites collecting evidence for M3.
   The tree starts from the observed symptom and forces the loss decomposition first, because a fade
   curve is a single scalar integrating every mechanism and cannot be evidence for any of them
   (Table S1, S3.1).
2. It does not promise a unique answer. Three branches terminate in “confounded” and say what would be
   needed to resolve them. A tree that resolved every branch would claim more than the measurements
   support; the residual confounds in S4.11 are an explicit part of the result.
3. It does not identify coupling. Every branch up to B6 assigns a mechanism. The operative claim is
   about loops, and mechanism identity does not imply coupling, because two mechanisms can both be present
   and uncoupled. Branch **B7** exists to close that gap, and it is a perturbation protocol rather than a
   measurement.

**Entry condition.** A cell that has faded measurably (≥5 % capacity loss or a detectable knee). For a cell
that has not yet faded, start at **D2** (S4.12) instead, the early-warning branch.

---

## S4.2 Node inventory and edge semantics

The tree has 20 nodes: 10 actions and decisions, 10 terminals. The entry node is the faded cell; each
decision names the observation that discriminates, and each terminal is either a mechanism assignment or an
explicit “confounded”.

| ID | Label | Section |
|---|---|---|
| B0 | Faded cell (≥5 % loss or knee) → slow reference cycle + dV/dQ decomposition | S4.3 |
| D1 | Identification of the dominant loss term | S4.3 |
| B1 | LLI dominates → HPC/CE + TGC (Li-metal) or ⁷Li NMR / 3-electrode reconstruction | S4.4 |
| B2 | Anode overpotential grew → VRP after charge, then rest-period CE test | S4.5 |
| B3 | LAM dominates → operando XRD across a full cycle | S4.6 |
| B4 | Structural change → ICP-MS (electrolyte + anode digest) + stack-pressure differential | S4.7 |
| B5 | Polarization dominates → EIS + DRT (not equivalent-circuit fitting) | S4.8 |
| B6 | Voltage fade only → operando XRD + ⁷Li MAS-NMR | S4.9 |
| B7 | Loop identification → knee-sensitivity perturbations | S4.10 |
| T-M1 … T-M4 | M1 (SEI) · M2 (dead Li) · M3 (dissolution) · M4 (fracture) | — |
| T-TL | TL (thermodynamic/potential loss) → energy balance, not capacity | S4.9 |
| T-LOOP | Loop confirmed → name it (A/B/C/D) | S4.10 |
| T-NOLOOP | No loop → evidence against the coupling framing; report it | S4.10 |
| T-CONF1…3 | Confounded → see S4.11 | S4.11 |
| D2 | No knee yet → CE tracking, VRP, cathode DRT | S4.12 |

**Edge labels are the discriminating outcomes, not descriptions of the action:** an edge out of D1 reads
“LLI dominates”, not “went to B1”. This is what makes the tree a decision procedure. Every edge label is a
physical observation a reader could actually make.

**Branch order is not arbitrary.** B1/B3/B5/B6 fan out from D1 in the order M1/M2 → M4/M3 → kinetics → TL,
so that a reader moving down the tree moves from quantity to location to chemistry, matching the three
questions of S3.1. B7 sits below all of them as a single convergence point: every mechanism terminal feeds
into it, because coupling is orthogonal to mechanism identity.

---

## S4.3 B0: establishment of the loss terms

**Measurement.** Run a slow (≤C/20) reference cycle and compute d*V*/d*Q*. Decompose the fade into lithium
inventory loss (LLI), loss of active material (LAM), and kinetic polarization.

Why this is step zero and not step one. The decomposition is the only measurement that addresses
question 1 (*which loss term moved*), and every downstream branch is conditioned on it. A tree that began
with a chemistry probe would be guessing at which chemistry to probe. The ≤C/20 rate matters because at
faster rates the kinetic contribution is confounded with the thermodynamic one and the d*V*/d*Q* features
broaden into each other.

**Discriminating outcomes:**
- LLI dominates → **B1**
- LAM dominates → **B3**
- Polarization dominates with little capacity loss → **B5**
- Voltage fade with only modest capacity fade → **B6**

**Confound resolved at this step.** A capacity fade reported as a single number. d*V*/d*Q* separates a peak
shifting (inventory loss) from a peak shrinking (active-material loss), which is the canonical
LLI/LAM split and is invisible in the fade curve. Without this step, “the cell lost 20 % capacity” cannot
be attributed to any mechanism.

**What it cannot do.** It cannot say where Li was lost (SEI vs dead Li vs isolated pocket) nor which
electrode lost active material. Those are B1/B2 and B3/B4 respectively. This limitation is structural, not
a matter of care: d*V*/d*Q* integrates over both electrodes.

---

## S4.4 B1: LLI dominance, M1 versus M2

**Measurement.** High-precision coulometry for the parasitic current, and — if the cell can be destroyed and is
Li-metal — titration gas chromatography (TGC). For sealed Li-ion cells, operando ⁷Li NMR if available;
otherwise electrode-resolved three-electrode reconstruction of the anode overpotential.

**Discriminating outcomes:**
- H₂ yield high (Li⁰ dominates inactive Li) → M2 (dead Li) `[FROM LITERATURE: 10.1038/s41586-019-1481-z]`
- SEI-bound Li⁺ dominates → **M1**
- Anode overpotential grew but cathode did not → M1/M2 on the anode → **B2** to split them
- Cathode overpotential grew → suspect **M3** even though the loss appears as LLI → **B4**

**Confound resolved at this step.** The field's tendency to equate “LLI” with “SEI growth”. TGC's result is
that in Li-metal cells unreacted Li⁰, not SEI-bound Li⁺, dominates inactive lithium, so an LLI-dominant
cell is more likely a dead-lithium cell than an SEI cell. That re-partitions the two most-studied families.
Note that Figure 1 panel (a) draws M1 and M2 as parallel sinks, both feeding the shared overpotential
bus. The TGC result does not make one a downstream product of the other; it changes which of the two is
expected to dominate in a Li-metal cell. The tree is what separates them; the figure does not
pre-judge the split.

The outcome that carries the most diagnostic value. A cathode overpotential rise producing an
LLI-appearing loss is the signature of M3 masquerading as M1: the cathode's impedance growth forces the
anode to a more reducing potential, so the anode plates and loses inventory, and the loss presents on the
LLI axis while its cause is at the other electrode. This is an instance of cross-electrode coupling
argued for here, and it is a trap that a mechanism-by-mechanism analysis walks directly into.

**Confound not resolved at this step.** In a sealed Li-ion cell there is no non-destructive equivalent of TGC, and
high-precision coulometry gives the total parasitic current but not its partition between direct SEI growth
and corrosion of irreversibly plated Li (which becomes SEI). This is the field's principal
diagnostic gap — see S4.11.

---

## S4.5 B2: separation of M1 from M2 at the anode

**Measurement.** First a voltage-relaxation profile (VRP) immediately after charge; then the rest-period CE test.

**Discriminating outcomes, and a trap that must be stated in the figure caption:**
- A voltage plateau during relaxation (mixed potential from Li⁰ stripping) → reversible plating present
  → **M2**
- No plateau → this rules out only reversible plating. It does not rule out dead Li: an
  electrically isolated Li⁰ deposit cannot strip, so it produces no relaxation signal at all. Do not
  assign M1 on a negative VRP.
- Then the rest-period CE test, which distinguishes the irreversible channels: CE improves after rest →
  the cell was plating-limited → **M2** (plated Li partly recovered); CE degrades monotonically across
  rest → **M1** (SEI-limited, no recoverable reservoir); CE approximately invariant to rest → neither
  channel dominates the anodic loss → return to **B4**.

**Confound resolved at this step.** The false inference “no plating signature, therefore SEI.” Dead lithium is
diagnostically silent in the relaxation measurement, so absence of evidence is genuinely not evidence of
absence here. Many mechanism assignments in the literature rest on exactly this invalid inference, and
naming it is one of the tree's specific contributions.

**Residual confound.** These rest-period tests separate reversible from
irreversible loss but still cannot split “irreversibly plated Li that then corroded into SEI” from “direct
SEI growth.“ That requires TGC or ⁷Li NMR. This is the same gap as S4.4's, approached from the other side,
and it is the reason the M1/M2 partition is not conserved over a cell's life.

---

## S4.6 B3: LAM dominance, electrode and structure

**Measurement.** Operando XRD across a full cycle. The lattice-parameter test is conclusive, because it is the
one thing M3 and M4 do not share.

**Discriminating outcomes:**
- Cathode lattice parameters shift irreversibly, or new spinel/rock-salt reflections appear → chemical
  change → M3, not M4 → B4 to confirm dissolution
- Cathode reflections unchanged but capacity lost → **M4** (fracture/isolation) or **M2** (isolated Li
  pockets); separate by the time law below
- Anode staging capacity lost with unchanged lattice → anode LAM (particle isolation, M4-driven)
- Both electrodes retain lattice but capacity is gone → electrically disconnected material → **M4**
  (contact loss) or **M2** (isolated Li pockets)

**Confound resolved at this step.** M3 versus M4 — two mechanisms that both destroy active material and both
look identical in a fade curve. Pure mechanical fracture leaves lattice parameters intact; dissolution and
reconstruction change them (notably the *c*-parameter). One measurement therefore separates them, and it is
an argument that can be stated briefly.

Time-law discriminator, applied before any LAM assignment. Fit the loss as Δ*C* = *a*√*t* + *b*·*t* over a
high-quality aging series:
- *b*/*a* ≈ 0 (square-root growth) → transport-limited interphase growth → **M1**
- measurable *b* term (linear in *area creation rate*, not time) → mechanically driven fresh-surface
  re-formation → **M4**

The ratio *b*/*a* is a direct if crude measure of the mechanical contribution, and it costs nothing beyond a
well-sampled fade curve, which is why it belongs in the tree before any instrument time is spent.

**Two M4 regimes require separation.** A C-rate sweep sees only
*gradient-stress* fracture (rate-dependent). *Coherency-stress* (“electrochemical shock”) fracture is nearly
rate-independent and occurs in phase-separating materials, so it proceeds even in slow cycling and can
mimic a calendar-driven mechanism. Therefore a null result from a C-rate sweep does not rule out M4.
Always pair the rate sweep with a calendar control at matched SOC and temperature.

---

## S4.7 B4: M3 dissolution versus M4 fracture

**Measurement.** ICP-MS on the electrolyte and on the anode digest, read together with B3's lattice test.

**Discriminating outcomes:**
- Significant Mn/Ni/Co detected on the anode or in electrolyte → M3 confirmed (dissolution happened)
- Negligible TM detected, but cracking/expansion seen with lattice intact → **M4**
- TM detected and cracking seen → M3 + M4 coupled; use the stack-pressure differential test: raise
  stack pressure. If lifetime improves with pressure, the M4→M3 arrow is active.
- Then separate dissolution-driven from reconstruction-driven fade: compare single-crystal vs
  polycrystalline of the same composition. M4 largely disappears; if fade persists, the residual is
  **M3 proper**.

**Confound resolved at this step.** “TM was detected” is routinely reported as “dissolution caused the fade.”
**Confirmed dissolution is not confirmed causation** — it proves TM has physically left the cathode, which
is a mass-loss fact, not a mechanistic one. The single-crystal control is what separates the dissolution
channel from the fracture channel that exposes fresh surface for further dissolution.

**Why the M3+M4 pair matters.** The M4→M3 arrow is bidirectional and self-reinforcing:
crack faces are unpassivated oxide, and the lattice-parameter collapse from TM loss feeds more cracking.
That bidirectionality is a loop, and it illustrates why the framework is drawn as arrows rather than as a
pathway.

---

## S4.8 B5: polarization dominance and the resistance location

**Measurement.** EIS with distribution-of-relaxation-times (DRT) deconvolution rather than equivalent-circuit
fitting, because the arcs overlap.

**Discriminating outcomes:**
- High-frequency arc grows → interphase resistance. On the cathode → CEI growth or M3 reconstruction; on
  the anode → M1 SEI growth, or M2 plating onset (operando EIS detects plating down to <0.6 % of graphite
  capacity via a rise in graphite SEI resistance `[FROM LITERATURE: 10.1016/j.xcrp.2021.100589]`)
- Mid-frequency arc grows → charge-transfer limitation (M3 reconstruction, or electrolyte depletion)
- Low-frequency / diffusion tail grows → transport limitation. If it scales with electrode
  thickness/areal capacity independently of chemistry, suspect Loop D rather than M4 — the
  distinguishing test is whether a flooded cell shows the same fade, which a Loop-D-limited cell will not
- Resolve anode vs cathode by three-electrode. Positioning matters: the reference electrode must be
  placed by modeling, not by convenience, or the measured half-cell overpotentials are artefacts.

**Confound resolved at this step.** Equivalent-circuit fitting assigns overlapping arcs arbitrarily, and the
assignment of a specific arc to M1 vs M3 is model-dependent. DRT removes the circuit-topology choice, which
is why it is specified rather than left optional. The second confound resolved is regional: an impedance
rise with no capacity loss is a different object from capacity fade, and the tree separates them at B5
rather than lumping them.

Why the flooded-cell test is the discriminator for Loop D. Loop D is a volumetric budget (S2.6): a
lean cell is salt-starved at ~9× overdraw, a flooded cell has ~15× more inventory. So a fade that
disappears when the cell is flooded is a Loop-D fade, and one that persists is not. This is a
*design-of-experiment* discriminator, not a measurement, which is why Table S1 has no row for it.

---

## S4.9 B6: the voltage-fade branch

**Measurement.** If the symptom is voltage fade with modest capacity fade: operando XRD + ⁷Li MAS-NMR,
looking for tetrahedral-site occupancy change and spinel/rock-salt phase growth.

**Discriminating outcomes:**
- Tetrahedral occupancy change / spinel growth → voltage fade → TL term, not KL
- If voltage fade and capacity fade are decoupled in the data, report that explicitly — it is a result
  about separability, not a measurement failure

**Confound resolved at this step.** Folding voltage fade into the kinetic-loss channel. Voltage fade is a
thermodynamic/potential loss (the fourth accounting channel, TL): the cell stores less energy at the same
capacity and the same impedance. Assigning it to KL would double-count it against the EIS measurement in
B5, which measures a physically distinct resistive loss with a different temperature dependence. Separating
them is what makes the capacity-balance claims well-posed.

**The scope statement this branch carries.** The reported study shows that voltage fade and capacity fade
can be decoupled (a 723.5–769.6 mV midpoint drop after 200 cycles alongside high capacity retention, and a
491 mV shift in one sample) `[FROM LITERATURE: 10.1039/D4SC07037B]`, which is why TL is required for energy while the LLI/LAM/KL triple is
complete *for capacity*. The tree's B6 branch therefore returns *TL*, not KL. The limitation is that TL
sits outside the loop framework: three of the four loops act on the capacity balance, and voltage fade
remains a named open problem rather than something the loops explain.

---

## S4.10 B7: loop identification

This is the branch that distinguishes the tree from a list.

**The problem B7 solves.** Every branch above assigns a mechanism. The Perspective's claim is about
coupling. Two mechanisms can both be present, both be measured, and still be uncoupled — each fading
the cell on its own without either driving the other. Mechanism identity therefore does not imply a loop,
and it would be wrong to infer one. B7 is the test that separates them, and it is required because no
measurement in Table S1 measures coupling directly (S3.5).

**The diagnostic logic.** A single mechanism gives a smooth, monotone fade. A positive-feedback loop gives
an acceleration whose onset moves with the driving variable. So:

1. Locate the acceleration. Compute the local fade-rate derivative d(Δ*C*)/d*N* and find its
   inflection: that cycle is the loop's onset, not the mechanism's onset. This is the same
   departure-from-baseline idea the reduced model uses (S1.5), applied to data rather than a simulation.
2. Perturb one loop-specific driving variable and test whether the knee moves:

| Loop | Perturbation | Expected if the loop is real |
|---|---|---|
| A — plating → dead Li → SEI → η → plating | Raise temperature, or lower C-rate | Knee moves sharply; a purely M3/M4 knee does not |
| B — dissolution → anode poisoning → η → dissolution | Add an HF scavenger, or switch to a coating | Knee moves; an M4 knee does not |
| C — fracture → fresh surface → SEI/dissolution | Raise stack pressure | Moves the M4→M3 leg |
| D — electrolyte depletion / porosity clogging | Flood the cell with extra electrolyte | Only a Loop-D knee responds |

3. Read the outcome. A knee whose onset moves under a loop-specific perturbation is evidence for that
   loop. A knee that does not move under any of the four perturbations is evidence against the loop
   framing for that cell — report it.

Why the negative terminal is marked explicitly. The tree carries its own falsification test. The loops
predict parameter sensitivity of the knee onset, so an insensitive knee is a counterexample, not a null
result. That terminal is what distinguishes a framework from a taxonomy: it hands the reader the experiment
that could refute the claim.

**Quantitative anchor from the reduced model.** S1's ablation gives the expected *sign and magnitude* of
the perturbation effect: severing the Loop-A arrow abolishes the knee entirely rather than delaying it
(coupled departure at cycle 285, severed: none within 6000), and the knee moves monotonically with rate
(2651 → 64 cycles from 0.5C to 2.5C, a factor of 41.4). A real cell that shows no knee displacement under
a 5× rate change is quantitatively inconsistent with a Loop-A knee, though the model's absolute numbers are
illustrative and only the *direction and order of sensitivity* should be used.

**What B7 cannot claim.** The perturbations are not orthogonal in a real cell — raising temperature changes
SEI growth, charge transfer, and dissolution simultaneously; flooding a cell changes pressure as well as
inventory. So a knee that moves does not by itself identify which loop moved it, and a full assignment
needs at least two perturbations with different fingerprints. B7 is a test for *whether coupling is present*,
not a method for *which coupling*, and the distinction is stated explicitly.

---

## S4.11 Residual confounds

These are the places where separability is incomplete. Each is a gray “confounded” terminal in the node
inventory of S4.2.

1. M1 vs M2 in sealed Li-ion cells, the field's principal diagnostic gap. There is no
   non-destructive equivalent of TGC for a commercial cell. High-precision coulometry gives the total
   parasitic current but not its partition between direct SEI growth and the corrosion of irreversibly
   plated Li (which becomes SEI). Note what is available: for Li-metal/anode-free cells TGC gives
   absolute Li⁰ and operando ⁷Li NMR is non-destructive; for graphite/Li-ion cells no method currently
   counts Li⁰ against SEI-Li⁺ without destroying the cell. Voltage relaxation, high-precision CE and
   operando EIS all detect plating, not the *dead-Li fraction*. This is the gap the tree cannot close,
   and it is stated explicitly rather than passed over.
2. M3 vs M1 at the anode interface. Deposited TM changes SEI composition and makes the interphase more
   electronically conductive, so “anode SEI degradation” in a cell that also has a dissolving cathode is
   partly M3. Element-resolved XPS/ICP helps but is surface-only or destructive. This is the same
   failure-mode the TGC result exposes on the Li-metal side, appearing again at the anode of a Li-ion cell.
3. M3 reconstruction vs CEI growth on impedance. Both appear in the same frequency range. Only
   depth-resolved structural probes (STEM-EELS, grazing-incidence XRD) can separate them.
4. M4 vs M2 under pressure, a two-sided confound. Stack pressure simultaneously suppresses cracking and
   changes plating behavior, so a pressure series moves the two in opposite directions. Worse, the sign of
   the M2 pressure effect is itself unresolved: beneficial pressure (75–1200 kPa) `[FROM LITERATURE: 10.1149/2.0091908jes]` is far below the Li yield
   stress, and creep is the plausible but undemonstrated explanation. A pressure series must be interpreted
   with both mechanisms in the model, not as a clean M4 assay. This directly limits B7's Loop-C
   perturbation, and the figure caption should say so.
5. M4's regimes. Gradient-stress fracture is rate-dependent; coherency-stress (“electrochemical
   shock“) fracture is nearly rate-independent. A C-rate sweep is therefore a valid M4 assay only for the
   first regime and will produce a false negative for the second. Always pair it with a calendar control.
6. Voltage fade vs capacity fade — resolvable, and now a stated scope boundary rather than an open
   problem. The two can be decoupled; TL captures the difference for energy. B6 is read as returning
   *TL*, not KL. What remains genuinely open is why the layered→spinel transition and voltage fade are
   not one-to-one: the extent of the transition does not by itself determine the voltage fade.

---

## S4.12 D2: the early-warning branch

Enter here only for a cell that has not yet faded measurably. The tree's main body assumes ≥5 % loss; D2
is what to do before that threshold.

**Actions and outcomes:**
- Track CE at high precision. A sustained CE below roughly 0.9995 is the earliest usable signal. That
  is a screening level, looser than the 99.978 % that S2.4 shows is needed for 1000 cycles
  at 80 % retention; it is set by the instrument's own noise floor and by the number of cycles over which CE
  is averaged, and should be reported as such rather than quoted as a constant. A cell that trips it is
  screened for the full branch; a cell that passes it is not thereby cleared.
- Track voltage relaxation after every charge. A growing plateau precedes measurable capacity loss.
- Track cathode impedance (DRT mid-frequency). M3 raises it before capacity moves.

**Why this branch exists.** The practical claim is that knee onset is a design variable and therefore
partly predictable. A diagnostic tree that operates only after the knee has arrived would concede that
claim. D2 tests whether the logic reaches earlier than the capacity curve; it does so by a modest margin,
using CE and relaxation, not by a wide one.

---

## S4.13 Branch summary

| Branch | Discrimination settled | Confound resolved |
|---|---|---|
| **B0** | Identity of the dominant loss term | A single fade number hiding LLI/LAM/kinetic partitions |
| **B1** | Partition of lost Li between SEI and dead Li | Equating LLI with SEI growth |
| **B2** | Separation of M1 from M2 at the anode | “No relaxation plateau, therefore SEI” (dead Li is diagnostically silent) |
| **B3** | Electrode attribution of LAM, and its structural character | M3 vs M4 — both destroy AM, only one moves the lattice |
| **B4** | Attribution between dissolution and fracture | “TM detected” mistaken for “dissolution caused the fade” |
| **B5** | Location of the dominant resistance | Arbitrary arc assignment from equivalent-circuit fitting; local vs regional loss |
| **B6** | Partition between voltage and capacity loss | Folding thermodynamic voltage fade into kinetic loss (double-counting TL as KL) |
| **B7** | Presence of a *loop* rather than mechanisms alone | Mechanism identity mistaken for coupling |
| **D2** | Detection of onset before the capacity curve moves | Waiting for the capacity curve before acting |

**In one sentence:** the tree proceeds quantity → location → chemistry → coupling, because each step's
confound is invisible to the step before it, and it terminates in a test designed to be able to fail.
