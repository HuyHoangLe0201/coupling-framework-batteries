# Supporting Information

## What this document contains

A lithium-ion cell usually does not fail gradually. It loses capacity slowly for hundreds of cycles and
then turns over and drops. That turnover is the knee. Its position differs from cell to cell and from
protocol to protocol, and it is usually explained as a fast fade. A fast fade, however, cannot produce a
sharp transition on its own. A sharp transition needs a process whose output feeds its own input.

Four such feedback loops are examined in the accompanying Perspective. Each is written as a chain that
returns to its own start:

- Loop A. Plating causes dead lithium, dead lithium carries fresh interphase, fresh interphase raises
  the local overpotential, and the higher overpotential drives more plating. The loop closes when the
  interphase resistance exceeds the plating threshold.
- Loop B. Transition-metal dissolution poisons the anode, which destabilizes the interphase, which
  consumes more lithium inventory and drives further dissolution. Acid generation is autocatalytic, which
  is what closes the loop.
- Loop C. Fracture exposes fresh surface, interphase grows on that surface, the interphase occupies
  pore volume and becomes load-bearing, and the changed local constraint drives further fracture.
- Loop D. Electrolyte depletion raises transport limitation, which concentrates current and raises
  local overpotential, which drives more plating and more interphase, which consumes more electrolyte.

The document addresses whether a knee follows from the loop, how large each coupling is, which measurement identifies which mechanism, and in what order the measurements apply. Each part is tabulated against the corresponding question.

1. S1, whether a knee necessarily follows from Loop A. A two-variable model is built that contains the
   loop, and then the loop is removed. If the knee survives that removal, the mechanism claim is empty. It
   does not survive: the knee disappears rather than moving later, so the knee is a consequence of the
   loop's structure rather than of the fade being fast.
2. S2, how large each coupling is compared with the effect it drives. A coupling is only worth
   modeling if its margin is of order unity. Each loop is reduced to a ratio of two quantities that can
   be estimated independently. Every ratio lands between roughly 1 and 100, which is what makes the
   mechanisms comparable rather than separable, and it is also why none of them can be dropped.
3. S3, which measurement identifies which mechanism. A capacity-fade curve integrates all loss
   mechanisms at once and cannot, by itself, attribute the loss. Twenty established techniques are
   tabulated against the questions that attribution requires. The order in which they should be
   applied is the contribution, not the list.
4. S4, in what order the measurements should be applied to one cell. The tree fixes the order:
   identify the loss term, locate the electrode, assign the mechanism, then perturb the loop and observe
   whether the knee moves. It terminates in a perturbation test, because coupling is the one claim that a
   static measurement cannot settle.

## Contents

| Section | Contents |
|---|---|
| **S1** | The Loop-A model: state variables, cycle-update equations, the plating threshold, the two self-limitation terms, parameters, numerical method, and results (baseline, the ablation, sensitivity sweep, secondary knee criteria), two applications of the framework to published fade curves (303 cells and 19 fitted exponents), and an explicit list of what the model does not claim. |
| Table S1 | Mechanism × measurement matrix: 20 techniques against the three questions, with what each can and cannot separate (in S3). |
| Table S2 | Parameters of the reduced model: 12 parameters with values, units, and provenance. |
| Table S3 | Baseline landmarks, the ablation, and the secondary knee criteria. |
| Table S4 | Sensitivity of the knee to the loop gain: eight values spanning 400×. |
| Table S5 | Operating-condition map: knee cycle count against C-rate and interphase-growth factor, 20 cells. |
| Table S6 | The framework's knee-to-EOL ratio against the published range: 303 cells from 17 studies (in S1.13). |
| **S2** | The derivations behind the four coupling ratios: interphase ohmic drop and its conductivity band; the plating threshold and the thickness it implies; interphase volume and pore filling; Coulombic-efficiency arithmetic and the cycle life it fixes; the Loop-B catalytic shortfall; the Loop-D salt budget; the Loop-C stress margin. Plus the dissolution unit-ambiguity worked example and the voltage-fade separability arithmetic. |
| **S3** | Table S1, a 20-row matrix of measurement against mechanism, giving for each technique what it constrains and what it does not, and which loop it addresses; and a 20-item reporting checklist in three tiers. |
| **S4** | The diagnostic decision tree, branches B0–B7: node inventory, edge semantics, and a walkthrough of each branch naming the confound it resolves. The tree is not a figure; it exists only as this protocol. |

## Conventions

- Status tags. `[DERIVED]` = computed here, arithmetic shown. `[FROM LITERATURE: DOI]` = supplied by
  a published source, DOI given. `[HYPOTHESIS]` = proposed, not established. `[ASSUMED]` = an
  order-of-magnitude figure used as input and not traceable to a specific measurement. No number appears
  without one of these tags.
- Units. Areal quantities in mAh cm⁻², mol cm⁻², µL cm⁻², µm; resistance in Ω cm²; current density in
  mA cm⁻² in the text, but A cm⁻² inside the threshold relation, where the conversion is shown explicitly
  each time; stress in GPa; conductivity in S cm⁻¹.
- Cycle counting. Cycle 0 is the state after formation. All "cycle N" values are post-cycle-N states.
- Knee. Primary definition, used unless stated otherwise: cumulative lithium-inventory loss reaching
  20 % of the initial capacity. Four secondary criteria are also reported, because the 20 % convention is
  arbitrary; the spread is disclosed rather than hidden.
- Precision. A "~" means the input is uncertain by at least a factor of 2. Where three significant
  figures are given, the input is a physical constant and the precision is real; it is the model it enters
  that is coarse.
- Judgement calls are flagged as `[HYPOTHESIS]` or `[ASSUMED]`. A reader should never have to guess
  which numbers are established and which are assumed.

## Symbols and abbreviations

| Term | Meaning |
|---|---|
| CE | Coulombic efficiency, the fraction of charge passed that is recovered on discharge. |
| CEI | Cathode electrolyte interphase. |
| cryo-EM | Cryogenic electron microscopy, used to image beam-sensitive lithium deposits without damaging them. |
| dead lithium | Metallic lithium that has plated but lost electrical contact, so it can no longer be cycled. |
| DEMS | Differential electrochemical mass spectrometry, which measures gas evolved during cycling. |
| DRT | Distribution of relaxation times, a deconvolution of impedance spectra that avoids assigning arcs to a circuit model in advance. |
| EIS | Electrochemical impedance spectroscopy. |
| HPC | High-precision coulometry, the measurement of Coulombic efficiency to a few parts per million. |
| ICP-MS | Inductively coupled plasma mass spectrometry, used to quantify dissolved transition metal. |
| interphase | The general term for a passivating film between an electrode and the electrolyte: the SEI on the anode, the CEI on the cathode. Where a quantity is said to be per unit interphase, the film is treated as a slab of uniform resistivity. |
| knee | The cycle at which capacity begins to fall sharply rather than linearly. Defined operationally in Conventions above. |
| KL | Kinetic loss: the part of capacity fade caused by increasing polarization rather than by lost inventory or active material. |
| LAM | Loss of active material: the electrode can no longer store the lithium it once could. |
| LLI | Loss of lithium inventory: cyclable lithium has been consumed and is no longer available. |
| Loop A–D | The four feedback loops defined in the opening section of this document. |
| M1–M4 | The four mechanisms the loops are built from: M1 interphase growth, M2 dead-lithium formation, M3 transition-metal dissolution and surface reconstruction, M4 particle fracture. |
| MAS-NMR | Magic-angle-spinning nuclear magnetic resonance, used to resolve lithium environments in the bulk. |
| N/P | Negative-to-positive capacity ratio of a cell. |
| pp | Percentage points, the arithmetic difference between two percentages. |
| Q1–Q3 | The three attribution questions of S3.1: which loss term moved (Q1), which electrode is responsible (Q2), which mechanism family is responsible (Q3). |
| R\* | Plating threshold: the interphase resistance at which the anode potential reaches 0 V versus Li/Li⁺ at a given current density. |
| SEI | Solid electrolyte interphase, the passivating film that forms on the anode. |
| SOC | State of charge. |
| SRL | Surface reconstruction layer, the disordered rock-salt surface phase left by transition-metal dissolution. |
| STEM-EELS | Scanning transmission electron microscopy with electron energy-loss spectroscopy, a spatially resolved probe of composition and bonding. |
| TGC | Titration gas chromatography, which measures the metallic lithium fraction of a cell's inactive lithium. |
| TL | Thermodynamic, or potential, loss: the part of energy fade caused by a shift in the cell's voltage curve rather than by capacity loss. |
| VRP | Voltage relaxation profile, measured in the rest period after charge. |
| XRD | X-ray diffraction, used here operando to track lattice parameters during cycling. |

### Mathematical symbols

Greek letters and constants used in S1 and S2, which are otherwise introduced only
at their first equation. Symbols local to one derivation are defined there.

| Symbol | Meaning | First used |
|---|---|---|
| *R*\* | Critical anode area-specific resistance for plating onset, (Δ − η_ct)/*j*. Rate-dependent through *j*; Δ itself is a material property (S1.16). | S1.4, S2.2 |
| *R*_SEI | Area-specific resistance of the anode interphase. | S1.2, S2.1 |
| Δ | Margin between the anode operating potential and 0 V vs Li/Li⁺. | S1.4, S2.2 |
| η_ct | Charge-transfer overpotential at the anode. | S1.4, S2.2 |
| *j* | Local current density, set by nominal capacity and C-rate. | S1.2, S2.2 |
| σ | Ionic conductivity of the interphase, taken as a band of 10⁻⁹–10⁻⁷ S cm⁻¹. | S2.1 |
| *d* | Interphase thickness; *d*\* is the thickness at which *R*_SEI reaches *R*\*. | S2.1, S2.2 |
| *b*_fresh | Loop gain: resistance added per unit of fresh interphase area. The only unanchored parameter. | S1.7 |
| *a*_SEI | Interphase area created per unit of lithium inventory lost. | S1.5 |
| *f*_dead | Fraction of plated lithium that becomes electrically isolated. Measured; 0.094 without FEC. | S1.5 |
| *f* | Inefficiency, 1 − CE, as a fraction of charge per cycle. | S2.4 |
| *Q*₀ | Nominal areal capacity, taken as 3.0 mAh cm⁻². | S2.3 |
| *V*_m | Molar volume of the interphase phase. | S2.3 |
| *E*, ν | Young's modulus and Poisson ratio of the cathode secondary particle. | S2.7 |
| *K*_Ic | Mode-I fracture toughness of the cathode secondary particle. | S2.7 |
| Ω | Partial molar volume of lithium in the host. | S2.7 |
| *c*_LLI | Areal density of lost lithium inventory. | S1.3 |

