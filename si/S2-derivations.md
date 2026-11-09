# S2. Derivations behind the reported quantities

## S2.0 Basis of the derivations

A coupling only matters if its margin is of order unity. If a feedback arrow delivers a thousandth of the
effect it is supposed to drive, it can be dropped and the mechanisms can be treated as independent. If it
delivers a thousand times that effect, the loop saturates immediately and one mechanism dominates. The
interesting case is the narrow one in between, and deciding which case each of the four loops falls into
requires a number for every arrow. This section supplies those numbers.

The arithmetic is coarse by construction. Each derivation is an order-of-magnitude estimate, not a
measurement and not a first-principles calculation, and each is stated to the precision its inputs
support, usually one significant figure. Quoting "11.19 µm" would misrepresent the precision; "~11 µm" is
the appropriate form. Several derivations carry a stated uncertainty of 2–5×, and the argument is built to
survive that uncertainty, because the conclusion is about orders of magnitude and not about a specific
value.

No number here is a measured value; each is arithmetic on stated inputs.
Second, where this section writes "~", the input is uncertain by at least a factor of 2, whereas three
significant figures are given only where the input is a physical constant and the precision is real.

Status tags are used throughout: `[DERIVED]` = computed here, arithmetic shown; `[FROM LITERATURE: DOI]` =
supplied by a published source; `[HYPOTHESIS]` = proposed, not established; `[ASSUMED]` = an
order-of-magnitude input that is not traceable to a specific measurement.

---

## S2.1 Loop A: the SEI ohmic drop

Consider the anode of a cell that is about to plate lithium. Whether it plates depends on the anode
potential: plating begins when that potential falls to 0 V versus Li/Li⁺. The anode is driven there by the
ohmic drop across the interphase, *j·R*, and it is held back by the operating margin Δ and by the
charge-transfer overpotential. So the interphase resistance controls plating onset, and the question for
this derivation is how large that resistance is, and therefore whether Loop A can be active in a real cell.

The sign and the magnitude are answered separately. The sign is robust: a resistive interphase always
pushes the anode toward plating, so the direction of the arrow requires no assumption. The magnitude
is not robust at all: it spans four orders of magnitude, because the conductivity of the interphase is not
known to better than that. The consequence is stated at the end of this section, and it constrains what
Loop A can and cannot be used to predict.


**The derivation.** Treat the interphase as a slab of thickness *d* and ionic conductivity σ carrying the
applied current density *j*. Its area-specific resistance is

$$R_{\text{SEI}} = \frac{d}{\sigma}\quad[\Omega\,\text{cm}^{2}] \tag{S2.E1}$$

and the ohmic potential drop across it is

$$\Delta\phi_{\text{SEI}} = j\,R_{\text{SEI}} = \frac{j\,d}{\sigma}\quad[\text{V}] \tag{S2.E2}$$

`[DERIVED]`: this is Ohm's law applied to a series slab; there is no modeling choice beyond treating the
interphase as uniform.

**Evaluating it.** Take *d* = 30 nm (a representative SEI thickness for a graphite anode after formation; the
surveyed band is ~10–200 nm, `[FROM LITERATURE: 10.1088/1361-6528/ac17fe]`. A round value is used because the spread, not the point, is the result) and
*j* = 3.0 mA cm⁻² = 3.0 × 10⁻³ A cm⁻² (1C for a 3 mAh cm⁻² electrode):

| σ (S cm⁻¹) | *R*_SEI (Ω cm²) | Δφ_SEI = *j*·*R*_SEI (mV) |
|---|---|---|
| 10⁻⁷ | 30 | 90 |
| 10⁻⁸ | 300 | 900 |
| 10⁻⁹ | 3000 | 9000 |

`[DERIVED]`: all three rows. Arithmetic: at σ = 10⁻⁸ S cm⁻¹, *R* = 30×10⁻⁷ cm / 10⁻⁸ S cm⁻¹ = 300 Ω cm²,
and Δφ = 3×10⁻³ A cm⁻² × 300 Ω cm² = 0.9 V.

Why the σ band is the point, not the value. Pure Li₂CO₃ is an electronic insulator with ionic
conductivity in the 10⁻⁹–10⁻⁷ S cm⁻¹ range depending on phase and microstructure, and measured SEI
conductivities span at least this band. The choice of σ inside this band changes the predicted SEI
overpotential by a factor of 100, from 90 mV to 9 V. That is not a precision problem to be narrowed; it
means the loop's driving term cannot be predicted from first principles, only measured per cell.

The cross-check that makes the band usable. A literal 0.9 V SEI drop (the σ = 10⁻⁸ case) is
incompatible with the total anode polarization of a working cell at 1C, 50–150 mV `[ASSUMED]`. A
0.9 V drop across the interphase alone would exceed the entire measured anode overpotential, which would
mean the anode was already plating at cycle 1 in every cell ever measured. It is not. Therefore the
effective σ in a functioning anode must be at or above the 10⁻⁷ S cm⁻¹ end, where Δφ_SEI ≈ 90 mV,
comparable to but not exceeding the measured polarization. `[DERIVED]` (the incompatibility argument);
`[HYPOTHESIS]` (that this reflects genuinely higher effective conductivity rather than, e.g., a thinner
effective interphase or a partially non-ohmic conduction mechanism).

Reconciling this band with the reduced model. The model of S1 adopts a fresh-cell anode
area-specific resistance of *R*₀ = 8.0 Ω cm². At *d* = 30 nm that corresponds to an effective conductivity
of 3.8 × 10⁻⁷ S cm⁻¹, marginally above the 10⁻⁷ S cm⁻¹ upper end of the band above. The two are not in
contradiction, but the difference must be stated rather than left implicit. The incompatibility argument
rules out *R*_SEI ≥ 300 Ω cm², since such a cell would plate from cycle 1; it does not fix *R*_SEI below
that. A functioning anode with *R*_SEI ≈ 8 Ω cm² is equally consistent with a thinner effective film
(≈ 8 nm at 10⁻⁷ S cm⁻¹) or with a more conductive one (≈ 4 × 10⁻⁷ S cm⁻¹ at 30 nm), and the
measurements available do not separate the two. The reduced model therefore takes *R*₀ as a lumped
parameter and does not commit to a thickness–conductivity pair. What it requires of S2.1 is only that
*R*₀ sit below *R*\*, which the band permits.

What the result supports, and what it does not. It supports the sign and the scale: the interphase
drop is of the same order as the margin between the anode operating potential and 0 V vs Li/Li⁺ (Δ ≈ 90 mV, from the Δφ_SEI = 90 mV case in S2.1), so the interphase resistance is a plausible control on plating onset, which is what Loop A
requires. It does not support any prediction of when a given cell will plate from its SEI thickness
alone (S1.10, items 1 and 7).

**Uncertainty.** σ is unknown to ±2 orders of magnitude, so Δφ_SEI is unknown to ±2 orders. The
ordering (interphase drop comparable to the plating margin) is robust; the value is not. The quantity is
therefore always reported as “comparable to” and never as a single number without its range.

---

## S2.2 The plating threshold *R*\* and the inverse problem

Section S2.1 gave the interphase resistance as a range four orders of magnitude wide, which is useless as
a design number. This section turns the relation around. Instead of asking how resistive a given
interphase is, ask what resistance would be *just enough* to start plating at a given current density. That
inverted quantity is the plating threshold *R*\*, and unlike the resistance itself it depends only on
operating variables.

**The derivation.** Plating requires the anode potential to fall below 0 V vs Li/Li⁺. Starting from an
operating anode potential Δ above 0 V and subtracting the charge-transfer overpotential *η*_ct and the
ohmic drop *j·R*, the anode reaches 0 V when

$$j\,R + \eta_{\text{ct}} = \Delta \quad\Longrightarrow\quad R^{*} = \frac{\Delta - \eta_{\text{ct}}}{j} \tag{S2.E3}$$

`[DERIVED]`. Note the dimensional check: (V − V)/(A cm⁻²) = Ω cm². At 1C with Δ = 90 mV, *η*_ct = 30 mV,
*j* = 3.0 × 10⁻³ A cm⁻²: *R*\* = 0.060 V / 0.0030 A cm⁻² = 20.0 Ω cm². The headroom is Δ − *η*_ct = 60 mV.

The equation that does the most work in this analysis. Rearranged, it converts an observable — a
resistance at which plating begins — into an *operating variable*, and shows what it does not depend on:

$$R^{*}(j) = \frac{60\ \text{mV}}{j} \tag{S2.E4}$$

so *R*\* falls as 1/*j*: 40.0 Ω cm² at 0.5C, 20.0 at 1C, 13.3 at 1.5C, 10.0 at 2C, 8.0 at 2.5C. No tabulated materials constant appears, though Δ itself is set by the anode material (S1.16). A cell
plates when its interphase resistance exceeds a rate-dependent threshold, which is why onset is a design
variable rather than a property value.

**The inverse problem: the interphase thickness corresponding to *R*\*.** Combining the resistance expression of S2.1 with the
threshold gives the *critical thickness*

$$d^{*} = \sigma\,R^{*} = \frac{\sigma\,(\Delta - \eta_{\text{ct}})}{j} \tag{S2.E5}$$

Evaluating at 1C (*R*\* = 20 Ω cm²) across the same σ band:

| σ (S cm⁻¹) | *d*\* = σ·*R*\* (nm) | Interpretation |
|---|---|---|
| 10⁻⁷ | 20 | ~20 nm of interphase is enough to trigger plating at 1C |
| 10⁻⁸ | 2 | 2 nm suffices — below a single monolayer's worth of compact SEI |
| 10⁻⁹ | 0.2 | sub-nanometer — physically implausible for a continuous film |

`[DERIVED]`. The result is informative because it converts an abstract threshold into a length: at the upper end of the conductivity band, a mere 20 nm of interphase
is sufficient to push a 1C cell into plating, and that is within the 10–200 nm a SEI reaches after formation. The threshold is not a distant failure mode; it is a near-term one. Conversely the
σ = 10⁻⁹ row is *self-refuting*: sub-nanometer continuous films do not exist, which is independent
evidence that the effective conductivity cannot be at the bottom of the band. This corroborates the
polarization cross-check in S2.1 from a completely different direction, and the two together are the
support available for the σ-band argument.

**Caveat.** *d*\* inherits every uncertainty of both *R*\* (a lumped single-Δ, single-*R* approximation) and
σ (two orders of magnitude). It is useful as a scaling statement (d* ∝ 1/j, so doubling the rate halves the interphase thickness
needed to plate) and should not be quoted as a number for a specific cell.

---

## S2.3 SEI volume and the pore-filling threshold

This is the derivation that connects Loop A to Loop C: interphase growth does not merely add resistance, it
**consumes anode pore volume**, and there is a finite amount of it. The link is a mass balance.

**Step 1 — charge to moles.** Reducing one Li⁺ and incorporating it into a typical SEI component consumes
one electron per Li (for Li₂CO₃, two Li per two electrons, the 1:1 ratio holds). One mAh cm⁻² is
10⁻³ A × 3600 s = 3.6 C cm⁻², so

$$n_{\text{SEI}} = \frac{3.6}{96485} = 3.73\times10^{-5}\ \text{mol cm}^{-2}\ \text{per mAh cm}^{-2} \tag{S2.E6}$$

`[DERIVED]`. Using *F* = 96485 C mol⁻¹.

**Step 2 — moles to volume.** With a representative SEI molar volume *V*_m ≈ 30 cm³ mol⁻¹:

$$t_{\text{SEI per mAh}} = 3.73\times10^{-5}\ \text{mol cm}^{-2} \times 30\ \text{cm}^{3}\ \text{mol}^{-1} = 1.12\times10^{-3}\ \text{cm} = \mathbf{11.2\ \mu m} \tag{S2.E7}$$

`[DERIVED]`: i.e. ~11 µm of SEI-equivalent thickness per mAh cm⁻² of lost lithium inventory.

**A labelling caution.** The 30 cm³ mol⁻¹ above is a representative value for a mixed SEI, not the
value for any single compound. The Li₂CO₃ end-member has
*V*_m = 34.8 cm³ mol⁻¹ and accordingly gives

$$3.73\times10^{-5}\times34.8\times10^{4} = \mathbf{12.9\ \mu m}\ \text{per mAh cm}^{-2} \tag{S2.E8}$$

and the plausible band *V*_m = 20–40 cm³ mol⁻¹ gives 7.4–14.8 µm. 11 µm and 12.9 µm are different
numbers answering different questions, representative SEI versus Li₂CO₃ end-member, and conflating
them is how a factor-of-1.17 discrepancy gets mistaken for a bug. The two are therefore quoted against
their own molar volumes (11 µm at 30 cm³ mol⁻¹; 12.9 µm at 34.8 cm³ mol⁻¹) and must not be interchanged.

Step 3 — volume to fraction of available pore space. Take a representative anode pore volume of
~3 µm of thickness per unit area. That figure corresponds to a coating about 10 µm thick at 30 % porosity,
which is a low-loading electrode; against a 3 mAh cm⁻² cathode it is N/P ≈ 0.13. The self-consistent
anode loading for such a cathode is ~77 µm, with ~23 µm of pore volume, and that is the case evaluated in
Step 5 below. The LLI required to fill it:

$$LLI_{\text{fill}} = \frac{3\ \mu m}{11.2\ \mu m\ \text{per}\ (\text{mAh cm}^{-2})} = \mathbf{0.27\ mAh\ cm^{-2}} \tag{S2.E9}$$

Against *Q*₀ = 3 mAh cm⁻², that is 8.9 % of capacity. `[DERIVED]`. So interphase growth alone reaches
the pore-filling limit after losing under 10 % of the cell's capacity, well before any capacity target
of 80 % retention is threatened, and therefore an order-unity margin, not a 10⁻² one.

**Step 4, the porosity correction.** The 0.27 mAh cm⁻² figure
treats the interphase as fully dense, which it is not: the SEI is 30–50 % porous `[ASSUMED]`. The correction
matters, and it must be stated with its convention, because two different porosity conventions appear in
this literature and they move the threshold in opposite directions. Stating which one is used is the
difference between a derivation and a fit.

*Convention A — effective solid volume available to block transport.* The fraction of the interphase
volume that is solid is (1 − *p*), so the thickness per mAh that actually contributes to blocking becomes
11.2 × (1 − *p*) µm. For *p* = 30–50 % this is 5.5–7.7 µm per mAh cm⁻², and

$$LLI_{\text{fill}} = \frac{3\ \mu m}{5.5\text{–}7.7\ \mu m\ \text{per}\ (\text{mAh cm}^{-2})} \approx \mathbf{0.39\text{–}0.55\ mAh\ cm^{-2}} \tag{S2.E10}$$

i.e. 13–18 % of a 3 mAh cm⁻² capacity. `[DERIVED]`.

*Convention B — geometric void filling.* If instead one asks how much solid SEI is needed to occupy a pore
of fixed geometric volume, a porous film reaches that volume with less solid, giving
3(1 − *p*)/11.2 = 0.13–0.19 mAh cm⁻², i.e. below the dense figure. `[DERIVED]`.

The two conventions differ by a factor of (1 − *p*)² ≈ 0.25–0.49, so the number is convention-dependent
while the conclusion is not. Under convention A the threshold is
0.39–0.55 mAh cm⁻²; under convention B it is 0.13–0.19; under the dense assumption it is 0.27. Every one
of these is far below 3 mAh cm⁻², by a factor of 5.5 to 23, so the claim that “interphase growth
reaches the pore-filling limit long before a capacity target of 80 % retention is threatened“ survives
either convention unchanged. The range can therefore be quoted without resolving the ambiguity.

The range adopted here: ~0.3–0.6 mAh cm⁻², i.e. ~10–20 % of capacity. This is
convention A (0.39–0.55) widened at the lower edge toward the dense case (0.27) and at the upper edge to
cover a 4 µm pore volume. Quoting only 0.27 would understate the
threshold; quoting only 0.55 would overstate the dense case; quoting convention B's 0.13–0.19 would be
defensible arithmetic but would sit below the dense case and invite the question of why porosity reduced
the requirement.

**Step 5, the self-consistent anode.** The 0.27–0.55 mAh cm⁻² thresholds above assume ~3–4 µm of pore
volume, i.e. a low-loading anode. At the *Q*₀ = 3 mAh cm⁻² used in the model of S1, the graphite anode is
~77 µm thick at 1.6 g cm⁻³ graphite density and 30 % porosity, giving ~23 µm of pore volume and an areal
capacity of ~2.06 mAh cm⁻², so N/P ≈ 0.69 against the 3 mAh cm⁻² cathode. Filling that pore volume requires

$$LLI_{\text{fill}} = \frac{23\ \mu m}{11.2\ \mu m\ \text{per}\ (\text{mAh cm}^{-2})} \approx \mathbf{2.1\ mAh\ cm^{-2}} \tag{S2.11}$$

`[DERIVED]`. That is ~68 % of *Q*₀, not ~9 %. The correction factor is the anode loading, not the SEI
porosity convention, and it is the larger of the two.

The consequence is stated plainly because it changes a conclusion. On the self-consistent anode, pore
filling is not reached until most of the capacity is gone, so it is a late-life rather than an early-life
mechanism. Loop C therefore does not close early on mechanical grounds at this loading. Whether it closes
at all depends on the porosity, and on thinner anodes the margin falls by the ratio of loadings: at a 10 µm
anode the threshold is 0.27 mAh cm⁻² and the loop closes at ~9 % loss. Both regimes are real; they differ by
the electrode design, and the range is reported here rather than a single number.

Coupling to the model. In the reduced model (S1), the coupled cell's LLI crosses 0.27 mAh cm⁻² at cycle
386, 144 cycles before its capacity knee at cycle 530. (Use the printed 0.27 rather than the
unrounded 0.2680: the cross is then at cycle 386, whereas the unrounded threshold gives 385. A reader
re-deriving from the text should reach the printed number, so the rounded value is the one quoted.) Over the
quoted range, the crossing moves from 386 (0.27) to 450 (0.39) to 513 (0.55), and the LLI ratio at the knee
is 530's LLI divided by the threshold: 2.22× on the dense basis, 1.54× at 0.39, 1.09× at 0.55. So on
any basis the pore-filling threshold is reached before the capacity knee, and the model-level statement of
“Loop A feeds Loop C” is that the interphase has already filled the pore volume by the time the capacity
curve turns over, with the margin depending on which threshold convention is used, which is itself the
reason not to quote a single number. This is a model result `[DERIVED]`, not a measurement, and it inherits
the model's parameters.

---

## S2.4 Coulombic-efficiency arithmetic and compounding laws

Coulombic efficiency is the most-quoted number in this field and the most often mis-converted into a cycle
life. Two different arithmetic laws are in use, and the same CE implies a different cycle life under
each, with the gap widening as CE falls. The section settles the arithmetic, then uses it to draw the
discriminator between the two channels that consume lithium inventory.

The inventory. Lithium inventory in a 3 mAh cm⁻² cell, expressed as a thickness of pure Li:

$$m_{\text{Li}} = 3\times10^{-3}\ \text{A h cm}^{-2}\times3600\ \text{C A}^{-1}\text{h}^{-1} / 96485 \times 6.941\ \text{g mol}^{-1} = 7.77\times10^{-4}\ \text{g cm}^{-2}$$

$$t_{\text{Li}} = \frac{7.77\times10^{-4}}{0.534} = 1.455\times10^{-3}\ \text{cm} = \mathbf{14.55\ \mu m} \tag{S2.12}$$

`[DERIVED]`, with ρ_Li = 0.534 g cm⁻³. At CE = 99.9 %, the absolute loss per cycle is
0.1 % × 14.55 µm = 14.55 nm of Li-equivalent per cycle.

Two laws, and the arithmetic of each.

- Model A — constant absolute loss per cycle. Loss is (1 − CE)·*Q* each cycle, independent of state.
  In this law the 20 %-retention life is *N*₈₀ = 0.20/(1 − CE), and full exhaustion is *N* = 1/(1 − CE).
  At 99.9 %: *N*₈₀ = 200 cycles, exhaustion = 1000 cycles.
- Model B — compounding (exponential) loss. Retained capacity is the CE raised to the cycle count,
  so the CE compounds. Then *N*₈₀ = ln 0.8/ln CE, and
  exhaustion is *N* = ln 0.01/ln CE. At 99.9 %: *N*₈₀ = ln 0.8/ln 0.999 = 223 cycles, exhaustion =
  **4603 cycles**.

`[DERIVED]`: all four numbers.

**The comparison, which is the point:**

| CE | *N*₈₀, constant-loss | *N*₈₀, compounding | ratio | Exhaustion, constant | Exhaustion, compounding | ratio |
|---|---|---|---|---|---|---|
| 99.90 % | 200 | 223 | 1.12 | 1000 | 4603 | 4.60 |
| 99.95 % | 400 | 446 | 1.12 | 2000 | 9208 | 4.60 |
| 99.98 % | 1000 | 1116 | 1.12 | 5000 | 23024 | 4.60 |
| 99.99 % | 2000 | 2231 | 1.12 | 10000 | 46049 | 4.60 |

The conclusions conflict.

1. For 80 %-retention claims the law barely matters, the two models agree within 11.6 % at every CE
   in the table. So a paper that says “CE = 99.9 % gives ~200 cycles to 80 % retention” is safe under
   either law, PROVIDED it says 80 % retention. This is the common case and the risk is low.
2. For “exhaustion” or “infinite-life” claims the law dominates by a factor of 4.6. A 99.9 % cell is
   exhausted at 1000 cycles under constant loss but survives 4603 under compounding. Anyone quoting a
   cycle count at a given CE must state which law is assumed, because the number can be wrong by 4.6×
   without any arithmetic error. A figure of “1000 cycles at 99.9 % CE” is a statement about one assumed
   law, not a measurement of cycle life.

The CE required for a target life. Inverting Model B for *N* cycles at 80 % retention gives a required CE equal to the *N*-th root of 0.8:

| Target life (cycles) | Required CE, Model B | Required CE, Model A | Difference |
|---|---|---|---|
| 200 | 99.8885 % | 99.9000 % | 0.0115 pp |
| 500 | 99.9554 % | 99.9600 % | 0.0046 pp |
| 1000 | 99.9777 % | 99.9800 % | 0.0023 pp |
| 2000 | 99.9888 % | 99.9900 % | 0.0012 pp |

`[DERIVED]`. The two laws agree to within 0.012 percentage points, far below any real CE measurement's
precision (state-of-the-art precision coulometry reaches ~0.001 pp, so this difference is at the edge of
resolvability but not practically important). The practical message: to reach 1000 cycles at 80 %
retention requires CE ≥ 99.978 %, which is a requirement most cells fail. That is a much more useful
statement than any cycle-count prediction, because it is a specification against which a design can be checked.

**Why this matters.** Loop A's parasitic current is the physical origin of CE
loss, so the CE requirement is the quantitative bridge between the mechanism (interphase growth) and the
performance target (cycle life). It also sets the scale for Loop D: 99.978 % CE on a 3.0 mAh cm⁻²
electrode means 0.66 µAh cm⁻² of charge lost per cycle, which on the 11 µm/mAh basis of S2.3 is
**~7.3 nm of interphase per cycle**. That is the number to compare with Loop B's dissolution budget and
Loop D's salt budget.

The discriminator between the two loss channels. Losing a charge *Q* can occur either as dead
lithium or as SEI. The two channels differ in the thickness of material they consume per unit of charge:

- Dead lithium, at 1:1 Li, consumes 4.85 µm per mAh cm⁻² of inventory, from ρ_Li and *M*_Li.
- SEI formation consumes 11 µm per mAh cm⁻² on the molar-volume basis of S2.3.

Both channels scale linearly with the charge lost, so their ratio does not depend on CE: 11/4.85 =
**2.27×**. The two channels are therefore of the same order, with SEI consuming about twice the
thickness per unit of inventory lost. A thickness basis ten times smaller would instead give 22×, which
would argue the opposite, namely one channel dominant. The 11 µm/mAh basis above is the one used, and the
discriminator is ~2.3×.

---

## S2.5 Loop B: the catalytic versus stoichiometric shortfall (~74×)

Loop B claims that dissolved transition metal poisons the anode, raises the local overpotential, and so
drives further dissolution. That claim runs into an immediate objection: dissolution is a stoichiometric
process, one metal ion per dissolution event, so a small amount of manganese cannot in itself catalyze
anything. The resolution is that the constraint is not the amount of manganese but its turnover - how
many times each ion can cycle between cathode and anode. This section computes the shortfall between a
stoichiometric account and the dissolution rate that Loop B requires.

**Step 1, the Mn inventory.** For a 20 mg cm⁻² cathode at 20 wt % Mn (NMC-class), with *M*_Mn = 54.94
g mol⁻¹:

$$n_{\text{Mn}} = \frac{20\times10^{-3}\times0.20}{54.94} = 7.28\times10^{-5}\ \text{mol cm}^{-2} = \mathbf{72.8\ \mu mol\ cm^{-2}} \tag{S2.13}$$

`[DERIVED]`.

Step 2 — how much actually dissolves over a realistic life. Measured dissolution rates in NMC cells
are of order 5 ppm of the cathode's Mn per cycle (`[ASSUMED]`, an order-of-magnitude figure; no single
published value is quoted). Over 1000 cycles:

$$n_{\text{dissolved}} = 7.28\times10^{-5}\times5\times10^{-6}\times1000 = 3.64\times10^{-7}\ \text{mol cm}^{-2} = \mathbf{0.364\ \mu mol\ cm^{-2}} \tag{S2.14}$$

As a fraction of inventory: 3.64×10⁻⁷/7.28×10⁻⁵ = 0.50 %. `[DERIVED]`.

**Step 3, the shortfall.** A cell targeting 20 % capacity loss over that 1000 cycles loses
0.20 × 3 mAh cm⁻² = 0.6 mAh cm⁻² of inventory, which is 0.6 × 3.73×10⁻⁵ = 2.24×10⁻⁵ mol cm⁻². Compare
with the 3.64×10⁻⁷ mol cm⁻² of Mn that actually dissolved:

$$\frac{\text{loss to be explained}}{\text{Mn dissolved}} = \frac{0.6\ \text{mAh cm}^{-2}}{0.50\%\ \text{of Mn}}:\quad \frac{20\%}{0.50\%} = \mathbf{40\times} \tag{S2.15}$$

`[DERIVED]`. Dissolved Mn accounts for ~2.5 % of the capacity loss it is supposed to cause.

Reconciling 40× with 74×, the denominators differ. The 40× above is a percentage ratio: 20 % capacity
loss against 0.50 % of the Mn inventory. But Mn is not the only inventory in play, and comparing a fraction
of Mn against a fraction of capacity mixes two denominators. On a mole-for-mole basis: the Mn inventory
(7.281×10⁻⁵ mol cm⁻²) is only 54.2 % of the Li inventory (1.3432×10⁻⁴ mol cm⁻² at 3.6 mAh cm⁻²;
Li/Mn = 1.845). The 3.6 mAh cm⁻² basis is the high-energy cell this section uses, and it is the basis on
which Li/Mn = 1.845 is quoted; the reduced model's reference cell in S1 is 3.0 mAh cm⁻². Each departing
Mn²⁺ destroys one Li⁺, so the dissolved Mn removes 0.50 % × 0.542 = 0.271 % of the Li inventory.
Against a 20 % capacity loss the shortfall is 0.20 / 0.00271 = 73.8×, i.e. ~74×. On the 3.0 mAh cm⁻²
basis the same arithmetic gives 61.5×, and the conclusion is unchanged either way: the shortfall is two
orders of magnitude, so dissolution cannot be stoichiometrically sufficient. The 40× figure is arithmetically correct but is not the physical
shortfall; the mole-for-mole ratio is what the turnover argument below must close. `[DERIVED]`.

How the loop closes the gap is set out below. The ~74× mole-for-mole gap is the whole reason Loop B must be
catalytic rather than stoichiometric. A Mn²⁺ ion that deposits on the anode is not consumed by doing so:
it sits in the SEI, raises its electronic conductivity, and, critically, can be re-released into solution
as the SEI is rebuilt, depositing again elsewhere. Each deposited ion can therefore poison more than one
site over the cell's life, and the relevant quantity is a turnover number, not a concentration. If each
Mn ion cycles through the anode ~74 times over 1000 cycles, a turnover every ~14 cycles, which is
plausible for an ion exchanging between SEI and electrolyte as the interphase is continuously rebuilt.
The budget then closes. `[HYPOTHESIS]`: the turnover number is not established in the literature; the
derivation shows only that a modest turnover suffices, which is a far weaker and much more defensible
claim than asserting a specific catalytic mechanism.

**The supported claim, and its limit.** The supported statement is that *a stoichiometric accounting falls
short by ~74×, so dissolution must act catalytically if it matters at all — a testable claim rather than
an assumption.* The catalytic mechanism is not established, and no turnover number is quoted as measured.
The admissible form of Loop B is therefore a conditional: if dissolution causes a substantial share of
fade, it does so catalytically, and the required turnover is ~74. That conditional is falsifiable, and
S4's branch B7 sets out the experiment (HF scavenger) that tests it.

**Sensitivity.** The shortfall scales as 1/(dissolution rate): 2 ppm/cycle gives 184× rather than 74×,
and 20 ppm/cycle gives 18×. The *order of magnitude* (tens, not units) is robust across the plausible range, which
is all the argument needs. The claim would fail only at ~200 ppm/cycle, which would
mean 20 % of the cathode's Mn dissolving in 1000 cycles, a catastrophic degradation mode inconsistent with
the cells in which Loop B is invoked.

---

## S2.6 Loop D: the salt-inventory budget

A lean cell contains only a few microliters of electrolyte per square centimeter, and every lithium atom
that enters the interphase takes electrolyte with it. Loop D claims that this consumption reaches a wall
before the capacity target does. Unlike Loops A to C, the argument here is a budget: total what will be
consumed over the cell's life and compare it with what is present at the start. The margin turns out to be
about a factor of 9, and, more usefully, it depends entirely on cell format.

Step 1, the consumption per unit LLI. Reducing Li⁺ to form SEI consumes ~1 Li per electron, so

$$n_{\text{per mAh}} = \frac{3.6\ \text{C cm}^{-2}}{96485\ \text{C mol}^{-1}} = 3.73\times10^{-5}\ \text{mol cm}^{-2}\ \text{per mAh cm}^{-2} \tag{S2.16}$$

`[DERIVED]` (the same constant as S2.3; the Faraday arithmetic appears in Loops A/C/D, so one
conversion underlies three of the four loops).

For a 4 mAh cm⁻² cell (a larger format than S1's 3.0 mAh cm⁻² reference, chosen so the budget is stressed) losing 20 % over its life, LLI ≈ 0.8 mAh cm⁻², so

$$n_{\text{consumed}} = 0.8 \times 3.73\times10^{-5} = 2.98\times10^{-5}\ \text{mol cm}^{-2} = \mathbf{29.8\ \mu mol\ cm^{-2}} \tag{S2.17}$$

`[DERIVED]`.

**Step 2, the inventory present.** At a lean electrolyte loading of 1 g Ah⁻¹ for a 4 mAh cm⁻² electrode:

$$m_{\text{elec}} = 4\times10^{-3}\ \text{Ah cm}^{-2}\times1\ \text{g Ah}^{-1} = 4\times10^{-3}\ \text{g cm}^{-2}$$
$$V_{\text{elec}} = \frac{4\times10^{-3}}{1.2} = 3.33\times10^{-3}\ \text{cm}^{3}\ \text{cm}^{-2} = \mathbf{3.33\ \mu L\ cm^{-2}} \tag{S2.18}$$

`[DERIVED]`, with ρ_electrolyte ≈ 1.2 g cm⁻³. Applying 1 M salt and ~12 M total solvent+anion species:

$$n_{\text{Li+}} = 1\ \text{mol L}^{-1}\times3.33\times10^{-6}\ \text{L cm}^{-2} = \mathbf{3.33\ \mu mol\ cm^{-2}} \tag{S2.19}$$
$$n_{\text{total}} = 12\ \text{mol L}^{-1}\times3.33\times10^{-6}\ \text{L cm}^{-2} = \mathbf{40\ \mu mol\ cm^{-2}} \tag{S2.20}$$

**Step 3, the budget:**

| Inventory | Present (µmol cm⁻²) | Consumed for 0.8 mAh cm⁻² LLI (µmol cm⁻²) | Consumed/present |
|---|---|---|---|
| Li⁺ salt only | 3.33 | 29.8 | 8.95× |
| Total electrolyte species | 40 | 29.8 | 0.75 |

`[DERIVED]`. The Li⁺ salt inventory is exceeded almost ninefold by the lithium projected to be lost, and even the
total electrolyte inventory is 75 % consumed. Salt depletion is therefore not a second-order correction
at long life; it is a hard limit.

**The principal caveat.** The 1:1 Li-to-electrolyte stoichiometry is an upper
bound: some SEI components consume Li without consuming a separate solvent molecule (LiF from LiPF₆),
and some electrolyte is consumed without consuming Li. The ~9× ratio is therefore an order-of-magnitude
result. The argument is nonetheless robust to the caveat: even a 3× overestimate leaves a ratio of ~3×,
which is still enough to make Loop D first-order. The conclusion does not depend on the stoichiometric
detail. `[DERIVED]` for the ratio;
`[HYPOTHESIS]` for the 1:1 stoichiometry as a model of real SEI chemistry.

**The format dependence, the practical payoff.** A flooded coin cell with 50 µL of electrolyte instead of
3.33 µL cm⁻² has 15× more absolute inventory (50/3.33). So the same chemistry that is salt-starved in a
lean pouch cell is salt-rich in a flooded coin cell, and coin-cell data cannot be extrapolated to pouch
cells on this axis. This explains, with no new chemistry, why “electrolyte volume” changes knee position
without changing the initial fade slope, and why thick high-areal-capacity electrodes are systematically
worse. It also gives S4's branch B5 its discriminator: a Loop-D-limited cell improves when flooded; a
genuinely M4-limited cell does not.

---

## S2.7 Loop C: diffusion-induced stress

Cracking a secondary particle exposes fresh surface, interphase grows on it, and the interphase then
becomes load-bearing and changes the local mechanical constraint. Loop C claims that the stress driving
this process is of the same order as the stress the particle can withstand, so fracture is neither
impossible nor guaranteed. The derivation has to be careful about which stress it computes, because two
very different numbers are in play, and they are easily conflated.

**Step 1, the concentration swing.** For layered NMC the molar volume is *V*_m ≈ 19.4 × 10⁻⁶ m³ mol⁻¹, so
the maximum Li concentration change is

$$\Delta c_{\max} = \frac{1}{V_m} = \frac{1}{19.4\times10^{-6}} = 5.15\times10^{4}\ \text{mol m}^{-3} = \mathbf{0.0515\ mol\ cm^{-3}} \tag{S2.21}$$

`[DERIVED]`. A value of 0.048 mol cm⁻³ is adopted here, a ~7 % reduction reflecting the fact that not
the full molar volume participates in a given cycle's swing. Both are correct answers to slightly
different questions; 0.048 is the figure used downstream.

Step 2, the elastic upper bound, which is NOT the fracture-relevant number. For a spherical particle
with a composition gradient under elastic (no-relaxation) conditions, the peak hoop stress is

$$\sigma_{\max} = \frac{E\,\Omega\,\Delta c}{3(1-\nu)} \tag{S2.22}$$

With *E* = 150 GPa, Ω = 3.5 × 10⁻⁶ m³ mol⁻¹, ν = 0.3, Δ*c* = 0.048 mol cm⁻³ = 4.8 × 10⁴ mol m⁻³:

$$\sigma_{\max} = \frac{150\times10^{9}\times3.5\times10^{-6}\times4.8\times10^{4}}{3\times0.7} = \mathbf{12.0\ GPa} \tag{S2.23}$$

`[DERIVED]`. The 12.0 GPa follows from the adopted Δc = 0.048 mol cm⁻³; the unrounded 0.0515 mol cm⁻³
would give 12.9 GPa, so the choice of Δc moves the ceiling by 7 %. This is an absolute upper bound
assuming the particle behaves elastically with the full composition swing simultaneously. This is physically unreachable, because plastic/creep relaxation and finite
lithiation rates reduce it by an order of magnitude. It is useful only as a ceiling.

Step 3, the realistic stress, obtained by inverting the same relation. Measured/estimated peak
stresses in Ni-rich secondary particles are 0.5–2 GPa. The corresponding gradient fraction is

$$\frac{\Delta c_{\text{real}}}{\Delta c_{\max}} = \frac{\sigma_{\text{real}}\,3(1-\nu)}{E\,\Omega\,\Delta c_{\max}}$$

For σ_real = 1.5 GPa: Δ*c*_real/Δ*c*_max = 1.5×10⁹ × 2.1/(150×10⁹ × 3.5×10⁻⁶ × 4.8×10⁴) = 12.5 %.
`[DERIVED]`. So a realistic 1.5 GPa stress corresponds to only ~12 % of the maximum concentration swing
being accommodated elastically at any instant, with the rest relaxed.

Step 4 — compare with the fracture stress. Using *K*_Ic = 2 MPa m^{½}, the stress required to propagate a
flaw of size *a* is σ_f = *K*_Ic/√(π*a*):

| Flaw size *a* | Fracture stress σ_f | Margin (σ_f / 0.5–1.1 GPa realistic) |
|---|---|---|
| 5 µm | 0.50 GPa | ~1 |
| 2 µm | 0.80 GPa | ~1 |
| 1 µm | 1.13 GPa | ~1 |
| 0.2 µm | 2.52 GPa | ~2–5 |

`[DERIVED]`. For realistic secondary-particle flaw sizes of 1–5 µm, the fracture stress is comparable to
the operating stress, a margin of order 1. Not 10² (safe by a wide margin) and not 10⁻² (certain to
fail), but *at the threshold*. This is the “margins are order unity” result, and it is why particle size
is a design variable with a real optimum rather than “smaller is better”:
smaller particles resist fracture (higher σ_f) but become surface-dominated and lose energy density.

The two errors this derivation is designed to prevent.
- Quoting 12 GPa as the stress. It is an elastic upper bound, not an operating stress, and quoting it
  would make fracture seem certain. The correct comparison is the 0.5–2 GPa realistic range.
- Quoting a margin of 10² or 10⁻². The Loop-C margin is ~1, which is
  what makes the coupling live rather than safely inactive.

**Uncertainty.** *K*_Ic = 2 MPa m^{½} for layered oxides is uncertain by ~2×; flaw sizes span 0.2–5 µm
(a 25× range in *a*, hence 5× in σ_f). The margin is therefore “order 1” with a spread of roughly 0.5–5,
which is the correct granularity for the claim, and stating it that way is more defensible than any single
number.

---

## S2.8 The dissolution unit ambiguity: a worked example

Most reports of transition-metal dissolution quote a concentration in ppm, which is a *dose into the
electrolyte*, while the coupling argument needs a *fraction of the cathode inventory*. The two are not
interchangeable, and the conversion depends on the cell format. This section works the conversion out, as
a cautionary example of how the same physical loss can be reported as two numbers that differ by nearly an
order of magnitude.

**The arithmetic.** For an NMC811 cathode (*M* = 97.3 g mol⁻¹) at 200 mAh g⁻¹ and 1 mAh cm⁻²:

$$m_{\text{cathode}} = \frac{1\ \text{mAh cm}^{-2}}{200\ \text{mAh g}^{-1}} = 5.0\ \text{mg cm}^{-2}$$
$$m_{\text{Mn}} = 5.0\times10^{-3}\times\frac{0.1\times54.94}{97.3} = \mathbf{282\ \mu g\ cm^{-2}} \tag{S2.24}$$

`[DERIVED]`. A 1 % Mn loss is therefore 2.82 µg cm⁻² = 0.051 µmol cm⁻².

**Now express that loss as a concentration — in two different cells:**

| Cell format | Electrolyte | 1 % Mn loss → | 100 ppm dose as fraction of Mn inventory |
|---|---|---|---|
| Lean coin | 6 µL ≈ 7.2 mg | ≈ 390 ppm | ≈ 0.25 % |
| Flooded | 50 µL ≈ 60 mg | ≈ 47 ppm | ≈ 2.1 % |

`[DERIVED]`. Arithmetic for the first row: 2.82 µg / 7.2 mg = 2.82×10⁻⁶ g / 7.2×10⁻³ g = 392 ppm. For the
second: 2.82 µg / 60 mg = 47 ppm.

**Two implications follow:**

1. The same 1 % Mn loss reads as 390 ppm or 47 ppm, an 8.3× ambiguity, purely from cell design.
   Dissolution published as ppm-in-electrolyte without electrolyte volume and cathode loading is
   **not comparable across papers.** This is the reporting gap the checklist (S3) is built to
   close; it is quantified rather than asserted.
2. A “100 ppm” crosstalk dose means 0.25 % of the Mn inventory in a lean cell but 2.1 % in a flooded
   one, an 8× range in what the same nominal dose delivers. The consequence is that the standard
   crosstalk experiment is not a gentle probe; in a flooded cell it is a large compressed insult. And
   the direction of the inference matters: such an experiment measures the cell's sensitivity to a
   large dose, not the rate at which dissolution occurs in an unperturbed cell. Anyone using a 100 ppm
   crosstalk result to infer a dissolution rate is reading the experiment backwards.

A claim this section explicitly does NOT make. It does not convert the 100 ppm dose into “cycles'
worth of dissolution“ at a stated ppm/cycle rate, because that conversion depends on an unstated rate and
is not what the source measurement supports. The dose's
significance here is as a concentration, not as a time-compressed equivalent, and the SI keeps it that
way.

---

## S2.9 Voltage fade is arithmetic-separable from capacity fade

A fourth accounting term, thermodynamic/potential loss (TL), is adopted for energy fade, and it is claimed
to be separable from the capacity channels. That claim requires evidence, and the evidence is that the
two can move independently by large amounts.

**The measurement.** In Li-rich/Mn-rich layered oxides after 200 cycles, the midpoint-voltage drop is
**723.5–769.6 mV** while capacity retention remains high, and one sample shows a 491 mV shift. Mean
capacity fade over the same interval is far smaller than the energy-density loss those voltage numbers
imply, which reaches roughly 30 % by the arithmetic below. `[FROM LITERATURE: 10.1039/D4SC07037B]`.

The arithmetic that makes it a separability result. Energy density is the product of capacity and
average voltage. A 200-cycle capacity retention of, say, 90 % combined with a 770 mV midpoint drop from a
~3.7 V average operating voltage gives an energy retention of 0.90 × (3.7 − 0.77)/3.7 = 0.90 × 0.79 =
**71 %**, i.e. an additional 19 percentage points of energy loss that the capacity balance does not capture.
`[DERIVED]` from the stated retention and voltage figures; illustrative capacity retention value, since
the relevant quantity is the order of magnitude.

Why this forces a fourth term rather than a fudge. Folding a 19 pp energy loss into the kinetic
(impedance) channel would double-count it against the EIS measurement in S4 branch B5, which measures a
resistive loss that is physically distinct from a thermodynamic potential shift. The two are measured by
different instruments and have different temperature dependences. So the LLI/LAM/KL triple is complete for
capacity and incomplete for energy, and TL is required, with the explicit scope statement that TL is
energy-only and does not enter the capacity balance. `[HYPOTHESIS]` for the ontology (that TL is the right
fourth term); `[DERIVED]` for the arithmetic showing the two fades are quantitatively separable.

**The scope limitation.** Three of the four loops (A, B, C) operate on the capacity balance; TL is outside
the loop framework entirely. The loop framework is therefore restricted to the capacity channels, and
voltage fade remains a named open problem; the four loops are not a complete account. S2.9 and S4's B6
branch both carry this caveat.

---

## S2.10 Summary of the ratios

| Quantity | Derivation | Value | Uncertainty |
|---|---|---|---|
| SEI ohmic drop at 1C, σ = 10⁻⁷ S cm⁻¹ | S2.1 | ~90 mV | ±2 orders (σ) |
| SEI-drop / anode-polarization cross-check | S2.1 | 0.9 V would exceed measured 50–150 mV | qualitative, robust |
| Plating threshold *R*\* at 1C | S2.2 | 20.0 Ω cm² | ±(Δ, *η*_ct definition) |
| Critical interphase thickness *d*\* at 1C | S2.2 | 20 / 2 / 0.2 nm (σ = 10⁻⁷/10⁻⁸/10⁻⁹) | ±2 orders |
| SEI-equivalent thickness per mAh cm⁻² | S2.3 | ~11.2 µm (30 cm³ mol⁻¹); 12.9 µm (Li₂CO₃) | ~±30 % (*V*_m) |
| Pore-filling LLI threshold | S2.3 | 0.27 mAh cm⁻² dense; 0.3–0.6 (10–20 %) with porosity | ±2× (pore volume; 2 conventions, S2.3) |
| Model LLI crosses pore-fill threshold | S2.3 | cycle 386, 144 cycles before the knee at 530 (LLI 0.27 vs 0.6 mAh cm⁻², 2.22×) | inherits S1 parameters |
| Li inventory thickness at 3 mAh cm⁻² | S2.4 | 14.55 µm | exact |
| CE required for 1000 cycles at 80 % | S2.4 | 99.978 % | law-independent to 0.002 pp |
| CE-law ambiguity in exhaustion life | S2.4 | 4.60× | exact |
| Dead-Li versus SEI discriminator | S2.4 | 2.27× (not 22×) | relies on the 11 µm/mAh molar-volume basis |
| Loop B shortfall (catalytic requirement) | S2.5 | ~74× | ±2× (dissolution rate) |
| Loop D Li⁺ salt budget | S2.6 | ~9× overdrawn | ±3× (stoichiometry) |
| Loop D format dependence | S2.6 | 15× (flooded vs lean) | exact |
| Loop C Δ*c*_max | S2.7 | 0.0515 (adopt 0.048) mol cm⁻³ | ±5 % |
| Loop C elastic upper bound | S2.7 | 12.9 GPa (quoted 12) | ceiling only |
| Loop C realistic stress vs fracture stress | S2.7 | 0.5–2 GPa vs 0.5–1.1 GPa → margin ~1 | ±2× (*K*_Ic), 0.5–5 |
| M3 ppm ambiguity | S2.8 | 390 vs 47 ppm (8.3×; the 8.4× below is the inventory fraction, a different ratio) | exact |
| M3 100 ppm dose as inventory fraction | S2.8 | 0.25 % vs 2.1 % (8.4×) | exact |
| Voltage-fade energy gap after 200 cycles | S2.9 | 723.5–769.6 mV → ~19 pp energy | ±(illustrative retention) |

**The claim these support.** Every ratio in the table that is a *coupling margin*, that is, SEI drop against
plating margin, pore fill against capacity, and the Loop B, Loop D and Loop C margins, lands between
roughly 1 and 100. None is of order 10⁻² and none is of order 10⁴. That clustering is the central
quantitative observation: the margins are all of order unity, which is why the mechanisms are
simultaneously active and why modeling them as independent terms is not a small approximation. It is also why design has implicitly optimized toward
several thresholds at once — enough SEI to passivate but not enough to fill pores, particles small enough
to resist fracture but not so small as to be surface-dominated, electrolyte enough to last but not so much
as to be a penalty. Coupled degradation is the price of that optimization.

**What would falsify the claim.** A single coupling whose margin is 10⁻³ (irrelevant) or 10⁴
(overwhelming) would break the symmetry of the argument. The Loop-B ~74× is the largest ratio in the table
and it is the weakest link: if dissolution rates were ~200 ppm/cycle the required turnover would collapse
to ~1.8 and Loop B would be near-stoichiometric, which would weaken but not destroy the framework (Loops A,
C, D are independent of it). This limit is stated explicitly because it bounds the framework.
