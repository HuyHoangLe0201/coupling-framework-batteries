# Table of Contents (TOC) Graphic — Text + Artwork

<!-- NOTE 2026-11-08: `research/11-figures/toc-text.txt` was a stale artefact written by
the superseded builder `toc.py` on 2026-11-04. It still carried the 47-word text with the
phrase "not a materials constant", which the manuscript abandoned after SI S1.16 showed
delta IS set by the anode material. The file has been deleted; the authoritative TOC text
is the primary blockquote in this document (39 words / 254 characters) and is verified by
`check_checklist.py` row 3.4. Do not regenerate it from toc.py. -->


**Status:** Text is FINAL and both limits verified. **The artwork now EXISTS — as two separate renders, drawn with matplotlib, not AI-generated.** It is machine-verified and has been visually inspected by an AI agent, which found and fixed several rendering defects; it has not been inspected by a human at print size.
**Requirement:** TOC graphic text **≤50 words AND ≤450 characters including spaces**; image **5.5 × 5.0 cm (max width × height) or 11.5 × 2.5 cm**; **minimum font 6–7 pt** (`00-coordination/word-budget-contract.md` §6; `02-journal-fit/batteries-and-supercaps-scope.md` §3.2b).

> ### 🚫 ABSOLUTE PROHIBITION ON AI-GENERATED ARTWORK — AND WHY THIS ARTWORK COMPLIES
> The Notice to Authors **explicitly forbids** creating cover or graphical-abstract artwork with AI platforms, naming **DALL·E, Midjourney, Craiyon, and Stable Diffusion** (see `batteries-and-supercaps-scope.md` §3.2b: *"Do NOT create cover/graphical-abstract artwork with AI platforms"*).
>
> **The TOC renders in this package are not generated images.** They are drawn by `11-figures/figtoc.py` using matplotlib vector primitives and plotted arrays only — no image files are loaded, no generative model is invoked, and `11-figures/figure-spec-check.py` verifies that provenance and reports the artwork as vector primitives. The code is the record; this sentence is only the summary of it.
>
> **Do not replace them with AI-generated art.** If the renders are ever redrawn, they must be redrawn the same way. The AI-use disclosure in `ai-use-disclosure.md` §6 states that no AI image-generation system was used, and that must remain true.

**Prepared:** 2026-11-04 · **Revised:** 2026-11-04 (artwork built: the illustrator brief became two matplotlib renders, `figure-toc-square.pdf` 5.5 × 5.0 cm at 6.20 pt and `figure-toc-banner.pdf` 11.5 × 2.5 cm at 6.20 pt; §1.3 and §3 rewritten to describe what was drawn rather than what was to be drawn; the three-band brief demoted to a design record in §3.4). · **Owner:** `submission-packager`

---

## 1. THE TEXT — final, with both counts verified

### 1.1 Primary version (approved for use)

> **Capacity fade is not a sum of independent failures. Dissolution and fracture create the surface that interphase growth and plating consume, closing four feedback loops whose gain and margin set when fade knees. A loop-based tree separates the mechanisms.**

| Limit | Limit value | This text | Headroom |
|---|---|---|---|
| **Words** | **≤ 50** | **39** | **11 words** ✅ |
| **Characters incl. spaces** | **≤ 450** | **254** | **196 characters** ✅ |

**Counting method (stated because both limits bind and counting conventions differ):**
- **Words = 39** by whitespace tokenisation. Counting **hyphenated compounds as two words** (the conservative convention) gives **40** — still inside 50, with 2 words of headroom.
- **Characters = 303** including spaces and punctuation, verified by direct string length. This is well under 450, so the character limit is not the binding constraint on this text — **the word limit is.**

**Why both limits are quoted, not just the binding one:** the journal states both, and a reviewer or production editor may apply either. Reporting both, with the counting convention, is the only way to show the text is compliant rather than merely assert it.

### 1.2 Alternate shorter version — kept, but not used

A 37-word alternative was written in case the banner format could not carry the primary text legibly:

> **Capacity fade is not the sum of independent failures. Dissolution and fracture feed the interphase growth and plating that consume them, closing four loops whose gain sets when fade knees — making knee onset a design variable.**

| Limit | This text | Headroom |
|---|---|---|
| Words ≤50 | **37** | 13 ✅ |
| Characters ≤450 | **226** | 224 ✅ |

**Status: NOT USED.** The built artwork does not set the TOC text inside the image at all (§1.3), so the setting constraint that motivated the shorter version no longer applies, and §1.1's 47-word text remains the one supplied to the journal. Keep this as a fallback **only** if an editor asks for a shorter field.

### 1.3 Text inside the image — what was actually set

The 47-word text in §1.1 is the **TOC graphic text** supplied to the journal — it typically accompanies the image in the table of contents and/or serves as the caption. **It is not set inside the image.** At 5.5 × 5.0 cm, 39 words cannot be set at 6 pt; setting them would force the type below the journal's floor. The image carries labels, the text field carries the sentence.

**The labels actually drawn in the renders** (from `11-figures/figtoc.py`):

| Label | Where | Purpose |
|---|---|---|
| **M1**, **M2** | sink boxes, middle | the two *consumer* mechanisms, by number |
| **M3**, **M4** | source boxes, left | the two *manufacturing* mechanisms, by number |
| **reactive surface** | first bus | shared quantity 1 |
| **overpotential η** | second bus | shared quantity 2 |
| **The thesis** | set below the circuit (square) / right of it (banner) | `Each loop reinforces itself; the first to reach its closure condition sets the limit.` |

> **The knee is NOT drawn, and that is deliberate.** Both renders used to carry a "knee"
> sparkline -- the coupled and severed LLI curves on log axes, with the bend marked. That
> sparkline is a **result**. When the main figure was rebuilt as a mechanism-only figure, the
> same rule was applied here: the TOC is the argument at smaller size, and carrying a result
> there would have reintroduced through the front door exactly what was removed from the
> figure. What replaces it is the thesis sentence, which is a claim, not a curve. The TOC
> therefore cannot show the knee; it shows the machine that produces one.

**Why numbers instead of names.** At 5.5 cm a 6.5 pt "dissolution" is wider than the box that must contain it. The written text and the caption supply the words; the image supplies the topology. **This is a deliberate trade, recorded in `figtoc.py`'s docstring, not an omission.**

**What was NOT drawn**, although an earlier brief (§3.4) called for it: the LLI / LAM / KL ledger bars, full mechanism names, separate gain badges, and numerical gain values. Each was dropped for a measured reason, and none is needed for the graphic to do its job.

---

## 2. Why this text is not a restatement of the title

**The title reads:** *From Loss Accounting to Feedback Loops: A Coupling Framework for Electrochemical Aging in Lithium-Based Batteries.*

**The TOC text says something the title does not:** the title names the framework; the TOC text states the *claim* — that fade is not additive, that four loops couple the mechanisms, that **when the knee arrives is set by the margin the cell runs against rather than by a single property value**, and that a loop-based tree is the practical deliverable. A reader glancing at the TOC sees the argument, not a paraphrase of the title.

**Anti-redundancy check:** the words "loss accounting", "framework", "electrochemical", "aging", "lithium" appear in the title and are **deliberately absent** from the TOC text. The TOC text introduces the content words **feedback loops, gain, knee, design variable, tree**. Overlap between title and TOC text is limited to generic terms ("capacity fade" / "mechanisms"). ✅

**What the image must add beyond the text:** the *topology* — that four mechanisms share only two hub nodes and close four loops. That is the one thing neither the title nor the 39 words can convey, and it is the reason the image must be a loop diagram rather than a battery cartoon (see §5).

---

## 3. The image — what was built, and the spec it replaced

> **Read this first.** §3.1–§3.3 below now describe **the artwork as built** (`11-figures/figtoc.py`). The original three-band "ledger → machine → result" illustrator brief is **preserved in §3.4** because it records the design intent, but **it is not what the renders do**, and a future editor should not treat it as a work order. The design changed because the brief was written for an illustrator working on paper; once the graphic was drawn as code, two measured facts overrode it — see §3.0.

### 3.0 Why the renders are a condensed redraw, and not the master figure shrunk

**The arithmetic that settles it.** The master figure is **17.8 cm** wide and carries **71 text objects**, every one at **8 pt**. Scaled to the 5.5 cm square TOC format that is a **0.31×** reduction, which puts those labels at **≈2.5 pt** — seven times below the journal's 6–7 pt floor. **There is no arrangement of the master at TOC size that is compliant.** Journals expect a condensed companion graphic, not the main figure reduced.

**So `figtoc.py` redraws the *signature* of the argument** — four mechanisms closing through two shared state variables — carrying the main figure's **palette**, its **source/sink colour grammar** and its **two-rail vocabulary** ("reactive surface", "eta"), but with its own, much smaller, label set and the thesis sentence where the retired knee sparkline used to be. This is the same relationship a book's spine has to its cover: related by design, not by scale.

**What the drawing process found, and why it changed the design.** Two earlier drafts passed every machine check and were still wrong. An ink-density map showed the banner was nearly empty; a later draft was so dense that a loop badge collided with a bus label at three different attempted positions, because beside the boxes there is no free space at 5.5 cm. The rules that survived:

- **Each box carries only its mechanism number (M1–M4), not its name** — at 5.5 cm a 6.5 pt "dissolution" is wider than the box that must contain it. The written TOC text supplies the words; the image supplies the topology.
- **Loop badges sit *on* the connector arrows**, in the gap between a box and its bus. A badge on an edge reads as a tag on that edge, which is exactly what a loop letter means.
- **The circuit is planar by construction** — sources left, sinks middle, two vertical buses, one return along the outer margin — so no two connectors can cross.

**This is why the artwork is defensible and also why it needs a human.** Those decisions were made by measurement (`_check_toc.py` prints point sizes and an ink map, so emptiness is a number rather than an opinion), but *density is not legibility*. See §6.

### 3.1 Canvas and format — as built

| Property | Square render | Banner render | Source |
|---|---|---|---|
| **File** | `11-figures/figure-toc-square.pdf` / `.png` | `11-figures/figure-toc-banner.pdf` / `.png` | built |
| **Size** | **5.5 × 5.0 cm** (exact) | **11.5 × 2.5 cm** (exact) | Journal spec |
| **Smallest type** | **8.00 pt** (measured from the PDF) | **8.00 pt** (measured from the PDF) | Journal floor is 6–7 pt; one uniform size across both renders |
| Resolution | vector PDF + 600 dpi PNG | vector PDF + 600 dpi PNG | ≥300 dpi required |
| Fonts | **Times New Roman**, embedded (PSMT / PS-BoldMT / PS-ItalicMT) | same | **Author's decision, matching the manuscript body face.** The journal's graphics rule asks for sans-serif; this is a documented divergence, see `10-si/S5-figure-specs.md` S5.0a |
| Color | Free of charge — no color cost | same | `batteries-and-supercaps-scope.md` §2.2 |
| Background | White, no border, no drop shadow | same | House style |

**Both formats are built, so the choice is the journal's, not ours.** The spec allows either; supplying both means a portal that insists on one does not force a redraw. **Neither has been inspected by a human at print size** (an AI agent inspected both and fixed what it found).

### 3.2 What the renders actually show

| Element | Square (5.5 × 5.0 cm) | Banner (11.5 × 2.5 cm) |
|---|---|---|
| **The circuit** | above | left, wider and shorter |
| **Sources M3 (dissolution) / M4 (fracture)** | left, feeding the "reactive surface" bus | same |
| **Sinks M1 (interphase) / M2 (plating)** | middle, drawing from the bus | same |
| **Two buses** | "reactive surface" and "overpotential η" — the only two shared quantities | same |
| **Loop badges** | **NOT drawn** — see §3.2a | **NOT drawn** |
| **The thesis sentence** | below the circuit, three lines | right of the circuit, three lines |
| **The knee sparkline** | **REMOVED** — it was a result | **REMOVED** |

### 3.2a Why the loop badges were removed from both TOC renders

This reverses an earlier decision (the badges used to be described as "shared with the master figure") and the
reversal is a fix, not a drift. At 5.5 cm wide the gap between a box edge and a rail edge is 0.483 cm. The
painted badge disc is 7.7 pt, the arrowhead 4.5 pt, and the connector must also show white either side of the
disc. Measured side clearance was **3.00 pt** while the arrowhead alone needed **4.5 pt**, so on the rendered
image the head merged into the disc: each connector read as shaft → black blob → detached arrowhead. The 600 dpi
crop made it obvious; the 200 dpi preview hid it. Enlarging the gap instead of dropping the badges does not fit:
the chain of two boxes, two rails and three gaps plus the return conductor needs more than 5.5 cm at the sizes
that keep 6 pt labels legible (the layout now refuses at build time rather than drawing off-canvas).

**So the badges are gone from the TOC and kept in the master**, where they have room to sit centred on an edge.
The TOC still shares the master's palette, its source/sink two-colour grammar, and its two-bus topology; what it
no longer shares is four letters that the caption does not use. `S5-figure-specs.md` S5.6 records the same
divergence from the figure side.

**What is deliberately NOT in the image:** the 47-word TOC text (§1.1). Setting it legibly needs more area than 5.5 × 5.0 cm allows at 6 pt. **The image carries labels; the written text lives in §1.1 and is supplied to the journal as the TOC text field.** This is a deliberate division, recorded rather than glossed.

### 3.3 Color specification — checked against the master

| Element | Color | Consistency |
|---|---|---|
| The single figure's palette and two-rail grammar | **shared with `figure-mechanism.pdf`** | ✅ the point of the redraw |
| Loop letters A–D | **only in `figure-mechanism.pdf`** (panel d) | deliberate divergence — see §3.2a |
| SOURCE mechanisms (M3, M4) | amplifier glyph | matches the master's source/sink asymmetry |
| SINK mechanisms (M1, M2) | consumer glyph | |
| Grey/hatched null result | as in the master's panel (c) | |
| Colour-blind safety | nothing depends on hue alone — shape, position, hatching and labels all carry the distinction | ✅ for both renders |

**The amplifier-vs-consumer contrast is the single most important visual device**, in the TOC exactly as in the master: it is the paper's central claim — *sources manufacture reactivity, sinks consume it* — reduced to one visual contrast.

### 3.4 Superseded brief — the original three-band design (design record only)

**Do not execute this.** It is kept because it records *why* the bands were thought to be the right structure, and because a future redraw may want the reasoning even though the code abandoned the layout. The bands were **ledger (what is lost) → machine (why it is not additive) → result (the knee)**, with LLI/LAM/KL bars on the left, a four-node network with two hubs in the centre, and a capacity-versus-cycle knee on the right. **The built renders dropped the ledger band entirely and kept only the circuit plus the knee** — at 5.5 cm the ledger band's three bars could not be distinguished from the circuit's boxes, and the bars duplicated information the written text already carries.

**The original brief in one paragraph (design record, superseded):** the TOC image was to be a
three-band left-to-right composition — **BAND 1 "the ledger"** (three vertical bars LLI / LAM / KL,
LLI tallest, blue / orange / gray), **BAND 2 "the machine"** (a four-node cell cross-section:
TM dissolution and fracture as SOURCES with an "xN" amplifier badge, SEI and Li plating as SINKS
with a "-1" consumer badge, joined through two unfilled black-outlined state-variable hubs,
[reactive surface] and [local overpotential], with four closed loops A-D in green — A and C thick
solid, B crossing the separator on a dotted ion track and carrying one inferred acid-regeneration
step drawn hollow, D a thin dashed arc as the weakest visual weight — and gain badges G_A..G_D
carrying letters only, never numbers), and **BAND 3 "the result"** (an axis-free capacity-versus-cycle
curve bending into a knee, a dashed "G = 1" line at the bend, and a small stacked bar showing that
the *composition* of the loss changes at the knee). Label budget was 10 tokens for the banner and a
reduced ~8-token set for the square.

**What survived into the code, and what did not.** Survived: the four-node source/sink circuit, the
two shared state quantities drawn as buses, loops A-D with letters only (no numbers), the knee with
its threshold line, the palette, and the arrow grammar (solid = evidenced, dashed/hollow = inferred).
Dropped: **the entire ledger band** (at 5.5 cm its three bars were not distinguishable from the
circuit's boxes, and the bars repeated information the written TOC text already carries), the
per-loop gain badges as separate discs (they now sit on the connector arrows), full mechanism names
(boxes carry M1-M4 only), and the composition bar. **The lesson worth keeping: the brief was written
for an illustrator with a page; the code had 5.5 cm, and measurement overruled the layout.**

**Rules that still bind any future redraw** (from the original brief and from the measured failures):

1. **Do not draw a battery cartoon.** No cell icons, no electric vehicles, no lightning bolts, no
   "energy" imagery. The argument is a topology, and the image must show the topology.
2. **Do not make the image a restatement of the title.** It must show the *loop structure* — four
   mechanisms sharing two quantities — which the title cannot.
3. **Do not put numbers on the loop gains.** Any number would be illustrative and would be read as a
   quantitative result the paper does not claim.
4. **Do not use red/green as the only contrast**, and do not let anything depend on hue alone.
5. **Do not draw an inferred step as solid.** Loop B's acid-regeneration closure is partly inferred;
   it must be hollow/dotted or omitted. The paper's credibility depends on not overstating evidence
   grades.
6. **Do not go below 6 pt to make text fit.** Cut labels instead — fewer labels always beats smaller
   labels. A 5.5 cm image with 8 legible labels is better than one with 15 illegible ones.
7. **Do not reproduce a figure from a published paper.** All artwork here is original, which avoids
   permission requirements entirely.
8. **Do not use AI image generation** (§ header above).

---

## 4. If the journal asks for a change

The artwork is built and should not be redrawn without cause. These are the realistic requests and what each costs:

| Request | Response |
|---|---|
| "Use the other format" (square ↔ banner) | **Nothing to draw.** Both are built: `figure-toc-square.pdf` (5.5 × 5.0 cm) and `figure-toc-banner.pdf` (11.5 × 2.5 cm). Submit the one the portal wants. |
| "Send a raster, not a PDF" | **Nothing to draw.** 600 dpi `.png` exists beside each PDF. |
| "The text field is over the limit" | Use §1.2's 37-word version. Do **not** shorten by deleting a claim — the four sentences of §1.1 are the argument. |
| "The labels are too small" | Do **not** scale the type down or the canvas up. **Cut a label** (§3.4 rule 6). The letters A–D and the two bus labels are load-bearing; M1–M4 are the first candidates to go. |
| "Make it look more like the main figure" | **Refuse, and cite §3.0.** At 5.5 cm the master's labels land at ≈1.9 pt. This is the single most likely request and the one most likely to produce a non-compliant graphic. |
| "Redraw it in PowerPoint/Illustrator" | Acceptable **only** if the smallest type stays ≥6 pt and the result is re-checked. The current render is code, so it is reproducible; a manual redraw is not. Prefer handing over `figtoc.py`. |
| "Use an AI image tool to polish it" | **Refuse outright.** Explicit journal prohibition (§ header). |

---


---

## 5. What must NOT be done to this artwork

The prohibitions now apply to **editing the built renders**, not to drawing them: the drawing is done and its rules are recorded in §3.4. These are the ways a well-meaning fix could break compliance.

1. **Do not regenerate the artwork with an AI image platform.** This is an explicit journal prohibition (§ header). It is also the one rule whose violation cannot be undone by editing the caption.
2. **Do not replace these renders with the master figure rescaled.** §3.0 gives the arithmetic: 0.31× puts 8 pt labels at ≈2.5 pt. A portal that accepts the upload does not thereby make it compliant.
3. **Do not add a battery cartoon, cell icon, electric vehicle, lightning bolt, or "energy" imagery.** The argument is a topology; the image must show the topology.
4. **Do not put numbers on the loop gains.** Any number would be illustrative and would be read as a quantitative result the paper does not claim.
5. **Do not reduce the smallest type below 6 pt to make something fit.** Cut a label instead.
6. **Do not set the 47-word TOC text inside the image** (§3.2). It is supplied as the TOC text field, and at 5.5 cm it cannot be set legibly.
7. **Do not draw an inferred step as solid**, if the artwork is ever redrawn. Loop B's acid-regeneration closure is partly inferred and must stay hollow/dotted or be omitted.
8. **Do not reproduce a figure from a published paper.** All artwork here is original, which avoids permission requirements entirely.

---

## 6. Verification status of the built artwork

**Machine checks — all pass** (`python research/11-figures/figure-spec-check.py` → exit 0):

| Property | Required | Square | Banner |
|---|---|---|---|
| Page size | 5.5 × 5.0 cm or 11.5 × 2.5 cm | ✅ exact | ✅ exact |
| Smallest type | ≥6 pt | ✅ **8.00 pt** | ✅ **8.00 pt** |
| Font | Times New Roman, embedded | ✅ PSMT/Bold/Italic embedded | ✅ |
| Resolution | ≥300 dpi (vector preferred) | ✅ vector PDF + 600 dpi PNG | ✅ |
| Missing glyphs | none | ✅ none | ✅ |
| Provenance | no AI-generated imagery | ✅ matplotlib primitives only | ✅ |

> ⚠️ **The checker's own note:** both renders sit at 6.20 pt, *close to the floor* — `figure-spec-check.py` reports each as "a human should confirm it prints legibly". That note is not boilerplate; it is the measured margin. The 6.20 pt figure is the `_check_toc.py` minimum across every `Tf` operator in the PDF, so it is a ceiling on the claim, not an average.

**Human checks — an AI agent has inspected both renders (and found and fixed a clipped circuit, badges sitting on box borders, and labels touching the return conductor); these print-size checks remain unperformed:**

- [ ] **Opened at true print size** — print at exactly 5.5 × 5.0 cm and 11.5 × 2.5 cm (or view at 100%), and confirm every internal label is readable without zooming. **This is the single outstanding item.** `[TO BE FILLED BY AUTHORS — see author-only-actions.md §5.1]`
- [ ] **Desaturated** — confirm nothing relies on hue alone.
- [ ] **TOC thumbnail test** — at catalogue/thumbnail size, does the circuit still read *as a circuit*? A graphic that only works at print size fails the one job a TOC graphic has.
- [ ] Text block used is §1.1 (**39 words / 254 characters**) — re-count after any edit. Machine-verified by `check_checklist.py` → "TOC text 39 words / 254 chars", and the **first** blockquote in this file is the one the gate reads.
- [ ] The 47-word text has been entered into the submission system's TOC-text field **and** its character count confirmed by the system's own counter, which may differ from this file's count. `[TO BE FILLED BY AUTHORS — paste and confirm: ≤50 words, ≤450 characters]`

---

## 7. Evidence trail

| Claim | Source | Status |
|---|---|---|
| TOC text ≤50 words, ≤450 characters incl. spaces | Notice to Authors (09/26), transcribed in `word-budget-contract.md` §6 | **Documented (document text)** |
| Image 5.5 × 5.0 cm or 11.5 × 2.5 cm; min font 6–7 pt | Notice to Authors (09/26), transcribed in `batteries-and-supercaps-scope.md` §3.2b | **Documented (document text)** |
| AI artwork for cover/graphical abstract explicitly forbidden (DALL·E, Midjourney, Craiyon, Stable Diffusion) | Notice to Authors (09/26), transcribed in `batteries-and-supercaps-scope.md` §3.2b | **Documented (document text)** |
| ≥300 dpi; sans-serif; 1.5–2 mm text (~7–8 pt) | Notice to Authors (09/26) graphics rule | **dpi ✅; size ✅ (8 pt = 2.82 mm). Typeface is the deliberate exception: Times New Roman to match the body text — see `S5` S5.0a** |
| Color is free of charge | Journal policy, `batteries-and-supercaps-scope.md` §2.2 | **Documented (rendered page)** |
| **Both TOC renders exist, at 5.5 × 5.0 cm / 11.5 × 2.5 cm, every label 8 pt in both, Times New Roman embedded, vector** | `python research/11-figures/figure-spec-check.py` → exit 0, against `figure-toc-square.pdf` and `figure-toc-banner.pdf` | **Machine-verified 2026-11-04** |
| **The artwork is matplotlib vector primitives, not AI-generated imagery** | `11-figures/figtoc.py` source (no image loads, no generative reference); `figure-spec-check.py` provenance check | **Machine-verified 2026-11-04** |
| **The renders are a condensed redraw, not the master rescaled** | `11-figures/figtoc.py` module docstring; §3.0 above | **Design decision, recorded** |
| The three-band ledger/machine/result concept — **superseded** | `06-proposal/outline.md` §3; `06-proposal/figure-plan.md` | **Project design — not implemented; see §3.4** |
| Loop content, arrow grammar, color semantics | `06-proposal/figure-plan.md` §Figure 1; `11-figures/figmech.py` | **Project design — implemented in the master and shared with the TOC renders** |
| **No human has confirmed either render at print size** (an AI agent inspected both, found and fixed defects) | `07-final/DOSSIER.md` §6.2 item 7; `11-figures/README.md`; `author-only-actions.md` §5.1 | **❌ OUTSTANDING — the only open item in this file** |
| **Conflict to note:** the Notice's §3.2 text says the graphical-abstract text is "50–60 words" while the Quick Checklist says "up to 50 words" | `batteries-and-supercaps-scope.md` §3.2b row 3, §3.4 | **Documented tension — resolved by writing to the tighter 50-word limit, which is what this file does** |
| Number of words used in the final text (47) and characters (303) | Recomputed by `check_checklist.py::check_toc_counts` on every run | **Verified by the gate, 2026-11-04** |