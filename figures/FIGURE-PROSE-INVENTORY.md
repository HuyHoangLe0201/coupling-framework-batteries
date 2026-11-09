# FIGURE-PROSE INVENTORY — what the prose locks about the single main figure

> ## SNAPSHOT — superseded on 2026-11-06. Read the banner, then read the rows as history.
>
> This inventory was prepared **before** the figure was rebuilt. The rebuild happened, and it
> went further than a redesign: the paper's figure became a **mechanism figure with four panels
> (a)–(d)**, and the two computed panels this document catalogues — the bifurcation plot and the
> operating map — were **removed from the artwork** because they were results. `figmaster.py` is
> retired; the live builder is `figmech.py`.
>
> **What is still true:** the colour semantics, the source/sink double encoding, the two named
> rails and their sub-labels, the 74× guard-lock, the canvas size, the grayscale requirement, the
> no-AI-imagery rule, and the "no number without a source" rule. Those survived the rebuild
> unchanged, and they are still binding.
>
> **What is now false:** every row that says "three panels", that names panel (b) as the
> bifurcation or panel (c) as the operating map, or that quotes a caption listing only (a)–(c).
> The current specification is `10-si/S5-figure-specs.md`; where this document and that one
> disagree, S5 wins, because S5 is maintained and this is a snapshot.
>
> The rows are left in their original wording on purpose: they are the evidence of what the
> artwork was asked to satisfy at the time, and rewriting them would destroy that record.

**Purpose:** read-only survey, prepared for a planned redesign of `11-figures/figmaster.py`
(fewer text annotations, different shapes, new layout). Everything below is quoted
verbatim from the prose that the artwork must satisfy. Where prose and the built figure
already disagree, that is flagged rather than resolved.

**Status of the redesign (2026-11-06):** executed, and overtaken by a later instruction. The
figure is now a **four-panel mechanism figure** drawn by `figmech.py`; it contains no computed
curve and no plotted quantity. Rows below that describe a three-panel figure describe the
**retired** one.

**Scope searched:** all of `research/**.md` (~34 files), plus the figure builders' own
README/VISUAL-DEFECTS. Line numbers are as of 2026-11-05.

> **Companion document — read both before the redesign.** `research/11-figures/AUDIT-CONSTRAINTS.md`
> inventories what the **eleven check scripts** impose (source-regex assertions on
> `panel_a`/`panel_b`/`panel_c` names, required filenames and dimensions, the 6 pt measurement
> path, `REG` keys, glyph bans, printed-string gate tokens, and a ranked pre-flight checklist).
> **This file covers the other half: what the prose locks.** The split is deliberate — the two
> failure surfaces are disjoint. `AUDIT-CONSTRAINTS.md` §10 states outright: *"Whether the figure
> still matches the manuscript prose. No check cross-references `research/08-manuscript/manuscript.md`
> against `figmaster.py`."* **Nothing enforces the constraints in this file except a human reader,
> which is why they are written down.**

**Sources that carry no figure constraint** (checked, nothing found): `02-journal-fit/*`
(except the TOC dimension spec reached via S5.5), `04-literature/*`, `05-gap-and-methods/*`
(they constrain *content*, not layout — see §3 note), `09-submission/coi-statement.md`,
`data-availability-statement.md` (names the builders, no layout prose), `title-page.md`.

---

## (1) FULL VERBATIM FIGURE 1 CAPTION

`research/08-manuscript/manuscript.md:145` — identical at
`research/08-manuscript/_manuscript.src.md:145` (confirmed byte-identical wording):

> **Figure 1.** Four loops, one circuit, one knee. (a) Dissolution (M3) and fracture (M4) are sources manufacturing reactive surface; interphase growth (M1) and plating (M2) are sinks consuming lithium inventory and surface. Both feed one surface bus and one overpotential bus, the only two quantities all four loops share, so four mechanisms reduce to two state variables. Solid arrows are evidenced, dashed inferred. (b) In a reduced Loop A model, severing the coupling abolishes departure from the early power law while leaving the fade rate intact. The severed comparison requires plating onset outside the baseline window, so it holds at 0.5 and 1 C but not 2.0 C. (c) Knee onset on a C-rate and SEI-growth grid. Illustrative scaling argument, not a lifetime prediction.

### Clauses in the caption that name a visual feature the artwork must contain

| # | Caption clause (verbatim fragment) | Visual feature it requires |
|---|---|---|
| C1 | “Four loops, one circuit, one knee” | The figure must read as **one circuit** (not four parallel diagrams) and must show **a knee**. |
| C2 | “(a) Dissolution (M3) and fracture (M4) are sources manufacturing reactive surface” | Panel (a): M3 and M4 present **and labelled M3/M4 by name**, marked as **sources**. |
| C3 | “interphase growth (M1) and plating (M2) are sinks consuming lithium inventory and surface” | Panel (a): M1 and M2 present **and labelled M1/M2**, marked as **sinks**. |
| C4 | “Both feed **one** surface bus and **one** overpotential bus” | **Exactly two shared buses**, each singular. Their existence is the caption's central claim. |
| C5 | “the only two quantities all four loops share, so four mechanisms reduce to two state variables” | Both buses must be **visibly shared by all four** mechanism boxes. A layout where a mechanism bypasses a bus contradicts the caption. |
| C6 | “**Solid arrows are evidenced, dashed inferred**” | The **solid/dashed distinction must be visible in the artwork**, and legible as a grammar. This is stated in the caption, so no separate legend is strictly required — but the distinction itself is mandatory. |
| C7 | “(b) In a reduced Loop A model, severing the coupling abolishes departure … while leaving the fade rate intact” | Panel (b): **two curves** — coupled and severed — from a shared baseline. Abolition plus preserved fade rate must be visually separable. |
| C8 | “The severed comparison requires plating onset outside the baseline window, so it holds at 0.5 and 1 C but not 2.0 C” | The **C-rate restriction must appear** — in caption (already) and, per S5.2, as the `2.0 C` provenance. A redesign must not remove the panel's C-rate provenance. |
| C9 | “(c) Knee onset on a **C-rate and SEI-growth grid**” | Panel (c): a **2-axis grid** (C-rate × SEI-growth factor), not a single-axis plot. |
| C10 | “Illustrative scaling argument, not a lifetime prediction” | The **“illustrative” disclaimer must be on or beside the artwork** — S5.4 line 2 makes it a mandatory footnote. |
| C11 | Title: “Four loops, one circuit, one knee” | The **word “loop(s)” is in the caption title**, so loop letters A–D need not be drawn for the caption to be true — but see §2, which is the real constraint. |

---

## (2) LOOP A–D DEFINITIONS — the critical sub-question

### 2.0 THE HEADLINE FINDING

**The letters A–D are NOT attached to mechanisms M1–M4, and they are NOT attached to
edges in a 1:1 way. They name *closed feedback pathways*, each of which traverses two or
more mechanisms.** Any redesign that treats “badge A on M1” as its meaning will be wrong.

The authoritative definitions, all agreeing on pathway content:

| Loop | Pathway (verbatim heading) | Mechanisms it traverses | Node it shares |
|---|---|---|---|
| **A** | “Plating → dead Li → more SEI → higher local overpotential → more plating” | **M2 → M1 → M2** | overpotential (with D) |
| **B** | “Cathode dissolution → anode poisoning → SEI destabilisation → more LLI” | **M3 → M1 → M3** | fresh surface (with C) |
| **C** | “Fracture → fresh surface → SEI growth → local stress → more fracture” | **M4 → M1 → M4** | fresh surface (with B) |
| **D** | “Electrolyte depletion / salt consumption → transport limitation → local overpotential → more plating and more SEI” | **bulk/context → M2 + M1** (no dedicated box) | overpotential (with A) |

### 2.1 The definitions, with verbatim quotes

**`research/01-scope/coupling-framework.md` — the governing definitions (headings verbatim)**

- L83: `### Loop A — Plating → dead Li → more SEI → higher local overpotential → more plating`
- L92: `### Loop B — Cathode dissolution → anode poisoning → SEI destabilisation → more LLI`
- L100: `### Loop C — Fracture → fresh surface → SEI growth → local stress → more fracture`
- L108: `### Loop D — Electrolyte depletion / salt consumption → transport limitation → local overpotential → more plating and more SEI`

**`research/01-scope/coupling-framework.md:117` — the structural claim tying letters to buses:**

> A and D share the overpotential node. B and C share the “fresh surface” node. The system therefore has two effective state variables that are driven by four mechanisms:

**`research/08-manuscript/manuscript.md` — the §4 definitions as the reader meets them**

- L59: `**Loop A. Plating → dead lithium → more interphase → higher local overpotential → more plating.**` … “The loop closes when *R*_SEI > *R*\* ≡ (Δ − η_ct)/*j*” … `**[well supported]**`
- L61: `**Loop B. Dissolution → anode poisoning → interphase destabilization → more inventory loss.**` … `**[supported]**`
- L63: `**Loop C. Fracture → fresh surface → interphase growth → local stress → more fracture.**` … `**[well supported]**`
- L65: `**Loop D. Electrolyte depletion → transport limitation → higher local overpotential → more plating and more interphase.**` … `**[mechanism supported; feedback untested]**`

**`research/08-manuscript/manuscript.md:73` — which loop a given condition selects (this is the sentence that assigns loops to *physics*, not to boxes):**

> Which loop reaches the boundary first is set by operating conditions rather than by chemistry: high rate and low temperature select Loop A, high voltage and a manganese-rich cathode select Loop B, high stack pressure or large polycrystals select Loop C, thick electrodes and lean electrolyte select Loop D.

**`research/06-proposal/figure-plan.md` — the richest statement of what each badge marks (verbatim, L79–L83). This is the closest thing to a drawing brief for the badges:**

> **Four loops, drawn as closed arrows with a consistent arrow grammar:**
> - **Loop A (green solid, thick):** M2 → dead Li → M1 (more interphase on dead Li) → ↑η_loc → M2. Annotate closure condition in small type: *“closes when Δη per cycle > margin to 0 V vs. Li/Li⁺”*.
> - **Loop B (green solid, medium):** M3 → TM²⁺/³⁺ crossover (draw a dotted ion track *through the separator*, the only loop that physically crosses the cell) → anode interphase → ↑parasitic current → ↑LLI, and back to M3 via acid regenerated at the anode. Annotate *“autocatalytic in HF — partly inferred”* with a small hollow arrow for the inferred step.
> - **Loop C (green solid, thick):** M4 → [fresh surface] → M1 → SEI volume/stress → M4. Annotate *“LAM leads LLI”*.
> - **Loop D (green dashed, thin — deliberately weaker):** [electrolyte inventory] → ↓salt transport → ↑η_loc → M2, and → ↑cathode potential → M3. Annotate *“emerging — least direct evidence”*.

**`research/10-si/S5-figure-specs.md:160–173` — where each badge actually sits on the artwork (the built meaning).** This is the operative drawing spec:

> | Badge | Position | Which edge it marks |
> |---|---|---|
> | **A** | (0.700, 0.391) | M2 → eta: plating raises the driving force |
> | **B** | (0.246, 0.790) | M3 → surface: dissolution feeds poisoning |
> | **C** | (0.590, 0.790) | M4 → surface: fracture feeds interphase |
> | **D** | (0.772, 0.148) | **Owns no mechanism box** — it is a cell-level condition, so it enters from below as an explicitly *inferred* input: a **dashed** arrow (0.772, 0.190) → (0.772, 0.268) labelled “electrolyte depletion” 6.1 pt italic green |

> **Put no numeric gain on any badge.** The reduced model does not compute a physical loop gain for a real cell, and any number would be misread as a prediction. If a number is ever added it must be labelled *illustrative*.

**`research/10-si/S4-decision-tree.md:138` — the one place the *parallel-sink* reading is stated in prose (a layout claim):**

> Note that Figure 1 panel (a) draws M1 and M2 as **parallel sinks**, both feeding the shared overpotential

**`research/09-submission/toc-graphic.md:59` and `:119` — the TOC carries the same letters:**

> | **A**, **B**, **C**, **D** | on the connector arrows | the four loops, letters only |

> | **Loop badges** | A–D on the connector arrows | same |

### 2.2 What breaks if the letters are dropped

- **Nothing in the caption** — the caption never names a letter. Its title is “Four loops”, not “Loops A–D”.
- **`S4-decision-tree.md:138`** refers to “M1 and M2 as **parallel sinks**” (a topology claim, not a letter) — survives dropping letters.
- **`toc-graphic.md` §3.3** asserts the TOC shares “loop letters A–D” with the master and calls that “the point of the redraw”. Dropping letters from the master while keeping them in the TOC would **break a documented design consistency claim**.
- **`09-submission/data-availability-statement.md:26`** describes `figmaster.py` output as “(a) coupling circuit…”, no letters.
- **`figure-plan.md` L79–L83** would become stale: it is written as “draw Loop A (green solid, thick)…” etc. If letters go, that block needs a note.
- **`S5-figure-specs.md` §S5.1 “Loop badges”** would need rewriting — it is a full geometric spec of four badges.
- **Prose never uses a bare letter as a *cross-reference to the figure*.** I searched: the manuscript's only letter uses are the §4 paragraph leads (“**Loop A.** Plating → …”), which are *headings for the argument*, not figure pointers. So **the letters survive in text regardless**; the question is only whether the *artwork* repeats them.

**Recommendation for the redesign:** keeping A–D is cheap (four small glyphs) and preserves the plan/SI/TOC consistency story; dropping them requires editing `figure-plan.md` L79–83, `S5-figure-specs.md` §S5.1, and `toc-graphic.md` §3.3 in the same pass. **Dropping them from the master but not the TOC is the one option that creates a defect.**

---

## (3) EVERY OTHER PROSE CONSTRAINT

### 3.1 Panel count and panel order — **locked at three, in this order**

| File:line | Verbatim quote | What it locks |
|---|---|---|
| `08-manuscript/manuscript.md:145` | “(a) … (b) … (c) …” | **Three panels, order a→b→c.** The caption's structure is the manuscript's commitment. |
| `11-figures/README.md:3` | “**One figure, three panels, plus two TOC renders.**” | Three panels. |
| `11-figures/README.md:80-82` | “\| **(a)** \| Four mechanisms as a closed circuit … \| **(b)** \| Coupled vs severed Li-inventory loss vs cycle, log–log … \| **(c)** \| Operating map of knee-onset cycle over C-rate × SEI-growth factor…” | Content of each panel, in order. |
| `10-si/S5-figure-specs.md:187` | ““(a)” 8.6 pt bold at (0.008, 0.998)…” | Panel letter labels are drawn at a specified position. |
| `10-si/si-contents.md:48` | “Production specification for the single **Figure 1** (three panels): panel (a) coupling circuit, panel (b)…” | Three panels. |
| `09-submission/submission-checklist-final.md:122` | “\| 4.3 \| **Figure 1 — the single three-panel figure** \|” | Three panels; this is a submission gate row. |
| `09-submission/data-reporting-checklist.md:65` | “The paper has one figure with three panels: panel **(a)** is an original schematic…” | Three panels; a formal reporting declaration. |
| `09-submission/author-only-actions.md:15` | “(display items restructured: four figures → **one three-panel figure**…)” | Three panels; change history. |
| `07-final/DOSSIER.md:371` | “**One figure, three panels**, which also serves as the TOC graphic…” | Three panels — **but see the contradiction in §3.6**. |
| `10-si/S5-figure-specs.md:88` | “\| (a) \| The eight forward edges (sources → surface, surface → sinks, sinks → eta) and the feedback return are **solid**…” | Panel (a) has **8 forward edges + 1 feedback return**. |
| `11-figures/figure-spec-check.py` (check, not prose) | “defines exactly 3 panels: panel_a, panel_b, panel_c” | **Machine gate**: a redesign must keep exactly 3 named panels or this fails. |

### 3.2 Label strings visible on the artwork — these are the hard constraints for a “fewer annotations” redesign

| File:line | Verbatim quote | What it locks |
|---|---|---|
| `10-si/S5-figure-specs.md:140` | “**Bus sub-labels**, 6.1 pt grey, right-aligned inside the right end of each bus: under the surface bus, *“created by the sources, consumed by the sinks”*; above the eta bus, *“raised by the sinks, exploited by the sources”*. **These two lines are the whole reduction argument and must not be dropped for space.**” | **Two bus sub-labels are explicitly non-droppable.** A “fewer annotations” redesign collides head-on with this sentence. |
| `10-si/S5-figure-specs.md:187` | “title “Four mechanisms close four loops through two shared state variables” 8.2 pt at (0.046, 0.998)” | **Panel (a) has a drawn title string.** |
| `10-si/S5-figure-specs.md:239` | “title “Sever the loop: the knee vanishes, the fade does not” 8.2 pt” | **Panel (b) drawn title.** |
| `10-si/S5-figure-specs.md:283` | “title “Knee onset is a setting, not a constant” 8.2 pt” | **Panel (c) drawn title.** |
| `10-si/S5-figure-specs.md:121-138` | Node table incl. “label “M3 dissolution” 7.6 pt bold; sub-label *“Mn(II) + HF → surface”* 6.0 pt italic green” | **Mechanism boxes carry a name + an italic sub-label each.** Six such strings in panel (a). |
| `10-si/S5-figure-specs.md:151` | “**M1 and M2 are parallel sinks**, each feeding the eta bus independently” | Parallel-sink topology; also echoed in `S4-decision-tree.md:138`. |
| `10-si/S5-figure-specs.md:66` | “**Ink / text / badges** \| `#1a1a1a` \| Loop badges are filled circles of this colour with white letters” | Badge = filled dark circle, white letter. |
| `10-si/S5-figure-specs.md:175-183` | Encoding legend: 4 entries, “A white rectangle with **green** 1.7 pt outline → “source: creates surface””, “A white rectangle with **blue** 1.7 pt outline → “sink: consumes Li and surface””, “A **solid** green line → “evidenced””, “A **dashed** green line → “inferred”” | **A four-entry encoding legend exists in panel (a)** and “is the only place the grammar is stated”. |
| `10-si/S5-figure-specs.md:348` | “\| 2 \| **Colour semantics unchanged** \| Source = green outline, sink = blue outline, loops green, buses tinted…” | Colour semantics fixed. |
| `10-si/S5-figure-specs.md:349` | “\| 3 \| **Arrow grammar consistent** \| Solid = evidenced, dashed = inferred… and (a)'s legend states it once” | The legend is *where* the grammar is stated. |
| `10-si/S5-figure-specs.md:350` | “\| 4 \| **Source/sink encoded twice** \| Every mechanism box carries both the outline colour **and the literal word “source”/“sink” in its sub-label**” | **Redundant encoding is mandatory**, explicitly “twice”. Directly opposes “fewer annotations”. |
| `11-figures/README.md:80` | “Both feed one “reactive surface” bus and one “overpotential” bus… Loops A–D badged; solid arrows evidenced, dashed inferred.” | Bus names drawn; badges drawn. |
| `09-submission/toc-graphic.md:53-59` | Drawn TOC labels: “**M1**, **M2** … **M3**, **M4** … **reactive surface** … **overpotential eta** … **A**, **B**, **C**, **D** … **knee**” | TOC label set. |

### 3.3 Numbers visible on the artwork

| File:line | Verbatim quote | What it locks |
|---|---|---|
| `10-si/S5-figure-specs.md:227-231` | ““leaves its power law at cycle 285” 6.2 pt”; “**knee 530** and **EOL 1044**: dashed vertical guides … labelled “knee 530” and “EOL 1044” 6.2 pt”; ““slope 0.91” 6.2 pt grey …; “slope 2.43” 6.2 pt grey” | **Five printed numbers in panel (b)**: 285, 530, 1044, 0.91, 2.43. |
| `10-si/S5-figure-specs.md:254-266` | “Value labels: knee cycle printed in every non-null cell, 6.4 pt…”; grid values `2651/910/330`, `3937/1315/530/249/126`, `268/157/104/72/49`, `55/51/44/37/29`; “**2 of 20 cells are genuinely null**” | **15 printed cell values + the word “none” in 2 cells** in panel (c). |
| `10-si/S5-figure-specs.md:274` | “`R* = (delta - eta_ct)/j = 0.5 C: 40   1 C: 20   2 C: 10   3 C: 7   ohm cm2` at 6.2 pt grey” | **An `R*` locus line with 4 more numbers** below panel (c). |
| `11-figures/README.md:82` | “R\* = (delta − eta_ct)/j = 40 / 20 / 10 / 6.7 ohm cm² at 0.5 / 1 / 2 / 3 C” | Same locus — **note the discrepancy: S5 says `3 C: 7`, README says `6.7`.** |
| `11-figures/README.md:181` | “The six printed quantities are labelled literals in `figmaster.py`” | Six quantities in panel (b); `_check_numbers.py` enforces equality with the model. |
| `10-si/S5-figure-specs.md:353` | “\| 5 \| **No number without a source or “illustrative”** \| Every numeric annotation is either a model output (b, c) or labelled illustrative in the caption” | Any number added must be sourced or labelled. |
| `10-si/S5-figure-specs.md:171` | “**Put no numeric gain on any badge.**” | **Forbids adding numbers to badges** — relevant if the redesign wants to label loops with gains. |

### 3.4 Visual elements a redesign could drop — and which are forbidden

| Element | Status | Evidence |
|---|---|---|
| **Bus sub-labels** (2 strings) | **FORBIDDEN to drop** | `S5-figure-specs.md:140`: “must not be dropped for space” |
| **Solid/dashed grammar** | **FORBIDDEN to drop** | Caption C6 + `S5:349` check 3 |
| **Four-entry encoding legend** | Frowned on, but droppable *if* grammar is stated elsewhere | `S5:349` says “(a)'s legend states it once”; the caption also states it (C6), so the legend is arguably redundant — **but dropping it leaves check 3 with no anchor**. Note `S5:175` calls it “the only place the grammar is stated, and it covers all three panels”. |
| **Loop badges A–D** | Droppable, with edits | See §2.2. Must not be half-dropped (master yes / TOC no). |
| **Hatching + “none” in null cells** | **FORBIDDEN to drop** | `S5:255-258`: “**The absence is a result**, not missing data… a reader must be able to see that it is deliberate.” |
| **Colourbar** | Locked by spec | `S5:268-272` (fraction, pad, label, 5.4 pt ticks). But see the 6 pt floor conflict in §3.5. |
| **Panel (b) inset dLLI/dn** | **FORBIDDEN to drop** | `S5:232`: “**required, not optional**: it is what replaces the impossible three-channel decomposition” |
| **Panel titles (3 strings)** | Not individually mandated by the caption; mandated by S5. | Droppable only with an S5 edit. |
| **Mechanism sub-labels** (`“Mn(II) + HF → surface”` etc.) | **Partial**: the literal word “source”/“sink” must stay | `S5:350` check 4 requires the word source/sink in the sub-label. The *chemical* part of the sub-label is droppable. |
| **Footnote line 1** (hatched/‘none’ explanation) | Mandatory | `S5:284-292` |
| **Footnote line 2** (illustrative disclaimer) | **FORBIDDEN to drop** | `S5:298`: “Line 2 is what keeps the figure honest. It must not be dropped for space.” |
| **`R*` locus annotation** | Mandatory | `S5:274`: “The R\* locus annotation, below the panel — **mandatory**” |

### 3.5 Artwork-level invariants (not prose, but gates that will fail a redesign)

| Constraint | Source | Value |
|---|---|---|
| Canvas | `S5:355` check 8; `figure-spec-check.py` | exactly **17.8 × 16.2 cm** |
| Min type | `S5:352` check 7; README | **8.00 pt** master (measured from PDF `Tf` operators), titles 9.5 pt |
| DPI | `figure-spec-check.py` | 600 dpi PNG floor 300 |
| Font | `S5:356` check 9 | Times New Roman only, embedded, no mathtext |
| Glyph set | `S5:366-378` (S5.7a) | **Times New Roman has U+207B**, so the area prints as a real `Ω cm⁻²`; the Arial-era `cm^-2` caret workaround is gone. The check now reads the font's cmap instead of a hard-coded blacklist |
| Greyscale | `S5:351` check 6 | no distinction in hue alone |
| Planarity | `S5:115-119` | panel (a) must be drawable with **no crossings** |
| Badge shape | `S5:376-380` (S5.7b) | badges must be **point-sized scatter markers**, not `Circle` in data coords (axes are anisotropic ≈2.09:1) |
| Panel count | `figure-spec-check.py` | exactly 3, all invoked by `build_master()` |

### 3.6 TOC graphic — what it constrains

| File:line | Verbatim quote | Locks |
|---|---|---|
| `10-si/S5-figure-specs.md:302` | “the TOC image is a **condensed render of the same design**, derived from panel (a)'s circuit plus the knee — not the master figure rescaled.” | TOC must be a **separate redraw**, not the master. |
| `09-submission/toc-graphic.md:129` | “The single figure's palette, loop letters A–D, two-bus grammar \| **shared with `figure-master.pdf`** \| ✅ the point of the redraw” | TOC **shares** palette + loop letters + two-bus grammar with the master. |
| `10-si/S5-figure-specs.md:311` | “same palette, same source/sink colour convention, same solid-vs-dashed grammar, same two-bus topology; **drop the bus sub-labels, the encoding legend, the annotations, and the panel letters**.” | The TOC is *specified* to drop exactly the annotations the master keeps. |
| `09-submission/toc-graphic.md:53-59` | Drawn labels: M1–M4, “reactive surface”, “overpotential eta”, A/B/C/D, “knee” | TOC label set is minimal already. |
| `10-si/S5-figure-specs.md:316-322` | “**5.5 × 5.0 cm** … **or** **11.5 × 2.5 cm**”; “**≤50 words AND ≤450 characters**”; “**6–7 pt**” | TOC size/text/type floor. |
| `11-figures/README.md:62-66` | “at that reduction a 6.2 pt label becomes ≈1.9 pt, below the journal's 6–7 pt floor. So the TOC is a **condensed redraw**” | Arithmetic forbidding master-rescale. |

**⚠️ Live contradiction found — `07-final/DOSSIER.md:371`**: “**One figure, three panels**, which also serves as the TOC graphic” — while the same paragraph, two sentences later, says the TOC renders are “condensed redraws in the same design language rather than rescalings of the master”. **Both cannot be true.** The rest of the package (README:62, S5.5, toc-graphic §3.0) is unanimous that the TOC is a *separate redraw*. The phrase “also serves as the TOC graphic” should be “sits beside two TOC renders derived from its design language”. **This is a prose defect, not an artwork defect — flagging it, not fixing it (read-only task).**

### 3.7 A second live inconsistency worth noting before the redesign

`10-si/S5-figure-specs.md:353` check 7 still says: “\| 7 \| **Type size** \| **Nothing below 6.0 pt** — currently **FAILS**: 3.78 pt colorbar ticks and 5.4 pt inset labels exist. See S5.7(c)”

and `S5:394-404` (S5.7c) says: “**The built figure violates the 6 pt floor.** The rendered PDF's smallest text measures **3.78 pt** … This is a **real, unresolved defect in the current artwork**”.

**But the current artwork passes:** `python research/11-figures/figure-spec-check.py` reports `[PASS] smallest text 8.00 pt (floor 8.0 pt); 2 distinct sizes` and exits 0. So **S5.7(c) and check 7 describe a defect that has been fixed and were never updated.** A redesigner reading S5 will believe the floor is violated when it is met. **Do not re-introduce the fix by “enlarging” labels; verify with the checker instead.**

---

## (4) SUMMARY — safe vs forbidden for the redesign

### A redesign may SAFELY change

1. **Node positions, box geometry, routing of the feedback return** — specified as fractions in `S5.1`, but no prose outside S5 depends on coordinates. Update S5 to match.
2. **Panel (a)'s anisotropy-driven box sizes and all edge endpoints.**
3. **The chemical part of the mechanism sub-labels** — e.g. “Mn(II) + HF → surface”, “crack → fresh surface”, “Li ion → SEI (lost)”, “Li(0) → isolated”. These are illustrative; only the literal words **source**/**sink** are gated (`S5:350`).
4. **Panel titles (3 strings)** — droppable or rewordable, if S5 is updated in the same pass.
5. **The four-entry encoding legend**, *provided* the solid/dashed grammar remains visible on the artwork (the caption states it, so the grammar survives; but `S5:349` check 3 currently anchors on the legend).
6. **Loop badges A–D from the master**, *if* `figure-plan.md` L79–83, `S5-figure-specs.md` §S5.1 “Loop badges”, and `toc-graphic.md` §3.3 are edited in the same pass — and **only if they are also dropped from the TOC**, since the TOC is documented as sharing them.
7. **Colourbar geometry, inset placement, tick densities** — within the 6 pt floor.
8. **Number-annotation *placement*** (leaders, offsets, bbox) — the values themselves are fixed but where they sit is not.
9. **The `R*` locus line's formatting** — values are mandatory, presentation is not.

### Prose FORBIDS changing

1. **Panel count (3) or order (a→b→c).** Locked by the caption, 6+ documents, and a machine check.
2. **Exactly two shared buses**, both fed by all four mechanisms, named “reactive surface” and “overpotential eta”. This is the paper's central claim (C4, C5).
3. **Sources = M3, M4; sinks = M1, M2**, encoded twice (colour + the literal word). `S5:350`.
4. **Solid = evidenced, dashed = inferred.** Caption + `S5:349`.
5. **The two bus sub-labels** — “must not be dropped for space”. `S5:140`.
6. **Panel (b): coupled vs severed curves, and the C-rate restriction (0.5/1 C valid, not 2.0 C).** Caption C8; C-rate restriction is separately defended in `DOSSIER:387` (“It stays.”).
7. **Panel (b) inset dLLI/dn** — “required, not optional”. `S5:232`.
8. **Panel (c): C-rate × SEI-growth grid, hatched “none” cells, “the absence is a result”.** `S5:255-258`.
9. **Both footnote lines**, especially line 2 (“must not be dropped for space”).
10. **The `R*` locus annotation** — “mandatory”. `S5:274`.
11. **Six panel-(b) numbers and fifteen panel-(c) numbers**, equal to model output. `_check_numbers.py` enforces.
12. **Canvas 17.8 × 16.2 cm; every label 8 pt, titles 9.5 pt; Times New Roman only; grayscale-safe; planar panel (a).**
13. **No numeric gain on any badge.** `S5:171`.
14. **No AI-generated imagery; matplotlib primitives only.** README rule 4, and a journal prohibition quoted in `ai-use-disclosure.md:73`.
15. **The TOC must remain a separate condensed redraw** — never the master rescaled (`README:62-66`, arithmetic: 0.31× → 1.9 pt).

### Three prose defects to fix in the same pass (flagged, not fixed here)

- **P1** — `07-final/DOSSIER.md:371` “also serves as the TOC graphic” contradicts the same paragraph's “condensed redraws … rather than rescalings”.
- **P2** — `10-si/S5-figure-specs.md` check 7 + §S5.7(c) claim the 6 pt floor is violated (3.78 pt / 5.4 pt); the current artwork measures 6.00 pt and the checker passes. Stale defect description.
- **P3 (minor, resolved by reading the builder)** — `R*` at 3 C reads **7** in `S5:274` but **6.7** in `README:82`. I ran `fig3_data.threshold_locus([0.5,1.0,2.0,3.0])`: the true values are **40.0000 / 20.0000 / 10.0000 / 6.6667**. `figmaster.py:542` formats them with `"%g C: %.0f"`, i.e. **zero decimals**, so the artwork genuinely prints **`7`**. Therefore **`S5:274` is correct and `README:82`'s “6.7” is the stale value** — README is describing a number the artwork does not print. Fix README, not the figure.

---

*Prepared read-only; no file outside this one was modified.*
