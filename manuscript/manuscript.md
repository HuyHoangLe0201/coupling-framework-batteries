# From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries

**Article type:** Perspective

**Keywords:** coupling; degradation; feedback loops; knee; lithium-ion batteries

---

## Abstract

Capacity fade in lithium-based batteries is reported mechanism by mechanism: an interphase study quotes Coulombic efficiency, a fracture study crack density, a cathode study parts-per-million dissolved manganese. Each is rigorous, yet the three cannot be combined into one account of why a given cell failed at a stated cycle. The mechanisms are not additive: dissolution and fracture create fresh surface, feeding interphase growth and plating, which raise the overpotential that drives both. Four feedback loops therefore convert linear fade into a sharp knee, and since each closes on a comparison between an accumulated quantity and an available margin, the knee is a design variable. All capacity loss passes through three channels — loss of lithium inventory (LLI), loss of active material (LAM), kinetic or polarization loss (KL) — and each mechanism leaves a characteristic trajectory, not a magnitude. Applied to 24 published cells between 90% and 100% retention, the prescription returns a positive coupling strength in 22, and the knee moves 2-fold for a 1.3-fold change in the operating margin against a 400-fold change in loop gain. We state six falsifiable predictions, a decision tree that tests whether coupling is present, and a minimum reporting set.

---

## Box 1: Terms used in this Perspective

**Knee.** The cycle at which fade stops being gradual and becomes abrupt. **Interphase.** The nanometer film where electrolyte meets electrode, through which lithium must pass. **Plating.** Lithium deposited as metal instead of entering the anode, which usually shortens life sharply. **LLI, LAM, KL.** Loss of lithium inventory, of active material, kinetic or polarization loss: the three channels through which capacity disappears. **C-rate.** How fast a cell is charged or discharged relative to its capacity; 1 C empties it in one hour. **Margin.** The gap between a loop's operating value and the threshold where it runs away.

---

## 1. Introduction

A cell that has lost 20% of capacity is described by several mechanisms at once: a thickened interphase,<sup>[1]</sup> a reconstructed cathode surface,<sup>[2]</sup> cracked particles.<sup>[3]</sup> Each description is defensible and correctly measured. Together they still do not say why this cell reached that loss at that cycle. The gap is compositional, not experimental.

The gap shows as disagreement. Cells of identical chemistry, same materials and process, reach 80% retention at cycle counts differing by an order of magnitude. Fade is gradual for most of life, then abrupt; the cycle at which it turns is the knee. Were the knee a materials property, identical chemistry would place it identically; it does not.

The mechanisms feed one another: one mechanism's product changes the driving force for another (Figure 1c), so the set is a dynamical system with thresholds, not a list to sum. Each loop closes when the accumulated quantity overtakes the margin available for it: rate, temperature, voltage window, stack pressure, electrolyte volume, and the anode's own headroom above 0 V. These are set by design and use, not universal constants. The knee is therefore a design variable: that is the claim.

Making the claim usable needs what a catalogue lacks: a unit in which every mechanism counts, and a diagram of which acts on which (Figure 1a). That unit is the capacity channel: loss of lithium inventory (LLI), loss of active material (LAM), or kinetic or polarization loss (KL).<sup>[4,5]</sup> The diagram runs through surface and overpotential.

Its absence shows as three reporting failures. Fade is quoted without rate, window, temperature, pressure, or format, so nominally identical results are incomparable.<sup>[6]</sup> Impedance rise is attributed to interphase growth without separating it from other sources, making the attribution unfalsifiable.<sup>[7]</sup> The knee is fitted, not derived.<sup>[8]</sup> Each reports a quantity without its margin.

The claim is testable: it predicts which operating variable moves the knee in a cell (Table 2) and supplies a decision tree separating the loops (§6). A knee failing to move under all four perturbations is evidence against coupling.

Prior work stops at the catalogue. Attia et al. classify knee trajectories, and their "snowball" class is the loop described here in earlier vocabulary, but they treat the knee as a feature to detect, not the output of a coupled system.<sup>[9]</sup> Yu, Zhu and Yu consolidate the cathode-side cascade and close with mitigation, a cathode-limited structure that cannot count inventory the anode destroys.<sup>[10]</sup> What we add is the accounting unit and the failure criterion: inventory across the whole cell, and predictions stating what would refute them.<sup>[11]</sup>

One last observation sets the scale. For every loop the ratio of operating value to threshold falls within two orders of magnitude, ratios of roughly 1 to 100 (SI S2), so no loop is negligible. Cell design has co-optimized several degradation thresholds, placing well-designed cells closest to several margins and making them especially susceptible to coupling-induced knees.

---

## 2. Loss accounting and the trajectory

Capacity is lost through three channels. LLI is lithium that can no longer be cycled: bound in the solid–electrolyte interphase (SEI), trapped in electrically isolated metal, or sequestered in closed porosity. LAM is host that can no longer store lithium: fractured or disconnected particles, phase-transformed material, delaminated composite. KL is capacity that exists thermodynamically but is inaccessible at the applied rate. Each is defined by what is gone, not by the measurement that detects it.<sup>[4]</sup>

The decomposition is complete for capacity: lithium not cycled is present but inaccessible at this rate (KL) or converted to a non-cyclable form (LLI), and an active site either functions or not (LAM). LLI and KL are not orthogonal at finite rate, so a reference rate and temperature must be quoted (§8).

The decomposition is standard and automated,<sup>[5]</sup> and the modes are extracted by fitting open-circuit-voltage curves.<sup>[12]</sup> The claim here is narrower: trajectories are diagnostic. Each mechanism moves the channels in a characteristic order and time law (Table 1), and that ordering discriminates where magnitude cannot. A cathode losing active material moves LAM before LLI; a plating-limited anode moves LLI while LAM stays flat; a cell whose impedance has grown moves KL with little capacity change. Magnitudes reflect history and do not transfer between cells; orderings reflect mechanism and do.

The practical consequence changes what is fitted. With *f* = 1 − CE (Coulombic efficiency), retention obeys *Q*(*N*)/*Q*₀ = 1 − *fN*, so *N*_R = (1 − *R*)/*f*. This is straight only if *f* is constant, so downward curvature measures d*f*/d*N*, the coupling strength. A fitted slope returns an average CE and conceals loop closure;<sup>[13]</sup> fit *f*(*N*) = *f*₀ + α*N* and report α with its window; no new experiment is required.

One limitation applies. The decomposition is complete for capacity, not energy: voltage fade in Mn-rich and Li-rich oxides is a thermodynamic shift of the host potential, decoupled experimentally from capacity fade.<sup>[14]</sup> Reporting energy fade would need a fourth channel, which we name an open problem.

---

## 3. Sources and sinks

The four mechanisms of Figure 1a are not equivalent. Dissolution (M3) and fracture (M4) act as sources: they generate reactive surface, enlarging the area for parasitic reaction.<sup>[15]</sup> Interphase growth (M1) and plating (M2) act as sinks: they consume lithium inventory and electrolyte (Figure 1b).<sup>[16,17]</sup> Sources set gain and sinks the offset. The classification is imperfect: dead lithium is a sink that adds surface, and we retain that hybrid.

Independence has an exact operational meaning, and it fails. Were the four mechanisms independent, the loss with all four running would equal the sum measured one at a time. It does not: a cathode releasing manganese shortens the life of an anode it never touches, and a crack consumes inventory the fracture did not remove.<sup>[18]</sup> Independence is falsifiable and already refuted.

A loop exists only if one mechanism's product is another's input, and only two quantities pass that way: fresh reactive surface, created by dissolution and fracture and consumed by interphase growth and plating, and local overpotential, raised by the sinks and exploited by the sources. The four mechanisms therefore reduce to two state variables, and all four loops run between them (Figure 1c).

The relation between sources and sinks carries more information than any arrow, because sources are not conserved. A little dissolution can be amplified into substantial inventory loss; a little interphase is unlikely to become substantial fracture. That gain asymmetry is a prediction: a cell with only sinks degrades monotonically, since a sink lowers the fade intercept while only a source raises its slope. The margin is the distance from a loop's operating value to the threshold at which it self-sustains, and design sets that distance.

---

## 4. The four loops

Each loop has four elements with an evidence grade: driving force, pathway, observable, and engagement condition. Well supported: mechanism measured, feedback observed in relevant cells. Supported: mechanism measured, feedback inferred. Mechanism supported, feedback untested: ingredients measured, interaction not.

**Loop A. Plating → dead lithium → more interphase → higher local overpotential → more plating.** The driving force is the local anode potential falling below 0 V vs Li/Li⁺. Lithium reduced at the graphite-separator interface is partly isolated on stripping, and the dead metal carries fresh interphase that raises local impedance and pushes the next charge below 0 V.<sup>[19–21]</sup> The observable is superlinear inventory loss with rising hysteresis and an efficiency decline cathode impedance cannot explain. The loop closes when *R*_SEI > *R*\* ≡ (Δ − η_ct)/*j*, where Δ is the margin between the operating anode potential and 0 V, η_ct the charge-transfer overpotential, and *j* the local current density. *R*\* is a ratio of operating quantities, not a fixed number. Evidence grade: well supported.

**Loop B. Dissolution → anode poisoning → interphase destabilization → more inventory loss.** The driving force is thermodynamic instability of the cathode surface: Mn³⁺ disproportionation, HF attack from salt hydrolysis, oxygen loss at high voltage.<sup>[22–24]</sup> Dissolved cations cross the separator, are reduced at the anode, and enter the interphase, while the cathode surface reconstructs to rock salt. The observations move together: oxygen loss, reconstruction-layer growth, rising interfacial impedance, and transition-metal loading on the anode.<sup>[25–26]</sup> That quartet discriminates, since no single-mechanism account predicts all four. Acid generation is autocatalytic and potential-gated, which closes the loop. Dissolution is not stoichiometrically sufficient. At an assumed 5 ppm of the cathode's manganese inventory per cycle, 0.5% leaves over 1000 cycles; even if each departing Mn²⁺ destroyed one Li⁺, that removes 0.27% of the lithium inventory against a ~20% capacity loss — a 74-fold shortfall — so the damage must be catalytic. One estimate puts it at ~10² trapped Li⁺ per deposited Mn ion, the order the arithmetic needs, though it is an estimate whose Mn-free control also changes Ni and Co, and it remains unverified.<sup>[26]</sup> Evidence grade: supported.

**Loop C. Fracture → fresh surface → interphase growth → local stress → more fracture.** The driving force is diffusion-induced stress, ∇*c* → ∇σ, amplified by second-phase stiffness mismatch.<sup>[27–29]</sup> Cracking exposes unpassivated surface that consumes lithium at once; the interphase then fills pore volume, becomes load-bearing, and changes the particle's constraint.<sup>[30–31]</sup> Gradient stress is rate-dependent and fades at slow cycling, so a low-rate sweep appears to exonerate fracture; coherency stress is rate-independent and survives any C-rate. A sweep probes only the first, so a null result at low rate does not test the loop. The observable is active-material loss leading inventory loss, sensitive to stack pressure not voltage window. It closes when interphase-filled pore volume sets the fracture threshold: 1 mAh/cm² of inventory loss makes ~11 µm of dense interphase-equivalent volume, so a 10 µm, 30%-porosity coating fills after 0.3–0.6 mAh/cm² (10–20% of capacity), while the ~77 µm anode matched to a 3 mAh/cm² cathode fills only after ~2 mAh/cm² (68%). Loop C closes early on thin anodes, late on conventional ones. Evidence grade: mechanism supported, timing loading-dependent.

**Loop D. Electrolyte depletion → transport limitation → higher local overpotential → more plating and more interphase.** The driving force is consumption of salt and solvent by the accelerated reactions, plus transference-number polarization.<sup>[32–33]</sup> Transport limitation concentrates current on the electrode nearest the separator; fade scales with thickness, not chemistry. The loop closes when salt consumption outruns diffusion: a lean cell at 1 g Ah⁻¹ holds ~3.3 µmol/cm² of salt against the ~30 µmol/cm² that 0.8 mAh/cm² of inventory loss consumes, an 8.95-fold exceedance. Evidence grade: mechanism supported; feedback untested.

Two loops carry a caveat. Loop A counts its sink as interphase-bound lithium, but titration gas chromatography counts unreacted Li⁰ as H₂; interphase-bound Li⁺ does not react with that reagent.<sup>[13]</sup> In lithium-metal cells unreacted Li⁰, not interphase-bound Li⁺, dominates the inactive lithium, so the field may have mis-partitioned, not mismeasured. Loop B's gain is the open question. The effect is not in doubt: manganese in solution raises parasitic current at graphite.<sup>[12]</sup> Missing is a scaling law for the magnitude, without which no account can say what the loop does to the trajectory. It is decidable: if spiking reproduces under 10% of the observed fade, the loop is unnecessary and the arrow points to cathode impedance.

## 5. The knee as a design variable

A knee is a change in the composition of loss, not merely in slope: the marginal loss shifts toward inventory loss, or the inventory exponent exceeds 1. It is testable on any decomposed curve.

No rate law is discontinuous. Each mechanism's rate is smooth in its own arguments, so a knee requires a system property: gains below a threshold restore the operating point after a perturbation, gains above it do not. Smooth laws therefore give a sharp transition, and a single-exponential fit succeeds locally but fails to predict. Which loop reaches the boundary first is set by operating conditions: high rate and low temperature select Loop A, high voltage and a manganese-rich cathode Loop B, high stack pressure Loop C, thick electrodes and lean electrolyte Loop D. Only Loop A is modeled here, so the assignment for B, C and D is an argument from the mechanism, not a result (SI S1.10). This accounts for identical chemistry showing different fade and for a cycle life quoted without these parameters being unphysical (Figure 1d). Such a transition is published for plating on graphite.<sup>[34]</sup>

A controlled contrast tests it. In a reduced Loop A model (SI), zeroing the feed-forward gain delays the knee from 530 to 670 cycles and capacity loss from 1044 to 1681; zeroing the dead-lithium fraction abolishes it within 6,000 cycles. The response is inelastic: a 400-fold gain change moves the knee about 2.2-fold, as a threshold crossing predicts, since gain sets how fast the margin is consumed, not where the boundary lies. Sweeping the margin separates the two: over a 1.33-fold window, chosen so plating starts after the departure detector's baseline, the knee moves 2.14-fold, so a 300-fold larger gain change buys about the same shift (SI S1.16). The severings are not equivalent: the dead-lithium fraction also removes an inventory sink, so the arrow is not isolated. It holds at 0.5 and 1 C, not 2.0 C. One limit qualifies it: the most influential margin is the least controllable, being set by the anode equilibrium potential, not a process setting.

Two evidence forms answer different questions: the margin sweep tests the mechanism; what follows asks only whether the quantity §2 asks for, α, is obtainable from published data. Harris et al. cycled 24 commercial pouch cells at 10 C and reported retention per cycle.<sup>[35]</sup> Fitting *f*(*N*) = *f*0 + α*N* over 100% to 90% retention gives α > 0 in 22 of 24 cells, median 5.6×10⁻⁷ per cycle. A constant *f* leaves 0.042 RMS in retention, a quadratic 0.008 with negative curvature in all 24; three estimates agree (SI S1.15). The limit is as plain: over 95–100% retention α > 0 in only 6 of 24, since early-cycle noise exceeds the curvature, so α is window-dependent and incomparable across studies that do not fix it. Positive α shows efficiency loss accelerates; it does not say which channel, since retention alone cannot separate LLI from LAM.

The model also fails a test the framework ought to pass. If the knee is an early-warning object, life must remain after it, and the model's knee-to-life ratio does not discriminate against published cells (SI S1.13). Its knee is its end of life under the manuscript's convention, a ratio of 1.00 against a published median of 1.26, with alternative conventions spanning 1.00–1.91. A test whose outcome is set by its own definition has no discriminating power, so we report it as inconclusive. What survives is weaker: fade accelerates after the knee in 13 of 19 cells (SI S1.14). The claim rests on operating-variable dependence, not on this ratio.

## 6. Diagnostic separability

Separability makes the predictions of §7 testable. The decision tree in SI S4 organizes diagnostics by loop, because a loop leaves a curvature signature in time that a mechanism does not, and each branch ends in a failing test.<sup>[36–38]</sup> SI Table S1 indexes each measurement; three confounds remain: interphase-bound and metallic lithium cannot be separated by coulometry alone, since both consume electrons without intercalation;<sup>[39]</sup> fracture-driven and reconstruction-driven loss both register as inactive material, needing post-mortem imaging; and electrolyte depletion and contact loss give superimposable impedance spectra. That last gap is the most restrictive.

## 7. Six falsifiable predictions

Each prediction names a contrast and what would refute it (Table 2).

**P1:** identical chemistry at different stack pressure shows knees at different cycle counts; refuted if they coincide.<sup>[40–41]</sup> **P2:** anode-free and graphite cells at matched inventory-loss rate show different efficiency curvature, since only the metal system closes Loop A; refuted if they coincide.<sup>[42]</sup> **P3:** suppressing dissolution moves the *slope* of inventory loss, not its intercept; refuted if only the intercept moves. **P4:** at fixed total additive mass, electrolyte loading in g Ah⁻¹ predicts life; refuted if life is invariant. The qualifier matters: added electrolyte carries added additive inventory, and irreversible loss grows with electrolyte volume until additive mass is fixed, a confound that could reverse the sign of P4.<sup>[43]</sup> **P5:** single-crystal and polycrystalline material differ in knee sharpness, not initial fade rate; refuted if fade rates differ while knee shape does not.<sup>[44]</sup> P5 tests only the gradient-stress branch. **P6:** within a retention window fixed before fitting and no narrower than 90%, retention is concave in cycle number, which is α > 0 in §2; refuted if a majority of cells are convex over that same window. P6 is the only one testable on data in hand, and §5 reports such a test (SI S1.15). The window clause is not decoration: over 95–100% retention the majority is convex, so the window belongs in the prediction or the test is only adjustable.

P3 needs one clarification, since the measurement already exists. Protocols that titrate dissolved transition metal into graphite measure the parasitic current during potentiostatic holds,<sup>[45]</sup> and they show the amplification occurs. P3 asserts something stricter: that the amplification bends the *slope of the inventory trajectory during cycling*, not only the height of a hold current. A cell can show both and still fail P3.

An unexecutable prediction is not falsifiable. A single mechanism gives monotone fade, a loop acceleration, so the inflection in d(Δ*Q*)/d*N* locates the onset; perturb one loop-specific variable (temperature for A, an HF scavenger for B, stack pressure for C, electrolyte volume for D) and ask whether the knee moves.<sup>[40,42]</sup> An insensitive knee is a counterexample, not a null result.

---

## 8. Outlook

A reporting set is one result that transfers; the checklist is in SI S3.4. Among its twenty items, the nine of Tier 1 are load-bearing: electrode composition and loading, N/P, electrolyte mass, water and HF, format and stack pressure, voltage window, rate and temperature, aging protocol, the fade-quoting cycle, and formation.<sup>[46]</sup> None needs new science; most are already measured. The failure is selective reporting: a reader cannot reconstruct the margin the cell ran against. A mandatory table would make the corpus comparable and allow retrospective loop testing.

The least demanding test is spiking: introduce dissolved transition metal at the flux inferred in §4 and ask whether the parasitic current rises as predicted. The others need local anode-potential mapping, isotope-resolved metal flux, crack-resolved operando tomography, and salt-concentration imaging, all of which exist but none routinely.

Two problems remain open: no non-destructive method partitions metallic from interphase-bound lithium in a sealed cell, and energy fade has no channel. A demonstration that life is invariant to electrolyte loading would remove Loop D and leave three.

Within these limits, failure at a given cycle is a sequence of loop closures, and a design outcome.

---

## Conflict of interest

The authors declare no conflict of interest.

## Data availability statement

This Perspective reports no new experimental data. The derivations behind the framework's own estimates, and the Supporting Information display items, are provided as Supporting Information; figures quoted from the literature are attributed at their point of use. The reduced model is specified in Section S1 in enough detail to be re-implemented. The model implementation, the scripts that regenerate both figures and every table, and the audit scripts that re-derive the order-of-magnitude estimates quoted here are openly available at https://github.com/HuyHoangLe0201/coupling-framework-batteries

## Acknowledgements and funding

This work received no specific funding from any agency in the public, commercial, or not-for-profit sectors.

---

## Figure legends

**Table 1.** First channel to move, and time law, for each mechanism. The ordering discriminates; the magnitude does not.

**Table 2.** Predictions, loops tested, refutation conditions, and data status.

**Figure 1.** Four mechanisms, two state variables, four limiting conditions. Mechanism drawing: no computed curve, no lifetime. **(a)** Locus of each mechanism in a cell section. Dissolution (M3) and fracture (M4) generate reactive surface; interphase growth (M1) and plating (M2) consume lithium inventory and surface. **(b)** Interphase architecture: a dense inorganic sublayer of a few nanometers under a porous organic region of tens of nanometers, leaky, not blocking, so a film thicker than the tunneling limit keeps growing until the pore volume fills. **(c)** Sources feed one surface rail and sinks one overpotential rail, reducing four mechanisms to two. **(d)** Engagement condition of each loop: the gap in each circle is the inequality under which the loop runs away. It marks onset, not termination. Schematic: no scale implied.

---


## References

[1] H. Adenusi, G. A. Chass, S. Passerini, K. V. Tian, and G. Chen, Lithium Batteries and the Solid Electrolyte Interphase (SEI)—Progress and Outlook, *Advanced Energy Materials* **2023**, *13*, 2203307. DOI 10.1002/aenm.202203307.

[2] A. Tornheim, S. Sharifi-Asl, J. C. Garcia, J. Bareño, H. Iddir, R. Shahbazian-Yassar, et al., Effect of electrolyte composition on rock salt surface degradation in NMC cathodes during high-voltage potentiostatic holds, *Nano Energy* **2019**, *55*, 216–225. DOI 10.1016/j.nanoen.2018.10.065.

[3] L. Wheatcroft, A. Bird, J. C. Stallard, R. L. Mitchell, S. G. Booth, A. J. Nedoma, et al., Fracture Testing of Lithium-Ion Battery Cathode Secondary Particles in-situ inside the Scanning Electron Microscope, *Batteries & Supercaps* **2023**, *6*, e202300032. DOI 10.1002/batt.202300032.

[4] C. R. Birkl, M. R. Roberts, E. McTurk, P. G. Bruce, and D. A. Howey, Degradation diagnostics for lithium ion cells, *Journal of Power Sources* **2017**, *341*, 373–386. DOI 10.1016/j.jpowsour.2016.12.011.

[5] F. J. Méndez-Corbacho, D. Nieto-Castro, I. Moreno-Artabe, D. del Olmo, G. Baraldi, and E. Ayerbe, DEST: A Simplified Model and Automated Tool for Loss of Lithium Inventory and Loss of Active Material Estimation in Li-ion Batteries, *ChemElectroChem* **2024**, *11*, e202300830. DOI 10.1002/celc.202300830.

[6] C. Pastor-Fernández, T. F. Yu, W. D. Widanage, and J. Marco, Critical review of non-invasive diagnosis techniques for quantification of degradation modes in lithium-ion batteries, *Renewable and Sustainable Energy Reviews* **2019**, *109*, 138–159. DOI 10.1016/j.rser.2019.03.060.

[7] J. S. Edge, S. O'Kane, R. Prosser, N. D. Kirkaldy, A. N. Patel, A. Hales, et al., Lithium ion battery degradation: what you need to know, *Physical Chemistry Chemical Physics* **2021**, *23*, 8200–8221. DOI 10.1039/d1cp00359c.

[8] W. Diao, S. Saxena, B. Han, and M. Pecht, Algorithm to Determine the Knee Point on Capacity Fade Curves of Lithium-Ion Cells, *Energies* **2019**, *12*, 2910. DOI 10.3390/en12152910.

[9] P. M. Attia, A. Bills, F. Brosa Planella, P. Dechent, G. dos Reis, M. Dubarry, et al., Review—"Knees" in Lithium-Ion Battery Aging Trajectories, *Journal of The Electrochemical Society* **2022**, *169*, 060517. DOI 10.1149/1945-7111/ac6d13.

[10] Y. Yu, W. Zhu, and R. Yu, Degradation Cascade in Ultrahigh-Ni Layered Cathodes: Mechanistic Origins and Multiscale Mitigation Strategies, *Batteries & Supercaps* **2026**, *9*, e70365. DOI 10.1002/batt.70365.

[11] T. Raj, A. A. Wang, C. W. Monroe, and D. A. Howey, Investigation of Path-Dependent Degradation in Lithium-Ion Batteries, *Batteries & Supercaps* **2020**, *3*, 1377–1385. DOI 10.1002/batt.202000160.

[12] M. Dubarry, C. Truchot, and B. Y. Liaw, Synthesize battery degradation modes via a diagnostic and prognostic model, *Journal of Power Sources* **2012**, *219*, 204–216. DOI 10.1016/j.jpowsour.2012.07.016.

[13] A. J. Smith, J. C. Burns, S. Trussler, and J. R. Dahn, Precision Measurements of the Coulombic Efficiency of Lithium-Ion Batteries and of Electrode Materials for Lithium-Ion Batteries, *Journal of The Electrochemical Society* **2010**, *157*, A196. DOI 10.1149/1.3268129.

[14] Q. Pang, M. Zhang, Y. Song, Y. Liu, M. Tang, S. Su, et al., Resolving the relationship between capacity/voltage decay and the phase transition by accelerating the layered to spinel transition, *Chemical Science* **2025**, *16*, 4237–4244. DOI 10.1039/d4sc07037b.

[15] F. Single, A. Latz, and B. Horstmann, Identifying the Mechanism of Continued Growth of the Solid–Electrolyte Interphase, *ChemSusChem* **2018**, *11*, 1950–1955. DOI 10.1002/cssc.201800077.

[16] M. Nojabaee, D. Kopljar, N. Wagner, and K. A. Friedrich, Understanding the Nature of Solid-Electrolyte Interphase on Lithium Metal in Liquid Electrolytes: A Review on Growth, Properties, and Application-Related Challenges, *Batteries & Supercaps* **2021**, *4*, 909–922. DOI 10.1002/batt.202000258.

[17] D. E. Brown, E. J. McShane, Z. M. Konz, K. B. Knudsen, and B. D. McCloskey, Detecting onset of lithium plating during fast charging of Li-ion batteries using operando electrochemical impedance spectroscopy, *Cell Reports Physical Science* **2021**, *2*, 100589. DOI 10.1016/j.xcrp.2021.100589.

[18] D. A. Santos, S. Rezaei, D. Zhang, Y. Luo, B. Lin, A. R. Balakrishna, et al., Chemistry–mechanics–geometry coupling in positive electrode materials: a scale-bridging perspective for mitigating degradation in lithium-ion batteries through materials design, *Chemical Science* **2023**, *14*, 458–484. DOI 10.1039/d2sc04157j.

[19] Y.-C. Hsieh, M. Leißing, S. Nowak, B.-J. Hwang, M. Winter, and G. Brunklaus, Quantification of Dead Lithium via In Situ Nuclear Magnetic Resonance Spectroscopy, *Cell Reports Physical Science* **2020**, *1*, 100139. DOI 10.1016/j.xcrp.2020.100139.

[20] R. A. Vilá, W. Huang, and Y. Cui, Nickel Impurities in the Solid-Electrolyte Interphase of Lithium-Metal Anodes Revealed by Cryogenic Electron Microscopy, *Cell Reports Physical Science* **2020**, *1*, 100188. DOI 10.1016/j.xcrp.2020.100188.

[21] J. Betz, J.-P. Brinkmann, R. Nölle, C. Lürenbaum, M. Kolek, M. C. Stan, et al., Cross Talk between Transition Metal Cathode and Li Metal Anode: Unraveling Its Influence on the Deposition/Dissolution Behavior and Morphology of Lithium, *Advanced Energy Materials* **2019**, *9*, 1900574. DOI 10.1002/aenm.201900574.

[22] Y. Tesfamhret, H. Liu, E. J. Berg, and R. Younesi, The role of ethylene carbonate (EC) and tetramethylene sulfone (SL) in the dissolution of transition metals from lithium-ion cathodes, *RSC Advances* **2023**, *13*, 20520–20529. DOI 10.1039/d3ra02535g.

[23] S. Sharifi-Asl, J. Lu, K. Amine, and R. Shahbazian-Yassar, Oxygen Release Degradation in Li-Ion Battery Cathode Materials: Mechanisms and Mitigating Approaches, *Advanced Energy Materials* **2019**, *9*, 1900551. DOI 10.1002/aenm.201900551.

[24] D. Huang, C. Engtrakul, S. Nanayakkara, D. W. Mulder, S.-D. Han, M. Zhou, et al., Understanding Degradation at the Lithium-Ion Battery Cathode/Electrolyte Interface: Connecting Transition-Metal Dissolution Mechanisms to Electrolyte Composition, *ACS Applied Materials & Interfaces* **2021**, *13*, 11930–11939. DOI 10.1021/acsami.0c22235.

[25] A. Tornheim, Q. Zhu, Q. Liu, D. P. Abraham, and J. R. Croy, Quantifying SEI Reaction Rate in the Presence and Absence of Mn2+, *Journal of The Electrochemical Society* **2026**, *173*, 040510. DOI 10.1149/1945-7111/ae4540.

[26] J. A. Gilbert, I. A. Shkrob, and D. P. Abraham, Transition Metal Dissolution, Ion Migration, Electrocatalytic Reduction and Capacity Loss in Lithium-Ion Full Cells, *Journal of The Electrochemical Society* **2017**, *164*, A389–A399. DOI 10.1149/2.1111702jes.

[27] W. H. Woodford, Y.-M. Chiang, and W. C. Carter, "Electrochemical Shock" of Intercalation Electrodes: A Fracture Mechanics Analysis, *Journal of The Electrochemical Society* **2010**, *157*, A1052. DOI 10.1149/1.3464773.

[28] S. S. Pandurangi, D. S. Hall, C. P. Grey, V. S. Deshpande, and N. A. Fleck, Chemo-Mechanical Analysis of Lithiation/Delithiation of Ni-rich Single Crystals, *Journal of The Electrochemical Society* **2023**, *170*, 050531. DOI 10.1149/1945-7111/acd47e.

[29] R. D. Deshpande and D. M. Bernardi, Modeling Solid-Electrolyte Interphase (SEI) Fracture: Coupled Mechanical/Chemical Degradation of the Lithium Ion Battery, *Journal of The Electrochemical Society* **2017**, *164*, A461–A474. DOI 10.1149/2.0841702jes.

[30] W. Ai, B. Wu, and E. Martínez-Pañeda, A coupled phase field formulation for modelling fatigue cracking in lithium-ion battery electrode particles, *Journal of Power Sources* **2022**, *544*, 231805. DOI 10.1016/j.jpowsour.2022.231805.

[31] S. Carelli and W. G. Bessler, Coupling Lithium Plating with SEI Formation in a Pseudo-3D Model: A Comprehensive Approach to Describe Aging in Lithium-Ion Cells, *Journal of The Electrochemical Society* **2022**, *169*, 050539. DOI 10.1149/1945-7111/ac716a.

[32] Z. Li, C.-X. Zhao, Y. Niu, D. Dong, T. Wang, Y. Li, et al., Unlocking cycle life of lithium metal batteries, *Science* **2026**, *393*, eaee1630. DOI 10.1126/science.aee1630.

[33] C. Fang, J. Li, M. Zhang, Y. Zhang, F. Yang, J. Z. Lee, et al., Quantifying inactive lithium in lithium metal batteries, *Nature* **2019**, *572*, 511–515. DOI 10.1038/s41586-019-1481-z.

[34] A. Klein, M. Sadd, N. Mozhzhukhina, M. Olsson, L. Broche, S. Xiong, et al., Identifying the Role of Electrolyte Additives for Lithium Plating on Graphite Electrode by Operando X-ray Tomography, *Batteries & Supercaps* **2024**, *7*, e202400070. DOI 10.1002/batt.202400070.

[35] S. J. Harris, D. J. Harris, and C. Li, Failure statistics for commercial lithium ion batteries: A study of 24 pouch cells, *Journal of Power Sources* **2017**, *342*, 589–597. DOI 10.1016/j.jpowsour.2016.12.083.

[36] R. Prosser, G. Offer, and Y. Patel, Lithium-Ion Diagnostics: The First Quantitative In-Operando Technique for Diagnosing Lithium Ion Battery Degradation Modes under Load with Realistic Thermal Boundary Conditions, *Journal of The Electrochemical Society* **2021**, *168*, 030532. DOI 10.1149/1945-7111/abed28.

[37] N. Costa, L. Sánchez, D. Anseán, and M. Dubarry, Li-ion battery degradation modes diagnosis via Convolutional Neural Networks, *Journal of Energy Storage* **2022**, *55*, 105558. DOI 10.1016/j.est.2022.105558.

[38] A. B. Gunnarsdóttir, C. V. Amanchukwu, S. Menkin, and C. P. Grey, Noninvasive In Situ NMR Study of "Dead Lithium" Formation and Lithium Corrosion in Full-Cell Lithium Metal Batteries, *Journal of the American Chemical Society* **2020**, *142*, 20814–20827. DOI 10.1021/jacs.0c10258.

[39] E. J. McShane, A. M. Colclasure, D. E. Brown, Z. M. Konz, K. Smith, and B. D. McCloskey, Quantification of Inactive Lithium and Solid–Electrolyte Interphase Species on Graphite Electrodes after Fast Charging, *ACS Energy Letters* **2020**, *5*, 2045–2051. DOI 10.1021/acsenergylett.0c00859.

[40] H. Wang, R. Wang, C. A. O'Keefe, E. Björklund, D. Proprentner, J. C. Stallard, et al., The interplay between stack pressure, mechanical expansion and degradation pathways in lithium-ion batteries, *Nature Energy* **2026**, *11*, 1032–1042. DOI 10.1038/s41560-026-02087-6.

[41] A. Barai, R. Tangirala, K. Uddin, J. Chevalier, Y. Guo, A. McGordon, et al., The effect of external compressive loads on the cycle lifetime of lithium-ion pouch cells, *Journal of Energy Storage* **2017**, *13*, 211–219. DOI 10.1016/j.est.2017.07.021.

[42] A. J. Louli, M. Genovese, R. Weber, S. G. Hames, E. R. Logan, and J. R. Dahn, Exploring the Impact of Mechanical Pressure on the Performance of Anode-Free Lithium Metal Cells, *Journal of The Electrochemical Society* **2019**, *166*, A1291–A1299. DOI 10.1149/2.0091908jes.

[43] C.-T. Lechtenfeld, J. Buchmann, J. Hagemeister, M. M. Bela, S. van Wickeren, S. Stock, et al., Analyzing the Effect of Electrolyte Quantity on the Aging of Lithium-Ion Batteries, *Advanced Science* **2024**, *11*, e2405897. DOI 10.1002/advs.202405897.

[44] L. Wheatcroft, A. Bird, N. Gollapally, S. G. Booth, S. A. Cussen, and B. J. Inkson, In Situ Fracture Behavior of Single Crystal LiNi0.8Mn0.1Co0.1O2 (NMC811), *Batteries & Supercaps* **2024**, *7*, e202400077. DOI 10.1002/batt.202400077.

[45] V. Meunier, M. L. De Souza, M. Morcrette, and A. Grimaud, Electrochemical Protocols to Assess the Effects of Dissolved Transition Metal in Graphite/LiNiO2 Cells Performance, *Journal of The Electrochemical Society* **2022**, *169*, 070506. DOI 10.1149/1945-7111/ac7e7a.

[46] P. Dechent, S. Greenbank, F. Hildenbrand, S. Jbabdi, D. U. Sauer, and D. A. Howey, Estimation of Li-Ion Degradation Test Sample Sizes Required to Understand Cell-to-Cell Variability, *Batteries & Supercaps* **2021**, *4*, 1821–1829. DOI 10.1002/batt.202100148.
