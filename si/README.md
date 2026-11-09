# Supporting Information — build and reading guide

## The only deliverable

**`SI.pdf`** is the Supporting Information. It is built from the markdown sources in this
directory and is the file to upload.

## Build

```
python build_si_tex.py          # si-contents.md + S1..S4  ->  SI.tex  ->  SI.pdf
```

Requires TeX Live on `PATH` (`D:\texlive\2026\bin\windows` on this machine).

`build_si_tex.py` exits `0` on success and carries its own verification pass. It checks, and
fails the build on: markdown residue in the output, unmapped characters, British spellings,
self-referential register, rhetorical questions, and ablation-table inconsistencies. Each of
those guards has been falsification-tested by injecting the defect it targets.

Exit codes: `0` = built and verified; `1` = verification failed (the message names the defect).

## Sources, in assembly order

| File | Contents |
|---|---|
| `si-contents.md` | Opening problem statement, the four loop definitions, which question each part answers, contents table, conventions, glossary |
| `S1-box1-model.md` | The Loop-A reduced model: state variables, update equations, plating threshold, ablation, sensitivity, limits. Tables S2–S5 |
| `S2-derivations.md` | The four coupling ratios and the arithmetic behind them. Equations S2.E1–S2.E10 and S2.11–S2.24 (sections S2.0–S2.10 keep a separate numbering) |
| `S3-table-S1-measurement-matrix.md` | Table S1, the 20-row mechanism × measurement matrix, and the reporting checklist |
| `S4-decision-tree.md` | The diagnostic decision tree, branches B0–B7 |

`S5-figure-specs.md` is **not** part of the SI. The SI carries no supplementary figures; it
refers to the main text's Figure 1.

## Retired files — do not read, do not rebuild

The SI was once assembled as a Word document. That pipeline is gone and the artefacts below
are **stale**; reading them will describe a document that no longer exists.

| Retired | Why it is stale |
|---|---|
| `build_si.py` | Built the docx. Superseded by `build_si_tex.py`. |
| `SI-combined.md` | Concatenation for the docx pipeline. Not the SI. |
| `SI-combined.docx` | The old Word deliverable. Hours older than the current sources. |
| `SI-completeness-check.py` | Verifies the docx. Exits `3` ("source numbering defective") when the docx is stale, which is its documented signal that the pipeline is retired rather than that content was lost. |

## Editing rules

- The manuscript is American English; so is the SI. `-ise`/`-isation` spellings fail the build.
- Each section opens with the physical situation or the question, states its conclusion, and
  only then gives the arithmetic. A section that opens with a constraint or a definition will
  not survive a cold read.
- No self-referential register: not "the paper", "this SI", "we", "our".
- No rhetorical questions in prose.
- Parameters are typeset as `*b*_fresh`, not as code spans. A code span containing `^` renders
  the caret literally.
- The ablation table appears twice (S1.5 and Table S3 part B). **Both copies must agree.** The
  model fixes the answer: `f_dead = 0` forces `d_dead = 0`, removing both coupling terms, so
  that row has no knee; severing only `b_fresh` delays the knee to 670 rather than removing it.
  This exact defect survived one whole rewrite because only one copy was fixed, which is why
  the build now gates it.

## Verifying a change

```
python build_si_tex.py                      # exit 0
python ../../08-manuscript/_conformance.py   # manuscript only, still must pass
```

To confirm a claim about a number, check it against the model itself rather than against the
prose: `research/06-proposal/_support/loopA_model_v4.py` is the authoritative implementation.
`simulate()` takes parameter overrides, so e.g. `simulate(1.0, 1.0, p={"f_dead": 0.0})`
reproduces the ablation row directly.

## Register: how the prose must read

A referee rejected the writing four times as "flowery" (van vo) while the
vocabulary and structure were already correct. The defect was emphasis used to
perform a finding rather than report it. It is now measured, not argued.

`research/08-manuscript/_register.py` counts ten mechanical signatures per 1000
prose words: bold emphasis, italic emphasis, em-dash, rhetorical contrast,
metaphor, self-commentary, editorial adverb, intensifier, fragment, rhetorical
question.

`build_si_tex.py` carries the same check as a build gate
(`register_problems`). It runs on the **raw markdown sources**, not on the
converted LaTeX: conversion turns `**` into textbf, so a check on the output
would always pass. That mistake was made and caught by falsification-testing the
gate: injecting a bold sentence and an italic word produced a clean PASS until
the check was moved to source scope.

Allowed, and therefore not counted:
  - bold cross-reference labels: **B7**, **M2**, **D2**
  - run-in headings at the start of a line: **The derivation.**
  - italic symbols: *R*, *f*, *N*, *d*
  - italic acronyms: *LLI*, *SEI*
  - latin terms: *in situ*, *operando*

Everything else loses its markers. When stripping emphasis from a source, use
`_strip_emphasis.py --apply`, which is idempotent and reaches a fixed point.

Note on the manuscript pipeline: `_manuscript.src.md` is the input that
`_md2tex.py` converts; `manuscript.md` is the output that `_count.py` and
`_conformance.py` check. Editing only `manuscript.md` leaves the PDF unchanged,
and `_sync_check.py` will still report IN SYNC because it compares content
markers rather than full text. Port edits to both files.

### The fourth-round axis: essayistic architecture

Four rounds of editing vocabulary, emphasis and structure all failed, because
none of them measured the actual defect. The prose still read as an essay: it
announced its own outline, ranked its own material, and carried a narrative
example from abstract to conclusion. A report does not do these things.

The gate now checks five signatures on the raw sources (`register_problems` in
`build_si_tex.py`, plus `ESSAY` in `research/08-manuscript/_register.py`):

  structure-announcement  "Three conclusions follow."  "the four parts"
  ordinal-roadmap         "The first step is ... The second is ..."
  self-ranking            "the decisive test"  "strongest available evidence"
  narrative-character     "the cell that dies at cycle 700"  "cell designer"
  editorializing          "deliberately"  "worth noting"  "we stress"

The rule for structure-announcement was deliberately narrowed after the first
run: a count that names the DOCUMENT'S OWN ORGANISATION is a defect, while a
count of technical objects is content. "The four parts answer four questions"
is a defect; "three questions a degradation paper must answer" is not.

Every signature was falsification-tested by injecting it into a clean source and
confirming the build exits 1: 4/4 caught, and the clean baseline returns no
findings. A gate that only prints PASS proves nothing.

### The fifth-round axis: epistemic humility

The referee's last complaint was that the prose is "too assertive and too AI".
That is not a vocabulary defect. It is an epistemic one: the paper stated
conclusions as though they were established, when several are arguments.

Measured with `research/08-manuscript/_humility.py` as the ratio of hedges
(may, suggest, appear, typically, consistent with) to boosters (must, never,
cannot, prove, demonstrate, clearly). Experimental academic prose normally sits
at or above 1.0. The manuscript was at **0.20** -- five assertions per
qualification -- and SI section S3 at **0.00**.

After this round: manuscript 0.43, S1 0.33, S2 0.38, S3 0.22, S4 0.50. Below
1.0 is defensible for a Perspective, which must advance claims; the point is
that qualification now exists where the claim is not measured.

`build_si_tex.py` gates this with two thresholds, both falsification-tested by
deleting every hedge from all five sources and confirming exit 1 with four
findings: a per-file floor of 0.15 (fires only above 15 boosters), and an
SI-wide floor of 0.30. A file that argues without once qualifying itself fails.

The same round removed claims about other people's work stated without
attribution ("the field did not mis-measure, it mis-partitioned" -> "so the
field may have mis-partitioned"), absolutes the measurement cannot carry
("can never become substantial fracture" -> "is unlikely to become"), and
self-narration of the author's own honesty ("stated, not papered over",
"not hand-waving", "not being smuggled in").
