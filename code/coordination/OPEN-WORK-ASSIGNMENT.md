# Open work in the paper, and who can close it

Written before delegating, because a checklist row saying "TODO" is not the same as
work that is still needed: **most of the 27 TODO rows are already satisfied by files
that exist.** The real open work is narrower, and it clusters into four problems plus
three scientific gaps.

## What the checklist claims vs. what is true

| Checklist status | Count | Reality |
|---|---|---|
| ✅ DONE | 11 | correct |
| 🟡 TODO | 27 | **~10 are stale** — the artefact exists and a script proves it |
| ⚠️ VERIFY | 3 | genuine |
| 🟠 RECOMMENDED | 1 | genuine |

Rows 5.1, 5.2, 5.3, 5.4 are already machine-verified by `08-manuscript/_conformance.py`
(58/58 checks, 42 references, 1..42 all cited, 0 citation-after-punctuation violations).
Rows 4.2 and 4.8 describe the manuscript and SI, both of which exist. Those rows need
**re-verification, not writing** — and a checklist that says TODO about a finished
artefact is itself a defect, because it makes the author redo work.

## The genuine blockers, which no agent can close

| Item | Row | Why |
|---|---|---|
| Funding statement / grant numbers | 6.6 | Fabricating a grant number is misconduct |
| Data Reporting Checklists D + E | 6.1–6.2 | The official forms exist only inside Research Exchange |
| **AI-use disclosure + CRediT** | **4.2b, 6.4** | **Reopened 2026-11-06.** The authors deliberately removed both sections from the manuscript; reinstating them is the authors' decision, and Wiley expects the AI disclosure whenever AI tools were used. The drafted text sits in [09-submission/ai-use-disclosure.md](../09-submission/ai-use-disclosure.md) — pasting it in is minutes of work, but the choice is not an agent's |
| ~~**A predictions table for §7**~~ | — | ✅ **RESOLVED 2026-11-07 — it was never an SI gap.** The "Table S2" pointer was a corrupted reference to a **main-text Table 2** that had been lost at the 4-figure cut. `06-proposal/figure-plan.md` states the intended inventory outright (*"2 tables in main text (Table 1 ledger/fingerprints, Table 2 falsification matrix), Table S1 in SI"*) and gives Table 2 a full 4-column spec; `01-scope/coupling-framework.md` §5 supplies the five rows. The table has now been rebuilt from that record as a real `table*` in §7 (`_assemble.py`), the pointer corrected to `(Table 2)`, and the caption added to the legends block. Cost **+10 net words** (legends 160→170) against the budget, since table bodies are not counted. A `banned dangling Table S2` check in `_conformance.py` now fails if the bad pointer returns (falsification-tested). Record: `09-submission/author-only-actions.md` §5.3 |

Plus: Zenodo DOI (6.3), whether a preprint exists (8.3), APC choice (8.7), the act of
submitting (8.1), and the author assertions 2.5/2.6/7.5/8.3/8.4 (a file can hold a name
but not a consent). Everything else can be advanced by an agent.

**Author identity (rows 2.1–2.3) is NO LONGER a blocker** — it was supplied 2026-11-06 and
is proven in two places: `09-submission/title-page.md` §2 and the rendered
`08-manuscript/wiley-njd/batt-main.pdf`. An earlier version of this table listed it as a
genuine blocker; that row had gone stale, which is the exact defect this dossier warns about.

---

## Package A — figures, generated and verified

**Closes rows 3.5, 4.3, 4.4, 4.5. Owner: `si-writer`.**

Four display items plus the TOC image. Three are *derivable from code and documents
already in the repository*:

- **Figure 3** (model sweeps: rate / temperature / R0, the knee, coupled-vs-severed) —
  `06-proposal/_support/loopA_model_v4.py` already computes every number
  (knee 530, EOL 1044, exponents 0.91 / 2.43, severed → None through 6000).
  It has no plotting code. Add it.
  > **NUMBERING CORRECTED 2026-11-04.** This line said "Figure 2", which was wrong. The
  > manuscript legends, `10-si/S5-figure-specs.md` and `figure-plan.md` L84 all agree:
  > **Fig 2 = ledger diagnostic, Fig 3 = the knee bifurcation / model sweeps.** The brief was
  > wrong and `si-writer` correctly built to the manuscript rather than to the brief. Files are
  > `fig2-ledger-diagnostic.*` and `fig3-knee-bifurcation.*`.
- **Figure 4** (decision tree) — `10-si/S4-decision-tree.md` specifies the tree.
- **TOC image** — `09-submission/toc-graphic.md` has the text (47 words / 303 chars) and
  both permitted geometries (5.5 × 5.0 cm or 11.5 × 2.5 cm).
- **Figure 1** exists only as an un-inspected draft (`figure1_draft.png`). No agent can
  *look* at it; an agent can regenerate it to the written spec and prove dimensions and
  font sizes by script.

**Hard constraint: the journal forbids AI-generated artwork.** Every figure must be
schematic or data-driven — never illustrative or AI-imaged. matplotlib is available
(3.10.1).

**Deliverable:** `research/11-figures/` containing each figure as PDF + PNG,
`figure-spec-check.py` asserting dpi ≥ 300, width 8.4 or 17.8 cm, min font 6 pt, and a
README distinguishing machine-verified properties from what a human must eyeball.

## Package B — verification harness for the incoming full texts

**Closes row 5.6. Owner: `lit-synth`.**

The author is fetching 13 PDFs (see `07-final/FULLTEXT-REQUEST-LIST.md`: 5 Tier-1,
5 Tier-2, 1 critical uncited, 2 closed). The moment they land, each claim must be checked
against a page. Build the machinery now so the check is mechanical, not a scramble:

- a claims register: for each paper, the exact sentence it supports and the number to find
- `verify_claims.py`: extracts text from a supplied PDF, greps for the claimed number,
  reports FOUND / NOT FOUND / AMBIGUOUS with the surrounding passage
- a results template recording page number + verbatim quote per verified value

**Critical honesty requirement:** the verdicts must be empty until the PDFs exist. A
harness that pretends to have checked is worse than no harness. The README must say so
in its first line.

**Deliverable:** `research/12-fulltext-verification/` with `claims-register.csv`,
`verify_claims.py`, `README.md`, and a `_selftest.py` that runs the extractor against a
synthetic PDF containing a known number, and against one where the number is altered —
the second must fail.

## Package C — rebuild the submission checklist from evidence

**Closes the stale rows. Owner: `submission-packager`.**

Rebuild `09-submission/submission-checklist-final.md` so every verdict is recomputed by a
script rather than inherited from the last edit. Specifically:

1. Rows 5.1–5.4, 4.2, 4.8: re-verify against the artefacts; mark DONE with the check named.
2. Draft the CRediT author-contributions **template** (row 2.6) with placeholders — this is
   a form, not a fact, so it can be drafted but not filled.
3. Sweep for self-declaration obligations (row 7.5): list what must be declared about
   related papers and preprints.
4. Produce a one-page "what only the author can supply" sheet, so the author is not asked
   to redo finished work.

**Deliverable:** revised checklist + `09-submission/check_checklist.py` that recomputes the
stale rows and fails if any row marked DONE is not backed by a passing script.

## Package D — the manuscript gaps that need no new PDFs

**Owner: `manuscript-writer`.**

1. **§3 is thin: 191 words against §4's 746.** The four-family section does less work than
   its importance warrants, and the budget has **126 words of slack** (3,374 / 3,500). A
   Perspective that introduces four mechanism families and then gives them a quarter of the
   space of the loops section is mis-proportioned.
2. **Figure legends describe four figures that do not exist yet.** Reconcile them with
   whatever Package A actually produces.
3. Keep the counted total ≤ 3,500 including abstract and legends; references are excluded.

**Deliverable:** revised §3 and reconciled legends, with `_count.py` and `_conformance.py`
still passing.

## Package E — the weakest number in the project

**Owner: `mech-cathode`.**

The entire shortfall argument runs on **5 ppm/cycle**, and the only source for a ppm/cycle rate
range is Bhandari & Bhattacharya 2016 (`10.1149/2.0101614jes`), which the dossier itself
flags as still open. Build the sensitivity analysis *now*, before the PDF arrives:

- re-derive the shortfall across a range of rates (1, 5, 10, 50, 200 ppm/cycle)
- state at what rate the conclusion changes from catalytic to stoichiometric
- rewrite the manuscript sentence so it is true across the range, or state it as
  regime-dependent
- identify what would have to be true for the thesis to fail

If the real rate is 50 ppm/cycle, the shortfall drops to 4× and the paper's central
quantitative claim weakens materially. Knowing this in advance is the point.

**Deliverable:** `05-gap-and-methods/dissolution-rate-sensitivity.md` + a recomputation
script, and the exact manuscript replacement sentence.

## Package F — the strategic uncertainty

**Owner: `journal-scout`.**

1. Whether a Perspective in *Batteries & Supercaps* requires a pre-submission enquiry
   (checklist row 8.8, RECOMMENDED). This is the largest strategic risk left: if
   Perspectives are invited-only in practice, a direct submission wastes weeks.
2. Draft the one-paragraph enquiry email.
3. **Keyword risk:** the five proposed keywords include `interfaces`, the highest-risk of
   the set and unconfirmed in any catalogue. Propose a replacement drawn only from language
   the journal uses about itself, and record the evidence.

**Deliverable:** `02-journal-fit/perspective-enquiry.md` and
`02-journal-fit/keyword-analysis.md`.

## Package G — the arm that turned out to be supported (DONE; premise was wrong)

**Owner: `mech-degradation`.** ✅ **COMPLETE.**

**⚠️ The briefing premise was wrong, and the agent correctly refused to act on it.** The task
said "Loop D currently has zero direct literature support — either find support or recommend
demotion." Searching *outside* the 155-entry pool found the support the dossier had declared
absent, so no demotion was manufactured:

- `10.1126/science.aee1630` (*Science* 2026) — SEI-driven electrolyte consumption → dry-out →
  cycle-life prediction is its **central claim**, under ultra-lean electrolyte. Not in our pool.
- `10.1002/advs.202405897` (*Adv. Sci.* 2024) — **the controlled electrolyte-quantity study the
  dossier said was missing**.
- `10.1126/science.adv1739` (*Science* 2025) — electro-osmotic drag, a better transport link.

**Outcome instead of demotion:** manuscript grade changed from `[emerging]` /
"supported mostly by modeling" (that sentence was FALSE — a referee would have checked it
against either source) to **[mechanism supported; feedback untested]**, with both papers cited.

**P4 was also too strong and possibly wrong in sign.** Lechtenfeld found irreversible Li loss and
interphase thickening *increase* with electrolyte volume — an additive-inventory artefact that
largely vanishes when additive mass is held constant. P4 now carries "at fixed total additive
mass". This strengthened the paper: Loop D is no longer untested speculation but a mechanism with
a known confound and a designed test.

**What remains genuinely open:** the feedback closure and P4. Evidence against is
*counter-evidence*, not silence — `10.1021/jacs.5c09562` (dead-Li/SEI "sudden death") and
`10.1002/advs.202502336` (charge-transfer on knee detection). No paper measures knee position
against electrolyte loading.

**Lesson recorded:** "no support exists" is the fastest-decaying claim in this project. Searching
a fixed pool and finding nothing establishes a fact about the pool, not about the literature.

Also: verify that Figure 3's numbers are *reproducible from the script* rather than copied
from the dossier, since it will become the paper's only computational evidence.

**Deliverable:** `03-mechanisms/M5-loop-d-support.md` with a verdict and a recommendation,
plus a reproducibility note for the figure numbers.

## Package H — integrate the results (depends on A–G)

**Owner: `proposal-writer`.**

Update `07-final/DOSSIER.md` and `07-final/TOM-TAT-TIENG-VIET.md` to reflect what A–G
actually produced, extend the audit suite, and re-run it. Depends on the others completing.

---

## The one judgement call I am not making

The pre-submission enquiry is RECOMMENDED, not required, and it is the author's decision
whether to send it before or instead of a direct submission. F handles the drafting; the
send is theirs.
