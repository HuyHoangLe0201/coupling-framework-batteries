# Advice: how this figure could be improved further, and which tools would do it

**Status:** the figure as delivered (2025-11-06) passes every gate and measures
**211 words / 12.8 % of the canvas** in text, down from **432 words / 26.9 %**.
This note records what was changed, what the literature on scientific figure design
says should change next, and — honestly — which of those recommendations **cannot be
implemented in this project's toolchain**, with the reason.

---

## 1. What was actually wrong, measured

| Metric | Before | After | Why it mattered |
|---|---|---|---|
| On-canvas words | 432 | **211** | 432 words is a page of prose that has been given a border |
| Text as % of canvas | 26.9 % | **12.8 %** | a drawing should be mostly drawing |
| Largest text block | 146 chars (footnote) / 118 words (panel d) | **85 chars** (thesis) | no block now competes with the drawing |
| Panel (d) | 2×2 table of sentences | **4 loop glyphs + 4 inequalities** | a table of conditions is not a mechanism drawing |
| Panel (b) right column | 16-line, 100-word paragraph | **3 numbered callouts** | it restated the Figure 1 legend almost verbatim |
| Footnote | 4 lines, 365 chars | **2 lines, 219 chars** | two of the four described conventions the figure no longer uses |

**The diagnosis that drove all of it:** 118 words of panel (d) were a **verbatim
duplicate of prose §4**. That is the signature failure mode — text migrates into a
figure because the figure has not been given a job only a figure can do. Deleting it
lost nothing, because the reader had already been told.

## 2. What the design literature recommends, and what was applied

Applied in this pass:

1. **One continuous scene beats a grid of lettered boxes.** Panels (a)–(c) now read
   left-to-right as *where → what → how*, with a shared visual grammar (green = source
   of reactive surface, blue = sink) rather than four unrelated frames.
2. **A figure carries nouns; the caption carries verbs.** The verbs that were inside
   panel (b) ("consumes Li⁺, raises R_SEI") moved to the legend, where they belong.
3. **The gap in a loop is a better closure condition than the sentence "closes when".**
   A broken circular arrow with an arrowhead on the tangent says *every loop runs until
   it stops* in one glance, and the inequality beneath it is then read as data rather
   than as prose. Four small circles on each arc mark its four links.
4. **Numbered discs instead of leader lines for naming.** A leader has to cross
   whatever lies between label and feature, and at 8 pt a crossing reads as a stray
   rule. A disc in clear space with a repeated number in a key points without drawing.
5. **Direction disambiguates dashes.** In panel (b) a red dashed stroke meant both
   "severed neck" (*no current*) and "electron leak path" (*current still flows*) — the
   same symbol making opposite claims. Leak paths are now solid hairlines with a small
   arrowhead at the escape end; severed necks stay dashed because a dash with no head
   is what a break looks like. One of each class is shown, not four.
6. **Irregular voids, not regular ones.** The first porosity pass drew evenly spaced
   pale strokes; at print size that reads as *combing*, and a regular array asserts a
   regular material — the opposite of a porous one. Pores are now irregular polygons of
   varied size and orientation with the organic blobs drawn over them.
7. **A visible lithiation ramp.** The anode's state-of-charge gradient is the local
   condition that makes plating possible at moderate average SoC, and it had been
   drawn in four tints two grey levels apart — invisible at print size. The ramp now
   spans `#f4f7fa → #93aec6`.
8. **No coloured text carrying meaning alone.** Source/sink is double-encoded: colour
   *and* the literal words "source"/"sink" in the footnote. Measured greyscale
   separation is only Δ14 and worst-case CVD 35, so a single encoding would fail.

## 2a. Round 2: what zooming found that the audits could not

The text was cut in round 1; round 2 was about the **drawing**, and every defect below
was found by rendering at 600 dpi and cropping one panel, not by any automated check.

| Defect | Measured | Fix |
|---|---|---|
| **Dense sublayer was 50 % of the film** | 0.130 cm of 0.260 cm, against the caption's "4 nm of 20–50 nm" = 8–20 % | 0.045 cm → **17 %**. A drawing must not contradict the number printed beneath it |
| **25 % of cathode particles were cracked** | 17 of 67 | **exactly two**, drawn explicitly on top of the field. A quarter-cracked field reads as texture, not as an event |
| **Particles overhung their layer boundary** | up to **0.095 cm** ≈ 1 mm at print size | per-layer clip paths |
| **Copper current collector carried chroma 42** (warm tan, same family as the cathode) | `#d8c9ae` | `#d8d4cc`, chroma 12. Invariant layers go quiet, moving species stay loud |
| **Graphite in (b) was a lattice of windows** | horizontal layers crossed by regular vertical ties | layer lines broken into offset flakes, ties dropped |
| **Panel (a)'s porous film was a flat band with a combed edge** | 0.215 cm of solid fill + a row of 0.018 cm ticks | same grammar as (b): wavy front, voids r 0.011–0.019, blobs r 0.024–0.034 |
| **Cathode was a honeycomb** | radii varied ±9 % on a fixed hex grid | radii 0.118–0.180 in two size classes, position jitter ±0.028 |

### Four measurement traps hit while fixing these — worth remembering

1. **`patch.get_extents()` is in display pixels, not data units.** Compared against
   centimetres, it reported "0.000 cm overflow" for every layer and printed a **PASS
   while checking nothing** (all 568 patches silently filtered out). Any guard must
   assert it actually tested something.
2. **A clip path removes pixels without changing the artist's extent.** The bbox test
   therefore cannot see a clipped field either way; only the rendered image can.
3. **`_poly()` returned `None`.** Every clip wrapper silently clipped nothing, because
   the wrapper skipped non-artists. A helper that draws for side effect cannot be
   wrapped; it has to return its patch.
4. **A strip that includes the label gutter measures typography.** The "Cu foil"
   descenders produced 1644 "violating" pixels on a correct drawing — a false failure,
   which trains the next person to ignore the guard.

All four now have a permanent guard: `_check_overhang.py`, registered in
`research/00-coordination/_full_audit.py` as **"Figure ink stays inside its layers"**.

---

## 3. Recommended next, listed with feasibility

### 3a. Possible in matplotlib, not yet done

| Recommendation | Effort | Why it would help |
|---|---|---|
| **Selective chroma**: desaturate invariant context (foils, separator, graphite) to ~40 %, keep full chroma only on what moves | low | The eye is currently asked to sort colour everywhere; greying the furniture tells it where to look |
| **Two-tone flat fill + 0.25 pt inner keyline** instead of raster gradients in panel (b)'s film | low | matplotlib gradients rasterise; a two-tone fill with a hairline keyline is vector, prints crisper, and reads as deliberate rather than as a blur |
| **Magnification callout** on panel (b) with converging connector wedges from a small box on panel (a)'s interphase | medium | The 20–50 nm film is drawn at a scale no reader can relate to the cell section; a proper magnifier would link the two panels geometrically instead of by shared encoding |
| **`path_effects.withStroke` white halo** on labels that cross busy fills | low | Would let the `M1`–`M4` badges in panel (a) sit closer to the features they name |
| **Optical margin** — let the single heaviest element (the thesis line) hang 0.15 cm proud of the text block | low | Small, but it is what separates a composed page from a filled one |

### 3b. Not possible in this project's toolchain, with the reason

These are the recommendations the research turned up that **would** improve the figure
and **cannot** be used here. Listing them, because "we could not" is different from
"we did not consider".

| Tool / technique | Why not |
|---|---|
| **Inkscape, `--export-type=pdf`** | Would keep text as text and give real path booleans. It is not installed, and adding an external converter puts a manual step between the source and the deliverable — the source must stay executable so the audits can re-render it |
| **cairosvg / svgutils / svgwrite / drawsvg** | None installed; `cairosvg` outlines text, which production rejects |
| **`vpype` / `vsketch`** | Not installed; optimises pen-plotter paths, a different problem |
| **`shapely` path booleans** | Not installed. This is matplotlib's real geometric gap: overlapping patches cannot be unioned, so every "one continuous region" in the figure is faked by drawing order. Where the figure needs a true union — the dissolution + reconstruction region in panel (a) — the mark is drawn as a single polygon by hand instead |
| **Figma / Illustrator as source of truth** | Would break the audit suite, which is the only thing keeping 84 text objects from colliding |
| **AI-generated imagery** | Forbidden by the project's own rules, and rightly: a generative image of an interphase would be a picture of a plausible-looking thing, not a drawing of a claim |

### 3c. Palette advice, if the figure is ever re-coloured

The current green/blue is chosen for a *meaning* (source/sink), not for hue harmony.
If re-coloured, the two palettes that are safe under colour-vision deficiency and are
widely used in journals are:

- **Okabe–Ito** — `#000000 #e69f00 #56b4e9 #009e73 #f0e442 #0072b2 #d55e00 #cc79a7`
- **Paul Tol bright / muted** — a lower-chroma set for large filled areas

The constraint that outranks both: greyscale safety. Measured worst-case CVD
separation between the current source green and sink blue is **35**, which is why the
encoding is doubled in words. Any re-colouring must be re-measured, not eyeballed.

## 4. The one thing still worth doing, and it needs a human

**Look at it at 17.8 cm on paper, not on a screen.** Every automated check in this
project passes, and has passed on revisions that were wrong — the audits catch
collisions, escapes and contradictions, and they cannot catch a drawing that is
correct and dull. The specific things to judge by eye:

1. Does panel (a) read as a cell section in under two seconds?
2. Does panel (c) read as **one closed circuit** rather than four boxes on two bars?
3. Does panel (d) read as *four loops that stop*, or as four refresh icons?
4. Is the red in panel (b) doing one job, or three?

The font question is separate and also needs the production editor: the journal's
artwork guidance asks for sans-serif (Arial), this figure uses Times New Roman to
match the manuscript body. 8 pt is compatible; the serif is a deliberate divergence,
recorded in `S5.0a` and `AUDIT-CONSTRAINTS.md`.
