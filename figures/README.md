# research/11-figures/ — figure deliverables

**One figure — a mechanism figure with four panels — plus two TOC renders.** All PDF (vector) + PNG (600 dpi),
Times New Roman embedded, exact journal widths, every label at 8 pt (titles 9.5 pt).

> ## ⚠️ READ THIS FIRST: no agent has looked at these figures
>
> **The figures have now been visually inspected, and the inspection found real
> defects.** This paragraph previously stated that no model in the project could accept an
> image, which was true of the *declaration* and not of the model: the route never declared
> `inputModalities`, so `read_image` refused. Once declared, a probe returned
> `content: "Red"` with `image_tokens: 184` for a synthetic red square -- the capability had
> been there all along. The earlier claim is retracted rather than deleted, because it was
> accurate when written and the reason it expired matters.
>
> The machine checks below still prove what they always proved: page geometry, DPI,
> embedded fonts, minimum point size measured from the PDF's own text operators, text
> overlap, canvas escape, connector routing and crossings, colour separation in greyscale
> and under simulated colour-vision deficiency, and that every number printed on the
> artwork equals the number the model computes.
>
> **What the visual pass found that those checks had not.** Full detail with measurements
> is in `VISUAL-DEFECTS.md`; the list, because it is the justification for looking at all:
>
> - **five of twenty heatmap cells were invisible** -- white text on a near-white fill in
>   panel (c)'s top row, and dark-on-dark on the darkest cell. The label colour was chosen
>   from the DATA value instead of the rendered fill;
> - **a wrong superscript** (`ohm cm2` for `Ω cm⁻²`), a defect no size check can detect
>   because the type was the right size and the string was simply wrong;
> - **two arrows drawn through annotation text** in panel (a). The line-vs-text audit
>   reported zero crossings here because it walked `Line2D` only and every connector is a
>   `FancyArrowPatch`;
> - **the square TOC render drew more than half its circuit outside the axes** and clipped
>   it away -- both buses sliced, two mechanism boxes missing, and the bus labels cut to
>   fragments. Twenty-nine machine checks passed while that shipped.
>
> **What visual inspection still cannot establish, and a human must confirm.** Looking at a
> picture is not a validation. These remain open:
>
> - whether the four panels read in the intended order and are legible at 17.8 cm in
>   print;
> - whether panel (c)'s circuit reads as a closed circuit rather than four boxes, to a
>   reader meeting it for the first time;
> - whether the TOC renders survive reduction to 5.5 × 5.0 cm and 11.5 × 2.5 cm on paper;
> - whether anything is scientifically wrong in a way a domain expert would spot;
> - greyscale: desaturate and confirm nothing relies on hue alone.
>
> Two of the six defects originally recorded were my own misreadings, disproved by
> measurement rather than argument (a guide through a label that was never crossed, and an
> arrow through text that the audit could see all along). That is recorded too, because a
> defect list nobody re-tested is a liability.
>
> If you change a builder, re-run **all six** checks in §Checks.

---

## Deliverables

| File | Size | Status |
|---|---|---|
| `figure-mechanism.{pdf,png}` | 17.8 × 16.2 cm | **the manuscript figure** (not the TOC graphic — see below) |
| `figure-toc-square.{pdf,png}` | 5.5 × 5.0 cm | TOC option A (square slot) |
| `figure-toc-banner.{pdf,png}` | 11.5 × 2.5 cm | TOC option B (banner slot) |

`figure-mechanism` is the manuscript figure and **only** that. The TOC slot is 5.5 cm wide: at
that reduction a 6.2 pt label becomes ≈1.9 pt, below the journal's 6–7 pt floor, so the TOC
cannot be the master rescaled. It is a **condensed redraw** in the same design language (same
palette, same two-bus grammar, same solid-vs-dashed convention) and not the master rescaled.
Both renders exist because the journal accepts either slot size; the
editor picks one and the other is discarded.

**Superseded, kept only as design history — do not submit:** `fig1-coupling-map.*`,
`fig2-ledger-diagnostic.*`, `fig3-knee-bifurcation.*`, `fig4-decision-tree.*`,
`toc-graphic.*` and their builders `fig1.py`…`fig4.py`, `toc.py`, plus the retired three-panel `figmaster.py` → `figure-master.*` (its builder is preserved verbatim at `_seed/figmaster_v3_with_results_panels.py` in case the results panels are reused in the SI).

### What the four panels are

This is a **mechanism figure**. It carries no computed curve, no operating map and no
cycle number: those are results, and they moved to the SI. What it carries instead is the
machine that produces a knee, at four levels of description.

| Panel | Question | Content | Type |
|---|---|---|---|
| **(a)** | *Where* does each mechanism act? | Section through the cell drawn as stratigraphy — Al foil / cathode / separator / anode / Cu foil — so each mechanism is marked in the layer where it happens. Dissolution (M3) and fracture (M4) are **sources**: they manufacture reactive surface, at cathode particles and on fresh crack faces. Interphase growth (M1) and plating (M2) are **sinks**: they consume lithium inventory and surface. M1–M4 badges sit at the site, so no leader line has to reach across the artwork. | schematic |
| **(b)** | What is the architecture of the interphase? | The bilayer at 8 pt: close-packed inorganic crystallites in a sublayer ~4 nm thick, under a porous organic region reaching into the pore space. Leak paths cross the dense layer, which is why a film far thicker than the 2–3 nm tunnelling limit keeps growing, and why loop A is capped by **pore fill** and not by passivation. Dead Li is drawn as isolated metal, never as missing charge. Reduced-TM clusters mark the catalytic route. | schematic |
| **(c)** | *How* do the four couple? | Four mechanisms wired to **two shared state variables** — "reactive surface" and "overpotential η". Sources feed the surface rail, sinks draw from it and feed the eta rail, and two feedback edges return eta to the sources. Both rail sub-labels are kept. Green = source, blue = sink, and the words in the notes repeat what the colours say, so the encoding survives greyscale. | schematic |
| **(d)** | What closes each loop? | Four broken circular arrows, one per loop. The **gap in each arc is the closure condition** — the loop runs until the inequality beneath it is met: A `R_SEI > R*,  R* = (Δ − η_ct)/j`; B `Mn loss > Li loss`; C `interphase vol > pore vol`; D `salt use > salt supply`. Four small marks on each arc mark the four links of the chain. Each loop reinforces itself, and **the first one to close sets the limit** — which is the paper's thesis, so this panel is not decoration. | glyph + inequality |

The retired panels, for the record: the coupled-vs-severed Li-inventory plot (knee 530, EOL
1044, departure 285, exponents 0.91/2.43) and the C-rate × SEI-factor operating map (2 null
cells of 20; R* = 40/20/10/7 Ω cm² at 0.5/1/2/3 C) are **results**, and they now live in
the SI. `fig3_data.py` still computes them and `figure-spec-check.py` still verifies them,
so the numbers have not been orphaned — they have been relocated.

---

## Generators

| Script | Produces | Notes |
|---|---|---|
| `figstyle.py` | — | page geometry, palette, `save()`; sets `FAMILY`/`LABEL_PT`/`TITLE_PT`; raises if the declared face is absent, asserts exact figsize |
| `fig3_data.py` | — | **sole number source**; imports `loopA_model_v4`, asserts documented milestones on import |
| `figmech.py` | `figure-mechanism` | `build_master()`; four mechanism panels; escalates font warnings to errors so a missing glyph fails the build |
| `figtoc.py` | both TOC renders | `build_square()`, `build_banner()` |
| `figaudit.py` | — | the geometric audit (see below) |
| `_run_figaudit.py` | — | runs the geometric audit on the mechanism figure |
| `_check_toc.py` | — | TOC point sizes from the PDF + ink maps |
| `_check_numbers.py` | — | proves every number printed on the **results** items equals the model's (the mechanism figure prints none) |
| `_balance.py` | — | ink distribution, squint test (blob count at TOC size) |
| `_ascii_view.py` | — | coarse ASCII ink map, the only way a non-visual agent can sanity-check gross layout |
| `figure-spec-check.py` | — | sizes, dpi, fonts, **point sizes read from the PDF**, panel count, glyph coverage |
| `layout-check.py` | — | text overlap, canvas escape; **fails closed** if it checks nothing |

Rebuild everything:

```
python figmech.py && python figtoc.py
```

---

## Checks

Run all eight; every one must exit 0. The whole set also runs as one gate:
`python research/00-coordination/_full_audit.py` (32+ checks).

| Command | What it proves |
|---|---|
| `python figure-spec-check.py` | exact page size, 600 dpi, declared family embedded, **smallest text measured from the PDF's Tf operators**, the 4 mechanism panels defined *and* invoked, **no result quantity drawn**, retired results builder still preserved and unimported |
| `python layout-check.py` | no text overlap, no canvas escape; fails closed on a missing module or an unexercised builder |
| `python _run_figaudit.py` | text overlap, canvas escape, arrow routing and crossings, colour separation (greyscale + deuteranopia/protanopia/tritanopia), font floor across **all 80 drawn text objects** |
| `python _check_numbers.py` | knee 530, EOL 1044, departure 285, exponents 0.91/2.43, severed → no knee, 2 null cells in the map — each re-derived from the model. **These now describe SI results**: the mechanism figure prints no number at all |
| `python _check_toc.py` | TOC point sizes from the PDF (8.0 pt floor, read from `figstyle`), declared-family only, ink map |
| `python _toc_budget.py` | the journal's graphical-abstract budget: **≤50 words AND ≤450 characters**. Neither was counted before; the renders carry a three-line thesis sentence, which is exactly the sort of addition that silently breaches a character cap. Both renders measure **24 words / 146 characters** |
| `python _measure.py` | every text bbox in centimetres, with the pairwise overlap table. This is the tool that found the 8 pt spacing defects — the ones no eye caught |
| `python _balance.py` | ink distribution; squint test at TOC size |

### Two auditors disagreeing was itself a finding

`figaudit.py` originally measured only the text artists the builder registered, and
reported "no text-on-text overlap at all" while `layout-check.py` — which crawls
`ax.texts` — flagged a 0.022 in² collision in panel (b). The registry held 27 of the
figure's **75** text objects; `ax.annotate()` and every axis tick label were invisible to
it. Both auditors now crawl the artist tree, so the stricter result is the shared truth.

Two classes of false positive were also fixed rather than tolerated, because a check that
cries wolf gets ignored:

- **CLOSEPOLY sentinel.** A `FancyArrowPatch` path ends with a CLOSEPOLY whose vertex is
  `(0, 0)`, so naive vertex interpolation invented a segment across the whole figure and
  reported arrows as crossing boxes they never touched. Segments are now read via path
  codes.
- **Invisible and off-view ticks.** Ticks of an `axis("off")` axes, and ticks whose value
  lies outside the axis limits, still carry real bounding boxes but are never drawn.
  Measuring them produced collisions at coordinates no reader can see (y = −130 px).

---

## The 8 pt floor, and why it is measured from the PDF

The current floor is **8.00 pt** — the author's instruction, one size for every label,
above the journal's 6–7 pt TOC minimum rather than below it. Panel titles are 9.5 pt,
and those two sizes are exactly what the delivered PDFs contain.

The floor is verified by decompressing the PDF content stream and reading its `Tf`
operators, **not** by trusting the source: two real violations were once invisible in the
source, both in the now-retired computed panels.

1. An inset set `labelsize=5.4` on tick labels it created itself — those never passed
   through the builder's `_txt()` helper, so no source-level audit saw them.
2. A log colorbar's default formatter emitted **mathtext**, whose superscript renders at
   0.7× its declared size: a 5.4 pt axis produced **3.78 pt** glyphs.

Both lessons survive the panels that produced them: mathtext is still forbidden
everywhere (subscripts are written with underscores — `R_SEI`, `eta_ct`, `R_crit`), and
every text object in the mechanism figure goes through `_txt()`, which registers it for
the audit. The check that matters now is not "is anything below 8 pt" but "does the
registry see everything" — `figaudit.py` crawls the artist tree rather than trusting it.

---

## Rules that must not be broken

1. **Every number on the artwork must equal the model's — and the mechanism figure
   prints none at all.** `figure-spec-check.py` enforces the second half mechanically by
   parsing `figmech.py` and failing if any result identifier reaches executable code.
   `_check_numbers.py` still enforces the first half on the SI items, where the six
   quantities live as labelled literals beside curves from `fig3_data`. Removing the
   panels did not license removing the check.
2. **A guard never seen to fail is indistinguishable from one that cannot.** Every check
   here has been crashed on purpose at least once (a corrupted label for the number guard,
   injected missing modules for `layout-check.py`) and then restored.
3. **`_check_numbers.py` cares about the definition, not just the window.** Its first
   version recomputed the power-law exponents over a window it invented and reported a
   mismatch with the figure's 0.91/2.43. The figure was right; the auditor was wrong. It
   now calls the model's own `exponent()` over the window `fig3_data` asserts on.
4. **No AI-generated imagery.** The journal's Notice names DALL·E, Midjourney, Craiyon and
   Stable Diffusion as forbidden for artwork. Every mark in these files is a matplotlib
   primitive. `09-submission/ai-use-disclosure.md` states this, and it stays true.
5. **Do not rely on hue.** Source/sink are separated by greyscale delta 14 and worst-case
   CVD 35 on a 255 scale; LLI blue vs LAM orange by 53. Checked by `_run_figaudit.py`.
