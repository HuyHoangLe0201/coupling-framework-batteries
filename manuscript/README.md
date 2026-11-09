# 08-manuscript — final counts and audit trail

**Deliverable:** [`manuscript.md`](manuscript.md) — Perspective for *Batteries & Supercaps*.
**Source of truth:** [`_manuscript.src.md`](_manuscript.src.md) holds the prose with `[[bibkey]]`
citation markers. `manuscript.md` is **generated** from it — never edit the numbers in the
output by hand; edit the source and rebuild.

**LaTeX deliverable (added 2026-11-06):** [`wiley-njd/batt-main.tex`](wiley-njd/batt-main.tex) +
compiled [`wiley-njd/batt-main.pdf`](wiley-njd/batt-main.pdf) — the same manuscript in the
official Wiley NJD v5 template (AMA references, Times, two columns, TeX Live 2026 on `D:`).
The markdown remains the source of truth: `_md2tex.py` converts it and `_assemble.py` emits
the `.tex`, so edits to the prose still happen here and are then re-rendered. Full build
notes, template provenance and the three class patches live in
[`wiley-njd/README-BUILD.md`](wiley-njd/README-BUILD.md).

**`_build.py` does NOT update the LaTeX. This catches everyone once.**
`_build.py` resolves citations and counts words in `manuscript.md`; it never touches
`wiley-njd/batt-main.tex`. So editing `_manuscript.src.md` and running `_build.py` leaves
the PDF showing the **old** prose while every gate still passes — the gates check
`manuscript.md` and the PDF separately, so both look healthy. This actually happened on
2026-11-07: a corrected SI pointer was in the source and in `manuscript.md`, the PDF still
printed the old one, and only a text extraction from the PDF revealed it.

The full chain, in order, from the repository root:

```powershell
cd research/08-manuscript
python _md2tex.py           # _manuscript.src.md -> _converted-body.tex
python _assemble.py         # -> wiley-njd/batt-main.tex
cd wiley-njd
pdflatex -interaction=nonstopmode batt-main.tex
bibtex batt-main
pdflatex -interaction=nonstopmode batt-main.tex
pdflatex -interaction=nonstopmode batt-main.tex
python _layoutcheck.py            # fails the build on layout/metadata defects
python _layoutcheck_selftest.py   # proves the guard still catches its defects
python _verify_pdf.py             # element/wording checks, 42 refs
```

**After any prose edit, verify the PDF itself, not just the source.** Extract the text and
grep for the specific string you changed; a passing gate suite is not evidence that the
rendered document reflects the source.

## 1. Final counts

| Component | Words | Note |
|---|---|---|
| Abstract | **185** | journal cap 200 |
| Body prose §1–§8 | **3,125** | plan 2,420 — see §3 |
| Display-item legends (Table 1 + Table 2 + the single Figure 1) | **170** | one legend for a four-panel mechanism figure, plus the two table captions. The 45-w internal allocation is **not a journal rule** — the Notice caps the article in its entirety. |
| **COUNTED TOTAL** | **3,480** | **ceiling 3,500 — 20 words of slack** |
| References | 42 entries | **excluded from the count** |

**The manuscript is at 3,480 words against a 3,500 ceiling, so the escape hatch
in the cover letter is NOT invoked and must be removed from it.** The submission is
inside the stated Perspective limit on the corrected counting rule. **The remaining
slack is 20 words**, so any late integration edit must be matched by an equal cut —
and the figure legend is already the largest single legend the budget allows.

**Both counters must agree and the build proves it every run.** `_build.py` now executes
`_count.py` and compares the two totals; it prints `Cross-check: _count.py agrees (3480)`.
It previously compared against a hard-coded `_EXPECTED = 3449` that had gone stale and
emitted a false `+35` warning while the two counters actually agreed — a hand-maintained
duplicate of the answer is not a cross-check. If you change the prose, both counters move
together and need no edit; if the `Cross-check` line ever disagrees, one counter is wrong.

**House style is American English, and nothing enforces it automatically.** A spelling
normaliser exists at `00-coordination/_americanize.py` with a correct pair table
(including `metre`→`meter` and `tunnelling`→`tunneling`), but it has **no `__main__`
block and is called by no build script** — it is orphaned, so it has never run. That is
how `nanometre` (×2) and `tunnelling` survived every build in the Figure 1 legend until
2026-11-07, when they were fixed by hand. `_count.py` gates only `ageing`, which is
the one pair that was hard-coded. **Do not assume a normaliser has run.** If a British
spelling matters, either add it to the `_count.py` housekeeping gate or wire the
normaliser into `_build.py`; a helper script that nothing invokes is not a guard.

### The paper has ONE figure

As of 2026-11-06 the article carries a **single** display figure
(`research/11-figures/figure-mechanism.pdf`, 17.8 × 16.2 cm), which also provides
the TOC graphic via a separate condensed render. The former Figures 1–4 were
retired. The figure is a **mechanism figure** and carries **no computed result**:
**(a)** a section through the cell marking where each of the four mechanisms acts,
**(b)** the interphase as a leaky bilayer rather than a blocking slab, **(c)** the
coupling of the four mechanisms through two shared state variables, and **(d)** the
ledger of what closes each loop and what caps it.

**The two computed panels that used to be here are gone by instruction.** The
coupled-vs-severed LLI plot and the C-rate × SEI-growth operating map are results;
a mechanism figure that carries results has stopped being a mechanism figure. They
now live in the SI, still generated from the same model.

Consequences a future editor must not undo:

- The figure legend is one paragraph, not four. Its last sentence about the severed
  comparison holding "at 0.5 and 1 C but not 2.0 C" is **required** — an automated
  guard in `_sync_check.py` asserts that string.
- Prose that used to cite Figure 2 (the ledger diagnostic) now cites **Table 1**; the
  three-channel trajectory idea is carried by Table 1 and Table S1, with no figure.
- Prose that used to cite Figure 4 (the decision tree) now cites **S4 in the
  Supporting Information**. The tree is not in the main text any more.
- The former Figure 3 content is **not a panel of the figure at all** any more: it is
  **SI text**, and `figure-spec-check.py` fails the build if a result quantity reappears
  in `figmech.py`.

## 2. Counting method

Whitespace tokens after stripping markup (`<sup>`, `**`, `*`), with section headings
excluded. Produced by [`_build.py`](_build.py), which prints the table above on every run:

```powershell
python research/08-manuscript/_build.py
```

The counted scope is **abstract + body prose + display-item legends**. Per the Lead's
correction (2026-11-04), the **reference list is excluded** from the 3,500-word
"in its entirety" figure. The Notice-to-Authors phrase "including 3–8 display items"
disambiguates display items only and does not extend to references.

## 3. Why body prose is 3,125 and not the 2,420 originally planned

The 2,420 figure was derived when the reference list was still believed to consume
~720 words of the 3,500. Once references were correctly excluded, that ~720 words of
headroom returned to the argument. The Lead explicitly directed restoration of prose
that had been cut on the false premise — chiefly §1 (lead-question paragraph and the
Attia/Yu differentiation), §4 (Loop B correlated quartet, Loop C two-regime split),
§5 (why a smooth system yields a sharp transition), §6 (the three confounds), and
§8 (the reporting-set justification).

A further pass (Package D, task-13) fixed a proportional defect: **§3 had fallen to
191 words against §4's 746** — a ratio of 0.26, when §3 is where the paper's central
claim lives. §3 was rebuilt by adding the missing argument, not by padding: an
operational definition of independence and its
refutation, and a justification for why the reduction to two state variables is
*forced* rather than merely convenient. **Current measured values: §3 = 288, §4 = 734,
ratio 0.39** — quote these from `_build.py`, not from this sentence, which will drift.

**The original per-section allocation in `00-coordination/word-budget-contract.md`
is superseded for §1, §3, §4, §5, §6, §7 and §8 — deliberately and by Lead decision, not
by drift.** The Lead confirmed the distribution is editorial judgement and will not
re-impose the old table. `_build.py` still prints the old per-section budgets as a
reference line and will flag those sections "OUT OF BAND"; that warning is expected
and must **not** be "fixed" by cutting the restored prose back. The only binding
constraint is the 3,500 ceiling, met with 16 words to spare.

## 4. Bibliography

- **42 references**, numbered in order of citation, verified ascending 1..42 with no
  gaps, no duplicates, and every listed reference cited in text. (This section said 40
  for a while after the pool grew; the number is checked by `_build.py`, `_count.py`,
  `_conformance.py` and `wiley-njd/_layoutcheck.py`, all of which read 42.)
- Each entry **includes the article title**, as required by the journal style notes
  (`02-journal-fit/batteries-and-supercaps-scope.md` §3.2: "article title included").
- ≤6 authors listed, otherwise first 6 + "et al."; 2022+ uses eLocators, ≤2021 page ranges.
- Every DOI verified against Crossref/OpenAlex. Reference-metadata corrections found:
  - **Dubarry, Truchot & Liaw 2012** is *J. Power Sources* **219**, 204–216 — **not**
    217, 239–250 as first supplied. The DOI metadata is authoritative and is what the
    manuscript uses. The paper has **three authors** (M. Dubarry, C. Truchot, B. Y. Liaw);
    citing it as "Dubarry & Liaw" omits Truchot and is an author-credit error.
  - Gilbert 2017's Mn-free control is **NCA**, so it changes Ni and Co as well as Mn;
    the manuscript states this limitation where the ~10² estimate is cited.
  - `raj2020investigation`, `mndezcorbacho2024dest` and `dechent2021estimation` had stray
    `**` inside the BibTeX title fields; corrected in `references.bib`.

## 5. Negative-claim policy (applies to all future edits)

**No "novelty by absence" claims.** Phrases such as "never been measured", "has not been
quantified", "unexplored" and "first time" are forbidden without explicit Lead approval.
They decay fastest: the Gilbert 2017 ~10² estimate and the Tornheim 2026 parasitic-current
measurement both surfaced late and each falsified a draft sentence. The paper now frames
its contribution as **magnitude and scaling law**, not existence, and `_build.py` fails
loudly on `negative novelty claim`.

## 6. Scripts (audit trail)

| Script | Purpose |
|---|---|
| `_build.py` | **authoritative.** Resolves `[[key]]` → numbered citations, regenerates the reference list from `references.bib`, prints counts + integrity probes |
| `_manuscript.src.md` | prose source with citation markers |
| `_count.py` | independent section counter and citation-order check |
| `_verify.py` | DOI/metadata cross-check of the reference list against `references.bib` |
| `_refs.py`, `_renumber.py`, `_recover.py` | one-off refactoring passes (kept for provenance) |
| `_conformance.py` | hard-requirement checklist |
| `_gilbert.py`, `_gilbert_abstract.txt` | retrieval and verification of the Gilbert 2017 abstract |

## 7. Protected blocks — all present

1. §1 TGC empirical card (Fang 2019, DOI 10.1038/s41586-019-1481-z; unreacted Li⁰ vs interphase-bound Li⁺; "mis-partitioned").
2. §1 margins paragraph (ratios 1–10, never 10⁻²/10⁴; co-optimized thresholds; well-designed cells most susceptible).
3. §5 *R*\* ≡ (Δ − η_ct)/*j*, and the coupled-vs-severed result (severing abolishes the knee, fade rate intact to 6,000 cycles, robust over a 400-fold parameter change).
4. §7 per-prediction refutation conditions and the B7 protocol ("An insensitive knee is a counterexample, not a null result.").
5. §2 curvature method (*N*_R = (1 − *R*)/*f*; fit *f*(*N*) = *f*₀ + α*N* and report α, not the slope).

### Gates must test substance, never the markup of the defect

A recurring failure mode in this project: a hard-requirement check was written
to freeze a string, and the string was itself the defect. When the prose was
corrected the gate failed, which then looked like a regression. This happened
four times in one session:

| Gate | Froze | Why it was wrong |
|---|---|---|
| `_conformance.py` | `**[mechanism supported; feedback untested]**` | Bold self-grading with no rubric was the worst register defect in the paper. Now the rubric is stated once in §4 and the grade is plain prose; a second check fails if bold grading ever returns. |
| `_conformance.py` | `*most* susceptible` | An italic intensifier inside an argument. Now matches `especially susceptible`, which is the claim, without the emphasis. |
| `_layoutcheck.py` | `Channel fingerprints` (Table 1 caption) | A metaphor that told the reader nothing. Now matches the caption's actual content. |
| `_sync_check.py` | `mechanism supported; feedback untested` | Same defect as the first row, caught in a second file. |

The rule this establishes: **a gate may freeze a fact, a number, or a
scientific claim. It may not freeze typography, metaphor, or the author's
self-assessment.** Before adding a check, ask whether the string would still be
correct if the prose around it improved.
