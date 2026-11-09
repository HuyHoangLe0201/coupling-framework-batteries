# Visual defects: what survives measurement

**Six were claimed from looking at crops. Two were real as described, two were real but
differently than claimed, and two were not defects at all.** Every entry below carries the
evidence that settled it, because an unverified defect list is worse than none: it sends
someone to fix a figure that is not broken.

Context: until now `read_image` refused with *"model does not declare image input"*. That
was true of the **declaration**, not the model -- the deploy-gateway route never declared
`inputModalities`. An endpoint probe returned `content: "Red"` with `image_tokens: 184` for
a synthetic red square *before* the declaration was written, so the declaration is truthful
rather than hopeful. The figure could then be inspected for the first time, after
twenty-nine geometric suites had passed.

---

## Real, and fixed

### V1 -- `3937` unreadable on the darkest cell

Before: dark text on near-black green. After: white text, **contrast 11.40:1**.

Root cause: the label colour was chosen from the **data value** --
`color="white" if v < 340 else INK`. What a reader sees is the **fill**, which is
`cmap(LogNorm(v))`. A threshold on `v` cannot be right at both ends of a colormap, because
perceived luminance is not a monotone function of the data through `LogNorm`.

Fix: `_label_colour(cmap, norm, value)` evaluates the rendered fill and picks the label by
WCAG contrast ratio. All 15 finite cells were then asserted >= 4.5:1; the minimum is 4.71:1
(the 1315 cell) and the maximum 17.76:1.

### V2 -- top row invisible, white on white

Before: `55 51 44 37 29` in white on an almost-white fill -- five of twenty cells
invisible, and that row is the one showing fast rates have no knee at all.

Same root cause and same fix as V1. Those five cells now carry dark labels at 16.3-17.8:1.

### V5 -- `ohm cm2` lost its superscript

Figure said `ohm cm2`; the caption and manuscript say `Ω cm²`. A point-size check cannot
detect this: the type is the right size, the string is simply wrong.

**Now `Ω cm⁻²`, with a real superscript minus.** The caret form `cm^-2` was a
workaround forced by Arial, which has `U+00B2` (²) but **not** `U+207B` (superscript minus) --
measured against `C:\Windows\Fonts\arial.ttf`. When the artwork moved to Times New Roman, which
**does** have `U+207B`, the workaround was no longer needed and the true notation came back.
Mathtext is still avoided everywhere (its superscripts render at 0.7x and would breach the size
floor from an 8 pt parent), but a real Unicode superscript is not mathtext, so nothing shrinks.

This is worth recording as a lesson: **a workaround is only correct while its premise holds.**
The premise was "the face lacks this glyph", and it expired with the typeface.

### V6 -- ASCII where the caption uses notation

`->` instead of an arrow, `eta` instead of η, `delta` instead of Δ, `R*` with a bare
asterisk. Four box subtitles plus the R* line. Now `U+2192`, `U+0394`, `U+03B7`, `U+2212`,
`U+03A9` -- every one verified present in the **actual face in use** before use. Under Arial
that check caught `U+22C6` (star operator) and `U+2605` (black star) as **absent** and kept the
ASCII `R*` that the manuscript itself uses.

`assert_glyphs` failed the build on the first attempt at `cm⁻²` with
*"Arial cannot render these characters"*. That guard earned its place -- and it later had to be
**rebuilt**, because a blacklist of one face's gaps is not a glyph check: it rejected `U+207B`
that Times New Roman has and could not have caught a gap in the new face. It now reads the
font's own cmap. See `AUDIT-CONSTRAINTS.md` §6.

---

## Claimed, but not real

### V3 -- "the guide is drawn through 'knee 530'" -- NOT CONFIRMED

Two independent measurements contradict it:

1. An all-lines-vs-all-text audit (8,000+ line segments against every glyph box, using
   Liang-Barsky clipping and a per-segment z-order test) found **no line crossing that
   label**.
2. Adding a white bbox behind the label left panel (b)'s PNG **byte-identical**
   (sha256 `0fdf34c0...` unchanged), which is only possible if there was nothing to cover.

What I was actually seeing was the label sitting close to the dashed guide on a downscaled
preview. The white bbox is kept anyway: it costs nothing and makes the arrangement robust if
the label ever moves.

**The audit did find one genuine crossing elsewhere** -- a dashed line through a `1000`
tick label in the inset -- which is a different problem in a different place, and a reminder
that the eyeball and the measurement disagree in both directions.

### V4 -- "the arrow is drawn through 'consumed'/'exploited'" -- NOT CONFIRMED

Those two annotations were already registered as `bus:surface:sub` and `bus:eta:sub`, so the
existing audit could see them all along. There was no unregistered-artist hole here; that
hypothesis was carried over from an earlier, unrelated bug (the 27-of-75 discovery) and
applied without checking.

---

## The false positives my own audits produced

These matter more than the fixed defects, because each was a checker inventing a defect.

### A. A phantom `x` in the heatmap

    [OVERLAP] 'none' x 'x'   14.74 pt^2   IoU(smaller) = 64.8%

`type(ax.text(0, 0, "x"))` was used to obtain the `Text` class. `ax.text(...)` does not look
up a class -- it **constructs** a Text artist and attaches it to the axes at data (0, 0).
In the heatmap, data (0,0) is the bottom-left cell whose label is `none`. The probe was
sitting on the cell it then reported as colliding. Fixed by importing `Text`.

### B. Two ghost collisions from artists that are never painted

    [OVERLAP] '1'   x 'slope 0.91'                        15.34 pt^2  IoU 83.5%
    [OVERLAP] '0.1' x 'leaves its power law at cycle 285'   5.66 pt^2  IoU 12.3%

Both vanished under two filters:

* text artists with `.axes is None` -- matplotlib has no route by which to draw them;
* inset tick labels whose ticks lie outside the inset's own view. One measured at
  **x = -727 px on a 2100 px canvas**: a real extent, no pixels.

Cropping the exact reported overlap rectangle showed only the innocent partner. So the
authority for "is this a collision" is now the **rendered ink**: an overlap counts only if
the overlap strip contains glyph pixels. Final result: **REAL 0, GHOST 0.**

---

## What this episode changes about the process

The audit suite exists because an agent's claims about its own work cannot be trusted. That
reasoning was applied to numbers and not to pixels, because pixels were unreachable, and
"verified" quietly came to mean "measured". Twenty-nine suites passed while five cells were
invisible.

The conclusion is not that the audits were worthless -- they caught phantom connector
crossings, 3.78 pt type, a colorbar tick at y = -130 px, and 27-of-75 missed text artists.
The conclusion is narrower and more useful:

> **A check must be able to fail for the reason the reader cares about.**
> `figaudit` could fail for overlap; it could never fail for legibility.

And a corollary, learned three times in one afternoon: **a checker that produces its own
findings is worse than no checker.** The phantom `x` and the ghost ticks did not merely
waste time -- each one looked exactly like a real defect, and one of them (V3) was written
into a document before it was tested.

## Standing checks added

| check | what it can now fail for |
|---|---|
| `_label_colour` + contrast assertion in `build_master` | a cell label that cannot be read on its fill |
| `assert_glyphs` (existing, now exercised) | a Unicode symbol absent from the face in use |
| `_audit_all_lines_vs_text.py` | any line, guide included, crossing a glyph box |
| `_verify_collisions_by_pixels.py` | a claimed collision with no ink behind it |
| `_unit_test_40x.py`, `_selftest_sweep.py` | a guard that has gone blind |

---

## The TOC renders: a structural defect that no check could see

The master figure's problems were small. The TOC graphic's problem was not: **more than half
the circuit was drawn outside the axes and clipped away.**

The square render showed only M4 and M2. Both buses were sliced at the top edge. The words
"surface" and "eta" appeared as fragments cut by the frame, because their centre was above
the visible area. It read as a broken diagram, and it was: the axes ran 0 to 47.5 in a data
space where the drawing reaches 96.5.

The cause was one line:

```python
ax.set_ylim(0, draw_w * (y_frac * h_cm) / (x_frac * w_cm))
```

This is the correct formula for **equal data units on both axes** -- and it silently assumed
the content would fit an aspect the layout never provided. An 82.5 x 98 unit circuit is
nearly square; the square TOC gives the circuit a 5.2 x 3.0 cm strip, which is 1.7:1 the
other way. The formula was right and the premise was wrong.

**Twenty-nine machine checks passed while this shipped.** They measured point sizes and ink
coverage -- of whatever happened to be in frame. No check asked whether the drawn extents
were inside the view, because until the picture was visible, nobody had thought to ask.

### What the fix broke in turn

Replacing the single data space with per-axis axes-fraction layout fixed the clipping and
introduced four new faults, each caught by looking again:

| fault | cause | caught by |
|---|---|---|
| every box became a huge blob | `rounding_size=0.30` is in DATA units and exceeded the box's own fraction (0.19) | the render |
| badges sat on box borders, 1.33 pt away | the gap was measured against the nominal marker diameter, not the painted disc (marker path + white edge) | a points-based clearance probe, then an assertion |
| "fracture"/"plating" sat on the return conductor | bottom labels hang below their boxes; the conductor runs along the margin | a vertical-clearance assertion at >= 2.5 pt |
| a column of dashes down the knee panel | `set_yticks([])` clears MAJOR ticks only; log minor ticks survived | the render |

The badge case is the most instructive. The first assertion asked *"does the disc fit in the
gap?"* and the answer was yes -- 1.33 pt of clearance. **Fitting is not the same as reading
clearly**: a tag 1 pt from a border looks attached to it, which is exactly what the render
showed. The assertion was rewritten to test a **3 pt visible gap on the painted extent**, and
it then refused to build until the columns moved apart.

### Standing checks added for the TOC

| check | what it can now fail for |
|---|---|
| per-axis physical sizes in `_circuit` | content drawn outside the axes at any aspect |
| badge gap assertion | a tag closer than 3 pt to a box or bus |
| vertical clearance assertion | a label touching the return conductor |
| `minorticks_off()` | stray log minor ticks |
| text/patch-in-axes assertion | any drawn extent outside the frame |

All of these are in `figtoc.py` itself, so `python figtoc.py` refuses to emit a broken
graphic rather than emitting one for a later check to catch.

---

# Round two: the aesthetic redesign, and what "all checks pass" still hid

The user's verdict on the artwork that the previous sections describe was blunt: **it was
ugly**. Not broken -- every one of the checks above passed -- but wrong at the level a
reader cares about. This section records the redesign and, more usefully, the class of
defect that thirty-plus passing suites could not see.

## Why the passing suites were not reassuring

Every check asked a question with a measurable answer: is this text above 6 pt, do these two
rectangles overlap, is this arrow on canvas, does this glyph exist in the face. **None asked
whether the composition read as intended.** A figure can satisfy all of them and still look
like a mid-2000s flowchart, which is what it did:

- panel (a) read as a **2×2 grid of boxes**, not as a circuit -- no wire was straight through
  from top to bottom, so nothing carried the eye;
- the four mechanism boxes were **staggered**, so the two columns had no vertical meaning;
- a **four-entry encoding legend** along the foot restated what the caption already said;
- four **italic chemistry sub-labels** repeated the caption's chemistry;
- the two grey **bus sub-labels floated in the right margin**, detached from the rails they
  describe;
- **badge D dangled below the circuit** with a stub arrow pointing at nothing;
- large **dead space** in the left third of panel (a).

The lesson is the one already learned twice in this project, now with a sharper edge:
**a check must be able to fail for the reason the reader cares about.** "All pass" is a
statement about the checks, never about the figure.

## The redesign

**Panel (a) -- two aligned columns on two rails.** Sources above the surface rail, sinks
between the rails. The mechanism columns are aligned, so the surface rail cuts one straight
wire per column: surface manufactured above, consumed below, the shared variable exactly in
between. That vertical reading *is* the reduction argument and it needs no words.

**Direction now carries the source/sink distinction.** Sources point **into** the surface
rail, sinks point **out** of it and into the eta rail. A reader learns which is which from
the arrows, which is why the encoding legend could be deleted rather than merely shrunk. The
spec's double-encoding requirement is still met -- colour **and** the literal role word.

**Text objects in panel (a): 24 → 19**, and every one of the five removed was redundant:

| removed | why it went |
|---|---|
| 4-entry encoding legend | restated the caption; grammar now carried by position and arrow direction |
| 4 chemistry sub-labels | restated the caption; the bare word *source* / *sink* keeps the double encoding |
| rotated "feedback" label | the filleted return stroke shows a return; naming it explained the drawing |
| "Four mechanisms close four loops..." title | replaced by "One circuit: four loops through two shared state variables", which says what the panel *is* |

**The return is filleted.** Three butt-jointed 90° segments read as a bounding box -- the
flowchart tell. Each corner is now a quadratic tangent to both straights (radius 0.026).

**Bus glosses moved inside their own rails**, right-aligned on the rail's midline. They were
loose grey prose in the margin; inside the bar they read as that rail's caption. The rail
name moved left to make room, so each bar is one tidy line: name, then gloss.

**Badges centred ON their edges.** They used to sit beside a mechanism box, which marked a
*mechanism*; A–D name *pathways*, and a pathway is an edge.

**Loop D became a mid-panel input.** It used to hang below the circuit as a loose badge with
a stub arrow into nothing. Entering the eta rail from below, between the two sink columns,
makes it a genuine third input to the shared variable.

## Five defects the redesign exposed, all invisible at preview resolution

Reading a 1401 px preview of a 17.8 cm figure is reading it at about 200 dpi -- enough to see
that something is wrong, not enough to see what. Each of these was found only by cropping the
600 dpi render at 1:1 and then looking:

### R1 -- the hatch ran through the word "none"

The two "no knee" cells are hatched to say *deliberately absent*. At 600 dpi the default hatch
stroke crossed the word, so the cell read as **damaged** rather than as a result.

Root cause, and it took two attempts: **a patch's `lw` does not control its hatch.**
`lw` sets the *border*; hatch weight comes from `rcParams["hatch.linewidth"]`. The first fix
set `lw=0.45` and thinned the border while leaving the hatch at its default ~1.0 pt, which is
why the stripes still looked heavy. Correct fix: set the rcParam around the patch, hatch at
0.35 pt, and draw the border in a second, hatch-free patch so the edge stays crisp.

An opaque pad behind the word was tried and **removed**: it punched a rectangular hole in the
texture that looked like a second defect. At 0.35 pt the hatch is light enough that the word
reads straight on top of it.

### R2 -- two identical rows of tick labels

Panel (b)'s inset sat at `y=0.075` with no frame, putting its own "10 100 1000" tick row in
the same band as the parent axis's "10 100 1000". Two identical runs of numbers stacked 1 mm
apart reads as a printing fault. Fixed by lifting the inset clear of the axis labels,
shaving its height, and giving it a white face with a hairline frame.

### R3 -- vertical guides ran through the inset

The knee and EOL guides were full-height `axvline`s, so both ran down through the dLLI/dn
inset. Only the knee needs a guide, and it does not need to span the whole axes: it now runs
from the curve at cycle 530 up to the tag row, clearing the inset entirely. The EOL marker is
the curve leaving the top of the axes -- a guide there was drawable but redundant.

### R4 -- the callout was heavy, then it was hidden

"leaves its power law at cycle 285" was a three-line block with a long curved leader: the
heaviest text on the panel, explaining in prose what the intersection marker shows. Cut to
one line, "departs at 285", with a straight leader.

The replacement's first anchor, x=21, put it **under the legend box** -- only the tail "85"
survived, visible in the crop. The legend occupies the upper-left down to about x=60 in data
units, so the label moved to x=115, in the band above the pre-knee curve.

### R5 -- the TOC badges did not fit, and neither did the outer conductor

At 5.5 cm the gap between a box edge and a rail edge is 0.483 cm. Measured side clearance for
a loop badge was **3.00 pt** while the arrowhead alone needed **4.5 pt**, so each connector
read as shaft → black blob → detached arrowhead. **The badges were removed from both TOC
renders**, not shrunk: at that size they cost more than they paid, the caption does not use
the letters, and the two-colour grammar plus the two named rails carry the argument. The
master keeps them, where there is room.

The return conductor also left the eta rail, ran **right** past it to x=0.958, jogged down,
then came all the way back left -- three of four segments redundant, and the jog read as a
printing fault. Rebuilt as one stroke with one elbow and a single bottom margin, filleted in
cm-space so the corner is not sheared by the axes' 1.8:1 anisotropy.

## The check that could have caught all of this, and now exists

The deepest gap was structural: **`_check_numbers.py` never read the figure.** It compared
literals in its own file against the model, so changing a printed label left every assertion
green. It now builds the figure into a throwaway directory, pulls every string back out of
the rendered `Text` artists, and requires the numbers the model asserts to be **present in
pixels** -- plus a cap on panel (a)'s text count, so the redesign cannot silently grow its
annotations back.

It was crashed on purpose before being kept: a corrupted `"slope 0.91"` is now caught with
`THE FIGURE DOES NOT CONTAIN THIS STRING` and exit code 1. A guard never observed to fail is
indistinguishable from one that cannot.
