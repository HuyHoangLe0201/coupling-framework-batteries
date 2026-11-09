# S1. The reduced Loop-A model: equations, parameters, ablation, and limits

## S1.1 Scope of the model

Loop A is a verbal argument: plating creates dead lithium, dead lithium carries fresh interphase, fresh
interphase raises the local overpotential, and the higher overpotential drives more plating. Read as a
sentence, it is plausible. Read as a mechanism, it makes a much stronger claim that a sentence cannot
settle: that a capacity knee follows necessarily from the loop, and that the knee is therefore a
property of the loop's structure rather than a symptom of the fade being fast.

Those two readings make different predictions, and only one of them can be tested. If the knee is merely
what a fast fade looks like, then any cell that fades fast enough will show one, and removing the loop
should at most move the knee later. If the knee is a threshold crossing inside the loop, then removing the
loop should remove the knee, not delay it. This section builds the smallest model that contains the loop,
runs it, and then removes the loop.

The model is a scaling argument, not a battery model. It is built to make that comparison possible,
including the possibility that the answer is no.

The formulation has three properties that constrain the numbers in this section.

1. Nothing is fitted to a dataset. No parameter was obtained by regression against measured capacity
   fade. Two parameters are taken from measurement (*f*_dead, via the cited DOI) and one is anchored to
   bulk transport (`a_SEI`); the rest are order-of-magnitude placeholders chosen to be physically
   defensible. They are labelled individually in Table S2.
2. No absolute number here is a prediction of any real cell's cycle life. The numbers that are
   load-bearing are comparative and structural: the knee exists in the coupled case and does not exist in
   the severed case; the pre-knee fade is approximately linear and the post-knee fade is superlinear; the
   knee onset moves monotonically with operating condition. These four statements survive the parameter
   choices, and Table S4 (the 400× sweep) is the evidence that they do.
3. The model represents Loop A only. Loops B, C, and D are not represented; the corresponding parts of
   Figure 1 panel (a) are qualitative. Loop D in particular is absent from the reduced model: no
   electrolyte inventory, no salt transport, so nothing here bears on it. The model also has no spatial
   dimension, no porosity field and no electrode thickness, so it cannot in principle support Loop D.
   Section S1.10 states this and the other limitations explicitly.

---

## S1.2 State variables

A model of a feedback loop has to carry, at minimum, the quantity that drives the loop and the quantity
that the loop consumes. Here the driver is the anode interphase resistance, because that is what pushes
the anode potential toward the plating threshold, and what the loop consumes is cyclable lithium. The
model therefore tracks exactly two state variables per unit electrode area.

If the loss channels were independent, the natural model would carry one variable
per mechanism and sum them. Carrying two coupled variables instead is the modeling statement that they
are not independent, and it is the assumption the ablation in S1.5 is designed to test.

| Symbol | Meaning | Unit | Physical interpretation |
|---|---|---|---|
| *R* | anode interphase area-specific ionic resistance | Ω·cm² | lumped resistance of the SEI plus any in-series interphase on the anode; the quantity that pushes the anode potential toward 0 V vs Li/Li⁺ at fixed current |
| *LLI* | cumulative lost lithium inventory | mAh·cm⁻² | charge that can no longer be cycled; the capacity-loss channel the model resolves |

Two derived quantities are tracked but are not state variables: the plating fraction *f*(*n*) (a
diagnostic of how far into the loop the cell is) and the dead-lithium accumulation (the portion of
plated Li that becomes electrically isolated). Neither feeds back except through *R* and *LLI*.

**Choice of state variables: *R* and *LLI*, rather than *R* and capacity.** Capacity loss would fold the LLI channel together
with any loss of active material, and the model has no LAM. Keeping *LLI* explicit means the model's
output is directly comparable to the *LLI* axis of the energy balance, which is the only axis it is
entitled to address.

---

## S1.3 Update equations

Discrete cycle update, applied once per cycle. The index *n* ≥ 1 runs over cycles; cycle 0 is the
post-formation state. `i` is used below for the same index inside the summation term.

Current density is set by the nominal capacity and the C-rate, and is constant during a test:

$$j = \frac{c_{\text{rate}}\,Q_0}{1000}\quad[\text{A cm}^{-2}] \tag{S1.E1}$$

with *Q*₀ in mAh cm⁻², so that *c*_rate = 1 gives *j* = 3.0 mA cm⁻². This point is easy to get wrong and
materially so: if *j* is allowed to fall as capacity falls, the feedback is throttled for a spurious
reason and a spurious knee appears. Current density is therefore held at the nominal value for the whole
test.

**Excess anode overpotential.** The anode is driven toward 0 V vs Li/Li⁺ by the ohmic drop across the
interphase. The quantity that matters is the margin left over after the charge-transfer overpotential:

$$\eta(n) = j\,R(n-1) + \eta_{\text{ct}} - \Delta \quad[\text{V}] \tag{S1.E2}$$

where Δ is the operating margin between the anode's equilibrium potential and 0 V vs Li/Li⁺, and
*η*_ct the charge-transfer overpotential at the operating rate. Plating begins when *η* > 0.

**Plating fraction.** Plating turns on smoothly rather than as a step, because a real electrode has a
distribution of local *R* across its area, so different patches cross the threshold at different times:

$$f(n) = \begin{cases} f_{\max}\left[1-\exp\left(-k_{\text{pl}}\,\eta(n)\right)\right] & \eta(n) > 0\\[2pt] 0 & \eta(n) \le 0\end{cases} \tag{S1.E3}$$

*f* is the fraction of the applied charge that goes to Li(0) rather than to intercalation. The
saturating form is the first self-limitation term: mass balance guarantees *f* ≤ *f*_max < 1, so
plating can never consume more charge than is passed. This is the structural fix for that failure mode,
and it is why the model has a finite end of life rather than a numerical divergence.

**Plated charge.**

$$p_{\text{plate}}(n) = f(n)\,Q_{\text{applied}},\qquad Q_{\text{applied}} = c_{\text{rate}}Q_0 \quad[\text{mAh cm}^{-2}] \tag{S1.E4}$$

**Dead-lithium increment.** A measured fraction of plated lithium becomes electrically isolated:

$$d_{\text{dead}}(n) = f_{\text{dead}}\,p_{\text{plate}}(n) \tag{S1.E5}$$

**Interphase resistance growth.** Two contributions, plus pore-filling saturation:

$$R(n) = R(n-1) + \left[\frac{a_{\text{SEI}}}{\sqrt{n}}\,T_{\text{factor}} + b_{\text{fresh}}\,d_{\text{dead}}(n)\right]\cdot h(n) \tag{S1.E6}$$

$$h(n) = \max\!\left(0,\;1-\frac{R(n-1)-R_0}{R_{\text{cap}}}\right) \tag{S1.E7}$$

The first term in brackets is the diffusion-limited baseline: interphase thickness grows as √*t*, so its
resistance grows as √*n*. It is present whether or not the loop is active, and it is the reason the
severed control cell still fades. The second term is the loop-closing arrow: fresh, unpassivated
interphase forms on each cycle's newly created dead-lithium surface, and *more dead Li* therefore means
*more interphase*, which means *higher R*, which means *more plating* next cycle. The coefficient
*b*_fresh is the loop gain. *h*(*n*) is the second self-limitation term: as the anode pore volume
fills with interphase, further growth is geometrically blocked, so *R* asymptotes to *R*₀ + *R*_cap.
Without *h* the loop would be unbounded even with *f* ≤ *f*_max, because *R* could still grow without
limit.

*T*_factor is an Arrhenius proxy that multiplies the SEI-growth prefactor; *T*_factor = 2 corresponds to
roughly +20 K. It is a crude lumping, used only to generate the sensitivity map in Table S4.

**Loss inventory.**

$$LLI(n) = LLI(n-1) + c_{LLI}\,\Delta R(n) + d_{\text{dead}}(n) \tag{S1.E8}$$

with Δ*R*(*n*) = *R*(*n*) − *R*(*n*−1). Two contributions to lost inventory: charge consumed in growing
the interphase (*c*_LLI per Ω·cm² of new interphase) and charge stranded as dead lithium. Note that
*c*_LLI·Δ*R* is charged on the whole resistance increment, including the √*n* baseline term, so even
the severed cell loses inventory, which is required for the ablation in S1.5 to be a fair test.

**End of life.** The cell is dead when LLI reaches *Q*₀. LLI is clipped at *Q*₀ because capacity cannot
be negative; the model stops at that cycle. Onset of the knee is a separate, earlier event, defined in
S1.6.

---

## S1.4 The plating threshold, R\*

The state equations say that plating begins once the excess overpotential turns positive. That condition
can be rearranged into a threshold on the interphase resistance, and the rearrangement is worth doing
because it separates what the cell's chemistry controls from what the operator controls. Plating begins
when *η* > 0 in (S1.E2):

$$\boxed{\;R > R^{*} \equiv \frac{\Delta - \eta_{\text{ct}}}{j}\;}\tag{S1.E9}$$

This is the single inequality on which the threshold interpretation of the knee rests. It is
worth being precise about what it does and does not depend on. *R*\* is a function of *j* (rate, hence
also of temperature through the kinetics) and Δ (operating SOC window, and weakly temperature through the
equilibrium potential). *R*\* is not itself a tabulated property value like a diffusion coefficient or a modulus -- it is
assembled from rate and margin -- and that is the formal content of calling knee onset a design
variable. But Δ is a material property (S1.16): for graphite it is the 0.08-0.10 V stage-1 plateau
relative to 0 V vs Li/Li⁺, so the margin is only as adjustable as the anode chemistry permits. The precision matters, because one input is only partly an
operating choice. Δ is the anode's headroom above 0 V, and that headroom is set by the anode's
equilibrium potential, which is a material property: about 0.08-0.10 V for the stage-1 plateau of
graphite (S1.16). A cell chemist can therefore raise *R*\* by cycling higher in the SOC window, by
lowering the rate, or by changing the anode material itself. The last is the most effective and the
least available, since it means a different cell chemistry and not a tuning of the existing one. A
material that delays the knee without moving Δ does so by keeping *R*(*n*) below *R*\*, which is a
different and slower lever.

With the reference parameters, at 1C: *j* = 3.0 mA cm⁻² = 0.0030 A cm⁻², so

$$R^{*} = \frac{0.090 - 0.030}{0.0030} = 20.0\ \Omega\,\text{cm}^{2}$$

The fresh cell starts at *R*₀ = 8.0 Ω·cm², i.e. at 40 % of the threshold, with 12 Ω·cm² of headroom.
The cell does not plate at cycle 1; it plates when the slow √*n* baseline plus the loop term carry *R*
past 20 Ω·cm². Under the reference parameters that happens at cycle 220 (first cycle with
*f* > 10⁻⁵), which is well before the capacity knee at cycle 530, an important ordering that
reproduces the qualitative observation that plating is detectable long before the capacity curve turns
over.

*R*\* scales inversely with rate (this table is inline here rather than in the S1.11 table block,
because it is read as part of the threshold argument):

| C-rate | *j* (mA cm⁻²) | *R*\* (Ω·cm²) | *R*\*/*R*₀ | knee (cycle) | EOL (cycle) |
|---|---|---|---|---|---|
| 0.5 | 1.500 | 40.00 | 5.00 | 2651 | 4570 |
| 1.0 | 3.000 | 20.00 | 2.50 | 530 | 1044 |
| 1.5 | 4.500 | 13.33 | 1.67 | 204 | 483 |
| 2.0 | 6.000 | 10.00 | 1.25 | 104 | 296 |
| 2.5 | 7.500 | 8.00 | 1.00 | 64 | 210 |

The last row is the limiting case: at 2.5C the threshold *equals the fresh-cell resistance*, so
*R*\*/*R*₀ = 1 and the cell is at the plating condition from cycle 1. The model then has no delay to
absorb, and the knee arrives at cycle 64. This illustrates the rate dependence.

A limitation of this table must be read with it. The departure detector of S1.5 fits the
early power law over cycles 30-200, which it can only do if plating has not begun inside that window.
At 1C plating starts at cycle 220, so the fit is genuinely pre-loop. At 1.5C, 2.0C and 2.5C plating
starts at cycles 47, 10 and 2 respectively, all inside the window, so for those three rows the fitted
baseline already contains loop feedback and the reported knee is a property of the detector's
calibration rather than a clean measurement. The R* column is unaffected, since it is arithmetic;
the knee and EOL columns for 1.5-2.5C should be read as model output, not as detectable knees. This
is the same contamination rule that governs the margin sweep in S1.16, where only delta = 0.090-0.120 V
survives.

A caveat that belongs next to (S1.E9). *R*\* uses a single lumped Δ and a single lumped *R*, so it is
an electrode-average statement. A real electrode has a potential distribution across its area, and
local *R* can exceed *R*\* in some patches long before the average does. The threshold therefore predicts
*onset of detectable plating*, not *first plating event*, the two differ by the width of the
distribution, which the model does not contain. No stronger claim is supported.

---

## S1.5 Ablation: severance of the coupling

This is the load-bearing test: if the knee survives severing the coupling, the mechanism claim is
empty. The ablation is constructed so that it could show that.

**Severing method.** Two terms in (S1.E6) and (S1.E5) carry the loop: the *b*_fresh arrow and the
*f*_dead fraction. Severing both (*b*_fresh = 0 and *f*_dead = 0) leaves a cell with identical
√*n* interphase growth but no feedback from plated lithium back into resistance. The cell still fades —
the √*n* term is untouched, so the comparison is against a fading control.

**Departure detection.** A knee is detected as a *departure from the cell's own early power law* rather
than as an absolute capacity. The early fade is fitted to *LLI* = *A*·*n*^p over cycles 30–200 (before the
first plating event at cycle 220 in the coupled case, so the fit window is genuinely pre-loop), and the
departure point is the first cycle after 200 at which LLI exceeds the extrapolated baseline by more than
10 %. The criterion is conservative in two ways: it requires the cell to exceed its own trend rather than
a fixed threshold, and it requires a 10 % excess rather than any excess.

| Quantity | Coupled | Severed |
|---|---|---|
| Early power-law fit (cycles 30–200) | *LLI* = 7.268 × 10⁻³ · *n*^{0.522} | identical |
| First plating (cycle) | 220 | 220 |
| Departure from early power law | cycle 285 | **none (to *n*_max)** |
| Knee, LLI ≥ 20 % *Q*₀ | cycle 530 | none |
| End of life, LLI = *Q*₀ | cycle 1044 | not reached by 6000 |
| *R* at end of run (Ω·cm²) | 75.1 | 60.5 |
| Terminal LLI (mAh cm⁻²) | 3.00 (clipped at *Q*₀) | 0.525 |

The severed cell reaches 6000 cycles at 82.5 % of *Q*₀ retained, and at the coupled cell's EOL cycle
(1044) it still retains 91.6 %. It has faded to 17.5 % loss over 5.7 times the coupled cell's life, and
it never leaves its early power law.

**The distinction that matters.** Severing the coupling does not merely delay the knee — it removes it.
The two curves are identical to cycle 200 by construction, so the difference is not a difference in fade
rate; it is a difference in *whether a departure ever occurs*. That is why the result bears on the
thesis rather than on the parameters: the knee and the fade rate are shown to be independent
axes, and the knee is a consequence of the loop's coupling structure, not of the fade being fast.

**Which term carries the loop.** A natural objection is that the ablation removes more than one factor at
once and therefore does not identify the mechanism. Table S3 part B separates them:

| Variant | Setting | Departure | Knee | EOL |
|---|---|---|---|---|
| Coupled | reference | 285 | 530 | 1044 |
| Feed-forward arrow severed | `b_fresh = 0` | 300 | 670 | 1681 |
| Dead-lithium fraction severed | `f_dead = 0` | none | none | 6000 |
| Fully severed | both zero | none | none | 6000 |

The result is asymmetric, and the asymmetry is informative, but it does not by itself separate the two couplings, because the two severing operations are not equivalent in scope.
Removing the dead-lithium fraction alone, `f_dead = 0`, abolishes the knee outright and gives a run
identical to the fully severed case. Removing the feed-forward arrow alone, `b_fresh = 0`, only delays the
knee, from 530 to 670 cycles.

The reason is structural rather than numerical. Setting `f_dead = 0` sends `d_dead = 0` in (S1.E5), which
removes both terms at once: the resistance contribution `b_fresh·d_dead` in (S1.E6) and the stranded-inventory
contribution in (S1.E8). The cell is then not a loop at all, which is why it matches the fully severed case
exactly. Setting `b_fresh = 0` leaves dead lithium forming and stranding inventory, so the fade continues
and the knee merely arrives later.

The loop therefore requires a nonzero dead-lithium fraction, and the feed-forward arrow sets when the knee
arrives rather than whether it exists. The claim is weaker than an identification: `f_dead` is necessary
for the loop, and `b_fresh` is a gain on one of its arrows. This is the structurally correct answer: *f*_dead is the
property that makes the coupling a loop, while *b*_fresh is a gain on one of its arrows. It also identifies
the measurement that would falsify the model. Anything showing that the fraction of plated lithium
becoming electrically isolated is negligibly small would break the loop, whereas a revision of the
interphase resistance per unit dead lithium would only move the knee in time.

**Robustness across *b*_fresh (claim C2 below).** The severing test is repeated at *b*_fresh = 10, 30, 60,
100 and 200: the coupled departure ranges 254–294 cycles and the severed case shows no departure at any
value. The ablation result is not an artefact of the reference parameter choice.

**Robustness across rate.** The severing test also runs at 0.5C and 2.0C. At 0.5C the coupled departure
is 2380 and the severed departure is none. At 2.0C neither case departs: the coupled cell reaches
its 20 %-LLI knee at cycle 104 before the pre-loop baseline fit can be established, so the departure
detector correctly declines to make a claim. That row is reported as invalid rather than omitted,
because a detector returning “none” for both cases should also be shown to return “some” for one of
them, and the 0.5C and 1.0C rows do.

---

## S1.6 Secondary knee definitions

The 20 %-of-*Q*₀ definition of the knee is arbitrary, and the model's conclusion would be weaker
than it looks if the knee existed only under that convention. Four independent secondary criteria were
therefore computed on the coupled baseline, alongside the primary:

| Criterion | Definition | Knee (cycle) |
|---|---|---|
| Cumulative LLI | LLI ≥ 0.20 *Q*₀ (primary, used throughout) | 530 |
| Second derivative, LLI | cycle of maximum d²(LLI)/d*n*² over the run | 470 |
| Retention curvature | cycle of maximum curvature of retained capacity vs *n* | 470 |
| Kneedle chord method | maximum distance from the chord joining first and last point | 479 |
| Local-exponent acceleration | cycle of fastest growth in local d log(LLI)/d log *n* | 278 |

Three of the geometric criteria cluster at 470–530; the local-exponent criterion fires earlier, at 278,
which is close to the departure point at 285, and that agreement is informative rather than
contradictory: the local-exponent method detects *when acceleration begins*, while the others detect
*when the acceleration has become large*. Both are legitimate readings of “onset”, and they differ by a
factor of ~1.7. The knee is therefore located within 278–530 cycles depending on definition, a band
of about a factor of 1.9. The 20 % convention is adopted because it is the most conservative member of the
cluster; suppressing the spread would leave a reader who prefers the second-derivative criterion to conclude
that the definition had been chosen to suit the argument.

**What this does not license.** No primary literature value should be compared numerically against these
cycle numbers. They are outputs of an unfitted model with a placeholder loop gain.

---

## S1.7 Sensitivity sweep over 400× in *b*_fresh

*b*_fresh is the one parameter with no external anchor, and it is also the parameter that most
strongly sets where the knee lands. It is therefore the model's weakest point. The sensitivity is
therefore reported in full rather than concealed.

*b*_fresh carries units Ω·cm² per (mAh cm⁻²) of dead lithium: resistance per unit of newly created
fresh interphase. Dividing by an assumed interphase resistivity ρ ≈ 10⁸ Ω·cm converts that coefficient
into a thickness. The dimensional check is worth stating, because the result is a length per unit *areal
charge* and not a length: (Ω cm²)/(mAh cm⁻²) divided by (Ω cm) gives cm³ mAh⁻¹, which is the same as cm per
(mAh cm⁻²). The conversion therefore yields *b*_fresh = 30 → 3.0 nm, *b*_fresh = 60 → 6.0 nm of
re-formed interphase per mAh cm⁻² of dead lithium. Three nanometers is physically plausible for a re-formed interphase; that is
the entire justification for 30, and it is an argument, not a measurement.

Sweep over 1 → 400 (a 400× range, 2.6 decades). `C1` is the claim that a knee exists; `C2` is that
severing abolishes it.

| *b*_fresh (Ω·cm² per mAh cm⁻²) | implied thickness (nm) | Knee | Departure | EOL | pre-knee exponent | post-knee exponent | *R*_end (Ω·cm²) |
|---|---|---|---|---|---|---|---|
| 1.0 | 0.1 | 663 | 299 | 1630 | 0.96 | 1.83 | 40.8 |
| 3.0 | 0.3 | 650 | 298 | 1542 | 0.96 | 1.90 | 43.9 |
| 10.0 | 1.0 | 610 | 294 | 1328 | 0.95 | 2.10 | 53.7 |
| 30.0 | 3.0 | 530 | 285 | 1044 | 0.91 | 2.43 | 75.1 |
| 60.0 | 6.0 | 462 | 275 | 873 | 0.86 | 2.56 | 94.8 |
| 100.0 | 10.0 | 410 | 267 | 768 | 0.81 | 2.54 | 109.4 |
| 200.0 | 20.0 | 348 | 254 | 667 | 0.71 | 2.37 | 123.5 |
| 400.0 | 40.0 | 300 | 244 | 613 | 0.61 | 2.09 | 127.8 |

**Conclusions, stated as narrowly as the data allow:**

- C1, a knee exists (8/8 values tested). Over a 400× range in the loop gain the knee moves from
  cycle 663 to 300, a factor of 2.21. The existence of a knee is therefore insensitive to the
  parameter that sets its position. This is the operative distinction: the argument requires a
  threshold plus feedback, not a specific gain.
- C2 — severing abolishes it (5/5 values tested, *b*_fresh = 10–200; the severing test spans
  a narrower range than C1; the asymmetry is stated rather than smoothed over).
- C3, the qualitative shape survives: pre-knee exponent 0.61–0.96 (always ≤ 1, i.e. never
  superlinear before the loop engages), post-knee exponent 1.83–2.56 (always > 1). The reference value
  30 was chosen partly because 0.91 is the closest to a linear pre-knee fade;
  lower values give exponent 0.96 (flatter) and higher values give 0.61 (markedly sublinear). The value
  is a stated choice, not a derived quantity, and is recorded as such.

**What the sweep cannot fix.** The absolute knee position (300–663 cycles) is still set by an unfitted
parameter, so the model cannot say where a real cell's knee will be. What it does establish is that a
knee of some position follows from the coupling, and that its position is controlled by an operating
variable (*R*\*, via rate and Δ) rather than by a tabulated property value.

---

## S1.8 Numerical method and discretization

The update is explicit and first-order: each cycle's state is computed from the previous cycle's state,
with no iteration and no implicit solve. There is no time integration inside a cycle, the cycle is the
time step. The scheme is therefore an Euler map on a discrete index, and its accuracy question is not
“is Δ*n* small enough” but “does the discrete √*n* approximation match the continuous √*t* law”.

The only place this matters is the interphase term *a*_SEI/√*n*, which is the discrete counterpart of
d*R*/d*t* ∝ *t*^{−1/2}. The exact continuous solution gives, for the continuous case, 2*a*√*n* by integrating a/√*i* from 0 to *n*; the discrete sum
Σ_{i=1}^{n} *a*/√*i* is systematically smaller:

| *n* | Σ *a*/√*i* | 2*a*√*n* | ratio |
|---|---|---|---|
| 100 | 8.3653 | 9.0000 | 0.9295 |
| 400 | 17.3541 | 18.0000 | 0.9641 |
| 1000 | 27.8105 | 28.4605 | 0.9772 |

The discrete scheme underestimates cumulative interphase growth by 7 % at 100 cycles, 3.6 % at 400, and
2.3 % at 1000. This is a systematic bias in the direction that makes the knee slightly later than the
continuous model would put it, i.e. it is conservative with respect to the claim (a later knee is harder
to attribute to fast fade). It is not corrected: correcting it would change all quoted cycle numbers, and
a 3 % bias is far inside the 2.21× range of knee positions that S1.7 spans.

**Stopping conditions.** `n_max = 6000`. The coupled baseline stops itself at cycle 1044 by reaching
LLI = *Q*₀. The severed control runs to *n*_max. The model is fully deterministic: there is no randomness
anywhere, so every quoted number is exactly reproducible.

---

## S1.9 Full operating-condition map

If the knee is a design variable rather than a fixed property value, then it must move when the operating
condition moves, and it must move in a predictable direction: faster cycling and faster interphase growth
should both bring the knee forward. The full map tests that prediction across the operating envelope, and
it also marks the region in which the model stops producing a knee at all.

Knee cycle count as a function of C-rate (rows) and the SEI-growth factor *T*_factor (columns), the
multiplier applied to the interphase growth rate:

| C-rate ↓ / *T*_factor → | 0.25× | 0.5× | 1.0× | 2.0× | 4.0× |
|---|---|---|---|---|---|
| 0.5C | none | none | 2651 | 910 | 330 |
| 1.0C | 3937 | 1315 | 530 | 249 | 126 |
| 2.0C | 268 | 157 | 104 | 72 | 49 |
| 3.0C | 55 | 51 | 44 | 37 | 29 |

Monotonic in both directions wherever a knee exists: higher rate → earlier knee at every *T*_factor;
faster SEI growth → earlier knee at every rate. The rate effect is steep: over the S1.4 rate table, 0.5C to 2.5C moves the knee from 2651 to 64, a factor of 41.4, and the temperature effect is shallower (0.5× to 2× *T*_factor
moves it 1315 → 249, a factor of 5.3 at 1C). The rate-dependence factor is therefore 41.4 (≈40).

Two “none” entries at 0.5C × {0.25×, 0.5×} deserve a note rather than a silent blank: at those
combinations interphase growth is slow enough that *R* does not reach *R*\* = 40 Ω·cm² within 6000 cycles,
so the loop never engages and there is no knee to find. That is the model behaving as designed — no
feedback, no knee, and it is the same statement as the ablation, obtained a different way.

**And where it breaks:** at 3.0C the knee arrives between cycle 29 and 55, at or below the fitting window used by the departure detector (30–200). The model is still internally consistent there, but the departure
diagnostic is not defined, so the 2.0C row is marked invalid rather than reported. The S1.5 “none” entries
are the two 0.5C columns at 0.25× and 0.5×, where no knee forms.

---

## S1.10 Claims the model does not support

A model of this kind is easy to over-read, so the boundary is stated explicitly. Each item below is a
claim that this model does not support, and the list is intended to be complete.

1. It does not predict any real cell's cycle life. None of 530, 1044, 285, or any other number is a
   prediction. They are outputs of an unfitted model with placeholder parameters.
2. It does not validate the coupling mechanism. It shows that if the Loop-A coupling exists with
   the assumed form, a knee follows and severing the coupling removes it. It is silent on whether the
   coupling exists in a real cell. That question is answered by measurement, not by this model;
   S4's branch B7 sets out the measurement.
3. It does not model Loops B, C, or D. No dissolution, no crossover, no fracture, no electrolyte
   inventory. The rest of Figure 1 panel (a) — every mechanism other than M1 and the M2 feedback path, and
   every edge not on the Loop A circuit — is qualitative, and the model gives it no quantitative support.
   Loop D is absent from the model altogether, not merely unvalidated by it.
4. It has no spatial dimension. No porosity, no electrode thickness, no potential distribution.
   Consequently it is not suited to Loop D (electrolyte depletion), which is intrinsically a volumetric
   argument. The Loop D budget in S2.6 is a separate, independent calculation with no model input.
5. It does not model loss of active material or kinetic polarization loss. The model resolves one of
   the three capacity-loss channels, lithium inventory, and is silent on the other two, active material and
   kinetics. It therefore says nothing about how the three partition in a real cell.
6. The knee definition is arbitrary and the spread is a factor of 1.9 (S1.6). Quoting a single knee
   cycle number without that band is over-precision.
7. The threshold is an electrode-average statement (S1.4), not a local one. It cannot resolve
   patchiness, and it does not predict the first plating event.
8. **No parameter is fitted, and *b*_fresh is not measured.** Its value 30 was chosen to give a
   physically plausible 3 nm re-formed interphase and a pre-knee exponent near 1. The 400× sweep indicates
   that this choice is unlikely to change the qualitative conclusions, though it does change every cycle
   number.
9. The model is not a “bifurcation” in the strict dynamical-systems sense. It has a threshold and a
   saturating nonlinearity, which produces a sharp but finite transition. The Perspective accompanying these derivations describes the
   knee as behaving as a bifurcation; in the strict sense that word is a misnomer, and the mechanism
   here is a threshold with a saturating nonlinearity.
10. Temperature enters only as a scalar multiplier on SEI growth. Real temperature dependence differs
    between the SEI-growth, charge-transfer, and transport terms, and the model does not represent that.

## S1.11 Tables S2–S5

### Table S2. Parameters of the reduced Loop-A model.

All values are for 1C, *Q*₀ = 3.0 mAh cm⁻² unless stated. “Provenance” distinguishes measured values
(traceable to a cited source) from illustrative placeholders; no parameter is fitted to a fade curve.

| Symbol | Value | Unit | Meaning | Provenance |
|---|---|---|---|---|
| *Q*₀ | 3.0 | mAh cm⁻² | nominal areal capacity, 1C reference | Illustrative (typical high-energy Li-ion) |
| *η*_ct | 0.030 | V | charge-transfer overpotential at the operating rate | Illustrative, order-of-magnitude |
| Δ | 0.090 | V | margin between anode operating potential and 0 V vs Li/Li⁺ | Illustrative; sets *R*\* |
| *R*₀ | 8.0 | Ω cm² | fresh-cell anode area-specific interphase resistance | Illustrative, order-of-magnitude |
| *a*_SEI | 0.45 | Ω cm² cycle^{−1/2} | diffusion-limited interphase growth prefactor | Anchored to √*t* transport law; magnitude illustrative |
| *b*_fresh | 30.0 | Ω cm² per mAh cm⁻² | resistance added per unit of dead Li → fresh interphase (loop gain) | No literature anchor. Reference value chosen for 3 nm implied thickness (ρ = 10⁸ Ω cm) and pre-knee exponent ≈ 1. Sweep in Table S4. |
| *R*_cap | 120.0 | Ω cm² | pore-filling saturation asymptote for interphase resistance | Illustrative (geometry of anode pore volume) |
| *k*_pl | 12.0 | V⁻¹ | sharpness of the plating turn-on | Illustrative (width of local-*R* distribution) |
| *f*_max | 0.02 | — | maximum fraction of applied charge that can plate | Illustrative upper bound enforcing mass balance |
| *f*_dead | 0.094 | — | fraction of plated Li becoming electrically isolated | Measured, no-FEC case: `10.1016/j.xcrp.2020.100139` [FROM LITERATURE]. FEC case 0.033 ± 0.006. |
| *c*_LLI | 0.010 | mAh cm⁻² per Ω cm² | LLI charged per unit of interphase resistance grown | Illustrative; converts Δ*R* into lost inventory |
| *n*_max | 6000 | cycles | integration limit | Numeric choice; only reached by the severed control |

Derived quantities at 1C: *j* = 3.000 mA cm⁻²; *R*\* = 20.00 Ω cm²; headroom Δ − *η*_ct = 60 mV;
threshold *R*\*/*R*₀ = 2.50.

*Notes.* [a] The √*n* form of the *a*_SEI term is the discrete counterpart of the √*t* law for
diffusion-limited interphase growth; S1.8 quantifies the discretization bias. [b] *b*_fresh is the only
parameter that both (i) lacks an external constraint and (ii) strongly controls the knee position; it is
the model's principal vulnerability and is disclosed as such. [c] *f*_dead is the only parameter obtained
from a direct measurement, and it comes from a Li-metal cell; its use in a graphite-based Loop A is an
assumption, labeled `[HYPOTHESIS]`.

### Table S3. Baseline landmarks and the ablation, 1C, reference parameters.

**(A) Baseline trajectory.**

| Quantity | Coupled | Severed |
|---|---|---|
| Early power-law fit, cycles 30–200 | *LLI* = 7.268 × 10⁻³ · *n*^{0.522} | identical |
| First plating (cycle) | 220 | 220 |
| Departure from early power law (cycle) | 285 | none to 6000 |
| Knee, LLI ≥ 20 % *Q*₀ (cycle) | 530 | none |
| End of life, LLI = *Q*₀ (cycle) | 1044 | not reached |
| *R*(0) (Ω cm²) | 8.00 | 8.00 |
| *R*(400) (Ω cm²) | 26.85 | 24.16 |
| *R*_max (Ω cm²) | 75.12 | 60.51 |
| Pre-knee exponent (10–90 % of knee) | 0.910 | — |
| Post-knee exponent (knee → 1.8× knee) | 2.434 | — |
| Retained capacity at cycle 1044 | 0 % | 91.6 % |
| Terminal LLI (mAh cm⁻²) | 3.00 (clipped) | 0.525 (at 6000) |

**(B) Which term carries the loop.**

| Variant | Setting | Departure | Knee | EOL |
|---|---|---|---|---|
| coupled | reference | 285 | 530 | 1044 |
| feed-forward arrow severed | *b*_fresh = 0 | 300 | 670 | 1681 |
| dead-lithium fraction severed | *f*_dead = 0 | none | none | 6000 |
| fully severed | both zero | none | none | 6000 |

Setting *f*_dead = 0 forces *d*_dead = 0 in (S1.E5) and therefore removes both the resistance term
*b*_fresh·*d*_dead in (S1.E6) and the inventory term in (S1.E8), so that row is identical to the fully
severed case. This is why the dead-lithium fraction, not the feed-forward arrow, is what makes the
coupling a loop.

(C) Secondary knee criteria on the coupled baseline.

| Criterion | Knee (cycle) |
|---|---|
| Cumulative LLI ≥ 20 % *Q*₀ | 530 |
| Max d²(LLI)/d*n*² | 470 |
| Max retention curvature | 470 |
| Kneedle chord method | 479 |
| Local-exponent acceleration | 278 |

*Notes.* [a] The departure test fits *A*·*n*^p over cycles 30–200 (pre-loop: first plating is at 220) and
flags the first cycle after 200 with >10 % excess over the extrapolation. [b] “None” means the criterion
is not met within *n*_max = 6000; it is a genuine null, not a failure to converge. [c] The 20 %-LLI
convention is the most conservative of the five criteria; the spread (278–530, a factor of 1.9) should be
quoted alongside any single number.

### Table S4. Sensitivity of the knee to the unanchored loop gain *b*_fresh.

Sweep over a 400× range (2.6 decades). Implied interphase thickness assumes ρ = 10⁸ Ω cm.

| *b*_fresh | Implied thickness | Knee | Departure | EOL | Pre-exp. | Post-exp. | *R*_end |
|---|---|---|---|---|---|---|---|
| 1.0 | 0.1 nm | 663 | 299 | 1630 | 0.96 | 1.83 | 40.8 |
| 3.0 | 0.3 nm | 650 | 298 | 1542 | 0.96 | 1.90 | 43.9 |
| 10.0 | 1.0 nm | 610 | 294 | 1328 | 0.95 | 2.10 | 53.7 |
| 30.0 | 3.0 nm | 530 | 285 | 1044 | 0.91 | 2.43 | 75.1 |
| 60.0 | 6.0 nm | 462 | 275 | 873 | 0.86 | 2.56 | 94.8 |
| 100.0 | 10.0 nm | 410 | 267 | 768 | 0.81 | 2.54 | 109.4 |
| 200.0 | 20.0 nm | 348 | 254 | 667 | 0.71 | 2.37 | 123.5 |
| 400.0 | 40.0 nm | 300 | 244 | 613 | 0.61 | 2.09 | 127.8 |

*Notes.* [a] Bold row is the reference value. [b] Knees exist at 8/8 values (C1); severing abolishes the
knee at 5/5 values tested (C2, *b*_fresh = 10–200, a narrower range than C1). [c] Knee range 300–663 is
a factor of 2.21, i.e. existence is robust while position is not. [d] Units of *b*_fresh: Ω cm² per
mAh cm⁻²; *R*_end in Ω cm². [e] Implied thickness = *b*_fresh/ρ, converted to nm.

### Table S5. Knee cycle count vs C-rate and SEI-growth factor (*T*_factor).

| C-rate ↓ / *T*_factor → | 0.25× | 0.5× | 1.0× | 2.0× | 4.0× |
|---|---|---|---|---|---|
| 0.5C | none | none | 2651 | 910 | 330 |
| 1.0C | 3937 | 1315 | 530 | 249 | 126 |
| 2.0C | 268 | 157 | 104 | 72 | 49 |
| 3.0C | 55 | 51 | 44 | 37 | 29 |

*Notes.* [a] “none” = *R* does not reach *R*\* within 6000 cycles, so no plating and no knee; this is the
ablation's conclusion obtained independently. [b] *T*_factor scales the SEI-growth prefactor; 2× ≈ +20 K.
[c] At 3C the knee precedes the departure-fit window (cycles 30–200), so the departure diagnostic is not
defined there even though the model remains internally consistent. [d] Knee cycle count at 1C, *T*_factor
= 1 is 530; over the S1.4 rate table, the 0.5C→2.5C span is 2651/64 = 41.4.

---

## S1.12 Summary of the model

The reduced model is a two-state, cycle-resolved scaling argument, not a fit: anode interphase
resistance *R* grows as √*n* plus a term proportional to freshly created dead lithium, and lithium
inventory loss *LLI* accumulates from interphase growth and from that dead lithium. Plating ignites when
the ohmic drop carries the anode past 0 V vs Li/Li⁺, i.e. when *R* > *R*\* = (Δ − *η*_ct)/*j* — a
threshold that depends on rate and operating window rather than on any tabulated property value. Two self-limiting terms
(mass balance, *f* ≤ *f*_max, and pore-filling saturation, *R* → *R*₀ + *R*_cap) keep every state
variable physical and give the transition a finite post-knee slope.

The ablation separates the two couplings. Removing the dead-lithium fraction (*f*_dead = 0) abolishes the
knee outright, leaving a cell that fades at the same early rate but never departs from its early power
law out to 6000 cycles, because *d*_dead = 0 removes both the resistance term and the stranded-inventory
term at once. Removing only the feed-forward arrow (*b*_fresh = 0) leaves dead lithium forming and
stranding inventory, and the knee is delayed from 530 to 670 cycles rather than removed. The knee is
therefore a structural consequence of the coupling rather than a kinetic one, and the parameter
that makes the coupling a loop is the dead-lithium fraction, not the loop gain.

## S1.13 The framework applied to published fade curves

The Perspective states that the framework is "testable on any published fade curve that has been
decomposed", and never performs the test. This section performs the part of it that does not require
refitting anyone's published data.

**What can be compared, and what cannot.** S1.6 warns that no primary literature cycle number should
be compared numerically with the model's, because the model is unfitted and its loop gain is a
placeholder. That warning rules out reading *530* against any published cycle count. It does not rule out comparing a
**dimensionless ratio**, because a common scale factor cancels. The one ratio the framework makes a
prediction about is the distance from the knee to the end of life: the framework is worth having only
if there is life left after the knee. Here the model is unhelpful in a way worth stating plainly. Its
primary knee convention is LLI ≥ 0.20 Q₀, which is 80 % retention by construction, and 80 % retention
is also the published definition of end of life. Under the primary convention used here the model
therefore has zero interval: its knee is its end of life. The meaningful interval only appears
when the knee is located by the onset criteria in S1.6, which place it at 278–285 cycles and leave
530 - 285 ≈ 245 cycles, a ratio of 1.86. So the quantity compared below is definition-dependent from
the model side as well as the data side, and that is the substance of the result.

**Data.** Knee point and end of life for 303 cells from 17 independent published studies, tabulated
from the original figures by Attia et al. (J. Electrochem. Soc. 169, 060517, 2022;
doi:10.1149/1945-7111/ac6d13) and taken from their public repository
(github.com/tinosulzer/kneepoint-review). End of life is 80 % of nominal capacity throughout, which
makes it the one quantity defined identically across all 17 studies. The values are the original
authors' readings of published figures, not independent measurements, and no cell was re-analyzed
here.

The comparison is definition-limited before it is model-limited. 83 of the 303 cells (27 %) have a
knee point after their end of life. This is not an error in the compilation: the 17 studies detect
the knee by different algorithms on different fades, and on a curve that has already passed 80 %
retention the detected inflection can fall later than the 80 % crossing. The dispersion is therefore
a property of the literature the framework is meant to organize. Any claim that the knee is a single
well-defined object has to survive this, and the framework currently does not address it.

**The ratio.** On the 220 cells with knee ≤ end of life, the published relation is close to linear:

| quantity | value |
|---|---|
| published median EOL / knee | 1.26 |
| published interquartile range | 1.14–1.31 |
| least-squares fit | EOL = 1.20 × knee + 22 (R² = 0.936, n = 220) |
| per-study medians | 1.03–1.46 (16 of 17 studies), 2.62 (petzl, n = 3) |

The model's own ratio depends entirely on which of the five knee definitions in S1.6 is used:

| knee definition | model knee (cycle) | model EOL, 80 % retention (cycle) | ratio |
|---|---|---|---|
| departure / local exponent | 278–285 | 530 | 1.86–1.91 |
| second derivative / Kneedle | 470–479 | 530 | 1.11–1.13 |
| LLI ≥ 0.20 *Q*₀ (manuscript's "knee") | 530 | 530 | 1.00 |

**Table S6.** The framework's ratio against the published range.

| | value |
|---|---|
| cells / studies in the compilation | 303 / 17 |
| cells with knee ≤ end of life | 220 (73 %) |
| cells with knee > end of life | 83 (27 %) |
| published median EOL / knee | 1.26 |
| published interquartile range | 1.14–1.31 |
| published least-squares fit | EOL = 1.20 × knee + 22 (R² = 0.936) |
| model ratio, onset knee definitions | 1.86–1.91 |
| model ratio, late knee definitions | 1.00–1.13 |

Result: the test is inconclusive, and this is reported rather than resolved. The model's ratio spans
1.00–1.91 depending on a definitional choice that the literature also does not make consistently. The
published interquartile range, 1.14–1.31, falls inside that span. Depending on which definition is
adopted the framework is either consistent with the data (using the late knee definitions) or sits
above it (using the onset definitions). A test whose outcome is fixed by the definition of its own
central object has no discriminating power, and presenting either branch as a confirmation would be
the same error corrected elsewhere.

One thing the comparison does establish. The framework's claim that the knee is a useful
*early-warning* object requires a measurable interval between the knee and end of life. In the
published data that interval is about a quarter of the knee value: the median cell reaches 80 %
retention at 1.26 × its knee cycle, not at the ~2 × the model produces under its onset definitions.
The interval exists, which supports the framing, but it is short in most published cells. Any use of
the knee as a warning signal is therefore operating on roughly a quarter of the knee-to-knee interval,
and a proposed application that assumes more should say where its larger interval comes from.

**What this does not establish.** It does not test whether the coupling explains the observed knees.
That requires the decomposition the Perspective asks for — LLI, LAM and KL resolved as functions of
cycle for individual published cells — and only then can the framework's diagnostic question ("which
loop is engaged?") be put to data. The published knee/EOL tabulation carries no decomposition, so the
most informative available test is deferred. This is the largest open item and is stated as such in the
accompanying Perspective.

## S1.14 A test that does not depend on where the knee is placed

S1.13 failed to discriminate because its outcome was fixed by the choice among five knee
definitions. The model makes a second, sharper prediction that does not require locating the knee at
all: the shape of the fade. Before the knee, lithium inventory accumulates close to linearly with
cycle number; after it, the feedback makes the accumulation accelerate. In the reference curve the
local exponent of LLI growth is 0.91 before the knee and 2.43 after (S1.7). An exponent can be
fitted to any published capacity curve over a chosen window, so the prediction can be tested
without the definitional choice that defeated S1.13.

**Data.** Harris et al. (2017), as compiled by Attia et al. (J. Electrochem. Soc. 169, 060517,
2022; `code/data/variability/harris2017.xlsx`, sheet `ZP2A`). Twenty-four cells cycled to 10 C. Of
these, 22 end below 95 % retention (every cell dips below 95 % at some point), 21 reach 80 %, and 19
meet the inclusion criterion below. The distinction between ending below a threshold and touching it
matters here, because a single low cycle should not place a cell in the accelerating group. This
is cell-level capacity against cycle number, which is what the test needs; it is not a
decomposition.

**Method.** For each cell the retained-capacity trace is smoothed with a running median to suppress
cycle-to-cycle scatter, converted to fractional loss (`1 - capacity`), and `log(loss)` is fitted
against `log(cycle)` separately before and after the cycle at which retention crosses 80 %. The
exponent of loss is the quantity the model states; fitting `log(retention)` instead is meaningless
because early retention sits at 0.9995, where the logarithm is flat, and a first version of this
analysis that did so returned -0.05 for every cell. Cells whose fitted exponent exceeded 8 in
magnitude were rejected as fits to residual scatter rather than to a trend, which removed 3 of 22.

**Result.** The direction of the prediction is supported in most cells and contradicted in a
minority that the framework cannot accommodate:

| | value |
|---|---|
| cells analyzed | 19 |
| median exponent before 80 % retention | 1.04 |
| median exponent after | 1.43 |
| median change | +0.44 |
| cells where the exponent rises | 13 of 19 (68 %) |
| cells where it is flat (within ±0.1) | 2 |
| cells where it falls | 4 of 19 (21 %) |

The rising majority is consistent with the framework: fade accelerates after the knee, as a
feedback loop requires. The four falling cells are the informative result. They do not scatter;
they settle at about 0.79 retention and then lose less than 0.003 of retention over the next
hundred cycles, which is an order of magnitude below the cycle-to-cycle variation of the cells
that accelerate. A framework whose central mechanism is a loop that can only amplify has no route
to a cell that decelerates after its knee. Those cells are evidence that something other than the
Loop-A feedback dominates their later life, and the framework as written does not predict them.

**Magnitudes are not compared.** The measured medians, 1.04 and 1.43, are of the same order as the
model's 0.91 and 2.43, but the model is unfitted and its loop gain is a placeholder (S1.6), so the
numerical proximity is not agreement and is not claimed as such. Only the sign of the change is a
fair test, and only the sign is used.

**What this still does not do.** It does not decompose capacity into LLI, LAM and KL. A rising loss
exponent is consistent with a feedback loop and equally consistent with any other accelerating
mechanism, including ones already in the literature. The test is therefore a necessary condition
and not evidence that the coupling is the cause. Performing the decomposition would require
low-rate OCV traces at several ages for individual cells with known half-cell curves; the public
compilations that carry knee and end-of-life do not include them, and the open datasets examined
here (Harris 2017; Ecker 2014; the Battery Life raw archive, whose cells span only 100 cycles and
reach 98 % retention) do not provide them either. The diagnostic question the Perspective actually
poses, which loop is engaged, therefore remains untested on published data, and this section is
reported as a partial test rather than as the demonstration the Perspective promises.

## S1.15 The Section 2 prescription run on a published dataset

Section 5 of the Perspective applies the accounting prescription to one public dataset and reports
both what it recovers and where it fails. This note gives the method and the full numbers.

**Data.** Harris et al., *Journal of Power Sources* 342, 589–597 (2017);
the file `raw/harris2017.xlsx` in `research/13-fade-application`,
sheet `ZP2A`, columns are normalized capacity retention per cycle for 24 commercial pouch cells
cycled at 10 C to 100 % depth of discharge over 593 cycles. This is retention only. It carries no
LLI/LAM/KL decomposition, so the analysis tests the shape the framework predicts, not the channel
attribution it would prefer. That limitation is stated in the Perspective and is not repaired here.

**Method.** The per-cycle loss is taken as the negative finite difference of retention,
*f*(*N*) = −[*Q*(*N*) − *Q*(*N*−1)]/*Q*_(N−1). This is fitted against cycle number as
*f*(*N*) = *f*0 + α*N* by ordinary least squares over the cycles where retention lies in a stated
window. α is the coupling strength of Section 2: the rate at which efficiency loss grows. The window
is a parameter, not a convenience, and the sensitivity to it is reported below rather than hidden.
Script: `research/13-fade-application/worked_example.py`; output `worked_example_results.json`.

**Result, primary window 90-100 % retention.** 24 cells analyzed. α > 0 in 22 of 24, median
5.57×10⁻⁷ per cycle, range −3.33×10⁻⁶ to 4.00×10⁻⁶. The two negative cells are not a
coherent group: one ends at 84.8 % retention, the other at 3.5 %, so in the second the fit window
is short and the slope is not meaningful. Neither undermines the sign of the majority.

**A constant *f* is not enough.** A single constant *f* fitted to the whole trace leaves a median
RMSE of 0.0420 in retention. A quadratic in *N* leaves 0.0082, better in 24 of 24 cells, and its
coefficient is negative in 24 of 24. Negative curvature in retention is the signature Section 2
predicts whenever *f* itself rises with cycle number, so the curvature is present in every cell of
this set.

**Three independent estimates.** (i) The finite-difference fit above. (ii) A global quadratic fit to
retention, with an effective coupling taken as minus twice the quadratic coefficient: positive in 24
of 24 cells, median 1.18×10⁻⁶. This estimate does not use *f* at all. (iii) Comparing a linear fit
to the first and second halves of the trace: the second-half slope is steeper in 24 of 24 cells.
The three agree on sign in every case, so the finding does not depend on the fitting scheme.

**Window sensitivity, which is the honest limit.** The sign of α is not a property of the cell alone:

| Window (retention) | cells | α > 0 | median α (per cycle) |
|---|---|---|---|
| 95-100 % | 24 | 6  | −1.43×10⁻⁷ |
| 90-100 % | 24 | 22 |  5.56×10⁻⁷ |
| 85-100 % | 24 | 23 |  8.34×10⁻⁷ |
| 80-100 % | 24 | 22 |  9.88×10⁻⁷ |

Over the narrowest window the curvature is smaller than the cycle-to-cycle scatter of a 10 C
protocol, so the sign inverts. This is not a defect of the dataset; it is what any efficiency-curvature
measurement faces when the window is chosen after seeing the data. A cross-study comparison of α is
therefore only meaningful if the window is fixed in advance, which no protocol in the literature
does. Window bounds belong in the reporting checklist of Section 8 alongside rate, temperature and stack
pressure. They also belong in prediction P6 of Section 7, and the reason is worth stating plainly,
because the first version of P6 did not have them and was therefore refuted by this very table. As
worded then, P6 said α is positive and is refuted if it changes sign while retention stays above
90 %. Every cell in the 95-100 % row satisfies that condition, and 18 of 24 have α < 0 there, so
the prediction was false on the data it cited as support. The amended P6 makes the window part of the
prediction rather than an adjustable setting: concave retention over a pre-registered window no
narrower than 90 %, with the 95-100 % inversion reported in the same paragraph as the limit. What P6
now claims is falsifiable and, on this dataset, not falsified.

**What this does and does not establish.** It establishes that the quantity Section 2 asks for is
measurable on published data at no experimental cost, and that it is positive in nearly every cell
of a well-known 24-cell set. It does not establish which channel drives the curvature, because
retention alone cannot separate LLI from LAM. It also does not establish that α is a materials
constant. Among the 22 cells with α > 0 the fitted value spans 8.1×10⁻⁹ to 4.0×10⁻⁶ per cycle, a
factor of about 500, across cells of one chemistry from one supplier run under one protocol. At that
spread α behaves as a cell-level property at least as much as a chemistry-level one. That is
consistent with the Perspective's framing, in which operating condition sets the rate at which a
margin is consumed. It is not evidence against a role for chemistry: a factor of 500 between two
cells of the same nominal chemistry says the chemistry label is too coarse to predict α, not that
chemistry is irrelevant. S1.16 shows that the most influential parameter in the model is in fact
electrode chemistry, which is the sharper caveat.

## S1.16 Direct sweep of the operating margin

Section 5 of the Perspective states that the knee is a design variable because each loop closes on an
operating margin. The reduced Loop-A model contains exactly one parameter that is that margin:
Δ in (S1.E2), the gap between the anode's equilibrium potential and 0 V vs Li/Li⁺. The plating
threshold follows from it as *R*\* = (Δ − η_ct)/*j*.

Every sweep reported so far in S1.7 and S1.9 varies something else. S1.7 varies *b*_fresh, the loop gain.
S1.9 varies C-rate and the SEI-growth factor. Neither is the margin. C-rate is not a clean substitute
for it: raising the rate lowers *R*\* through *j*, but it also raises *Q*_applied in (S1.E4), so a C-rate
sweep moves the plated charge per cycle at the same time. This note closes that gap. Δ is varied at
fixed C-rate (1 C), fixed *Q*₀ (3.0 mAh cm⁻²) and fixed *b*_fresh (30), so *j* and *Q*_applied are
constant and the margin is the only thing that moves. Script:
`research/06-proposal/_support/margin_sweep.py`.

**Range, and why it is narrow.** The departure detector of S1.5 fits its pre-loop baseline over cycles
30-200. If plating begins before cycle 200, that baseline is no longer pre-loop and the resulting knee
is not comparable with the reference case. Above Δ = 0.090 V plating starts after cycle 200, so the
clean window runs from 0.090 to 0.120 V, a factor of 1.33. Below 0.090 V the rows are reported but marked
contaminated. This is a limit of the analysis, not a choice, and the narrow window weakens what the
sweep can claim.

| Δ (V) | *R*\* (Ω cm²) | knee | EOL | plating at | baseline |
|---|---|---|---|---|---|
| 0.120 | 30.0 | 1134 | 1717 | 771 | clean |
| 0.115 | 28.3 | 1007 | 1577 | 651 | clean |
| 0.110 | 26.7 |  891 | 1449 | 543 | clean |
| 0.105 | 25.0 |  786 | 1333 | 447 | clean |
| 0.100 | 23.3 |  692 | 1227 | 361 | clean |
| 0.095 | 21.7 |  606 | 1131 | 285 | clean |
| 0.090 | 20.0 |  530 | 1044 | 220 | clean |
| 0.085 | 18.3 |  463 |  967 | 164 | contaminated |
| 0.080 | 16.7 |  404 |  898 | 116 | contaminated |
| 0.070 | 13.3 |  308 |  785 |  47 | contaminated |
| 0.060 | 10.0 |  239 |  699 |  10 | contaminated |

**Result.** Across the clean window Δ 0.120 → 0.090 V, a factor of 1.33, the knee moves from 1134 to
530 cycles, a factor of 2.14. The local elasticity d(log knee)/d(log Δ) is 2.5-2.8 and is stable across
the window, so the response is not an artefact of one operating point. The structural reason is visible
in the threshold: *R*\* is linear in Δ with slope 1/*j* = 333 Ω cm² V⁻¹, so a 10 mV change moves
the threshold by 3.3 Ω cm², which at the reference *R*\* = 20 Ω cm² is a 17 % change in the
threshold itself.

Comparison with the gain sweep, on equal footing. The comparison that needs no fitting is the span
itself: the loop gain moves the knee by a factor of 2.21 across a 400-fold range (S1.7), while the margin
moves it by 2.14 across a 1.33-fold range. A 300-fold larger change in the gain buys about the same
shift in the knee.

The elasticities, d(log knee)/d(log x), make the same point in local terms. For the margin it is
2.5-2.8 and rises slowly with Δ. For the gain it is 0.13 over the whole range but reaches 0.17-0.23
locally between 10 and 400. Taking the local gain value, the margin is still roughly a dozen times more
effective per e-fold; taking the overall gain value it is about twenty times. Either way the ordering
is large and unambiguous, which is the quantitative form of the statement that the knee is set by the
operating condition and not by the materials.

**What this does not settle.** Three things, and the first two cut against the framing of the
Perspective rather than for it.

First, Δ is a placeholder, not a measured value, so the sweep establishes the sensitivity of the knee
to the margin and not its position in any real cell.

Second, and more awkwardly, Δ is not a process knob. It is the gap between the anode's equilibrium
potential and 0 V vs Li/Li⁺, and that equilibrium potential is a property of the electrode material:
about 0.08-0.10 V for the stage-1 plateau of graphite. Moving Δ therefore means changing the anode
chemistry, not turning a dial on the line. The other margins named in the Perspective are more
tractable: C-rate, temperature, voltage window, stack pressure and electrolyte loading are all genuine
operating variables. So the sweep shows that the most influential margin in the model is the least
accessible one, which weakens rather than strengthens the practical claim. What survives is the
conceptual point: the knee is set by a threshold crossing, and a threshold is not a materials
constant in the sense the literature assumes.

Third, the model has one loop. Whether the same ordering of sensitivities survives when all four loops
compete is not tested, and the Perspective states that ranking as a prediction for that reason.
